#!/usr/bin/env python3
"""Continue building_5i: fill remaining 4 X-Part parts on exclusive GPU, then STL/CADFit/assembly."""
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

CASE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/building_5i_p3_xpart_cadfit_routea_v1")
PIPE = CASE / "scripts/run_pipeline.py"
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
LOG = CASE / "logs/continue_xpart4.log"
MIN_FREE_MB = 40000
MAX_FOREIGN_MB = 6000
TARGET = ["PART_002", "PART_003", "PART_004", "PART_006"]


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
                # re-check after lock
                free2 = dict(gpu_free_mb()).get(idx, 0)
                foreign2 = gpu_foreign_mb(idx)
                if free2 < MIN_FREE_MB or foreign2 > MAX_FOREIGN_MB:
                    log(f"unlock gpu{idx} raced free={free2} foreign={foreign2}")
                    fcntl.flock(fd, fcntl.LOCK_UN)
                    os.close(fd)
                    continue
                log(f"locked gpu{idx} free={free2} foreign={foreign2}")
                return idx, fd
            except BlockingIOError:
                os.close(fd)
        best = rows[0] if rows else (-1, 0)
        log(f"waiting exclusive GPU >={MIN_FREE_MB} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(30)


def run(cmd: list[str], env: dict | None = None) -> int:
    log("CMD " + " ".join(cmd))
    with LOG.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(CASE), env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"RC {rc}")
    return rc


def missing_targets() -> list[str]:
    out = []
    for pid in TARGET:
        idx = pid.split("_")[1]
        obj = CASE / "xpart" / pid / f"complete_part_{idx}.obj"
        if not (obj.is_file() and obj.stat().st_size > 0):
            out.append(pid)
    return out


def convert_stl(part_ids: list[str]) -> None:
    import trimesh

    stl_dir = CASE / "cadfit_routea/input_stl"
    stl_dir.mkdir(parents=True, exist_ok=True)
    for pid in part_ids:
        idx = int(pid.split("_")[1])
        obj = CASE / "xpart" / pid / f"complete_part_{idx:03d}.obj"
        if not obj.is_file():
            log(f"stl skip missing {pid}")
            continue
        mesh = trimesh.load(obj, force="mesh", process=False)
        stl = stl_dir / f"{pid}.stl"
        mesh.export(stl, file_type="stl")
        log(f"stl wrote {pid} bytes={stl.stat().st_size}")


def wait_other_pipeline() -> None:
    """Avoid racing the older retry_missing STL/CADFit stages."""
    while True:
        out = subprocess.check_output(["pgrep", "-af", "building_5i.*run_pipeline|building_5i.*obj_to_stl|building_5i.*run_cadfit"], text=True)
        lines = [l for l in out.splitlines() if "continue_xpart4" not in l and "pgrep" not in l]
        # ignore ourselves later
        busy = [l for l in lines if "retry_missing" in l or "obj_to_stl" in l or "run_cadfit" in l or "run_pipeline" in l]
        if not busy:
            return
        log(f"waiting other pipeline to finish ({len(busy)} procs)")
        time.sleep(60)


def main() -> int:
    miss = missing_targets()
    log(f"targets still missing={miss}")
    if miss:
        gpu, fd = acquire_gpu()
        try:
            env = os.environ.copy()
            env["CUDA_VISIBLE_DEVICES"] = str(gpu)
            env["HY3DGEN_MODELS"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart"
            env.setdefault("MPLCONFIGDIR", str(CASE / "logs/mpl"))
            Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
            env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
            for octree in (512, 256):
                miss = missing_targets()
                if not miss:
                    break
                log(f"xpart octree={octree} parts={miss}")
                rc = run(
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
                        "--skip-existing",
                        "--source-mesh",
                        str(CASE / "source/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"),
                        "--p3-dir",
                        str(CASE / "p3"),
                        "--out-dir",
                        str(CASE / "xpart"),
                        "--only-parts",
                        *miss,
                    ],
                    env,
                )
                log(f"xpart{octree} rc={rc} still={missing_targets()}")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            log(f"released gpu{gpu}")

    still = missing_targets()
    log(f"after xpart still_missing={still}")
    done_now = [p for p in TARGET if p not in still]
    if done_now:
        convert_stl(done_now)

    # Wait for older retry_missing (currently rewriting all STLs) to leave CADFit alone.
    wait_other_pipeline()

    # Ensure PART_020 retry still pending
    iou20 = CASE / "cadfit_routea/cadfit_raw/PART_020/final_iou.json"
    if iou20.is_file():
        log("PART_020 already has final_iou")
    else:
        raw20 = CASE / "cadfit_routea/cadfit_raw/PART_020"
        if raw20.is_dir() and not (raw20 / "best_greedy_parallel_iterative.step").is_file():
            # keep raw but ensure no stale lock
            lock = raw20 / ".running.lock"
            if lock.is_file():
                lock.unlink()
                log("cleared PART_020 lock")

    rc = run(
        [
            sys.executable,
            "-u",
            str(PIPE),
            "--stage",
            "cadfit",
            "--skip-canary",
            "--jobs",
            "4",
            "--inner-workers",
            "4",
        ]
    )
    run([sys.executable, "-u", str(PIPE), "--stage", "step"])
    rc_asm = run([sys.executable, "-u", str(PIPE), "--stage", "assembly"])
    asm = CASE / "assembly/assembly_manifest.json"
    n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0) if asm.is_file() else 0
    n_xp = sum(
        1
        for d in (CASE / "xpart").glob("PART_*")
        if (d / f"complete_part_{d.name.split('_')[1]}.obj").is_file()
    )
    log(f"done xpart={n_xp}/62 still={missing_targets()} assembly={n_asm} rc_asm={rc_asm}")
    return 0 if rc_asm == 0 and n_asm > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
