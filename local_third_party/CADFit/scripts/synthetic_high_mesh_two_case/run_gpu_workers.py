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


CASES = ["case_a_flange", "case_b_bracket"]


def success_outputs(obj_dir: Path) -> bool:
    return all((obj_dir / name).exists() and (obj_dir / name).stat().st_size > 0 for name in [
        "best_greedy_parallel_iterative.py",
        "best_greedy_parallel_iterative.stl",
        "final_iou.json",
    ])


def run_case(case: str, output_root: Path, workers: int, gpu: str, timeout: int, skip_existing: bool) -> dict:
    data = Path("datasets/synthetic_high_mesh_two_case_v1") / case
    out = output_root / case
    inp = out / "cadfit_input"
    inp.mkdir(parents=True, exist_ok=True)
    shutil.copy2(data / "input_high_mesh.stl", inp / "input_high_mesh.stl")
    for forbidden in ["ground_truth.py", "ground_truth.step"]:
        p = inp / forbidden
        if p.exists():
            p.unlink()
    obj = out / "input_high_mesh"
    status_path = out / "run_status.json"
    stdout = out / "stdout.log"
    stderr = out / "stderr.log"
    audit = json.loads((data / "mesh_audit.json").read_text())
    status = {
        "case_name": case,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": "",
        "runtime_seconds": 0.0,
        "exit_code": None,
        "status": "exception",
        "error": "",
        "prior_mode": "no_prior",
        "gpu_requested": gpu,
        "cadfit_inner_workers": workers,
        "step_face_count": audit.get("ground_truth_step_faces"),
        "input_triangle_count": audit.get("triangle_count"),
        "command": [],
    }
    if skip_existing and success_outputs(obj):
        status.update({"status": "success", "exit_code": 0, "error": "skipped_existing"})
        status["end_time"] = datetime.now(timezone.utc).isoformat()
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
        return status
    cmd = [
        sys.executable, "run_pipeline.py", str(inp),
        "--output-folder", str(out),
        "--max-iterations", "1",
        "--limit", "1",
        "--skip-existing",
    ]
    status["command"] = cmd
    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = str(workers)
    env["CUDA_VISIBLE_DEVICES"] = gpu
    t0 = time.time()
    try:
        with stdout.open("wb") as so, stderr.open("wb") as se:
            proc = subprocess.run(cmd, stdout=so, stderr=se, timeout=timeout, env=env)
        status["exit_code"] = proc.returncode
        if proc.returncode != 0:
            status["status"] = "process_error"
            status["error"] = f"run_pipeline exited {proc.returncode}"
        elif not success_outputs(obj):
            status["status"] = "missing_output"
            status["error"] = "missing iterative code/stl/final_iou"
        else:
            script = obj / "best_greedy_parallel_iterative.py"
            code = subprocess.run([sys.executable, script.name], cwd=script.parent, capture_output=True, text=True, timeout=300, env=env)
            mesh = trimesh.load(obj / "best_greedy_parallel_iterative.stl", force="mesh")
            iou = json.loads((obj / "final_iou.json").read_text())
            if code.returncode != 0:
                status["status"] = "invalid_program"
                status["error"] = code.stderr[-1200:]
            elif len(mesh.faces) <= 0 or abs(mesh.volume) <= 0 or "final_iou" not in iou:
                status["status"] = "missing_output"
                status["error"] = "invalid generated mesh or final_iou"
            else:
                status["status"] = "success"
                status["final_iou"] = iou.get("final_iou")
                status["cadfit_reported_duration"] = iou.get("duration")
    except subprocess.TimeoutExpired:
        status["status"] = "timeout"
        status["error"] = f"timeout after {timeout}s"
    except Exception as exc:
        status["status"] = "exception"
        status["error"] = repr(exc)
    finally:
        status["runtime_seconds"] = time.time() - t0
        status["end_time"] = datetime.now(timezone.utc).isoformat()
        status_path.write_text(json.dumps(status, indent=2), encoding="utf-8")
    return status


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-root", default="outputs/synthetic_high_mesh_two_case_v1_gpu_workers4")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--gpu", default="0")
    ap.add_argument("--timeout-seconds", type=int, default=3600)
    ap.add_argument("--skip-existing", action="store_true")
    args = ap.parse_args()
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    results = []
    for case in CASES:
        result = run_case(case, output_root, args.workers, args.gpu, args.timeout_seconds, args.skip_existing)
        results.append(result)
        print(f"{case} status={result['status']} runtime={result['runtime_seconds']:.1f}s", flush=True)
    (output_root / "gpu_workers_run_summary.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    return 0 if any(r["status"] == "success" for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
