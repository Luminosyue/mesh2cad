#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MANIFEST = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
)
CADFIT = (
    ROOT
    / "ours3/deepcad_style_iou_cd_ir_evaluation_v1/cadfit_comparison_v1/CADFIT_val1000.csv"
)
OLD_P1 = (
    ROOT
    / "ours3/deepcad_style_iou_cd_ir_evaluation_v1/cadfit_comparison_v1/P1_val1000.csv"
)


def truth(value) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def valid_iou(row: dict) -> bool:
    if not truth(row["iou_valid"]) or not row.get("iou"):
        return False
    value = float(row["iou"])
    return bool(np.isfinite(value) and -1e-9 <= value <= 1 + 1e-9)


def valid_cd(row: dict) -> bool:
    return bool(
        truth(row["cd_valid"])
        and row.get("cd_deepcad") not in (None, "")
        and np.isfinite(float(row["cd_deepcad"]))
    )


def valid(row: dict) -> bool:
    return not truth(row["deepcad_invalid"]) and valid_iou(row) and valid_cd(row)


def mean(rows: list[dict], key: str):
    return float(np.mean([float(x[key]) for x in rows])) if rows else None


def stats(rows: list[dict], key: str) -> dict:
    values = np.asarray([float(x[key]) for x in rows], dtype=float)
    return {
        "n": len(values),
        "mean": float(values.mean()) if len(values) else None,
        "median": float(np.median(values)) if len(values) else None,
        "p25": float(np.percentile(values, 25)) if len(values) else None,
        "p75": float(np.percentile(values, 75)) if len(values) else None,
    }


def metrics(
    ids: list[str],
    p1: dict[str, dict],
    cadfit: dict[str, dict],
    frozen_gt_ok: dict[str, bool],
) -> dict:
    p1_rows = [p1[x] for x in ids]
    cf_rows = [cadfit[x] for x in ids]
    pairs = [
        (p1[x], cadfit[x])
        for x in ids
        if frozen_gt_ok[x] and valid(p1[x]) and valid(cadfit[x])
    ]
    left = [x for x, _ in pairs]
    right = [x for _, x in pairs]
    return {
        "N": len(ids),
        "P1_invalid_N": sum(truth(x["deepcad_invalid"]) for x in p1_rows),
        "P1_IR": sum(truth(x["deepcad_invalid"]) for x in p1_rows) / len(ids),
        "CADFit_invalid_N": sum(truth(x["deepcad_invalid"]) for x in cf_rows),
        "CADFit_IR": sum(truth(x["deepcad_invalid"]) for x in cf_rows) / len(ids),
        "frozen_GT_valid_N": sum(frozen_gt_ok[x] for x in ids),
        "strict_common_valid_N": len(pairs),
        "P1_IoU": stats(left, "iou"),
        "CADFit_IoU": stats(right, "iou"),
        "IoU_delta_P1_minus_CADFit": mean(left, "iou") - mean(right, "iou") if pairs else None,
        "P1_CD": stats(left, "cd_deepcad"),
        "CADFit_CD": stats(right, "cd_deepcad"),
        "CD_delta_P1_minus_CADFit": (
            mean(left, "cd_deepcad") - mean(right, "cd_deepcad") if pairs else None
        ),
    }


def triple_metrics(
    ids: list[str],
    old: dict[str, dict],
    new: dict[str, dict],
    cadfit: dict[str, dict],
    frozen_gt_ok: dict[str, bool],
) -> dict:
    common_ids = [
        case_id
        for case_id in ids
        if frozen_gt_ok[case_id]
        and valid(old[case_id])
        and valid(new[case_id])
        and valid(cadfit[case_id])
    ]
    result = {"strict_triple_common_valid_N": len(common_ids)}
    for label, source in (("old_P1", old), ("new_P1v2", new), ("CADFit", cadfit)):
        selected = [source[x] for x in common_ids]
        result[label] = {
            "IoU": stats(selected, "iou"),
            "CD": stats(selected, "cd_deepcad"),
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--eval-root", type=Path, required=True)
    parser.add_argument("--num-shards", type=int, default=8)
    args = parser.parse_args()
    manifest = [json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    p1 = {}
    for index in range(args.num_shards):
        path = args.eval_root / f"P1v2_val1000_shard{index}.partial.jsonl"
        for line in path.read_text().splitlines():
            row = json.loads(line)
            p1[row["case_id"]] = row
    with CADFIT.open(newline="") as handle:
        cadfit = {x["case_id"]: x for x in csv.DictReader(handle)}
    with OLD_P1.open(newline="") as handle:
        old_p1 = {x["case_id"]: x for x in csv.DictReader(handle)}
    ids = [x["cad_id"] for x in manifest]
    frozen_gt_ok = {x["cad_id"]: Path(x["gt_step_path"]).is_file() for x in manifest}
    missing = [x for x in ids if x not in p1 or x not in cadfit]
    if missing or len(p1) != len(ids):
        raise RuntimeError(f"alignment failure p1={len(p1)} expected={len(ids)} missing={missing[:10]}")
    rows = [p1[x] for x in ids]
    keys = sorted({key for row in rows for key in row})
    with (args.eval_root / "P1v2_val1000.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "schema_version": "P1V2_VS_CADFIT_DEEPCAD_STYLE_IOU_CD_IR_FINAL_V1",
        "protocol": "frozen DeepCAD-style IoU/CD/IR; IoU/CD on strict common-valid pairs",
        "alignment_N": len(ids),
        "duplicate_or_extra_P1_N": len(p1) - len(ids),
        "old_P1_IR": sum(truth(old_p1[x]["deepcad_invalid"]) for x in ids) / len(ids),
        "all": metrics(ids, p1, cadfit, frozen_gt_ok),
        "triple_common": triple_metrics(ids, old_p1, p1, cadfit, frozen_gt_ok),
        "by_dataset": {},
    }
    for source in ("deepcad", "fusion360"):
        source_ids = [x["cad_id"] for x in manifest if x["source"].lower() == source]
        summary["by_dataset"][source] = metrics(source_ids, p1, cadfit, frozen_gt_ok)
        summary["by_dataset"][source]["triple_common"] = triple_metrics(
            source_ids, old_p1, p1, cadfit, frozen_gt_ok
        )
    (args.eval_root / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
