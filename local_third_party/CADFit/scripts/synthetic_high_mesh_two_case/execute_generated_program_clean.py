#!/usr/bin/env python3
"""Execute generated_cad.py in a clean temp dir and export the final solid."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tempfile
import traceback
from pathlib import Path

import cadquery as cq


def pick_final_solid(ns: dict):
    """Prefer explicit final variables; never prefer intermediate solid_* alone."""
    for key in ("final_result", "result"):
        if key in ns and ns[key] is not None:
            return key, ns[key]
    # last assignment-like Solid/Workplane
    for key, value in list(ns.items())[::-1]:
        if key.startswith("_"):
            continue
        if hasattr(value, "val") or hasattr(value, "wrapped"):
            if key.startswith("solid_") or key.startswith("sketch_") or key.startswith("plane_"):
                continue
            return key, value
    # fallback: union all solid_* if present
    solids = [ns[k] for k in sorted(ns) if k.startswith("solid_")]
    if solids:
        acc = solids[0]
        for s in solids[1:]:
            try:
                acc = acc.add(s)
            except Exception:
                try:
                    acc = acc.union(s)
                except Exception:
                    pass
        return "union_of_solid_star", acc
    return None, None


def execute_case(case_name: str, art_root: Path) -> dict:
    case_dir = art_root / case_name
    script = case_dir / "generated_cad.py"
    out_dir = case_dir / "clean_reexport"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "case_name": case_name,
        "script": str(script.resolve()) if script.exists() else "",
        "export_var": None,
        "success": False,
        "stdout": "",
        "stderr": "",
        "error": "",
        "clean_stl": str(out_dir / "clean_reconstructed.stl"),
        "clean_step": str(out_dir / "clean_reconstructed.step"),
    }
    if not script.exists():
        report["error"] = "missing generated_cad.py"
        (out_dir / "exec_report.json").write_text(json.dumps(report, indent=2))
        return report

    with tempfile.TemporaryDirectory(prefix=f"cadfit_clean_{case_name}_") as td:
        tmp = Path(td)
        tmp_script = tmp / "generated_cad.py"
        shutil.copy2(script, tmp_script)
        # capture prints
        import io
        from contextlib import redirect_stdout, redirect_stderr
        buf_out, buf_err = io.StringIO(), io.StringIO()
        try:
            with redirect_stdout(buf_out), redirect_stderr(buf_err):
                ns = {"__name__": "__main__", "__file__": str(tmp_script)}
                code = compile(tmp_script.read_text(encoding="utf-8"), str(tmp_script), "exec")
                exec(code, ns, ns)
            report["stdout"] = buf_out.getvalue()[-4000:]
            report["stderr"] = buf_err.getvalue()[-4000:]
            var, obj = pick_final_solid(ns)
            report["export_var"] = var
            if obj is None:
                report["error"] = "no final solid found"
            else:
                stl = out_dir / "clean_reconstructed.stl"
                step = out_dir / "clean_reconstructed.step"
                cq.exporters.export(obj, str(stl))
                cq.exporters.export(obj, str(step))
                # reopen step sanity
                try:
                    cq.importers.importStep(str(step))
                    report["step_reopen_ok"] = True
                except Exception as e:
                    report["step_reopen_ok"] = False
                    report["step_reopen_error"] = repr(e)
                report["success"] = stl.exists() and stl.stat().st_size > 0
        except Exception as e:
            report["stdout"] = buf_out.getvalue()[-4000:]
            report["stderr"] = buf_err.getvalue()[-4000:]
            report["error"] = repr(e)
            report["traceback"] = traceback.format_exc()[-4000:]

    (out_dir / "exec_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (out_dir / "stdout.txt").write_text(report.get("stdout", ""), encoding="utf-8")
    (out_dir / "stderr.txt").write_text(report.get("stderr", ""), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case", default=None)
    args = ap.parse_args()
    root = Path(__file__).resolve().parents[2]
    art = root / "artifacts/synthetic_high_mesh_two_case_v1"
    cases = [args.case] if args.case else ["case_a_flange", "case_b_bracket"]
    results = {c: execute_case(c, art) for c in cases}
    out = art / "clean_reexport_summary.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))
    return 0 if all(v.get("success") for v in results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
