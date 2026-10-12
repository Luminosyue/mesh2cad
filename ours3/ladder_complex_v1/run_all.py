#!/usr/bin/env python3
"""Full tank protocol for complex cases: frontend then concurrent CADFit+STEP+assembly."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_complex_v1"
LOG = LADDER / "logs/run_all.log"
CADFIT_JOBS = 3
INNER = 8
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


def progress_stages(case: Path) -> set[str]:
    path = case / "logs/progress.txt"
    if not path.is_file():
        return set()
    stages = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            stages.add(json.loads(line).get("stage"))
        except json.JSONDecodeError:
            continue
    return stages


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
    """Memory used by compute apps that are not this user."""
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


def pick_gpu(min_free_mb: int = MIN_FREE_MB) -> int:
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
            log(f"picked gpu{idx} free={free} foreign={foreign}")
            return idx
        best = rows[0]
        log(f"waiting for exclusive GPU >={min_free_mb} MiB; best gpu{best[0]}={best[1]}")
        time.sleep(30)


def stl_ready(case: Path) -> bool:
    stls = list((case / "cadfit_routea/input_stl").glob("PART_*.stl"))
    return "stl" in progress_stages(case) or len(stls) > 0


def cadfit_pending(case: Path) -> list[str]:
    stl_dir = case / "cadfit_routea/input_stl"
    raw = case / "cadfit_routea/cadfit_raw"
    pending = []
    for stl in sorted(stl_dir.glob("PART_*.stl")):
        iou = raw / stl.stem / "final_iou.json"
        if not (iou.is_file() and iou.stat().st_size > 0):
            pending.append(stl.stem)
    return pending


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


def run_frontend(spec: dict) -> dict:
    case = Path(spec["case_root"])
    row = {"label": spec["label"], "case": str(case)}
    if stl_ready(case):
        log(f"{spec['label']} frontend already done")
        row["frontend"] = "skip"
        row["status"] = "frontend_ok"
        return row
    gpu = pick_gpu()
    batch = int(spec.get("xpart_batch_size") or 4)
    rc = run_stage(
        case,
        ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", str(batch)],
        "frontend.log",
    )
    row["frontend_rc"] = rc
    row["gpu"] = gpu
    row["xpart_batch_size"] = batch
    if rc != 0:
        gpu = pick_gpu()
        log(f"{spec['label']} frontend retry gpu={gpu} batch=1")
        rc = run_stage(
            case,
            ["--stage", "frontend", "--gpu", str(gpu), "--xpart-batch-size", "1"],
            "frontend.log",
        )
        row["frontend_rc"] = rc
        row["gpu"] = gpu
        row["xpart_batch_size"] = 1
    row["status"] = "frontend_ok" if rc == 0 and stl_ready(case) else "frontend_fail"
    return row


def run_cadfit_case(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    row = {"label": label, "case": str(case), "status": "ok"}
    if not stl_ready(case):
        row["status"] = "wait_stl"
        return row
    pending = cadfit_pending(case)
    log(f"{label} pending CADFit {len(pending)} {pending}")
    if pending:
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
        still = cadfit_pending(case)
        if still:
            row["status"] = "cadfit_partial"
            row["still_pending"] = still
    rc = run_stage(case, ["--stage", "step"], "step.log")
    row["step_rc"] = rc
    rc = run_stage(case, ["--stage", "assembly"], "assembly.log")
    row["assembly_rc"] = rc
    if row["status"] == "ok" and (row.get("step_rc", 1) != 0 or row.get("assembly_rc", 1) != 0):
        row["status"] = "partial"
    log(f"{label} cadfit/step/assembly status={row['status']}")
    return row


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    log(f"complex frontend start n={len(cases)}")
    frontend = []
    for spec in cases:
        row = run_frontend(spec)
        frontend.append(row)
        log(f"{spec['label']} frontend status={row['status']}")
    (LADDER / "logs/frontend_summary.json").write_text(
        json.dumps({"finished_at": utc_now(), "results": frontend}, indent=2) + "\n"
    )
    ready = [s for s, r in zip(cases, frontend) if r.get("status") == "frontend_ok"]
    log(f"CADFit concurrent start jobs={CADFIT_JOBS} ready={[s['label'] for s in ready]}")
    results = []
    if ready:
        with ProcessPoolExecutor(max_workers=len(ready)) as pool:
            futs = {pool.submit(run_cadfit_case, spec): spec["label"] for spec in ready}
            for fut in as_completed(futs):
                label = futs[fut]
                try:
                    row = fut.result()
                except Exception as exc:
                    row = {"label": label, "status": "exception", "error": repr(exc)}
                results.append(row)
                log(f"finished {label} {row}")
    out = LADDER / "logs/run_all_summary.json"
    out.write_text(
        json.dumps(
            {
                "finished_at": utc_now(),
                "frontend": frontend,
                "cadfit": results,
            },
            indent=2,
        )
        + "\n"
    )
    log(f"done {out}")
    bad = [r for r in frontend if r.get("status") != "frontend_ok"] + [
        r for r in results if r.get("status") not in ("ok",)
    ]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
