#!/usr/bin/env python3
"""Wait for CADFit Route A completion, then export STEP + QA + renders."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_OUT = ROOT / "ours3/cadfit_xpart45_routea_v1"
CADFIT_ENV_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python")


def count_done(raw_dir: Path, expected: int) -> tuple[int, list[str], list[str]]:
    inp_parts = sorted(p.stem for p in (raw_dir.parent / "input_stl").glob("PART_*.stl"))
    if not inp_parts:
        inp_parts = [f"PART_{i:03d}" for i in range(1, expected + 1)]
    done = []
    running = []
    for pid in inp_parts:
        iouf = raw_dir / pid / "final_iou.json"
        lock = raw_dir / pid / ".running.lock"
        if iouf.is_file() and iouf.stat().st_size > 0:
            done.append(pid)
        elif lock.is_file():
            running.append(pid)
    return len(done), running, [p for p in inp_parts if p not in done]


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-process CADFit Route A after all parts finish.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--expected", type=int, default=45)
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--skip-wait", action="store_true", help="Run export/QA/render immediately")
    args = parser.parse_args()

    out = args.output_dir
    raw_dir = out / "cadfit_raw"
    scripts = ROOT / "scripts"

    if not args.skip_wait:
        print(f"Waiting for {args.expected}/{args.expected} CADFit parts in {out} ...")
        while True:
            n_done, running, pending = count_done(raw_dir, args.expected)
            print(f"  {n_done}/{args.expected} done  running={running or '-'}  pending={len(pending)}")
            if n_done >= args.expected:
                break
            time.sleep(args.poll_seconds)

    py = str(CADFIT_ENV_PYTHON if CADFIT_ENV_PYTHON.is_file() else Path(sys.executable))
    steps = [
        ([py, str(scripts / "cadfit_routea_export_step.py"), "--output-dir", str(out)], "STEP export"),
        ([py, str(scripts / "cadfit_routea_qa.py"), "--output-dir", str(out)], "QA"),
        ([py, str(scripts / "cadfit_routea_render.py")], "Render"),
    ]
    for cmd, label in steps:
        print(f"\n=== {label} ===")
        res = subprocess.run(cmd, cwd=str(ROOT))
        if res.returncode != 0:
            print(f"{label} failed with exit {res.returncode}", file=sys.stderr)
            return res.returncode

    gate = out / "gate.json"
    if gate.is_file():
        g = json.loads(gate.read_text())
        print(f"\nPost-process complete. ROUTE_A_GATE={g.get('ROUTE_A_GATE')}  MEAN_IOU={g.get('MEAN_IOU')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
