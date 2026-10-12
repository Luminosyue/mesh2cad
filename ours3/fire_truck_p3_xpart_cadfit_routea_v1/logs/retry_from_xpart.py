#!/usr/bin/env python3
"""Retry fire_truck from frozen P3: exclusive GPU X-Part -> STL -> CADFit -> STEP -> assembly."""
from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CASE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/fire_truck_p3_xpart_cadfit_routea_v1")
PIPE = CASE / "scripts/run_pipeline.py"
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
LOG = CASE / "logs/retry_from_xpart.log"
MIN_FREE_MB = 30000
MAX_FOREIGN_MB = 512


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


def acquire_gpu() -> tuple[int, int]:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        rows = gpu_free_mb()
        log(f"gpu free {rows}")
        for idx, free in rows:
            if free < MIN_FREE_MB:
                continue
            foreign = gpu_foreign_mb(idx)
            if foreign > MAX_FOREIGN_MB:
                log(f"skip gpu{idx} foreign={foreign} MiB")
                continue
            lock_path = LOCK_DIR / f"gpu{idx}.lock"
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                log(f"locked gpu{idx} free={free} foreign={foreign}")
                return idx, fd
            except BlockingIOError:
                os.close(fd)
        best = rows[0] if rows else (-1, 0)
        log(f"waiting exclusive GPU >={MIN_FREE_MB} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(20)


def run(cmd: list[str], env: dict | None = None) -> int:
    log("CMD " + " ".join(cmd))
    with LOG.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(CASE), env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"RC {rc}")
    return rc


def xpart_success() -> int:
    manifest = CASE / "xpart/manifest.json"
    if not manifest.is_file():
        return 0
    try:
        return int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0)
    except Exception:
        return 0


def p3_parts() -> int:
    meta = CASE / "p3/part_metadata.json"
    return int(json.loads(meta.read_text()).get("num_parts") or 0) if meta.is_file() else 0


def stl_count() -> int:
    return len(list((CASE / "cadfit_routea/input_stl").glob("PART_*.stl")))


def wipe_outputs() -> None:
    xp = CASE / "xpart"
    if xp.is_dir():
        for p in xp.glob("PART_*"):
            shutil.rmtree(p, ignore_errors=True)
        (xp / "manifest.json").unlink(missing_ok=True)
    stl = CASE / "cadfit_routea/input_stl"
    for p in stl.glob("PART_*.stl"):
        p.unlink()
    for sub in ("cadfit_raw", "step"):
        d = CASE / "cadfit_routea" / sub
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)
    asm = CASE / "assembly"
    if asm.is_dir():
        for p in asm.glob("*"):
            if p.is_file():
                p.unlink()


def run_xpart(gpu: int, octree: int) -> int:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HY3DGEN_MODELS"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart"
    env.setdefault("MPLCONFIGDIR", str(CASE / "logs/mpl"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    return run(
        [
            str(HY3D_PY),
            "-u",
            str(CASE / "scripts/run_xpart.py"),
            "--gpu",
            str(gpu),
            "--octree-resolution",
            str(octree),
            "--batch-size",
            "1",
            "--source-mesh",
            str(CASE / "source/FIRE_TRUCK.obj"),
            "--p3-dir",
            str(CASE / "p3"),
            "--out-dir",
            str(CASE / "xpart"),
        ],
        env,
    )


def main() -> int:
    n_p3 = p3_parts()
    if n_p3 <= 0:
        log("no frozen P3, abort")
        return 1
    log(f"retry fire_truck v2 from frozen P3 parts={n_p3}; keep any xpart512>0, only fallback 256 if 512=0")
    wipe_outputs()

    gpu, fd = acquire_gpu()
    try:
        rc = run_xpart(gpu, 512)
        n_xp = xpart_success()
        log(f"xpart512 rc={rc} success={n_xp}/{n_p3}")
        # Do NOT wipe a partial 512 success — last time 3/8 was wiped then 256 OOM'd to 0.
        if n_xp <= 0:
            log("xpart512 empty, retry octree=256")
            wipe_xpart_only()
            rc = run_xpart(gpu, 256)
            n_xp = xpart_success()
            log(f"xpart256 rc={rc} success={n_xp}/{n_p3}")
        else:
            log(f"keep xpart512 success={n_xp}, skip 256 fallback")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        log(f"released gpu{gpu}")

    if xpart_success() <= 0:
        log("X-Part still 0, abort backend")
        return 1

    rc = run([sys.executable, "-u", str(PIPE), "--stage", "stl"])
    if rc != 0 or stl_count() <= 0:
        log(f"stl failed count={stl_count()}")
        return 1
    run([sys.executable, "-u", str(PIPE), "--stage", "dora"])
    rc = run(
        [
            sys.executable,
            "-u",
            str(PIPE),
            "--stage",
            "cadfit",
            "--skip-canary",
            "--jobs",
            "1",
            "--inner-workers",
            "4",
        ]
    )
    run([sys.executable, "-u", str(PIPE), "--stage", "step"])
    rc_asm = run([sys.executable, "-u", str(PIPE), "--stage", "assembly"])
    asm = CASE / "assembly/assembly_manifest.json"
    n_asm = 0
    if asm.is_file():
        n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0)
    log(f"done xpart={xpart_success()} stl={stl_count()} assembly_parts={n_asm} assembly_rc={rc_asm}")
    return 0 if rc_asm == 0 and n_asm > 0 else 1


def wipe_xpart_only() -> None:
    xp = CASE / "xpart"
    if xp.is_dir():
        for p in xp.glob("PART_*"):
            shutil.rmtree(p, ignore_errors=True)
        (xp / "manifest.json").unlink(missing_ok=True)
    stl = CASE / "cadfit_routea/input_stl"
    for p in stl.glob("PART_*.stl"):
        p.unlink()


if __name__ == "__main__":
    raise SystemExit(main())
