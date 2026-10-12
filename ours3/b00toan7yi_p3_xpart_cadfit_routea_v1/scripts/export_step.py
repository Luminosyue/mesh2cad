#!/usr/bin/env python3
"""CadQuery .py -> STEP for robot Route A. Skip existing STEP files."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CADFIT_PY, CADFIT_RAW, STEP_DIR  # noqa: E402


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
            [str(CADFIT_PY), str(wrapper)],
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
    rows = []
    parts = sorted(p.parent.name for p in CADFIT_RAW.glob("PART_*/final_iou.json"))
    if not parts:
        parts = [p.stem for p in (CADFIT_RAW.parent / "input_stl").glob("PART_*.stl")]
    for pid in parts:
        pyf = CADFIT_RAW / pid / "best_greedy_parallel_iterative.py"
        if not pyf.is_file():
            # Some CADFit runs only write the non-iterative best script.
            pyf = CADFIT_RAW / pid / "best_greedy_parallel.py"
        iouf = CADFIT_RAW / pid / "final_iou.json"
        if not (pyf.is_file() and iouf.is_file() and iouf.stat().st_size > 0):
            continue
        step_path = STEP_DIR / pid / f"{pid}.step"
        recon_stl = STEP_DIR / pid / f"{pid}_reconstructed.stl"
        raw_step = CADFIT_RAW / pid / "best_greedy_parallel_iterative.step"
        if step_path.is_file() and step_path.stat().st_size > 0:
            rows.append({"part_id": pid, "status": "skipped_existing", "step": str(step_path)})
            print(f"[skip] {pid}")
            continue
        step_path.parent.mkdir(parents=True, exist_ok=True)
        ok, log = export_step(pyf, step_path, recon_stl)
        (STEP_DIR / pid / "step_export.log").write_text(log)
        if ok and step_path.is_file():
            raw_step.write_bytes(step_path.read_bytes())
            rows.append({"part_id": pid, "status": "ok", "bytes": step_path.stat().st_size})
            print(f"[ok] {pid}  {step_path.stat().st_size} bytes")
        else:
            rows.append({"part_id": pid, "status": "fail", "log_tail": log[-800:]})
            print(f"[fail] {pid}")
    STEP_DIR.mkdir(parents=True, exist_ok=True)
    (STEP_DIR / "export_summary.json").write_text(json.dumps(rows, indent=2) + "\n")
    n_ok = sum(1 for r in rows if r["status"] in ("ok", "skipped_existing"))
    n_fail = sum(1 for r in rows if r["status"] == "fail")
    print(f"Done ok_or_skip={n_ok} fail={n_fail}")
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
