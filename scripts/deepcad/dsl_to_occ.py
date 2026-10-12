#!/usr/bin/env python3
"""Execute program.dsl with CadQuery/OCP and export STEP (+ optional STL)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "DeepCAD"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from edge_aware_cad_planner_v1.cad_dsl import execute_dsl, parse_dsl  # noqa: E402


def run_dsl_to_occ(
    dsl_path: Path,
    step_path: Path,
    stl_path: Path | None = None,
    source_json: Path | None = None,
) -> dict:
    code = dsl_path.read_text(encoding="utf-8")
    try:
        parse_dsl(code)
        return execute_dsl(code, step_path, stl_path)
    except Exception as dsl_err:
        if source_json is None:
            raise RuntimeError(f"DSL execution failed: {dsl_err}") from dsl_err
        from deepcad_occ_builder import export_deepcad_json

        out = export_deepcad_json(source_json, step_path, stl_path)
        out["dsl_error"] = str(dsl_err)
        return out


def main() -> int:
    parser = argparse.ArgumentParser(description="program.dsl → STEP")
    parser.add_argument("--dsl", type=Path, required=True)
    parser.add_argument("--step", type=Path, required=True)
    parser.add_argument("--stl", type=Path, default=None)
    parser.add_argument(
        "--source-json",
        type=Path,
        default=None,
        help="DeepCAD source JSON for OCP fallback when DSL execution fails",
    )
    args = parser.parse_args()
    result = run_dsl_to_occ(args.dsl, args.step, args.stl, args.source_json)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
