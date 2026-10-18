#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import runpy
from pathlib import Path

import cadquery as cq


def export_script(script: Path, out_step: Path) -> dict:
    ns = runpy.run_path(str(script))
    candidates = []
    for k in ["final_result", "result"]:
        if k in ns:
            candidates.append(ns[k])
    for _, v in ns.items():
        if hasattr(v, "val") or hasattr(v, "wrapped"):
            candidates.append(v)
    last_err = ""
    for obj in candidates:
        try:
            cq.exporters.export(obj, str(out_step))
            cq.importers.importStep(str(out_step))
            return {"step_export_success": True, "step_path": str(out_step), "error": ""}
        except Exception as e:
            last_err = repr(e)
    return {"step_export_success": False, "step_path": str(out_step), "error": last_err or "no CadQuery object found"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifacts-root", default="artifacts/abc_hard_two_case_demo")
    args = ap.parse_args()
    root = Path(args.artifacts_root)
    summary = {}
    for case in ["case_a", "case_b"]:
        script = root / case / "generated_cad.py"
        out = root / case / "reconstructed_cad.step"
        if script.exists():
            summary[case] = export_script(script, out)
        else:
            summary[case] = {"step_export_success": False, "step_path": str(out), "error": "missing generated_cad.py"}
    (root / "step_export_audit.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if any(v["step_export_success"] for v in summary.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
