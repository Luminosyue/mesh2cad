#!/usr/bin/env python3
"""Concurrent tank-protocol pool for the 10 complex cases.

- Frontend (P3/X-Part): grab exclusive free GPUs as they appear; multiple frontends OK.
- Backend (CADFit/STEP/assembly): start as soon as a case has STLs; do not wait for other
  cases' frontends. Multiple CADFits run in parallel on CPU.
- cabinet_drawer: retry from frozen P3 (X-Part failed previously).
- school_bus / speaker_big: if CADFit already running, only watch then STEP+assembly.
"""
from __future__ import annotations

import fcntl
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_complex_ten_v1"
LOG = LADDER / "logs/run_parallel_pool.log"
LOCK_DIR = Path("/tmp/mesh2cad_gpu_locks")
HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
CADFIT_JOBS = 4
INNER = 4
MIN_FREE_MB = 30000
# Speed mode: if free VRAM is enough for P3/X-Part, take the card even if others
# have small footprints (exclusive wait was stalling for hours).
MAX_FOREIGN_MB = 20000
MAX_BACKEND = 4  # concurrent CADFit/STEP/assembly jobs


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


_log_lock = threading.Lock()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with _log_lock:
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


def try_acquire_gpu(min_free_mb: int = MIN_FREE_MB) -> GpuLease | None:
    LOCK_DIR.mkdir(parents=True, exist_ok=True)
    for idx, free in gpu_free_mb():
        if free < min_free_mb:
            continue
        foreign = gpu_foreign_mb(idx)
        if foreign > MAX_FOREIGN_MB:
            log(f"skip gpu{idx} free={free} foreign={foreign} (>{MAX_FOREIGN_MB})")
            continue
        lock_path = LOCK_DIR / f"gpu{idx}.lock"
        fd = os.open(str(lock_path), os.O_CREAT | os.O_RDWR, 0o666)
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            log(f"picked gpu{idx} free={free} foreign={foreign}")
            return GpuLease(idx, fd)
        except BlockingIOError:
            os.close(fd)
    return None


def acquire_gpu_blocking(label: str) -> GpuLease:
    while True:
        lease = try_acquire_gpu()
        if lease is not None:
            return lease
        rows = gpu_free_mb()
        best = rows[0] if rows else (-1, 0)
        log(f"{label} waiting GPU free>={MIN_FREE_MB} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(8)


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


def iou_count(case: Path) -> int:
    return len(list((case / "cadfit_routea/cadfit_raw").glob("PART_*/final_iou.json")))


def assembly_done(case: Path) -> bool:
    return any((case / "assembly").glob("*_cad_native.step")) if (case / "assembly").is_dir() else False


def cadfit_running_locks(case: Path) -> list[str]:
    raw = case / "cadfit_routea/cadfit_raw"
    if not raw.is_dir():
        return []
    return [p.name for p in sorted(raw.glob("PART_*")) if (p / ".running.lock").is_file()]


def our_cadfit_procs(case: Path) -> list[int]:
    needle = str(case / "cadfit_routea")
    try:
        out = subprocess.check_output(["pgrep", "-af", "run_cadfit_parallel|greedy_search|_run_single"], text=True)
    except subprocess.CalledProcessError:
        return []
    pids = []
    for line in out.splitlines():
        if needle not in line:
            continue
        if "pgrep" in line:
            continue
        try:
            pids.append(int(line.split(None, 1)[0]))
        except ValueError:
            continue
    return pids


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
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
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
    if assembly_done(case):
        row["status"] = "already_done"
        return row
    if stl_count(case) > 0 and xpart_success(case) >= max(1, (p3_parts(case) + 1) // 2):
        log(f"{label} frontend already complete stl={stl_count(case)}")
        row["status"] = "frontend_ok"
        row["stl"] = stl_count(case)
        return row

    # Frozen P3 but failed X-Part: wipe and retry from X-Part only via full frontend
    # (pipeline skips existing P3).
    if p3_parts(case) > 0 and xpart_success(case) == 0:
        log(f"{label} retry from frozen P3={p3_parts(case)}; wipe prior xpart")
        wipe_xpart(case)

    lease = acquire_gpu_blocking(label)
    gpu = lease.idx
    batch = int(spec.get("xpart_batch_size") or 1)
    try:
        # Skip Dora SES (does not feed CADFit) to save time.
        run_stage(case, ["--stage", "p3", "--gpu", str(gpu)], "frontend.log")
        rc = run_stage(
            case,
            ["--stage", "xpart", "--gpu", str(gpu), "--xpart-batch-size", str(batch)],
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
            log(f"{label} X-Part too few ({n_xp}/{n_p3}); retry octree=256")
            wipe_xpart(case)
            rc2 = retry_xpart_octree256(case, gpu, spec["mesh"])
            row["xpart256_rc"] = rc2
            row["xpart_success"] = xpart_success(case)
        run_stage(case, ["--stage", "stl"], "frontend.log")
    finally:
        lease.release()
        log(f"{label} released gpu{gpu}")

    row["stl"] = stl_count(case)
    row["status"] = "frontend_ok" if stl_count(case) > 0 else "frontend_fail"
    log(f"{label} frontend status={row['status']} p3={row.get('p3_parts')} xpart={row.get('xpart_success')} stl={row['stl']}")
    return row


def wait_existing_cadfit(case: Path, label: str, timeout_s: int = 7 * 24 * 3600) -> None:
    """Wait until in-flight CADFit (orphan from old scheduler) finishes."""
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        locks = cadfit_running_locks(case)
        procs = our_cadfit_procs(case)
        n_stl = stl_count(case)
        n_iou = iou_count(case)
        if not locks and not procs and n_stl > 0 and n_iou >= n_stl:
            log(f"{label} existing CADFit complete iou={n_iou}/{n_stl}")
            return
        if not locks and not procs and n_stl > 0 and n_iou > 0:
            # some parts may have failed; treat as done if no workers left
            log(f"{label} existing CADFit idle iou={n_iou}/{n_stl} (no workers); continue")
            return
        if not locks and not procs and n_iou == 0 and n_stl > 0:
            # CADFit never started or died early — fall through to start
            log(f"{label} no live CADFit workers; will start backend")
            return
        log(f"{label} watch CADFit iou={n_iou}/{n_stl} locks={locks[:2]} procs={len(procs)}")
        time.sleep(60)
    log(f"{label} CADFit watch timeout")


def run_backend(spec: dict, watch_existing: bool = False) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    row: dict = {"label": label, "case": str(case), "status": "ok"}
    if assembly_done(case):
        row["status"] = "already_done"
        return row
    if stl_count(case) <= 0:
        row["status"] = "no_stl"
        return row

    if watch_existing or cadfit_running_locks(case) or our_cadfit_procs(case):
        log(f"{label} backend: watching existing CADFit")
        wait_existing_cadfit(case, label)
        # If still incomplete after watch with no workers, start remaining
        if iou_count(case) < stl_count(case) and not our_cadfit_procs(case) and not cadfit_running_locks(case):
            log(f"{label} resume CADFit remaining {iou_count(case)}/{stl_count(case)}")
            run_stage(
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
    else:
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
    if assembly_done(case):
        row["status"] = "ok"
    log(f"{label} backend status={row['status']} assembly_parts={n_asm}")
    return row


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    log(f"parallel-pool start n={len(cases)} labels={[c['label'] for c in cases]}")

    results: dict[str, dict] = {}
    results_lock = threading.Lock()
    backend_sem = threading.Semaphore(MAX_BACKEND)
    backend_futures = []

    def submit_backend(spec: dict, watch_existing: bool = False) -> None:
        def _job() -> None:
            with backend_sem:
                try:
                    back = run_backend(spec, watch_existing=watch_existing)
                except Exception as exc:
                    log(f"{spec['label']} backend exception {exc!r}")
                    back = {"label": spec["label"], "status": "exception", "error": repr(exc)}
                with results_lock:
                    results[spec["label"]] = {**results.get(spec["label"], {}), **back}

        fut = executor.submit(_job)
        backend_futures.append(fut)

    with ThreadPoolExecutor(max_workers=len(cases) + MAX_BACKEND) as executor:
        # Phase: classify each case
        need_frontend: list[dict] = []
        for spec in cases:
            case = Path(spec["case_root"])
            label = spec["label"]
            if assembly_done(case):
                log(f"{label} already has assembly; skip")
                results[label] = {"label": label, "status": "already_done"}
                continue
            if stl_count(case) > 0:
                # Frontend done — start/watch CADFit immediately, do not block others
                watch = bool(cadfit_running_locks(case) or our_cadfit_procs(case))
                log(f"{label} STL ready iou={iou_count(case)}/{stl_count(case)}; enqueue backend watch={watch}")
                results[label] = {"label": label, "status": "frontend_ok", "stl": stl_count(case)}
                submit_backend(spec, watch_existing=watch)
            else:
                need_frontend.append(spec)

        log(f"need_frontend={[c['label'] for c in need_frontend]}")

        # Priority: cabinet_drawer first (user-requested), grab a GPU before others.
        priority = [c for c in need_frontend if c["label"] == "cabinet_drawer"]
        rest = [c for c in need_frontend if c["label"] != "cabinet_drawer"]
        need_frontend = priority + rest

        # Frontend pool: as many concurrent as free GPUs (cabinet first in queue)
        fe_lock = threading.Lock()
        fe_idx = {"i": 0}

        def frontend_worker() -> None:
            while True:
                with fe_lock:
                    i = fe_idx["i"]
                    if i >= len(need_frontend):
                        return
                    fe_idx["i"] = i + 1
                    spec = need_frontend[i]
                label = spec["label"]
                log(f"=== frontend start {label} ===")
                try:
                    front = run_frontend(spec)
                except Exception as exc:
                    log(f"{label} frontend exception {exc!r}")
                    front = {"label": label, "status": "exception", "error": repr(exc)}
                with results_lock:
                    results[label] = {**results.get(label, {}), **front}
                if front.get("status") == "frontend_ok":
                    # Immediately CADFit — do not wait for other frontends
                    submit_backend(spec, watch_existing=False)
                else:
                    log(f"{label} skip backend (frontend_fail)")

        # Start cabinet alone first so it wins the first free GPU, then open the floodgates.
        if priority:
            log("priority frontend: cabinet_drawer first")
            fe_futures_prio = [executor.submit(frontend_worker)]
            # Wait until cabinet has acquired a GPU (or finished/failed) before launching others.
            # Heuristic: poll until cabinet leaves "waiting GPU" or has gpu in results / 90s max.
            t_prio = time.time()
            while time.time() - t_prio < 90:
                with results_lock:
                    st = results.get("cabinet_drawer", {})
                if st.get("gpu") is not None or st.get("status") in ("frontend_ok", "frontend_fail", "exception", "already_done"):
                    break
                # also break once a p3 process for cabinet exists
                try:
                    subprocess.check_output(["pgrep", "-f", "cabinet_drawer_p3_xpart.*/run_p3"], text=True)
                    break
                except subprocess.CalledProcessError:
                    pass
                time.sleep(2)
            log("priority window done; launching remaining frontend workers")
            n_fe_workers = min(len(rest), 4)
            fe_futures = fe_futures_prio + [executor.submit(frontend_worker) for _ in range(n_fe_workers)]
        else:
            n_fe_workers = min(len(need_frontend), 4) if need_frontend else 0
            fe_futures = [executor.submit(frontend_worker) for _ in range(n_fe_workers)]
        for fut in fe_futures:
            fut.result()

        for fut in backend_futures:
            fut.result()

    out = LADDER / "logs/run_parallel_pool_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": results}, indent=2) + "\n")
    log(f"done {out}")
    bad = [r for r in results.values() if r.get("status") not in ("ok", "already_done")]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
