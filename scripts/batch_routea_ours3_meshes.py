#!/usr/bin/env python3
"""Batch Route A on ours3/meshes — aggressive GPU pool + resume on new GPU."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import queue
import re
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MESHES = ROOT / "ours3/meshes"
TEMPLATE = ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1"
ASM_TMPL = ROOT / "ours3/ladder_more_v2/templates/build_assembly.py"
SHARP = ROOT / "ours3/dora_ses_xpart45_v1/vendor/sharp_sample.py"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
PYTHON = Path("/data/miniconda3/envs/hy3d/bin/python")

# Grab any card with enough free VRAM even if others have a footprint.
MIN_FREE_MB = 8000
MAX_FOREIGN_MB = 32000
POLL_SEC = 2
# Keep swapping GPUs forever until case_done(); only stop on --max-attempts if set.
MAX_RETRIES = 0  # 0 = unlimited
# CADFit / STEP are mostly CPU — do not hold exclusive GPU locks for them.
CPU_STAGES = frozenset({"cadfit", "step", "qa"})

_log_lock = threading.Lock()
_summary_lock = threading.Lock()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str, log_path: Path | None = None) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    if log_path:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with _log_lock:
            with log_path.open("a", encoding="utf-8") as f:
                f.write(line + "\n")


def slug_from_mesh(name: str) -> str:
    stem = Path(name).stem
    return re.sub(r"[^a-zA-Z0-9]+", "_", stem).strip("_").lower()[:60].strip("_")


def case_for_mesh(mesh: Path) -> Path | None:
    for case in (ROOT / "ours3").iterdir():
        if not case.is_dir():
            continue
        src = case / "source"
        if src.is_dir() and (src / mesh.name).is_file():
            return case
    slug = slug_from_mesh(mesh.name)
    cand = ROOT / "ours3" / f"{slug}_p3_xpart_cadfit_routea_v1"
    return cand if cand.is_dir() else None


def case_done(case: Path) -> bool:
    asm = (case / "assembly").is_dir() and any((case / "assembly").glob("*_cad_native.step"))
    stl_dir = case / "cadfit_routea/input_stl"
    raw = case / "cadfit_routea/cadfit_raw"
    if not stl_dir.is_dir():
        return False
    stls = sorted(stl_dir.glob("PART_*.stl"))
    if not stls:
        return False
    iou = sum(1 for s in stls if (raw / s.stem / "final_iou.json").is_file())
    return asm and iou >= len(stls)


def stage_for_case(case: Path | None) -> str:
    if case is None or not case.is_dir():
        return "all"
    stl_dir = case / "cadfit_routea/input_stl"
    raw = case / "cadfit_routea/cadfit_raw"
    if stl_dir.is_dir() and list(stl_dir.glob("PART_*.stl")):
        stls = sorted(stl_dir.glob("PART_*.stl"))
        iou = sum(1 for s in stls if (raw / s.stem / "final_iou.json").is_file())
        if iou < len(stls):
            return "cadfit"
        if not any((case / "assembly").glob("*_cad_native.step")) if (case / "assembly").is_dir() else True:
            return "step"
        return "step"
    if (case / "xpart/manifest.json").is_file():
        xp = json.loads((case / "xpart/manifest.json").read_text(encoding="utf-8"))
        if int(xp.get("XPART_SUCCESSFUL_PARTS") or 0) > 0:
            return "cadfit"
        if (case / "p3/part_metadata.json").is_file():
            return "xpart"
    if (case / "p3/part_metadata.json").is_file():
        return "xpart"
    return "all"


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
    def __init__(self, idx: int, fd: int, free_mb: int) -> None:
        self.idx = idx
        self._fd = fd
        self.free_mb = free_mb

    def release(self) -> None:
        if self._fd >= 0:
            fcntl.flock(self._fd, fcntl.LOCK_UN)
            os.close(self._fd)
            self._fd = -1


def try_acquire_gpu(exclude: set[int] | None = None) -> GpuLease | None:
    exclude = exclude or set()
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    for idx, free in gpu_free_mb():
        if idx in exclude:
            continue
        if free < MIN_FREE_MB:
            continue
        foreign = gpu_foreign_mb(idx)
        if foreign > MAX_FOREIGN_MB:
            continue
        lock_path = LOCK_DIR / f"gpu{idx}.lock"
        fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return GpuLease(idx, fd, free)
        except BlockingIOError:
            os.close(fd)
    return None


def acquire_gpu_blocking(label: str, log_path: Path, exclude: set[int] | None = None) -> GpuLease:
    """Grab any free GPU. If exclude blocks all candidates, clear exclude and cycle."""
    exclude = set(exclude or set())
    waited = 0
    while True:
        lease = try_acquire_gpu(exclude)
        if lease is not None:
            log(f"{label} locked gpu{lease.idx} free={lease.free_mb} exclude={sorted(exclude)}", log_path)
            return lease
        # If every free card is excluded, drop exclude so we can reuse GPUs.
        free_ok = [i for i, free in gpu_free_mb() if free >= MIN_FREE_MB and gpu_foreign_mb(i) <= MAX_FOREIGN_MB]
        if exclude and free_ok and all(i in exclude for i in free_ok):
            log(f"{label} all free GPUs tried {sorted(exclude)}; cycling", log_path)
            exclude.clear()
            continue
        rows = gpu_free_mb()
        best = rows[0] if rows else (-1, 0)
        if waited % 10 == 0:
            log(f"{label} waiting GPU free>={MIN_FREE_MB}; best gpu{best[0]}={best[1]}", log_path)
        waited += 1
        time.sleep(POLL_SEC)


def scaffold_case(mesh: Path, case: Path) -> None:
    if (case / "scripts/run_pipeline.py").is_file():
        return
    import shutil
    import textwrap

    scripts = case / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    for sub in (
        "source",
        "logs",
        "artifacts",
        "dora_ses/vendor",
        "cadfit_routea/input_stl",
        "cadfit_routea/cadfit_raw",
        "cadfit_routea/step",
    ):
        (case / sub).mkdir(parents=True, exist_ok=True)
    for py in (TEMPLATE / "scripts").glob("*.py"):
        if py.name == "paths.py":
            continue
        shutil.copy2(py, scripts / py.name)
    if ASM_TMPL.is_file():
        shutil.copy2(ASM_TMPL, scripts / "build_assembly.py")
    if SHARP.is_file():
        shutil.copy2(SHARP, case / "dora_ses/vendor/sharp_sample.py")
    dst = case / "source" / mesh.name
    if not dst.is_file():
        shutil.copy2(mesh, dst)
    paths = textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        from pathlib import Path

        ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
        CASE = ROOT / "ours3/{case.name}"
        SOURCE = CASE / "source/{mesh.name}"
        SOURCE_ORIG = ROOT / "ours3/meshes/{mesh.name}"
        P3_DIR = CASE / "p3"
        XPART_DIR = CASE / "xpart"
        DORA_DIR = CASE / "dora_ses"
        CADFIT_DIR = CASE / "cadfit_routea"
        STL_DIR = CADFIT_DIR / "input_stl"
        CADFIT_RAW = CADFIT_DIR / "cadfit_raw"
        STEP_DIR = CADFIT_DIR / "step"
        LOGS = CASE / "logs"

        HUNYUAN_PY = Path("/data/miniconda3/envs/hunyuan/bin/python")
        HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
        CADFIT_PY = Path("/data/miniconda3/envs/cadfit-env/bin/python")
        BLENDER_PY = Path("/data/home/hhfzhang/.conda/envs/blender/bin/python")
        CADFIT_REPO = ROOT / "CADFit"
        XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
        P3_ROOT = ROOT / "Hunyuan3D-Part/P3-SAM"
        HY3DGEN_MODELS = ROOT / "ours3/.cache/xpart"
        """
    )
    (scripts / "paths.py").write_text(paths, encoding="utf-8")


GPU_STAGES = frozenset({"all", "xpart", "p3"})
CPU_TAIL_STAGES = frozenset({"cadfit", "step", "qa"})


def build_queue(limit: int, stage_filter: str | None = None) -> list[dict]:
    items = []
    for mesh in sorted(MESHES.glob("*.obj")):
        case = case_for_mesh(mesh)
        if case and case_done(case):
            continue
        slug = slug_from_mesh(mesh.name)
        case_name = f"{slug}_p3_xpart_cadfit_routea_v1"
        case_root = case if case else ROOT / "ours3" / case_name
        st = stage_for_case(case)
        if stage_filter == "gpu" and st not in GPU_STAGES:
            continue
        if stage_filter == "cpu" and st not in CPU_TAIL_STAGES:
            continue
        items.append(
            {
                "mesh": str(mesh),
                "mesh_name": mesh.name,
                "case_name": case_name,
                "case_root": str(case_root),
                "stage": st,
            }
        )
    # Prefer GPU stages first so free cards are not idled behind STEP/CADFit CPU tails.
    def _prio(it: dict) -> tuple[int, str]:
        st = it["stage"]
        if st in GPU_STAGES:
            return (0, it["mesh_name"])
        if st == "cadfit":
            return (1, it["mesh_name"])
        return (2, it["mesh_name"])

    items.sort(key=_prio)
    return items[:limit]


def pipe_stage_for(stage: str) -> str:
    if stage == "all":
        return "all"
    if stage == "cadfit":
        return "cadfit"
    if stage == "xpart":
        return "xpart"
    if stage in {"qa", "step"}:
        return "step"
    return stage


def wipe_xpart(case: Path) -> None:
    import shutil

    xp = case / "xpart"
    if xp.is_dir():
        for p in xp.glob("PART_*"):
            shutil.rmtree(p, ignore_errors=True)
        (xp / "manifest.json").unlink(missing_ok=True)
    stl = case / "cadfit_routea/input_stl"
    if stl.is_dir():
        for p in stl.glob("PART_*.stl"):
            p.unlink(missing_ok=True)


def run_xpart_octree256(case: Path, mesh: Path, gpu: int, log_path: Path) -> int:
    """Tank-protocol fallback: wipe failed X-Part and retry with octree=256."""
    wipe_xpart(case)
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HY3DGEN_MODELS"] = str(ROOT / "ours3/.cache/xpart")
    env.setdefault("MPLCONFIGDIR", str(case / "logs/mpl"))
    Path(env["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)
    cmd = [
        str(PYTHON),
        "-u",
        str(case / "scripts/run_xpart.py"),
        "--gpu",
        str(gpu),
        "--octree-resolution",
        "256",
        "--batch-size",
        "1",
        "--source-mesh",
        str(case / "source" / mesh.name),
        "--p3-dir",
        str(case / "p3"),
        "--out-dir",
        str(case / "xpart"),
    ]
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{utc_now()}] XPART256 CMD {' '.join(cmd)}\n")
        return subprocess.run(cmd, cwd=str(case), env=env, stdout=f, stderr=subprocess.STDOUT).returncode


def _run_pipeline_cmd(
    case: Path,
    log_path: Path,
    gpu: int,
    pipe_stage: str,
    cadfit_jobs: int,
    inner_workers: int,
    xpart_batch_size: int,
) -> int:
    args = [
        "--stage",
        pipe_stage,
        "--gpu",
        str(gpu),
        "--skip-canary",
        "--xpart-batch-size",
        str(xpart_batch_size),
    ]
    if pipe_stage in {"cadfit", "all"}:
        args += ["--jobs", str(cadfit_jobs), "--inner-workers", str(inner_workers)]
    cmd = [str(PYTHON), "-u", str(case / "scripts/run_pipeline.py"), *args]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{utc_now()}] gpu={gpu} stage={pipe_stage} CMD {' '.join(cmd)}\n")
        return subprocess.run(cmd, cwd=str(case), stdout=f, stderr=subprocess.STDOUT).returncode


def run_pipeline_once(
    item: dict,
    log_path: Path,
    gpu: int,
    cadfit_jobs: int,
    inner_workers: int,
    xpart_batch_size: int = 1,
) -> int:
    mesh = Path(item["mesh"])
    case = Path(item["case_root"])
    scaffold_case(mesh, case)
    stage = stage_for_case(case)
    # STEP alone never marks case_done (needs assembly). Run both.
    if stage in {"step", "qa"}:
        rc = _run_pipeline_cmd(case, log_path, gpu, "step", cadfit_jobs, inner_workers, xpart_batch_size)
        if rc != 0:
            return rc
        return _run_pipeline_cmd(case, log_path, gpu, "assembly", cadfit_jobs, inner_workers, xpart_batch_size)
    pipe_stage = pipe_stage_for(stage)
    return _run_pipeline_cmd(case, log_path, gpu, pipe_stage, cadfit_jobs, inner_workers, xpart_batch_size)


def run_one(item: dict, log_root: Path, cadfit_jobs: int, inner_workers: int, max_attempts: int = 0) -> dict:
    """Retry forever (or until max_attempts) swapping GPUs until case_done."""
    mesh = Path(item["mesh"])
    case = Path(item["case_root"])
    log_path = log_root / f"{slug_from_mesh(mesh.name)}.log"
    label = mesh.name
    tried_gpus: set[int] = set()
    xpart_fail_streak = 0
    step_nop_streak = 0
    row = {
        "mesh": mesh.name,
        "case_name": item["case_name"],
        "status": "failed",
        "attempts": [],
    }
    attempt = 0
    while True:
        attempt += 1
        if max_attempts > 0 and attempt > max_attempts:
            row["status"] = "failed" if not row.get("done") else "ok"
            break
        if case.is_dir() and case_done(case):
            row["status"] = "ok"
            row["done"] = True
            break

        stage_before = stage_for_case(case)
        lease: GpuLease | None = None
        gpu_idx = 0

        # CADFit/STEP are CPU-heavy: do not hold exclusive GPU locks.
        if stage_before in CPU_STAGES:
            log(f"{label} stage={stage_before} CPU path (no GPU lock)", log_path)
            gpu_idx = 0
        else:
            if len(tried_gpus) >= 8:
                tried_gpus.clear()
            lease = acquire_gpu_blocking(label, log_path, exclude=tried_gpus)
            tried_gpus.add(lease.idx)
            gpu_idx = lease.idx

        att = {"attempt": attempt, "gpu": gpu_idx, "cpu_stage": stage_before in CPU_STAGES}
        try:
            if stage_before == "xpart" and xpart_fail_streak >= 1 and lease is not None:
                log(f"{label} X-Part fallback octree=256 on gpu{gpu_idx}", log_path)
                rc256 = run_xpart_octree256(case, mesh, gpu_idx, log_path)
                att["xpart256_rc"] = rc256
                if rc256 == 0:
                    xpart_fail_streak = 0
                    # Release GPU before CADFit so other P3/XPart jobs can grab it.
                    if lease is not None:
                        lease.release()
                        lease = None
                    rc = run_pipeline_once(item, log_path, gpu_idx, cadfit_jobs, inner_workers, xpart_batch_size=1)
                else:
                    rc = rc256
            else:
                rc = run_pipeline_once(item, log_path, gpu_idx, cadfit_jobs, inner_workers, xpart_batch_size=1)
                # After successful P3/XPart landing in cadfit, free the card ASAP.
                if rc == 0 and lease is not None and stage_for_case(case) in CPU_STAGES:
                    lease.release()
                    lease = None
                    log(f"{label} released GPU after frontend; next is CPU cadfit/step", log_path)

            att["returncode"] = rc
            att["stage"] = stage_for_case(case)
            att["done"] = case_done(case) if case.is_dir() else False
            row["gpu"] = gpu_idx
            row["attempts"].append(att)

            if att["done"]:
                row["status"] = "ok"
                break

            if rc == 0:
                row["status"] = "partial"
                # Detect CADFit no-op spin: stage unchanged + instant return.
                if stage_before in CPU_STAGES and att["stage"] == stage_before:
                    # Clear stale locks that make cadfit say "Nothing pending"
                    for lock in (case / "cadfit_routea/cadfit_raw").glob("PART_*/.running.lock"):
                        try:
                            lock.unlink()
                            log(f"{label} cleared stale lock {lock}", log_path)
                        except OSError:
                            pass
                    step_nop_streak += 1
                    log(
                        f"{label} no-progress on {stage_before}; "
                        f"streak={step_nop_streak}; backoff then retry",
                        log_path,
                    )
                    # Don't pin workers forever on broken STEP/assembly tails.
                    if stage_before == "step" and step_nop_streak >= 3:
                        row["status"] = "partial"
                        log(f"{label} give up step after {step_nop_streak} no-progress", log_path)
                        break
                    time.sleep(15)
                else:
                    log(f"{label} partial stage={att['stage']} -> continue", log_path)
                    xpart_fail_streak = 0
                    step_nop_streak = 0
                    # One CADFit slice per worker turn — free slot for X-Part / P3 queue.
                    if stage_before == "cadfit" and att["stage"] == "cadfit":
                        row["status"] = "partial"
                        log(f"{label} cadfit slice done; yield worker for GPU queue", log_path)
                        break
            else:
                row["status"] = "failed"
                if att["stage"] in {"xpart", "all"} or stage_before == "xpart":
                    xpart_fail_streak += 1
                log(
                    f"{label} attempt {attempt} failed rc={rc} gpu={gpu_idx} "
                    f"stage={att['stage']} streak={xpart_fail_streak} -> swap gpu & retry",
                    log_path,
                )
        except Exception as exc:
            att["error"] = repr(exc)
            row["attempts"].append(att)
            log(f"{label} attempt {attempt} exception {exc!r} -> swap gpu & retry", log_path)
        finally:
            if lease is not None:
                lease.release()

        time.sleep(1)

    row["done"] = case_done(case) if case.is_dir() else False
    if row["done"]:
        row["status"] = "ok"
    log(f"{label} finished status={row['status']} attempts={len(row['attempts'])}", log_path)
    return row


def worker(
    work_q: queue.Queue,
    log_root: Path,
    cadfit_jobs: int,
    inner_workers: int,
    summary: dict,
    summary_path: Path,
    counter: dict,
    total: int,
    pool_log: Path,
    max_attempts: int,
) -> None:
    while True:
        try:
            item = work_q.get_nowait()
        except queue.Empty:
            return
        try:
            row = run_one(item, log_root, cadfit_jobs, inner_workers, max_attempts=max_attempts)
        except Exception as exc:
            row = {"mesh": item["mesh_name"], "status": "exception", "error": repr(exc)}
        with _summary_lock:
            summary["results"].append(row)
            key = row.get("status", "failed")
            summary[key] = summary.get(key, 0) + 1
            counter["done"] += 1
            n = counter["done"]
            summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        print(
            f"[{n}/{total}] {item['mesh_name']} -> {row.get('status')} attempts={len(row.get('attempts', []))}",
            flush=True,
        )
        log(f"worker done {item['mesh_name']} status={row.get('status')}", pool_log)
        work_q.task_done()


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggressive parallel Route A batch")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--jobs", type=int, default=6, help="Max concurrent cases")
    parser.add_argument("--cadfit-jobs", type=int, default=2)
    parser.add_argument("--inner-workers", type=int, default=4)
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=0,
        help="Per-mesh attempt cap; 0 = keep swapping GPUs until success",
    )
    parser.add_argument("--log-root", type=Path, default=ROOT / "ours3/batch_routea_100_v1/logs")
    parser.add_argument("--manifest", type=Path, default=ROOT / "ours3/batch_routea_100_v1/manifest.json")
    parser.add_argument(
        "--gpu-only",
        action="store_true",
        help="Only queue all/xpart/p3 cases (skip cadfit/step tails)",
    )
    parser.add_argument(
        "--cpu-only",
        action="store_true",
        help="Only queue cadfit/step tails",
    )
    parser.add_argument(
        "--resume-summary",
        action="store_true",
        help="Append to existing summary.json instead of resetting counters",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    stage_filter = None
    if args.gpu_only:
        stage_filter = "gpu"
    elif args.cpu_only:
        stage_filter = "cpu"

    queue_items = build_queue(args.limit, stage_filter=stage_filter)
    payload = {
        "created_at": utc_now(),
        "limit": args.limit,
        "jobs": args.jobs,
        "stage_filter": stage_filter,
        "min_free_mb": MIN_FREE_MB,
        "max_attempts": args.max_attempts,
        "count": len(queue_items),
        "queue": queue_items,
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"count": len(queue_items), "jobs": args.jobs, "max_attempts": args.max_attempts}, indent=2))

    if args.dry_run:
        for i, item in enumerate(queue_items[:10], 1):
            print(f"{i}. {item['mesh_name']} stage={item['stage']}")
        return 0

    pool_log = args.log_root / "parallel_pool.log"
    summary_path = args.manifest.parent / "summary.json"
    if args.resume_summary and summary_path.is_file():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        summary["resumed_at"] = utc_now()
        summary["jobs"] = args.jobs
        summary["stage_filter"] = stage_filter
        for k in ("ok", "partial", "failed", "exception"):
            summary.setdefault(k, 0)
        summary.setdefault("results", [])
    else:
        if summary_path.is_file():
            bak = args.manifest.parent / f"summary_prev_{int(time.time())}.json"
            summary_path.rename(bak)
        summary = {
            "started_at": utc_now(),
            "jobs": args.jobs,
            "stage_filter": stage_filter,
            "max_attempts": args.max_attempts,
            "ok": 0,
            "partial": 0,
            "failed": 0,
            "exception": 0,
            "results": [],
        }
    work_q: queue.Queue = queue.Queue()
    for item in queue_items:
        work_q.put(item)

    log(
        f"pool start n={len(queue_items)} jobs={args.jobs} filter={stage_filter or 'all'} "
        f"min_free={MIN_FREE_MB} max_attempts={args.max_attempts or 'unlimited'}",
        pool_log,
    )
    threads = []
    counter = {"done": 0}
    for _ in range(min(args.jobs, len(queue_items))):
        t = threading.Thread(
            target=worker,
            args=(
                work_q,
                args.log_root,
                args.cadfit_jobs,
                args.inner_workers,
                summary,
                summary_path,
                counter,
                len(queue_items),
                pool_log,
                args.max_attempts,
            ),
            daemon=True,
        )
        t.start()
        threads.append(t)
    for t in threads:
        t.join()

    summary["finished_at"] = utc_now()
    with _summary_lock:
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    log(f"pool done ok={summary['ok']} partial={summary['partial']} failed={summary['failed']}", pool_log)
    return 0 if summary.get("failed", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
