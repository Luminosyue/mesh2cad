#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import cadquery as cq

from common import CASES


def export_one(case_name: str) -> dict:
    case_dir = Path("artifacts/synthetic_high_mesh_two_case_v1") / case_name
    script = case_dir / "generated_cad.py"
    out_step = case_dir / "reconstructed_cad.step"
    if not script.exists():
        return {"step_export_success": False, "error": "missing generated_cad.py", "step_path": str(out_step)}
    old_cwd = Path.cwd()
    try:
        ns = runpy.run_path(str(script))
        candidates = []
        for key in ["final_result", "result"]:
            if key in ns:
                candidates.append(ns[key])
        for value in ns.values():
            if hasattr(value, "val") or hasattr(value, "wrapped"):
                candidates.append(value)
        last_error = ""
        for obj in candidates:
            try:
                cq.exporters.export(obj, str(out_step))
                reopened = cq.importers.importStep(str(out_step))
                shape = reopened.val()
                return {
                    "step_export_success": True,
                    "step_path": str(out_step),
                    "reopened_faces": len(shape.Faces()),
                    "reopened_solids": len(shape.Solids()),
                    "error": "",
                }
            except Exception as e:
                last_error = repr(e)
        return {"step_export_success": False, "error": last_error or "no CadQuery object found", "step_path": str(out_step)}
    finally:
        try:
            import os
            os.chdir(old_cwd)
        except Exception:
            pass


def main() -> int:
    argparse.ArgumentParser().parse_args()
    audit = {case: export_one(case) for case, _ in CASES}
    out = Path("artifacts/synthetic_high_mesh_two_case_v1/reconstructed_step_audit.json")
    out.write_text(json.dumps(audit, indent=2), encoding="utf-8")
    print(json.dumps(audit, indent=2))
    return 0 if any(v.get("step_export_success") for v in audit.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
