#!/usr/bin/env python3
"""Sequential tank protocol for ladder_more_v2: frontend on GPU 4, then CADFit+STEP+assembly."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_more_v2"
LOG = LADDER / "logs/run_all.log"
CADFIT_JOBS = 2
INNER = 8
MIN_FREE_MB = 22000


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
        [
            "nvidia-smi",
            "--query-gpu=index,memory.free",
            "--format=csv,noheader,nounits",
        ],
        text=True,
    )
    rows = []
    for line in out.strip().splitlines():
        idx, free = [p.strip() for p in line.split(",")]
        rows.append((int(idx), int(float(free))))
    return sorted(rows, key=lambda r: -r[1])


def pick_gpu(min_free_mb: int = MIN_FREE_MB) -> int:
    while True:
        rows = gpu_free_mb()
        idx, free = rows[0]
        log(f"gpu free {rows}")
        if free >= min_free_mb:
            return idx
        log(f"waiting for GPU with >={min_free_mb} MiB free; best gpu{idx}={free}")
        time.sleep(60)


def cadfit_busy() -> bool:
    """Avoid stacking on toaster/car CADFit workers."""
    markers = (
        "toaster_p3_xpart_cadfit_routea_v1/scripts/run_cadfit_parallel.py",
        "car_p3_xpart_cadfit_routea_v1/scripts/run_cadfit_parallel.py",
    )
    try:
        out = subprocess.check_output(["ps", "-ef"], text=True)
    except Exception:
        return False
    return any(m in out for m in markers)


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
    log(f"RC {case.name} {args[1] if len(args)>1 else args} rc={proc.returncode}")
    return proc.returncode


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    summary = []
    log(f"frontend start n={len(cases)}")
    for spec in cases:
        case = Path(spec["case_root"])
        stages = progress_stages(case)
        row = {"label": spec["label"], "case": str(case)}
        if "xpart" in stages and "stl" in stages:
            log(f"{spec['label']} frontend already done")
            row["frontend"] = "skip"
        else:
            gpu = pick_gpu()
            rc = run_stage(case, ["--stage", "frontend", "--gpu", str(gpu)], "frontend.log")
            row["frontend_rc"] = rc
            row["gpu"] = gpu
            if rc != 0:
                gpu = pick_gpu()
                log(f"{spec['label']} frontend retry gpu={gpu}")
                rc = run_stage(case, ["--stage", "frontend", "--gpu", str(gpu)], "frontend.log")
                row["frontend_rc"] = rc
                row["gpu"] = gpu
            if rc != 0:
                row["status"] = "frontend_fail"
                summary.append(row)
                continue
        while cadfit_busy():
            log(f"{spec['label']} waiting for toaster/car CADFit to free CPU")
            time.sleep(90)
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
        row["status"] = "ok" if row.get("step_rc", 1) == 0 and row.get("assembly_rc", 1) == 0 else "partial"
        summary.append(row)
        log(f"{spec['label']} status={row['status']}")
    out = LADDER / "logs/run_all_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "results": summary}, indent=2) + "\n")
    log(f"done {out}")
    bad = [r for r in summary if r.get("status") not in ("ok",)]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
