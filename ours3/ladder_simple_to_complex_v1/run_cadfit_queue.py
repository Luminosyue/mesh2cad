#!/usr/bin/env python3
"""Concurrent CADFit+STEP for the simple-to-complex ladder.

Cases run in parallel. Inside each case, CADFit uses ProcessPool jobs.
Skip-existing via final_iou.json / STEP files. Does not re-run P3 or X-Part.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
LADDER = ROOT / "ours3/ladder_simple_to_complex_v1"
LOG = LADDER / "logs/cadfit_queue.log"
JOBS = 3
INNER = 8


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


def stl_ready(case: Path) -> bool:
    return "stl" in progress_stages(case) or any((case / "cadfit_routea/input_stl").glob("PART_*.stl"))


def cadfit_pending(case: Path) -> list[str]:
    stl_dir = case / "cadfit_routea/input_stl"
    raw = case / "cadfit_routea/cadfit_raw"
    pending = []
    for stl in sorted(stl_dir.glob("PART_*.stl")):
        iou = raw / stl.stem / "final_iou.json"
        if not (iou.is_file() and iou.stat().st_size > 0):
            pending.append(stl.stem)
    return pending


def run_cmd(case: Path, args: list[str], log_name: str) -> int:
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
    return proc.returncode


def run_case(spec: dict) -> dict:
    case = Path(spec["case_root"])
    label = spec["label"]
    row = {"label": label, "case": str(case), "status": "ok"}
    if not stl_ready(case):
        row["status"] = "wait_stl"
        row["error"] = "frontend STL not ready"
        return row
    pending = cadfit_pending(case)
    log(f"{label} pending CADFit {len(pending)} {pending}")
    if pending:
        rc = run_cmd(
            case,
            [
                "--stage",
                "cadfit",
                "--skip-canary",
                "--jobs",
                str(JOBS),
                "--inner-workers",
                str(INNER),
            ],
            "cadfit.log",
        )
        row["cadfit_rc"] = rc
        if rc != 0:
            still = cadfit_pending(case)
            row["status"] = "cadfit_partial" if still else "ok"
            row["still_pending"] = still
    rc = run_cmd(case, ["--stage", "step"], "step.log")
    row["step_rc"] = rc
    row["pending_after"] = cadfit_pending(case)
    if rc != 0 and row["status"] == "ok":
        row["status"] = "step_fail"
    log(f"{label} done status={row['status']}")
    return row


def main() -> int:
    cases = json.loads((LADDER / "cases.json").read_text())["cases"]
    ready = [s for s in cases if stl_ready(Path(s["case_root"]))]
    waiting = [s["label"] for s in cases if s not in ready]
    log(f"CADFit concurrent start jobs={JOBS} inner={INNER} ready={[s['label'] for s in ready]} waiting={waiting}")
    if not ready:
        log("nothing ready")
        return 1
    results = []
    with ProcessPoolExecutor(max_workers=len(ready)) as pool:
        futs = {pool.submit(run_case, spec): spec["label"] for spec in ready}
        for fut in as_completed(futs):
            label = futs[fut]
            try:
                row = fut.result()
            except Exception as exc:
                row = {"label": label, "status": "exception", "error": repr(exc)}
            results.append(row)
            log(f"finished {label} {row}")
    out = LADDER / "logs/cadfit_concurrent_summary.json"
    out.write_text(json.dumps({"finished_at": utc_now(), "jobs": JOBS, "inner": INNER, "results": results}, indent=2) + "\n")
    log(f"CADFit concurrent complete {out}")
    bad = [r for r in results if r.get("status") not in ("ok",)]
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
