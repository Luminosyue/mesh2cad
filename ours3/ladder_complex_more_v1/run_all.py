#!/usr/bin/env python3
"""Full tank protocol for 4 unused complex cases, sequential.

P3 freeze -> Official X-Part (batch=1) -> Dora SES fork | CADFit Route A
-> STEP -> assembly (uniform scale + centroid, tank Route A).
Waits for an exclusive GPU. If X-Part recovers too few parts, retries octree=256.
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

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_complex_more_v1"
LOG = LADDER / "logs/run_all.log"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
CADFIT_JOBS = 4
INNER = 4
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
        rows = gpu_free_mb()
        log(f"gpu free {rows}")
        for idx, free in rows:
            if free < min_free_mb:
                continue
            foreign = gpu_foreign_mb(idx)
            if foreign > MAX_FOREIGN_MB:
                log(f"skip gpu{idx} foreign={foreign} MiB")
                continue
            lock_path = LOCK_DIR / f"gpu{idx}.lock"
            fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                log(f"picked gpu{idx} free={free} foreign={foreign}")
                return GpuLease(idx, fd)
            except BlockingIOError:
                os.close(fd)
        best = rows[0] if rows else (-1, 0)
        log(f"waiting exclusive GPU >={min_free_mb} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(30)


def run_stage(case: Path, args: list[str], log_name: str) -> int:
    script = case / "scripts/run_pipeline.py"
    log_path = case / "logs" / log_name
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log(f"CMD {case.name} {' '.join(args)}")
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(
            [sys.executable, "-u", str(script), *args],
            cwd=str(case),
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    log(f"RC {case.name} {args} rc={proc.returncode}")
    return proc.returncode


def p3_parts(case: Path) -> int:
    meta = case / "p3/part_metadata.json"
    if not meta.is_file():
        return 0
    return int(json.loads(meta.read_text()).get("num_parts") or 0)


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


def retry_xpart_octree256(case: Path, gpu: int, mesh_name: str) -> int:
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HY3DGEN_MODELS"] = str(ROOT / "ours3/.cache/xpart")
    env.setdefault("MPLCONFIGDIR", str(case / "logs/mpl"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    log_path = case / "logs/xpart_octree256.log"
    cmd = [
        str(HY3D_PY),
        "-u",
        str(case / "scripts/run_xpart.py"),
        "--gpu",
        str(gpu),
        "--octree-resolution",
        "256",
        "--batch-size",
        "1",
        "--source-mesh",
        str(case / "source" / mesh_name),
        "--p3-dir",
        str(case / "p3"),
        "--out-dir",
        str(case / "xpart"),
    ]
    log("CMD " + " ".join(cmd))
    with log_path.open("a", encoding="utf-8") as f:
        rc = subprocess.run(cmd, cwd=str(case), env=env, stdout=f, stderr=subprocess.STDOUT).returncode
    log(f"xpart256 rc={rc} success={xpart_success(case)}")
    return rc


def run_frontend(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    row: dict = {"label": label, "case": str(case)}
    if stl_count(case) > 0 and xpart_success(case) >= max(1, (p3_parts(case) + 1) // 2):
        log(f"{label} frontend already complete")
        row["frontend"] = "skip"
        row["status"] = "frontend_ok"
        return row

    lease = acquire_gpu()
    gpu = lease.idx
    batch = int(spec.get("xpart_batch_size") or 1)
    try:
        rc = run_stage(
            case,
            ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", str(batch)],
            "frontend.log",
        )
        row["frontend_rc"] = rc
        row["gpu"] = gpu
        n_p3 = p3_parts(case)
        n_xp = xpart_success(case)
        row["p3_parts"] = n_p3
        row["xpart_success"] = n_xp
        min_keep = max(1, (n_p3 + 1) // 2) if n_p3 else 1
        if n_p3 > 0 and n_xp < min_keep:
            log(f"{label} X-Part too few ({n_xp}/{n_p3}); retry octree=256 batch=1")
            wipe_xpart(case)
            rc2 = retry_xpart_octree256(case, gpu, spec["mesh"])
            row["xpart256_rc"] = rc2
            row["xpart_success"] = xpart_success(case)
            run_stage(case, ["--stage", "stl"], "frontend.log")
            run_stage(case, ["--stage", "dora"], "frontend.log")
    finally:
        lease.release()

    row["stl"] = stl_count(case)
    row["status"] = "frontend_ok" if stl_count(case) > 0 else "frontend_fail"
    log(f"{label} frontend status={row['status']} p3={row.get('p3_parts')} xpart={row.get('xpart_success')} stl={row['stl']}")
    return row


def run_backend(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    row: dict = {"label": label, "case": str(case), "status": "ok"}
    if stl_count(case) <= 0:
        row["status"] = "no_stl"
        return row
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
    asm = case / "assembly/assembly_manifest.json"
    n_asm = 0
    if asm.is_file():
        n_asm = int(json.loads(asm.read_text()).get("parts_in_assembly") or 0)
    row["assembly_parts"] = n_asm
    if row.get("step_rc", 1) != 0 or row.get("assembly_rc", 1) != 0 or n_asm <= 0:
        row["status"] = "partial"
    log(f"{label} backend status={row['status']} assembly_parts={n_asm}")
    return row


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    log(f"complex-more start n={len(cases)} labels={[c['label'] for c in cases]}")
    results = []
    for spec in cases:
        log(f"=== start {spec['label']} ===")
        try:
            front = run_frontend(spec)
            if front.get("status") != "frontend_ok":
                results.append(front)
                continue
            back = run_backend(spec)
            results.append({**front, **back})
        except Exception as exc:
            log(f"{spec['label']} exception {exc!r}")
            results.append({"label": spec["label"], "status": "exception", "error": repr(exc)})
    out = LADDER / "logs/run_all_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"done {out}")
    bad = [r for r in results if r.get("status") not in ("ok",)]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
