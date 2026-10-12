#!/usr/bin/env python3
"""Retry incomplete Route A cases concurrently; skip cases already running."""
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
LOG = OURS3 / "retry_failed_routea/logs/retry.log"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
MIN_FREE_MB = 36000
MAX_FOREIGN_MB = 512
CADFIT_JOBS = 4
INNER = 4
MAX_WORKERS = 8
MIN_P3_PARTS = 3  # re-run P3 if frozen count below this (paintmaker had 2)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_case_specs() -> list[dict]:
    specs: dict[str, dict] = {}
    for path in OURS3.glob("ladder_*/cases.json"):
        data = json.loads(path.read_text())
        for c in data.get("cases", []):
            label = c["label"]
            specs[label] = {
                "label": label,
                "case_root": c["case_root"],
                "xpart_batch_size": c.get("xpart_batch_size", 4),
                "slug": c.get("slug", f"{label}_p3_xpart_cadfit_routea_v1"),
            }
    for case_dir in OURS3.glob("*_p3_xpart_cadfit_routea_v1"):
        label = case_dir.name.split("_p3_")[0]
        if label not in specs:
            specs[label] = {
                "label": label,
                "case_root": str(case_dir),
                "xpart_batch_size": 4,
                "slug": case_dir.name,
            }
    return list(specs.values())


def assembly_done(case: Path) -> bool:
    asm = case / "assembly"
    return asm.is_dir() and bool(list(asm.glob("*_cad_native.step")))


def stl_ready(case: Path) -> bool:
    stl_dir = case / "cadfit_routea/input_stl"
    return stl_dir.is_dir() and bool(list(stl_dir.glob("PART_*.stl")))


def p3_parts(case: Path) -> int:
    meta = case / "p3/part_metadata.json"
    if meta.is_file():
        try:
            return int(json.loads(meta.read_text()).get("num_parts") or 0)
        except Exception:
            pass
    return len(list((case / "p3").glob("part_*.obj"))) if (case / "p3").is_dir() else 0


def xpart_ok(case: Path) -> bool:
    manifest = case / "xpart/manifest.json"
    if not manifest.is_file():
        return False
    try:
        return int(json.loads(manifest.read_text()).get("XPART_SUCCESSFUL_PARTS") or 0) > 0
    except Exception:
        return False


def case_active(case: Path) -> bool:
    slug = case.name
    try:
        out = subprocess.check_output(["ps", "-ef"], text=True)
    except Exception:
        return False
    markers = (
        f"{slug}/scripts/run_pipeline.py",
        f"{slug}/scripts/run_p3.py",
        f"{slug}/scripts/run_xpart.py",
        f"{slug}/scripts/run_cadfit",
    )
    return any(m in out for m in markers)


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
        time.sleep(25)


def run_cmd(cmd: list[str], cwd: Path, log_path: Path) -> int:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log(f"CMD {' '.join(cmd)}")
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(cmd, cwd=str(cwd), stdout=f, stderr=subprocess.STDOUT)
    log(f"RC {proc.returncode}")
    return proc.returncode


def run_pipeline(case: Path, args: list[str], log_name: str) -> int:
    return run_cmd(
        [sys.executable, "-u", str(case / "scripts/run_pipeline.py"), *args],
        case,
        case / "logs" / log_name,
    )


def run_xpart(case: Path, gpu: int, octree: int, batch: int) -> int:
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
            str(batch),
        ],
        case,
        case / "logs/xpart_retry.log",
    )


def clear_xpart(case: Path) -> None:
    xp = case / "xpart"
    if not xp.is_dir():
        return
    for p in xp.glob("PART_*"):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
    (xp / "manifest.json").unlink(missing_ok=True)


def clear_p3(case: Path) -> None:
    p3 = case / "p3"
    if not p3.is_dir():
        return
    for p in p3.glob("part_*"):
        if p.is_file():
            p.unlink()
    for p in p3.glob("*.json"):
        p.unlink(missing_ok=True)


def needs_p3_reset(case: Path) -> bool:
    n = p3_parts(case)
    return 0 < n < MIN_P3_PARTS


def ensure_frontend(case: Path, spec: dict) -> dict:
    label = spec["label"]
    row: dict = {"label": label, "case": str(case)}

    if stl_ready(case):
        row["status"] = "frontend_ok"
        row["frontend"] = "skip"
        return row

    if needs_p3_reset(case):
        log(f"{label} reset partial P3 parts={p3_parts(case)}")
        clear_p3(case)
        clear_xpart(case)

    batch = int(spec.get("xpart_batch_size") or 4)
    lease = acquire_gpu()
    gpu = lease.idx
    log(f"{label} frontend gpu={gpu} batch={batch}")
    try:
        rc = run_pipeline(
            case,
            ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", str(batch)],
            "frontend_retry.log",
        )
        if rc != 0 or not stl_ready(case):
            lease.release()
            lease = acquire_gpu()
            gpu = lease.idx
            log(f"{label} frontend retry gpu={gpu} batch=1")
            rc = run_pipeline(
                case,
                ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", "1"],
                "frontend_retry.log",
            )
    finally:
        lease.release()

    if stl_ready(case):
        row["status"] = "frontend_ok"
        return row

    # P3 done but XPart failed: try lower octree
    if p3_parts(case) >= MIN_P3_PARTS and not stl_ready(case):
        for octree, batch in ((512, 1), (256, 1), (128, 1)):
            if xpart_ok(case):
                break
            clear_xpart(case)
            lease = acquire_gpu()
            gpu = lease.idx
            log(f"{label} xpart-only octree={octree} batch={batch} gpu={gpu}")
            try:
                rc = run_xpart(case, gpu, octree, batch)
            finally:
                lease.release()
            if rc == 0 and xpart_ok(case):
                break
        rc = run_pipeline(case, ["--stage", "stl"], "stl_retry.log")
        if rc == 0 and stl_ready(case):
            row["status"] = "frontend_ok"
            return row

    row["status"] = "frontend_fail"
    return row


def run_backend(case: Path, label: str) -> dict:
    row: dict = {"label": label, "case": str(case), "status": "ok"}
    if not stl_ready(case):
        row["status"] = "no_stl"
        return row
    log(f"{label} CADFit -> STEP -> assembly")
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


def run_case(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    if assembly_done(case):
        return {"label": label, "status": "skip_done"}
    if case_active(case):
        return {"label": label, "status": "skip_active"}
    log(f"=== retry {label} ===")
    try:
        if stl_ready(case):
            return run_backend(case, label)
        front = ensure_frontend(case, spec)
        if front.get("status") != "frontend_ok":
            return front
        return run_backend(case, label)
    except Exception as exc:
        log(f"{label} exception {exc!r}")
        return {"label": label, "status": "exception", "error": repr(exc)}


def pending_cases() -> list[dict]:
    out = []
    for spec in load_case_specs():
        case = Path(spec["case_root"])
        if not case.is_dir():
            continue
        if assembly_done(case):
            continue
        out.append(spec)
    return out


def main() -> int:
    cases = pending_cases()
    log(f"retry start pending={len(cases)} workers={min(MAX_WORKERS, len(cases))}")
    results = []
    workers = min(MAX_WORKERS, max(len(cases), 1))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(run_case, spec): spec["label"] for spec in cases}
        for fut in as_completed(futs):
            label = futs[fut]
            try:
                row = fut.result()
            except Exception as exc:
                row = {"label": label, "status": "exception", "error": repr(exc)}
            results.append(row)
            log(f"done {label} status={row.get('status')}")
    out = OURS3 / "retry_failed_routea/logs/retry_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"summary {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
