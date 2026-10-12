#!/usr/bin/env python3
"""Print robot CADFit Route A progress (one snapshot)."""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CADFIT_DIR, CADFIT_RAW, STL_DIR  # noqa: E402

PID_FILE = CADFIT_DIR / "logs/parallel_run.pid"


def alive() -> bool:
    if not PID_FILE.is_file():
        return False
    pid = PID_FILE.read_text().strip()
    return Path(f"/proc/{pid}").exists() if pid.isdigit() else False


def main() -> None:
    stls = sorted(p.stem for p in STL_DIR.glob("PART_*.stl"))
    total = len(stls) or 1
    done = []
    running = []
    now = time.time()
    for pid in stls:
        iou_path = CADFIT_RAW / pid / "final_iou.json"
        lock = CADFIT_RAW / pid / ".running.lock"
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
    filled = int(bar_w * n / total)
    bar = "#" * filled + "-" * (bar_w - filled)

    print(f"Robot CADFit Route A  {datetime.now().strftime('%H:%M:%S')}")
    print(f"[{bar}]  {n}/{total}")
    print(f"coordinator: {'RUNNING' if alive() else 'STOPPED'}")
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
