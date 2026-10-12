#!/usr/bin/env python3
"""Assemble any tank-protocol case that already has STEP parts and no assembly STEP yet."""
from __future__ import annotations

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CADFIT_PY = Path("/data/miniconda3/envs/cadfit-env/bin/python")
LOG = ROOT / "ours3/ladder_more_v2/logs/watch_assemble.log"

WATCH = [
    ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1",
    ROOT / "ours3/toaster_p3_xpart_cadfit_routea_v1",
    ROOT / "ours3/car_p3_xpart_cadfit_routea_v1",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log(msg: str) -> None:
    line = f"[{utc_now()}] {msg}"
    print(line, flush=True)
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def n_stl(case: Path) -> int:
    return len(list((case / "cadfit_routea/input_stl").glob("PART_*.stl")))


def n_iou(case: Path) -> int:
    return len(list((case / "cadfit_routea/cadfit_raw").glob("PART_*/final_iou.json")))


def n_step(case: Path) -> int:
    return len(list((case / "cadfit_routea/step").glob("PART_*/PART_*.step")))


def assembly_ready(case: Path) -> bool:
    label = case.name.split("_p3_")[0]
    step = case / "assembly" / f"{label}_cad_native.step"
    # canister used a slightly different name in the first script
    alt = case / "assembly" / f"{label}_cad_native.step"
    return step.is_file() or alt.is_file() or (case / "assembly/assembly_manifest.json").is_file()


def export_step(case: Path) -> int:
    script = case / "scripts/export_step.py"
    if not script.is_file():
        return 1
    log_path = case / "logs/step_watch.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(
            ["/usr/bin/python3", "-u", str(script)],
            cwd=str(case),
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    return proc.returncode


def assemble(case: Path) -> int:
    script = case / "scripts/build_assembly.py"
    log_path = case / "logs/assembly.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        proc = subprocess.run(
            [str(CADFIT_PY), "-u", str(script)],
            cwd=str(case),
            stdout=f,
            stderr=subprocess.STDOUT,
        )
    return proc.returncode


def try_case(case: Path) -> str:
    if not case.is_dir():
        return "missing"
    if assembly_ready(case):
        return "already"
    stl, iou, step = n_stl(case), n_iou(case), n_step(case)
    if stl == 0:
        return "wait_stl"
    if iou < stl:
        return f"wait_cadfit {iou}/{stl}"
    if step < iou:
        log(f"{case.name} exporting STEP iou={iou} step={step}")
        export_step(case)
        step = n_step(case)
    if step == 0:
        return "no_step"
    log(f"{case.name} assembling step={step}/{stl}")
    rc = assemble(case)
    return "assembled" if rc == 0 else f"assembly_fail rc={rc}"


def main() -> int:
    deadline = time.time() + 16 * 3600
    done = set()
    while time.time() < deadline:
        pending = 0
        for case in WATCH:
            key = str(case)
            if key in done:
                continue
            status = try_case(case)
            log(f"{case.name} {status}")
            if status in ("already", "assembled"):
                done.add(key)
            elif status not in ("missing",):
                pending += 1
        if pending == 0 and len(done) == len([c for c in WATCH if c.is_dir()]):
            log("all existing cases assembled")
            break
        time.sleep(120)
    out = {
        "finished_at": utc_now(),
        "done": sorted(done),
    }
    (ROOT / "ours3/ladder_more_v2/logs/watch_assemble_summary.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
