#!/usr/bin/env python3
"""Evaluate new P1v2 predictions and pair them with the frozen CADFit results."""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = ROOT / "ours3/deepcad_style_iou_cd_ir_evaluation_v1"
MANIFEST = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
)
FROZEN_CADFIT = EVAL / "cadfit_comparison_v1/CADFIT_val1000.csv"
sys.path.insert(0, str(EVAL / "evaluator"))
from run_p1_cadfit_val1000 import evaluate, gt_path  # noqa: E402


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = sorted({key for row in rows for key in row})
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def truth(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def valid(row: dict) -> bool:
    return (
        not truth(row["deepcad_invalid"])
        and truth(row["iou_valid"])
        and truth(row["cd_valid"])
    )


def mean(rows: list[dict], key: str):
    return float(np.mean([float(row[key]) for row in rows])) if rows else None


def metrics(ids: list[str], p1: dict[str, dict], cadfit: dict[str, dict]) -> dict:
    p1_rows = [p1[x] for x in ids]
    cf_rows = [cadfit[x] for x in ids]
    pairs = [(p1[x], cadfit[x]) for x in ids if valid(p1[x]) and valid(cadfit[x])]
    p1_common = [x for x, _ in pairs]
    cf_common = [x for _, x in pairs]
    return {
        "N": len(ids),
        "P1_invalid_N": sum(truth(x["deepcad_invalid"]) for x in p1_rows),
        "P1_IR": sum(truth(x["deepcad_invalid"]) for x in p1_rows) / len(ids) if ids else None,
        "CADFit_invalid_N": sum(truth(x["deepcad_invalid"]) for x in cf_rows),
        "CADFit_IR": sum(truth(x["deepcad_invalid"]) for x in cf_rows) / len(ids) if ids else None,
        "strict_common_valid_N": len(pairs),
        "P1_IoU": mean(p1_common, "iou"),
        "CADFit_IoU": mean(cf_common, "iou"),
        "P1_CD": mean(p1_common, "cd_deepcad"),
        "CADFit_CD": mean(cf_common, "cd_deepcad"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--shard-index", type=int)
    parser.add_argument("--num-shards", type=int)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    manifest = [json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    if (args.shard_index is None) != (args.num_shards is None):
        parser.error("--shard-index and --num-shards must be used together")
    suffix = f"_shard{args.shard_index}" if args.shard_index is not None else ""
    if args.num_shards is not None:
        if not 0 <= args.shard_index < args.num_shards:
            parser.error("shard index is out of range")
        manifest = [
            row for index, row in enumerate(manifest)
            if index % args.num_shards == args.shard_index
        ]
    partial = args.out / f"P1v2_val1000{suffix}.partial.jsonl"
    done = {}
    if args.resume and partial.is_file():
        for line in partial.read_text().splitlines():
            row = json.loads(line)
            done[row["case_id"]] = row

    started = time.time()
    for index, row in enumerate(manifest, 1):
        case_id = row["cad_id"]
        if case_id in done:
            continue
        step = args.pred_root / case_id / "pred.step"
        result = evaluate(
            case_id,
            gt_path(row),
            lambda path=step: __import__("cadquery").importers.importStep(str(path)).val(),
        )
        result["source"] = row["source"].lower()
        done[case_id] = result
        with partial.open("a") as handle:
            handle.write(json.dumps(result) + "\n")
        if index % 10 == 0:
            print(f"processed {index}/{len(manifest)} elapsed={time.time()-started:.1f}s", flush=True)

    p1_rows = [done[row["cad_id"]] for row in manifest]
    cadfit_rows = read_csv(FROZEN_CADFIT)
    p1 = {x["case_id"]: x for x in p1_rows}
    cadfit = {x["case_id"]: x for x in cadfit_rows}
    ids = [x["cad_id"] for x in manifest]
    missing = [x for x in ids if x not in cadfit]
    if missing:
        raise RuntimeError(f"frozen CADFit results missing {len(missing)} ids")

    by_dataset = {}
    for source in ("deepcad", "fusion360"):
        source_ids = [x["cad_id"] for x in manifest if x["source"].lower() == source]
        by_dataset[source] = metrics(source_ids, p1, cadfit)
    summary = {
        "schema_version": "P1V2_VS_CADFIT_DEEPCAD_STYLE_IOU_CD_IR_V1",
        "protocol": "frozen DeepCAD-style IoU/CD/IR; IoU/CD on strict common-valid pairs",
        "prediction_root": str(args.pred_root),
        "cadfit_source": str(FROZEN_CADFIT),
        "all": metrics(ids, p1, cadfit),
        "by_dataset": by_dataset,
        "elapsed_sec": time.time() - started,
    }
    write_csv(args.out / f"P1v2_val1000{suffix}.csv", p1_rows)
    (args.out / f"SUMMARY{suffix}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
