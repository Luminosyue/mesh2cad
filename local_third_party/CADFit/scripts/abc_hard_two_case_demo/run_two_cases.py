#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from common import read_csv_dicts, successful_outputs


def run_case(row: dict, output_root: Path, max_iterations: int, timeout: int, skip_existing: bool, fillet: bool) -> dict:
    case = row["case_name"]
    case_root = output_root / case
    case_root.mkdir(parents=True, exist_ok=True)
    input_dir = case_root / "input"
    input_dir.mkdir(exist_ok=True)
    input_stl = input_dir / f"{row['abc_id']}.stl"
    if not input_stl.exists():
        shutil.copy2(row["source_stl"], input_stl)
    per_obj = case_root / row["abc_id"]
    stdout_path = case_root / "stdout.log"
    stderr_path = case_root / "stderr.log"
    status_path = case_root / "run_status.json"
    status = {
        "case_name": case,
        "abc_id": row["abc_id"],
        "step_face_count": row["step_face_count"],
        "triangle_count": row["triangle_count"],
        "command": [],
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": "",
        "runtime_seconds": 0,
        "exit_code": None,
        "status": "exception",
        "error": "",
    }
    if skip_existing and successful_outputs(per_obj):
        status.update({"end_time": datetime.now(timezone.utc).isoformat(), "status": "success", "exit_code": 0, "error": "skipped_existing"})
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    cmd = [
        sys.executable, "run_pipeline.py", str(input_dir),
        "--output-folder", str(case_root),
        "--max-iterations", str(max_iterations),
        "--limit", "1",
        "--skip-existing",
    ]
    if fillet:
        cmd.append("--fillet-chamfer")
    status["command"] = cmd
    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = "1"
    t0 = time.time()
    try:
        with stdout_path.open("wb") as out, stderr_path.open("wb") as err:
            p = subprocess.run(cmd, stdout=out, stderr=err, timeout=timeout, env=env)
        status["exit_code"] = p.returncode
        if p.returncode != 0:
            status["status"] = "process_error"
            status["error"] = f"run_pipeline exited {p.returncode}"
        elif successful_outputs(per_obj):
            status["status"] = "success"
        else:
            status["status"] = "missing_output"
            status["error"] = f"missing expected outputs in {per_obj}"
    except subprocess.TimeoutExpired:
        status["status"] = "timeout"
        status["error"] = f"timeout after {timeout}s"
    except Exception as e:
        status["status"] = "exception"
        status["error"] = repr(e)
    finally:
        status["runtime_seconds"] = time.time() - t0
        status["end_time"] = datetime.now(timezone.utc).isoformat()
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="datasets/abc_hard_two_case_demo/manifests/selected_two_cases.csv")
    ap.add_argument("--output-root", default="outputs/abc_hard_two_case_demo")
    ap.add_argument("--max-iterations", type=int, default=1)
    ap.add_argument("--timeout-seconds", type=int, default=3600)
    ap.add_argument("--skip-existing", action="store_true")
    ap.add_argument("--fillet-chamfer", action="store_true")
    args = ap.parse_args()
    rows = read_csv_dicts(args.manifest)
    output_root = Path(args.output_root)
    statuses = []
    for row in rows[:2]:
        statuses.append(run_case(row, output_root, args.max_iterations, args.timeout_seconds, args.skip_existing, args.fillet_chamfer))
        print(f"RUN_STATUS {row['case_name']} {statuses[-1]['status']} {statuses[-1]['runtime_seconds']:.1f}s")
    return 0 if all(s["status"] == "success" for s in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
