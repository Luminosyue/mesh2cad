#!/usr/bin/env python3
"""Re-export P1v2 canonical DeepCAD programs into source coordinates."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MANIFEST = (
    ROOT
    / "ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/manifests/VAL1000_EVAL_MANIFEST.jsonl"
)
EXECUTOR = ROOT / "scripts/deepcad/dsl_to_occ.py"
PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "scripts/deepcad")]


def process(item: tuple[dict, str, int]) -> dict:
    from cad_canonical import CoordinateTransform, transform_dsl

    source, pred_root_text, timeout = item
    case_id = source["cad_id"]
    case = Path(pred_root_text) / case_id
    result_path = case / "row.json"
    row = json.loads(result_path.read_text())
    canonical_path = case / "pred_canonical.dsl"
    transform_path = Path(source["surface_path"]).parent / "coordinate_transform.json"
    try:
        transform = CoordinateTransform.from_json(json.loads(transform_path.read_text()))
        source_code = transform_dsl(canonical_path.read_text(), transform, inverse=True)
        dsl = case / "pred_source.dsl"
        dsl.write_text(source_code if source_code.endswith("\n") else source_code + "\n")
        step = case / "pred.step"
        stl = case / "pred.stl"
        step.unlink(missing_ok=True)
        stl.unlink(missing_ok=True)
        proc = subprocess.run(
            [str(PYTHON), str(EXECUTOR), "--dsl", str(dsl), "--step", str(step), "--stl", str(stl)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        ok = proc.returncode == 0 and step.is_file() and step.stat().st_size > 0
        error = None if ok else (proc.stderr or proc.stdout)[-1000:]
    except subprocess.TimeoutExpired:
        ok = False
        error = f"source_step_timeout_{timeout}s"
    except Exception as exc:
        ok = False
        error = f"{type(exc).__name__}: {exc}"
    row["parsed"] = (case / "pred_source.dsl").is_file()
    row["step_ok"] = ok
    row["step"] = str(case / "pred.step") if ok else None
    row["stl"] = str(case / "pred.stl") if ok and (case / "pred.stl").is_file() else None
    row["error"] = error
    row["output_coordinate_policy"] = "manifest_transform_inverse_to_source"
    result_path.write_text(json.dumps(row, indent=2) + "\n")
    return {"case_id": case_id, "step_ok": ok, "error": error}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pred-root", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    manifest = [json.loads(x) for x in MANIFEST.read_text().splitlines() if x.strip()]
    deepcad = [x for x in manifest if x["source"].lower() == "deepcad"]
    results = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(process, (row, str(args.pred_root), args.timeout)) for row in deepcad]
        for index, future in enumerate(as_completed(futures), 1):
            results.append(future.result())
            if index % 25 == 0 or index == len(futures):
                print(f"re-exported {index}/{len(futures)}", flush=True)
    report = {
        "schema_version": "P1V2_DEEPCAD_SOURCE_REEXPORT_V1",
        "N": len(results),
        "step_ok_N": sum(x["step_ok"] for x in results),
        "step_invalid_N": sum(not x["step_ok"] for x in results),
        "transform_source": "per-pack coordinate_transform.json",
        "rows": results,
    }
    (args.pred_root / "deepcad_source_reexport_report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps({key: value for key, value in report.items() if key != "rows"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
