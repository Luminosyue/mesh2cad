#!/usr/bin/env python3
"""Run all tier-batch cases concurrently: frontend (GPU) then CADFit+STEP+assembly."""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_tier_batch_v1"
LOG = LADDER / "logs/run_all_concurrent.log"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
CADFIT_JOBS = 4
INNER = 4
MIN_FREE_MB = 36000
MAX_FOREIGN_MB = 512
MAX_WORKERS = 14


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def progress_stages(case: Path) -> set[str]:
    path = case / "logs/progress.txt"
    if not path.is_file():
        return set()
    stages = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            stages.add(json.loads(line).get("stage"))
        except json.JSONDecodeError:
            continue
    return stages


def gpu_free_mb() -> list[tuple[int, int]]:
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.free", "--format=csv,noheader,nounits"],
        text=True,
    )
    rows = []
    for line in out.strip().splitlines():
        idx, free = [p.strip() for p in line.split(",")]
        rows.append((int(idx), int(float(free))))
    return sorted(rows, key=lambda r: -r[1])


def gpu_foreign_mb(idx: int) -> int:
    try:
        out = subprocess.check_output(
            [
                "nvidia-smi",
                f"--id={idx}",
                "--query-compute-apps=pid,used_memory",
                "--format=csv,noheader,nounits",
            ],
            text=True,
        )
    except subprocess.CalledProcessError:
        return 0
    total = 0
    for line in out.strip().splitlines():
        parts = [p.strip() for p in line.split(",") if p.strip()]
        if len(parts) < 2:
            continue
        try:
            pid, used = int(parts[0]), int(float(parts[1]))
        except ValueError:
            continue
        try:
            owner = subprocess.check_output(["ps", "-o", "user=", "-p", str(pid)], text=True).strip()
        except subprocess.CalledProcessError:
            owner = ""
        if owner and owner != "cuiyuehan":
            total += used
    return total


class GpuLease:
    def __init__(self, idx: int, fd: int) -> None:
        self.idx = idx
        self._fd = fd

    def release(self) -> None:
        if self._fd >= 0:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = -1


def acquire_gpu(min_free_mb: int = MIN_FREE_MB) -> GpuLease:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        for idx, free in gpu_free_mb():
            if free < min_free_mb:
                continue
            if gpu_foreign_mb(idx) > MAX_FOREIGN_MB:
                continue
            lock_path = LOCK_DIR / f"gpu{idx}.lock"
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                return GpuLease(idx, fd)
            except BlockingIOError:
                os.close(fd)
        time.sleep(20)


def stl_ready(case: Path) -> bool:
    stls = list((case / "cadfit_routea/input_stl").glob("PART_*.stl"))
    return "stl" in progress_stages(case) or len(stls) > 0


def run_stage(case: Path, args: list[str], log_name: str) -> int:
    script = case / "scripts/run_pipeline.py"
    log_path = case / "logs" / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(
            [sys.executable, "-u", str(script), *args],
            cwd=str(case),
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    return proc.returncode


def run_frontend(case: Path, spec: dict) -> dict:
    label = spec["label"]
    row: dict = {"label": label, "case": str(case)}
    if stl_ready(case):
        row["frontend"] = "skip"
        row["status"] = "frontend_ok"
        return row

    batch = int(spec.get("xpart_batch_size") or 4)
    lease = acquire_gpu()
    gpu = lease.idx
    log(f"{label} frontend gpu={gpu} batch={batch}")
    try:
        rc = run_stage(
            case,
            ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", str(batch)],
            "frontend.log",
        )
        row["frontend_rc"] = rc
        row["gpu"] = gpu
        row["xpart_batch_size"] = batch
        if rc != 0:
            lease.release()
            lease = acquire_gpu()
            gpu = lease.idx
            log(f"{label} frontend retry gpu={gpu} batch=1")
            rc = run_stage(
                case,
                ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", "1"],
                "frontend.log",
            )
            row["frontend_rc"] = rc
            row["gpu"] = gpu
            row["xpart_batch_size"] = 1
    finally:
        lease.release()

    row["status"] = "frontend_ok" if rc == 0 and stl_ready(case) else "frontend_fail"
    log(f"{label} frontend status={row['status']}")
    return row


def run_backend(case: Path, label: str) -> dict:
    row: dict = {"label": label, "case": str(case), "status": "ok"}
    if not stl_ready(case):
        row["status"] = "no_stl"
        return row

    log(f"{label} CADFit -> STEP -> assembly")
    rc = run_stage(
        case,
        [
            "--stage",
            "cadfit",
            "--skip-canary",
            "--jobs",
            str(CADFIT_JOBS),
            "--inner-workers",
            str(INNER),
        ],
        "cadfit.log",
    )
    row["cadfit_rc"] = rc
    rc = run_stage(case, ["--stage", "step"], "step.log")
    row["step_rc"] = rc
    rc = run_stage(case, ["--stage", "assembly"], "assembly.log")
    row["assembly_rc"] = rc
    if row.get("step_rc", 1) != 0 or row.get("assembly_rc", 1) != 0:
        row["status"] = "partial"
    log(f"{label} backend status={row['status']}")
    return row


def run_case(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    log(f"=== start {label} ===")
    try:
        front = run_frontend(case, spec)
        if front.get("status") != "frontend_ok":
            return {**front, "status": front.get("status", "frontend_fail")}
        back = run_backend(case, label)
        return {**front, **back}
    except Exception as exc:
        log(f"{label} exception {exc!r}")
        return {"label": label, "case": str(case), "status": "exception", "error": repr(exc)}


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    n = len(cases)
    workers = min(MAX_WORKERS, n)
    log(f"tier batch concurrent start n={n} workers={workers}")
    results = []
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(run_case, spec): spec["label"] for spec in cases}
        for fut in as_completed(futs):
            label = futs[fut]
            try:
                row = fut.result()
            except Exception as exc:
                row = {"label": label, "status": "exception", "error": repr(exc)}
            results.append(row)
            log(f"finished {label} status={row.get('status')}")

    out = LADDER / "logs/run_all_concurrent_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"done {out}")
    bad = [r for r in results if r.get("status") not in ("ok", "frontend_ok")]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
