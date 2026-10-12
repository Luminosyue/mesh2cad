#!/usr/bin/env python3
"""Fresh construction_30 run: empty GPU, X-Part batch=1, then CADFit."""
from __future__ import annotations

import fcntl
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

CASE = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/construction_30_p3_xpart_cadfit_routea_v1")
PIPE = CASE / "scripts/run_pipeline.py"
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
LOCK_PATH = Path("/tmp/mesh2cad_gpu_locks/gpu5.lock")
GPU = 5
LOG = CASE / "logs/rerun_from_scratch.log"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def run(cmd: list[str]) -> int:
    log("CMD " + " ".join(cmd))
    with LOG.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(CASE), stdout=f, stderr=subprocess.STDOUT).returncode
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
    if not meta.is_file():
        return 0
    return int(json.loads(meta.read_text()).get("num_parts") or 0)


def stl_count() -> int:
    return len(list((CASE / "cadfit_routea/input_stl").glob("PART_*.stl")))


def main() -> int:
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(LOCK_PATH), os.O_CREAT | os.O_RDWR, 0o666)
    log(f"acquire gpu{GPU} lock")
    fcntl.flock(fd, fcntl.LOCK_EX)
    log(f"locked gpu{GPU}")
    try:
        rc = run(
            [
                sys.executable,
                "-u",
                str(PIPE),
                "--stage",
                "frontend",
                "--gpu",
                str(GPU),
                "--xpart-batch-size",
                "1",
            ]
        )
        n_p3 = p3_parts()
        n_xp = xpart_success()
        log(f"frontend rc={rc} p3={n_p3} xpart={n_xp} stl={stl_count()}")
        if n_p3 > 0 and n_xp < max(8, n_p3 // 2):
            log(f"X-Part too few ({n_xp}/{n_p3}); retry octree=256 batch=1")
            xp = CASE / "xpart"
            if xp.is_dir():
                for p in xp.glob("PART_*"):
                    if p.is_dir():
                        subprocess.run(["rm", "-rf", str(p)])
                (xp / "manifest.json").unlink(missing_ok=True)
            env = os.environ.copy()
            env["CUDA_VISIBLE_DEVICES"] = str(GPU)
            env["HY3DGEN_MODELS"] = "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart"
            env.setdefault("MPLCONFIGDIR", str(CASE / "logs/mpl"))
            Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
            log("CMD xpart octree=256")
            with LOG.open("a", encoding="utf-8") as f:
                rc2 = subprocess.run(
                    [
                        str(HY3D_PY),
                        "-u",
                        str(CASE / "scripts/run_xpart.py"),
                        "--gpu",
                        str(GPU),
                        "--octree-resolution",
                        "256",
                        "--batch-size",
                        "1",
                        "--source-mesh",
                        str(CASE / "source/30_CONSTRUCTION_SET.obj"),
                        "--p3-dir",
                        str(CASE / "p3"),
                        "--out-dir",
                        str(CASE / "xpart"),
                    ],
                    cwd=str(CASE),
                    env=env,
                    stdout=f,
                    stderr=subprocess.STDOUT,
                ).returncode
            log(f"xpart256 rc={rc2} success={xpart_success()}")
            run([sys.executable, "-u", str(PIPE), "--stage", "stl"])
            log(f"stl after retry={stl_count()}")
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
        log(f"released gpu{GPU}")

    if stl_count() <= 0:
        log("no STL, abort backend")
        return 1

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
    n_xp = xpart_success()
    asm = CASE / "assembly/assembly_manifest.json"
    n_asm = 0
    if asm.is_file():
        n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0)
    log(f"done xpart={n_xp} stl={stl_count()} assembly_parts={n_asm} cadfit_rc={rc} assembly_rc={rc_asm}")
    return 0 if rc_asm == 0 and n_asm > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
