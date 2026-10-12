#!/usr/bin/env python3
"""Re-export frozen P1 Fusion360 predictions with an input-derived transform.

The legacy Fusion360 geometry packs contain a stale transform whose source bbox
is 10x smaller than surface_points_source.npy.  Recompute the transform from
the input points and apply its inverse to the canonical P1 DSL.  No GT geometry
or case-specific registration is used.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/deepcad")]

from cad_canonical import compute_transform, transform_dsl  # noqa: E402

MANIFEST = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/"
    "VAL1000_EVAL_MANIFEST.jsonl"
)
DEFAULT_PRED = ROOT / "ours3/p1_exact9998_val1000_eval_v2"
DEFAULT_OUT = ROOT / "ours3/p1_fusion360_coordinate_repair_v1"
EXECUTOR = ROOT / "scripts/deepcad/dsl_to_occ.py"
CADFIT_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-root", type=Path, default=DEFAULT_PRED)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    rows = [json.loads(line) for line in MANIFEST.read_text().splitlines()]
    rows = [row for row in rows if row["source"].lower() == "fusion360"]
    if args.limit is not None:
        rows = rows[: args.limit]
    args.out.mkdir(parents=True, exist_ok=True)

    report = []
    for index, row in enumerate(rows, 1):
        case_id = row["cad_id"]
        case_out = args.out / case_id
        result_path = case_out / "row.json"
        if args.resume and result_path.is_file():
            report.append(json.loads(result_path.read_text()))
            continue
        case_out.mkdir(parents=True, exist_ok=True)

        pred_dir = args.pred_root / case_id
        canonical_path = pred_dir / "pred_canonical.dsl"
        if not canonical_path.is_file():
            canonical_path = pred_dir / "pred.dsl"
        pack = Path(row["surface_path"]).parent
        source_points_path = pack / "surface_points_source.npy"
        source_points = np.load(source_points_path)[:, :3]
        transform = compute_transform(source_points, target_diagonal=6.0)
        canonical = canonical_path.read_text(errors="replace")
        dsl_path = case_out / "pred_source.dsl"
        step_path = case_out / "pred.step"
        stl_path = case_out / "pred.stl"
        transform_error = ""
        proc = None
        try:
            source_dsl = transform_dsl(canonical, transform, inverse=True)
            dsl_path.write_text(source_dsl)
            proc = subprocess.run(
                [
                    str(CADFIT_PYTHON),
                    str(EXECUTOR),
                    "--dsl",
                    str(dsl_path),
                    "--step",
                    str(step_path),
                    "--stl",
                    str(stl_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )
        except Exception as exc:
            transform_error = f"{type(exc).__name__}: {exc}"
        (case_out / "coordinate_transform_recomputed.json").write_text(
            json.dumps(transform.to_json(), indent=2) + "\n"
        )
        result = {
            "case_id": case_id,
            "source": "fusion360",
            "input_surface_points_source": str(source_points_path),
            "input_surface_sha256": sha256(source_points_path),
            "canonical_prediction": str(canonical_path),
            "canonical_prediction_sha256": sha256(canonical_path),
            "transform_source": "recomputed_from_input_surface_points_source_only",
            "transform": transform.to_json(),
            "step_ok": proc is not None and proc.returncode == 0 and step_path.is_file(),
            "step": str(step_path) if step_path.is_file() else None,
            "stl": str(stl_path) if stl_path.is_file() else None,
            "executor_returncode": proc.returncode if proc is not None else None,
            "executor_error": transform_error
            or ((proc.stderr or proc.stdout)[-1000:] if proc and proc.returncode else ""),
        }
        result_path.write_text(json.dumps(result, indent=2) + "\n")
        report.append(result)
        print(f"[{index}/{len(rows)}] {case_id} step_ok={result['step_ok']}", flush=True)

    summary = {
        "schema_version": "P1_FUSION360_COORDINATE_REPAIR_V1",
        "N": len(report),
        "step_ok_N": sum(bool(row["step_ok"]) for row in report),
        "uses_ground_truth_for_transform": False,
        "transform_source": "surface_points_source.npy bbox, target diagonal 6.0",
        "historical_predictions_modified": False,
        "rows": report,
    }
    (args.out / "report.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
