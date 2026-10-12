#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MANIFEST = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
)


def block(rows: list[dict]) -> dict:
    scores = [x["op_f1"] for x in rows if x.get("op_f1") is not None]
    n = len(rows)
    return {
        "N": n,
        "parse_valid_N": sum(bool(x["parsed"]) for x in rows),
        "step_valid_N": sum(bool(x["step_ok"]) for x in rows),
        "step_valid_rate": sum(bool(x["step_ok"]) for x in rows) / n,
        "max_length_N": sum(x.get("stop_reason") == "MAX_LENGTH" for x in rows),
        "max_length_rate": sum(x.get("stop_reason") == "MAX_LENGTH" for x in rows) / n,
        "op_f1_available_N": len(scores),
        "mean_op_f1": float(np.mean(scores)) if scores else None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-root", type=Path, required=True)
    args = parser.parse_args()
    manifest = [json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    rows = []
    missing = []
    for source in manifest:
        path = args.pred_root / source["cad_id"] / "row.json"
        if not path.is_file():
            missing.append(source["cad_id"])
            continue
        rows.append(json.loads(path.read_text()))
    if missing:
        raise RuntimeError(f"missing {len(missing)} rows: {missing[:10]}")
    report = {
        "schema_version": "P1V2_CORRECTED_VAL1000_AGGREGATE_V1",
        "manifest_N": len(manifest),
        "row_N": len(rows),
        "missing_N": 0,
        "all": block(rows),
        "by_dataset": {
            name: block([x for x in rows if x["dataset"] == name])
            for name in ("deepcad", "fusion360")
        },
        "fusion_corrected_input_N": sum(
            x["dataset"] == "fusion360"
            and x.get("surface_input_policy") == "corrected_from_source_points"
            for x in rows
        ),
    }
    (args.pred_root / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    (args.pred_root / "rows.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
