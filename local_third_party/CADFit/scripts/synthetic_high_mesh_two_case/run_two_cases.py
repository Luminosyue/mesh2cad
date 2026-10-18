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

import trimesh

from common import CASES, has_success_outputs


def run_case(case_name: str, timeout: int, skip_existing: bool) -> dict:
    data_dir = Path("datasets/synthetic_high_mesh_two_case_v1") / case_name
    out_dir = Path("outputs/synthetic_high_mesh_two_case_v1") / case_name
    input_dir = out_dir / "cadfit_input"
    input_dir.mkdir(parents=True, exist_ok=True)
    isolated_stl = input_dir / "input_high_mesh.stl"
    if not isolated_stl.exists():
        shutil.copy2(data_dir / "input_high_mesh.stl", isolated_stl)
    # Guardrail: CADFit input dir must not contain ground-truth files.
    for forbidden in ["ground_truth.py", "ground_truth.step"]:
        if (input_dir / forbidden).exists():
            raise RuntimeError(f"Forbidden file in CADFit input dir: {input_dir / forbidden}")
    stdout = out_dir / "stdout.log"
    stderr = out_dir / "stderr.log"
    status_path = out_dir / "run_status.json"
    audit = json.loads((data_dir / "mesh_audit.json").read_text())
    status = {
        "case_name": case_name,
        "command": [],
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": "",
        "runtime_seconds": 0.0,
        "exit_code": None,
        "status": "exception",
        "error": "",
        "prior_mode": "no_prior",
        "step_face_count": audit.get("ground_truth_step_faces"),
        "input_triangle_count": audit.get("triangle_count"),
    }
    if skip_existing and has_success_outputs(out_dir):
        status.update({"status": "success", "exit_code": 0, "error": "skipped_existing", "end_time": datetime.now(timezone.utc).isoformat()})
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    cmd = [
        sys.executable, "run_pipeline.py", str(input_dir),
        "--output-folder", str(out_dir),
        "--max-iterations", "1",
        "--limit", "1",
        "--skip-existing",
    ]
    status["command"] = cmd
    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = "1"
    t0 = time.time()
    try:
        with stdout.open("wb") as out, stderr.open("wb") as err:
            p = subprocess.run(cmd, stdout=out, stderr=err, timeout=timeout, env=env)
        status["exit_code"] = p.returncode
        if p.returncode != 0:
            status["status"] = "process_error"
            status["error"] = f"run_pipeline exited {p.returncode}"
        elif not has_success_outputs(out_dir):
            status["status"] = "missing_output"
            status["error"] = "Missing best_greedy_parallel_iterative.py/.stl or final_iou.json"
        else:
            rec = out_dir / "input_high_mesh" / "best_greedy_parallel_iterative.stl"
            py = out_dir / "input_high_mesh" / "best_greedy_parallel_iterative.py"
            iou = json.loads((out_dir / "input_high_mesh" / "final_iou.json").read_text())
            mesh = trimesh.load(rec, force="mesh")
            code_check = subprocess.run([sys.executable, py.name], cwd=py.parent, capture_output=True, text=True, timeout=300)
            if code_check.returncode != 0:
                status["status"] = "invalid_program"
                status["error"] = code_check.stderr[-1000:]
            elif len(mesh.faces) <= 0 or abs(mesh.volume) <= 0 or "final_iou" not in iou:
                status["status"] = "missing_output"
                status["error"] = "Generated STL or final_iou invalid"
            else:
                status["status"] = "success"
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
    ap.add_argument("--timeout-seconds", type=int, default=3600)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()
    statuses = []
    case_a = run_case("case_a_flange", args.timeout_seconds, args.skip_existing)
    statuses.append(case_a)
    print(f"CASE_A_STATUS={case_a['status']}")
    if case_a["status"] == "success":
        case_b = run_case("case_b_bracket", args.timeout_seconds, args.skip_existing)
        statuses.append(case_b)
        print(f"CASE_B_STATUS={case_b['status']}")
    else:
        print("CASE_B_STATUS=not_run_case_a_failed")
    return 0 if any(s["status"] == "success" for s in statuses) else 1


if __name__ == "__main__":
    raise SystemExit(main())
