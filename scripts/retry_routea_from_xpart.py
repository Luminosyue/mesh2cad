#!/usr/bin/env python3
"""Retry Route A case from frozen P3: X-Part -> STL -> CADFit -> STEP -> assembly."""
from __future__ import annotations

import argparse
import fcntl
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
MIN_FREE_MB = 30000
MAX_FOREIGN_MB = 512


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(log_path: Path, msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
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


def acquire_gpu(log_path: Path) -> tuple[int, int]:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    while True:
        rows = gpu_free_mb()
        log(log_path, f"gpu free {rows}")
        for idx, free in rows:
            if free < MIN_FREE_MB:
                continue
            foreign = gpu_foreign_mb(idx)
            if foreign > MAX_FOREIGN_MB:
                log(log_path, f"skip gpu{idx} foreign={foreign} MiB")
                continue
            lock_path = LOCK_DIR / f"gpu{idx}.lock"
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                log(log_path, f"locked gpu{idx} free={free} foreign={foreign}")
                return idx, fd
            except BlockingIOError:
                os.close(fd)
        best = rows[0] if rows else (-1, 0)
        log(log_path, f"waiting exclusive GPU >={MIN_FREE_MB} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(20)


def source_mesh(case: Path) -> Path:
    for line in (case / "scripts/paths.py").read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("SOURCE =") and ".obj" in line:
            rel = line.split('"')[1]
            return case / rel
    objs = list((case / "source").glob("*.obj"))
    if not objs:
        raise FileNotFoundError(f"no source obj in {case / 'source'}")
    return objs[0]


def p3_parts(case: Path) -> int:
    meta = case / "p3/part_metadata.json"
    return int(json.loads(meta.read_text()).get("num_parts") or 0) if meta.is_file() else 0


def xpart_success(case: Path) -> int:
    manifest = case / "xpart/manifest.json"
    if not manifest.is_file():
        return 0
    try:
        return int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0)
    except Exception:
        return 0


def stl_count(case: Path) -> int:
    return len(list((case / "cadfit_routea/input_stl").glob("PART_*.stl")))


def wipe_xpart(case: Path) -> None:
    xp = case / "xpart"
    if xp.is_dir():
        for p in xp.glob("PART_*"):
            shutil.rmtree(p, ignore_errors=True)
        (xp / "manifest.json").unlink(missing_ok=True)
    stl = case / "cadfit_routea/input_stl"
    for p in stl.glob("PART_*.stl"):
        p.unlink()


def run_cmd(case: Path, log_path: Path, cmd: list[str], env: dict | None = None) -> int:
    log(log_path, "CMD " + " ".join(cmd))
    with log_path.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(case), env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    log(log_path, f"RC {rc}")
    return rc


def run_xpart(case: Path, log_path: Path, gpu: int, src: Path, octree: int) -> int:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HY3DGEN_MODELS"] = str(ROOT / "ours3/.cache/xpart")
    env.setdefault("MPLCONFIGDIR", str(case / "logs/mpl"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    return run_cmd(
        case,
        log_path,
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
            "--source-mesh",
            str(src),
            "--p3-dir",
            str(case / "p3"),
            "--out-dir",
            str(case / "xpart"),
        ],
        env,
    )


def retry_case(slug: str) -> int:
    case = ROOT / "ours3" / f"{slug}_p3_xpart_cadfit_routea_v1"
    pipe = case / "scripts/run_pipeline.py"
    log_path = case / "logs/retry_from_xpart.log"
    src = source_mesh(case)
    n_p3 = p3_parts(case)
    if n_p3 <= 0:
        log(log_path, f"{slug}: no frozen P3, abort")
        return 1

    log(log_path, f"=== retry {slug} from frozen P3 parts={n_p3} source={src.name} ===")
    wipe_xpart(case)

    gpu, fd = acquire_gpu(log_path)
    try:
        rc = run_xpart(case, log_path, gpu, src, 512)
        n_xp = xpart_success(case)
        log(log_path, f"xpart512 rc={rc} success={n_xp}/{n_p3}")
        if n_xp < max(1, (n_p3 + 1) // 2):
            log(log_path, "too few parts, retry octree=256")
            wipe_xpart(case)
            rc = run_xpart(case, log_path, gpu, src, 256)
            n_xp = xpart_success(case)
            log(log_path, f"xpart256 rc={rc} success={n_xp}/{n_p3}")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        log(log_path, f"released gpu{gpu}")

    if xpart_success(case) <= 0:
        log(log_path, f"{slug}: X-Part still 0, abort backend")
        return 1

    rc = run_cmd(case, log_path, [sys.executable, "-u", str(pipe), "--stage", "stl"])
    if rc != 0 or stl_count(case) <= 0:
        log(log_path, f"stl failed count={stl_count(case)}")
        return 1

    run_cmd(case, log_path, [sys.executable, "-u", str(pipe), "--stage", "dora"])
    run_cmd(
        case,
        log_path,
        [
            sys.executable,
            "-u",
            str(pipe),
            "--stage",
            "cadfit",
            "--skip-canary",
            "--jobs",
            "4",
            "--inner-workers",
            "4",
        ],
    )
    run_cmd(case, log_path, [sys.executable, "-u", str(pipe), "--stage", "step"])
    rc_asm = run_cmd(case, log_path, [sys.executable, "-u", str(pipe), "--stage", "assembly"])

    asm = case / "assembly/assembly_manifest.json"
    n_asm = 0
    if asm.is_file():
        n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0)
    log(
        log_path,
        f"done {slug} xpart={xpart_success(case)} stl={stl_count(case)} "
        f"assembly_parts={n_asm} assembly_rc={rc_asm}",
    )
    return 0 if rc_asm == 0 and n_asm > 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("slugs", nargs="+", help="case slug without _p3_xpart_cadfit_routea_v1 suffix")
    args = parser.parse_args()
    rc = 0
    for slug in args.slugs:
        if retry_case(slug) != 0:
            rc = 1
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
