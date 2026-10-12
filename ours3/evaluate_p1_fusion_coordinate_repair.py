#!/usr/bin/env python3
"""Evaluate coordinate-repaired P1 against frozen CADFit on Fusion360 VAL44."""

from __future__ import annotations

import csv
import json
import math
import statistics
import sys
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = ROOT / "ours3/deepcad_style_iou_cd_ir_evaluation_v1/evaluator"
sys.path.insert(0, str(EVAL))

import cadquery as cq  # noqa: E402
from run_p1_cadfit_val1000 import (  # noqa: E402
    CFROOT,
    MANIFEST,
    cadfit_names,
    evaluate,
    gt_path,
    inverse_normalize,
    stl_solid,
)

PRED = ROOT / "ours3/p1_fusion360_coordinate_repair_v1"
OUT = PRED / "evaluation"


def finite(row: dict, key: str) -> bool:
    try:
        return math.isfinite(float(row[key]))
    except (KeyError, TypeError, ValueError):
        return False


def stats(values: list[float]) -> dict:
    return {
        "n": len(values),
        "mean": statistics.fmean(values) if values else None,
        "median": statistics.median(values) if values else None,
    }


def main() -> int:
    manifest = [json.loads(line) for line in MANIFEST.read_text().splitlines()]
    manifest = [row for row in manifest if row["source"].lower() == "fusion360"]
    results = {"P1_REPAIRED": [], "CADFit": []}
    for index, row in enumerate(manifest, 1):
        case_id = row["cad_id"]
        repaired = PRED / case_id / "pred.step"
        sid, cadfit_path = cadfit_names(case_id)
        cadfit_input = CFROOT / "input_recovered_v2" / f"{sid}.stl"
        gt = gt_path(row)
        results["P1_REPAIRED"].append(
            evaluate(case_id, gt, lambda path=repaired: cq.importers.importStep(str(path)).val())
        )
        results["CADFit"].append(
            evaluate(
                case_id,
                gt,
                lambda path=cadfit_path, inp=cadfit_input: inverse_normalize(stl_solid(path), inp),
            )
        )
        print(f"[{index}/{len(manifest)}] {case_id}", flush=True)

    OUT.mkdir(parents=True, exist_ok=True)
    for method, rows in results.items():
        keys = sorted({key for row in rows for key in row})
        with (OUT / f"{method.upper()}_VAL44.csv").open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=keys)
            writer.writeheader()
            writer.writerows(rows)

    pairs = []
    for p1, cadfit in zip(results["P1_REPAIRED"], results["CADFit"]):
        if (
            not p1["deepcad_invalid"]
            and not cadfit["deepcad_invalid"]
            and p1["iou_valid"]
            and cadfit["iou_valid"]
            and p1["cd_valid"]
            and cadfit["cd_valid"]
            and finite(p1, "iou")
            and finite(cadfit, "iou")
            and 0 <= float(p1["iou"]) <= 1
            and 0 <= float(cadfit["iou"]) <= 1
            and finite(p1, "cd_deepcad")
            and finite(cadfit, "cd_deepcad")
        ):
            pairs.append((p1, cadfit))
    p_iou = [float(p["iou"]) for p, _ in pairs]
    c_iou = [float(c["iou"]) for _, c in pairs]
    p_cd = [float(p["cd_deepcad"]) for p, _ in pairs]
    c_cd = [float(c["cd_deepcad"]) for _, c in pairs]
    summary = {
        "N": len(manifest),
        "common_valid_N": len(pairs),
        "P1_repaired_invalid_N": sum(row["deepcad_invalid"] for row in results["P1_REPAIRED"]),
        "CADFit_invalid_N": sum(row["deepcad_invalid"] for row in results["CADFit"]),
        "P1_repaired_IoU": stats(p_iou),
        "CADFit_IoU": stats(c_iou),
        "P1_repaired_CD": stats(p_cd),
        "CADFit_CD": stats(c_cd),
        "P1_IoU_wins": sum(a > b for a, b in zip(p_iou, c_iou)),
        "CADFit_IoU_wins": sum(b > a for a, b in zip(p_iou, c_iou)),
        "P1_CD_wins": sum(a < b for a, b in zip(p_cd, c_cd)),
        "CADFit_CD_wins": sum(b < a for a, b in zip(p_cd, c_cd)),
    }
    (OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
