#!/usr/bin/env python3
"""Export STEP for all CADFit Route A parts that have a CadQuery program."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_OUT = ROOT / "ours3/cadfit_xpart45_routea_v1"
CADFIT_ENV_PYTHON = "/data/miniconda3/envs/cadfit-env/bin/python"


def export_step(cq_script: Path, step_path: Path, stl_path: Path) -> tuple[bool, str]:
    wrapper = step_path.parent / f"_export_{step_path.stem}.py"
    wrapper.write_text(
        "import cadquery as cq\n"
        "import math\n"
        + cq_script.read_text(errors="ignore")
        + "\n\n"
        + "try:\n"
        + "    _shape = locals().get('result') or locals().get('final_result')\n"
        + "    if _shape is None:\n"
        + "        _shape = [v for k,v in list(locals().items()) if k.startswith('solid_') or k.startswith('result')][-1]\n"
        + f"    cq.exporters.export(_shape, r'{step_path}', 'STEP')\n"
        + f"    cq.exporters.export(_shape, r'{stl_path}', 'STL')\n"
        + "    print('STEP_OK')\n"
        + "except Exception as e:\n"
        + "    print(f'STEP_FAIL {e}')\n"
    )
    try:
        res = subprocess.run(
            [CADFIT_ENV_PYTHON, str(wrapper)],
            capture_output=True,
            text=True,
            timeout=180,
            cwd=str(cq_script.parent),
        )
        output = res.stdout + res.stderr
        ok = res.returncode == 0 and "STEP_OK" in output
        return ok, output
    except Exception as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description="Export STEP for CADFit Route A parts.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    out = args.output_dir
    cadfit_raw = out / "cadfit_raw"
    step_dir = out / "step"
    rows = []
    part_ids = sorted(p.name for p in cadfit_raw.glob("PART_*") if p.is_dir())
    for pid in part_ids:
        pyf = cadfit_raw / pid / "best_greedy_parallel_iterative.py"
        iouf = cadfit_raw / pid / "final_iou.json"
        if not (pyf.is_file() and iouf.is_file() and iouf.stat().st_size > 0):
            continue
        step_path = step_dir / pid / f"{pid}.step"
        recon_stl = step_dir / pid / f"{pid}_reconstructed.stl"
        raw_step = cadfit_raw / pid / "best_greedy_parallel_iterative.step"
        if step_path.is_file() and step_path.stat().st_size > 0:
            rows.append({"part_id": pid, "status": "skipped_existing", "step": str(step_path)})
            print(f"[skip] {pid}")
            continue
        step_path.parent.mkdir(parents=True, exist_ok=True)
        ok, log = export_step(pyf, step_path, recon_stl)
        (step_dir / pid / "step_export.log").write_text(log)
        if ok and step_path.is_file():
            raw_step.write_bytes(step_path.read_bytes())
            rows.append({"part_id": pid, "status": "ok", "bytes": step_path.stat().st_size})
            print(f"[ok] {pid}  {step_path.stat().st_size} bytes")
        else:
            rows.append({"part_id": pid, "status": "fail", "log_tail": log[-800:]})
            print(f"[fail] {pid}")
    summary = step_dir / "export_summary.json"
    summary.parent.mkdir(parents=True, exist_ok=True)
    summary.write_text(json.dumps(rows, indent=2) + "\n")
    n_ok = sum(1 for r in rows if r["status"] in ("ok", "skipped_existing"))
    n_fail = sum(1 for r in rows if r["status"] == "fail")
    print(f"Done ok_or_skip={n_ok} fail={n_fail}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
