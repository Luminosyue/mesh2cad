#!/usr/bin/env python3
"""Retry building_5i: fill missing X-Part parts, redo failed CADFit, reassemble.

Keeps successful CADFit results. Exclusive GPU for X-Part.
"""
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
LOG = CASE / "logs/retry_missing.log"
MIN_FREE_MB = 38000
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


def missing_xpart_ids() -> list[str]:
    p3 = {
        f"PART_{int(p.stem.split('_')[1]):03d}"
        for p in (CASE / "p3").glob("part_*.obj")
    }
    have = set()
    for d in (CASE / "xpart").glob("PART_*"):
        idx = d.name.split("_")[1]
        if (d / f"complete_part_{idx}.obj").is_file():
            have.add(d.name)
    return sorted(p3 - have)


def wipe_failed_cadfit(part_id: str) -> None:
    raw = CASE / "cadfit_routea/cadfit_raw" / part_id
    if raw.is_dir():
        shutil.rmtree(raw, ignore_errors=True)
        log(f"wiped cadfit_raw/{part_id}")
    step = CASE / "cadfit_routea/step" / part_id
    if step.is_dir():
        shutil.rmtree(step, ignore_errors=True)
        log(f"wiped step/{part_id}")


def main() -> int:
    missing = missing_xpart_ids()
    log(f"missing xpart parts={missing} count={len(missing)}")

    # PART_020 previously exited 0 without final_iou.json — force retry.
    wipe_failed_cadfit("PART_020")

    if missing:
        gpu, fd = acquire_gpu()
        try:
            env = os.environ.copy()
            env["CUDA_VISIBLE_DEVICES"] = str(gpu)
            env["HY3DGEN_MODELS"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart"
            env.setdefault("MPLCONFIGDIR", str(CASE / "logs/mpl"))
            Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
            env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
            rc = run(
                [
                    str(HY3D_PY),
                    "-u",
                    str(CASE / "scripts/run_xpart.py"),
                    "--gpu",
                    str(gpu),
                    "--octree-resolution",
                    "512",
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
                    *missing,
                ],
                env,
            )
            still = missing_xpart_ids()
            log(f"xpart rc={rc} still_missing={still}")
            if still:
                log("retry remaining with octree=256")
                rc = run(
                    [
                        str(HY3D_PY),
                        "-u",
                        str(CASE / "scripts/run_xpart.py"),
                        "--gpu",
                        str(gpu),
                        "--octree-resolution",
                        "256",
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
                        *still,
                    ],
                    env,
                )
                still = missing_xpart_ids()
                log(f"xpart256 rc={rc} still_missing={still}")
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
            os.close(fd)
            log(f"released gpu{gpu}")
    else:
        log("no missing xpart; skip GPU stage")

    # Force STL rebuild for any new xparts (stage_stl skips when counts match).
    # Temporarily remove stl skip by deleting STLs for newly filled parts only.
    for pid in missing:
        stl = CASE / "cadfit_routea/input_stl" / f"{pid}.stl"
        if stl.is_file():
            stl.unlink()
    # Also ensure PART_020 stl exists.
    if not (CASE / "cadfit_routea/input_stl/PART_020.stl").is_file():
        pass

    rc = run([sys.executable, "-u", str(PIPE), "--stage", "stl"])
    if rc != 0:
        log("stl failed")
        return 1

    # CADFit only pending (includes PART_020 + any new parts without final_iou).
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
    log(f"cadfit rc={rc}")

    run([sys.executable, "-u", str(PIPE), "--stage", "step"])
    rc_asm = run([sys.executable, "-u", str(PIPE), "--stage", "assembly"])

    asm = CASE / "assembly/assembly_manifest.json"
    n_asm = 0
    if asm.is_file():
        n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0)
    n_xp = 0
    xp_manifest = CASE / "xpart/manifest.json"
    if xp_manifest.is_file():
        n_xp = int(json.loads(xp_manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0)
    still = missing_xpart_ids()
    log(f"done xpart={n_xp} still_missing={still} assembly_parts={n_asm} assembly_rc={rc_asm}")
    return 0 if rc_asm == 0 and n_asm > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
