#!/usr/bin/env python3
"""Retry the 7 X-Part-failed cases with exclusive GPU and lower octree."""
from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
LOG = OURS3 / "retry_failed_routea/logs/retry_xpart_seven.log"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
MIN_FREE_MB = 38000
MAX_FOREIGN_MB = 512
CADFIT_JOBS = 4
INNER = 4
OCTREES = (256, 128)

SLUGS = [
    "kitch_island_p3_xpart_cadfit_routea_v1",
    "birdhouse_p3_xpart_cadfit_routea_v1",
    "birdhouse_toy_p3_xpart_cadfit_routea_v1",
    "food_processor_p3_xpart_cadfit_routea_v1",
    "speaker_small_p3_xpart_cadfit_routea_v1",
    "fire_truck_p3_xpart_cadfit_routea_v1",
    "white_cabinet_p3_xpart_cadfit_routea_v1",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


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


def acquire_gpu() -> GpuLease:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        for idx, free in gpu_free_mb():
            if free < MIN_FREE_MB:
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


def run_cmd(cmd: list[str], cwd: Path, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log(f"CMD {' '.join(cmd)}")
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=f, stderr=subprocess.STDOUT)
    log(f"RC {proc.returncode}")
    return proc.returncode


def xpart_ok(case: Path) -> bool:
    manifest = case / "xpart/manifest.json"
    if not manifest.is_file():
        return False
    try:
        return int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0) > 0
    except Exception:
        return False


def stl_ready(case: Path) -> bool:
    stl_dir = case / "cadfit_routea/input_stl"
    return stl_dir.is_dir() and bool(list(stl_dir.glob("PART_*.stl")))


def clear_xpart(case: Path) -> None:
    xp = case / "xpart"
    if not xp.is_dir():
        return
    for p in xp.glob("PART_*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    (xp / "manifest.json").unlink(missing_ok=True)


def run_pipeline(case: Path, args: list[str], log_name: str) -> int:
    return run_cmd(
        [sys.executable, "-u", str(case / "scripts/run_pipeline.py"), *args],
        case,
        case / "logs" / log_name,
    )


def run_xpart(case: Path, gpu: int, octree: int) -> int:
    return run_cmd(
        [
            str(HY3D_PY),
            "-u",
            str(case / "scripts/run_xpart.py"),
            "--gpu",
            str(gpu),
            "--octree-resolution",
            str(octree),
            "--batch-size",
            "1",
        ],
        case,
        case / "logs/xpart_seven.log",
    )


def run_backend(case: Path, label: str) -> dict:
    row: dict = {"label": label, "status": "ok"}
    rc = run_pipeline(
        case,
        ["--stage", "cadfit", "--skip-canary", "--jobs", str(CADFIT_JOBS), "--inner-workers", str(INNER)],
        "cadfit.log",
    )
    row["cadfit_rc"] = rc
    rc = run_pipeline(case, ["--stage", "step"], "step.log")
    row["step_rc"] = rc
    rc = run_pipeline(case, ["--stage", "assembly"], "assembly.log")
    row["assembly_rc"] = rc
    if row.get("step_rc", 1) != 0 or row.get("assembly_rc", 1) != 0:
        row["status"] = "partial"
    return row


def run_case(slug: str) -> dict:
    case = OURS3 / slug
    label = slug.split("_p3_")[0]
    log(f"=== {label} ===")
    if stl_ready(case):
        log(f"{label} STL already ready")
        return run_backend(case, label)
    if not (case / "p3/part_metadata.json").is_file():
        return {"label": label, "status": "no_p3"}

    if not xpart_ok(case):
        clear_xpart(case)
        for octree in OCTREES:
            lease = acquire_gpu()
            gpu = lease.idx
            log(f"{label} X-Part octree={octree} gpu={gpu}")
            try:
                rc = run_xpart(case, gpu, octree)
            finally:
                lease.release()
            if rc == 0 and xpart_ok(case):
                break
            clear_xpart(case)
        if not xpart_ok(case):
            return {"label": label, "status": "xpart_fail"}

    rc = run_pipeline(case, ["--stage", "stl"], "stl.log")
    if rc != 0 or not stl_ready(case):
        return {"label": label, "status": "stl_fail"}
    return run_backend(case, label)


def main() -> int:
    log(f"xpart seven start n={len(SLUGS)} octrees={OCTREES}")
    results = []
    with ProcessPoolExecutor(max_workers=2) as pool:
        futs = {pool.submit(run_case, slug): slug for slug in SLUGS}
        for fut in as_completed(futs):
            slug = futs[fut]
            label = slug.split("_p3_")[0]
            try:
                row = fut.result()
            except Exception as exc:
                row = {"label": label, "status": "exception", "error": repr(exc)}
            results.append(row)
            log(f"done {label} status={row.get('status')}")
    out = OURS3 / "retry_failed_routea/logs/retry_xpart_seven_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"summary {out}")
    return 0 if all(r.get("status") in ("ok", "partial") for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
