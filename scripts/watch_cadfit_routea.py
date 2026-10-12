#!/usr/bin/env python3
"""Print CADFit Route A progress (one snapshot)."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime
from pathlib import Path

DEFAULT_OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1")


def alive(pid_file: Path) -> bool:
    if not pid_file.is_file():
        return False
    pid = pid_file.read_text().strip()
    return Path(f"/proc/{pid}").exists() if pid.isdigit() else False


def main() -> None:
    parser = argparse.ArgumentParser(description="Print CADFit Route A progress.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--total", type=int, default=None)
    args = parser.parse_args()
    out = args.output_dir
    raw = out / "cadfit_raw"
    pid_file = out / "logs" / "parallel_run.pid"
    input_dir = out / "input_stl"
    if args.total is not None:
        total = args.total
    else:
        stls = sorted(input_dir.glob("PART_*.stl"))
        total = len(stls) if stls else 45

    done = []
    running = []
    now = time.time()
    for i in range(total):
        pid = f"PART_{i:03d}"
        iou_path = raw / pid / "final_iou.json"
        lock = raw / pid / ".running.lock"
        if iou_path.is_file() and iou_path.stat().st_size > 0:
            data = json.loads(iou_path.read_text())
            done.append((pid, data.get("final_iou"), data.get("duration"), iou_path.stat().st_mtime))
        elif lock.is_file():
            running.append((pid, (now - lock.stat().st_mtime) / 60.0))

    n = len(done)
    remain = total - n
    durs = [x[2] for x in done if x[2]]
    mean = (sum(durs) / len(durs)) if durs else None
    eta_min = None
    if mean and remain:
        jobs = max(len(running), 3)
        eta_min = remain * (mean / 60.0) / jobs

    ious = [x[1] for x in done if x[1] is not None]
    bar_w = 40
    filled = int(bar_w * n / total) if total else 0
    bar = "#" * filled + "-" * (bar_w - filled)

    print(f"CADFit Route A  {datetime.now().strftime('%H:%M:%S')}")
    print(f"[{bar}]  {n}/{total}")
    print(f"coordinator: {'RUNNING' if alive(pid_file) else 'STOPPED'}")
    if ious:
        print(f"mean IoU: {sum(ious)/len(ious):.4f}")
    if mean:
        print(f"avg duration: {mean/60:.1f} min/part")
    if eta_min is not None:
        print(f"ETA: ~{eta_min/60:.1f} h ({eta_min:.0f} min) remaining")
    print("running:")
    if running:
        for pid, age in running:
            print(f"  {pid}  {age:.1f} min")
    else:
        print("  (none)")
    print("latest done:")
    for pid, iou, dur, _mtime in sorted(done, key=lambda x: x[3])[-5:]:
        iou_s = f"{iou:.4f}" if iou is not None else "n/a"
        dur_s = f"{dur/60:.1f} min" if dur else "n/a"
        print(f"  {pid}  IoU={iou_s}  {dur_s}")


if __name__ == "__main__":
    main()
