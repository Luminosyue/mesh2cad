#!/usr/bin/env python3
"""Parallel CADFit Route A runner for X-Part watertight parts."""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CADFIT_ROOT = ROOT / "CADFit"
DEFAULT_OUT = ROOT / "ours3/cadfit_xpart45_routea_v1"
DEFAULT_INPUT = DEFAULT_OUT / "input_stl"
DEFAULT_RAW = DEFAULT_OUT / "cadfit_raw"
DEFAULT_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")
DEFAULT_PART_TIMEOUT = int(os.environ.get("CADFIT_PART_TIMEOUT", "10800"))
STALE_LOCK_SECONDS = int(os.environ.get("CADFIT_STALE_LOCK_SECONDS", "7200"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, default=str) + "\n")


def is_done(raw_dir: Path, part_id: str) -> bool:
    f = raw_dir / part_id / "final_iou.json"
    return f.is_file() and f.stat().st_size > 0


def _lock_is_live(lock: Path) -> bool:
    try:
        age = time.time() - lock.stat().st_mtime
    except OSError:
        return False
    if age < STALE_LOCK_SECONDS:
        return True
    part_dir = str(lock.parent.resolve())
    try:
        out = subprocess.check_output(["ps", "-eo", "args="], text=True, errors="ignore")
    except Exception:
        return age < STALE_LOCK_SECONDS
    for line in out.splitlines():
        if part_dir in line and ("_run_single.py" in line or "greedy_search.py" in line):
            return True
    return False


def pending_parts(input_dir: Path, raw_dir: Path, part_ids: list[str] | None) -> list[str]:
    if part_ids:
        candidates = part_ids
    else:
        candidates = sorted(p.stem for p in input_dir.glob("PART_*.stl"))
    out = []
    for pid in candidates:
        stl = input_dir / f"{pid}.stl"
        if not stl.is_file():
            continue
        if is_done(raw_dir, pid):
            continue
        lock = raw_dir / pid / ".running.lock"
        if lock.is_file():
            if _lock_is_live(lock):
                continue
            try:
                lock.unlink()
                print(f"cleared stale lock {lock}", flush=True)
            except OSError:
                continue
        out.append(pid)
    return out


def _kill_pg(pid: int) -> None:
    try:
        os.killpg(pid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def worker(payload: dict) -> dict:
    part_id = payload["part_id"]
    stl_path = Path(payload["stl_path"])
    raw_dir = Path(payload["raw_dir"])
    cadfit_root = Path(payload["cadfit_root"])
    python_bin = payload["python_bin"]
    inner_workers = payload["inner_workers"]
    max_iterations = payload["max_iterations"]
    keep_history = payload["keep_history"]
    part_timeout = int(payload.get("part_timeout", DEFAULT_PART_TIMEOUT))
    log_path = Path(payload["log_path"])

    part_raw = raw_dir / part_id
    part_raw.mkdir(parents=True, exist_ok=True)
    lock = part_raw / ".running.lock"
    lock.write_text(datetime.now(timezone.utc).isoformat() + "\n", encoding="utf-8")

    worker_script = part_raw / "_run_single.py"
    worker_script.write_text(
        f"""import sys
sys.path.insert(0, {str(cadfit_root)!r})
from run_pipeline import process_single_stl

process_single_stl(
    stl_path={str(stl_path)!r},
    folder_name={str(raw_dir)!r},
    max_iterations={max_iterations},
    keep_history={keep_history},
)
""",
        encoding="utf-8",
    )

    env = os.environ.copy()
    env["CADFIT_INNER_WORKERS"] = str(inner_workers)
    env.setdefault("CADFIT_GREEDY_TIMEOUT", "3000")
    env["PYTHONPATH"] = str(cadfit_root) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")

    t0 = time.time()
    row = {
        "part_id": part_id,
        "status": "failed",
        "runtime_seconds": 0.0,
        "final_iou": None,
        "error": "",
    }
    log_path.parent.mkdir(parents=True, exist_ok=True)
    proc = None
    try:
        with log_path.open("w", encoding="utf-8") as log:
            proc = subprocess.Popen(
                [python_bin, str(worker_script)],
                cwd=str(cadfit_root),
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                start_new_session=True,
            )
            try:
                returncode = proc.wait(timeout=part_timeout)
            except subprocess.TimeoutExpired:
                _kill_pg(proc.pid)
                try:
                    proc.wait(timeout=60)
                except subprocess.TimeoutExpired:
                    pass
                row["error"] = f"part_timeout={part_timeout}s"
                return row
        iou_path = part_raw / "final_iou.json"
        if returncode == 0 and iou_path.is_file() and iou_path.stat().st_size > 0:
            iou_data = json.loads(iou_path.read_text(encoding="utf-8"))
            row["status"] = "success"
            row["final_iou"] = iou_data.get("final_iou")
        else:
            row["error"] = f"exit_code={returncode}"
    except Exception as exc:
        if proc is not None and proc.poll() is None:
            _kill_pg(proc.pid)
        row["error"] = repr(exc)
    finally:
        row["runtime_seconds"] = time.time() - t0
        if lock.is_file():
            lock.unlink(missing_ok=True)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CADFit Route A in parallel.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--input-stl-dir", type=Path, default=None)
    parser.add_argument("--raw-dir", type=Path, default=None)
    parser.add_argument("--jobs", type=int, default=4, help="Concurrent parts")
    parser.add_argument("--inner-workers", type=int, default=4, help="CADFIT_INNER_WORKERS per part")
    parser.add_argument("--max-iterations", type=int, default=1)
    parser.add_argument("--keep-history", action="store_true", default=True)
    parser.add_argument("--part-timeout", type=int, default=DEFAULT_PART_TIMEOUT)
    parser.add_argument("--parts", nargs="*", help="Optional PART_XXX list")
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    args = parser.parse_args()

    out = args.output_dir
    input_dir = args.input_stl_dir or (out / "input_stl")
    raw_dir = args.raw_dir or (out / "cadfit_raw")
    logs_dir = out / "logs" / "parallel"
    logs_dir.mkdir(parents=True, exist_ok=True)

    if not args.python.is_file():
        print(f"Python not found: {args.python}", file=sys.stderr)
        return 1
    if not input_dir.is_dir():
        print(f"Input STL dir not found: {input_dir}", file=sys.stderr)
        return 1

    todo = pending_parts(input_dir, raw_dir, args.parts)
    if not todo:
        print("Nothing pending.")
        return 0

    manifest = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "jobs": args.jobs,
        "inner_workers": args.inner_workers,
        "max_iterations": args.max_iterations,
        "part_timeout": args.part_timeout,
        "pending_parts": todo,
        "results": [],
    }
    print(f"Pending {len(todo)} parts, jobs={args.jobs}, inner_workers={args.inner_workers}")

    payloads = []
    for pid in todo:
        payloads.append(
            {
                "part_id": pid,
                "stl_path": str((input_dir / f"{pid}.stl").resolve()),
                "raw_dir": str(raw_dir.resolve()),
                "cadfit_root": str(CADFIT_ROOT.resolve()),
                "python_bin": str(args.python.resolve()),
                "inner_workers": args.inner_workers,
                "max_iterations": args.max_iterations,
                "keep_history": args.keep_history,
                "part_timeout": args.part_timeout,
                "log_path": str((logs_dir / f"{pid}.log").resolve()),
            }
        )

    t0 = time.time()
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(worker, p): p["part_id"] for p in payloads}
        for fut in as_completed(futures):
            pid = futures[fut]
            try:
                row = fut.result()
            except Exception as exc:
                row = {"part_id": pid, "status": "exception", "error": repr(exc), "final_iou": None}
            manifest["results"].append(row)
            iou = row.get("final_iou")
            iou_s = f"{iou:.4f}" if isinstance(iou, (int, float)) else "n/a"
            print(f"[{row.get('status')}] {pid} IoU={iou_s} ({row.get('runtime_seconds', 0):.1f}s)")

    manifest["runtime_seconds"] = time.time() - t0
    manifest["finished_at"] = datetime.now(timezone.utc).isoformat()
    manifest["success_count"] = sum(1 for r in manifest["results"] if r.get("status") == "success")
    manifest["failed_count"] = len(manifest["results"]) - manifest["success_count"]
    write_json(out / "parallel_manifest.json", manifest)
    print(f"Done: success={manifest['success_count']} failed={manifest['failed_count']}")
    return 0 if manifest["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
