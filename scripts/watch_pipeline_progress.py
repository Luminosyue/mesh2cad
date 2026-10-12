#!/usr/bin/env python3
"""Log once when a part starts or finishes. Do not heartbeat."""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path


def append_line(root: Path, message: str) -> None:
    log_dir = root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
    print(line, end="", flush=True)
    for name in ("parts.log", "run.log"):
        with (log_dir / name).open("a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())


def live_mac_ids() -> set[str]:
    ids: set[str] = set()
    try:
        import subprocess

        proc = subprocess.run(
            ["pgrep", "-af", "run_mac_graph_job.py"],
            capture_output=True,
            text=True,
            check=False,
        )
    except Exception:
        return ids
    for line in proc.stdout.splitlines():
        if "P3_COMPONENT_" not in line:
            continue
        for token in line.split("/"):
            if token.startswith("P3_COMPONENT_"):
                ids.add(token)
    return ids


def event_state(root: Path, seen: set[str]) -> dict[str, str]:
    events: dict[str, str] = {}
    comps_root = root / "03_components"
    if not comps_root.is_dir():
        return events
    live = live_mac_ids()
    for comp in sorted(comps_root.glob("P3_COMPONENT_*")):
        cid = comp.name
        selected = comp / "11_selected/selected_manifest.json"
        mac_result = comp / "06_mac/mac_graph_result.json"
        if selected.is_file():
            payload = json.loads(selected.read_text(encoding="utf-8"))
            events[f"done:{cid}"] = (
                f"DONE {cid} backend={payload.get('selected_backend')} "
                f"cad={payload.get('cad_native')} qa={payload.get('qa_pass')}"
            )
        elif cid in live:
            events[f"start:{cid}"] = f"START {cid} (MAC running)"
        elif (comp / "06_mac/generated.step").is_file():
            man = comp / "06_mac/mac_candidate_manifest.json"
            extra = ""
            if man.is_file():
                payload = json.loads(man.read_text(encoding="utf-8"))
                extra = f" step_ok={payload.get('step_success')} cad={payload.get('cad_native')}"
            events[f"mac:{cid}"] = f"MAC_DONE {cid}{extra}"
    assembly = root / "05_mixed_assembly/build_a_robot_pipeline_a_repair_v2.step"
    if assembly.is_file():
        events["assembly"] = f"ASSEMBLY {assembly} ({assembly.stat().st_size}B)"
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--interval", type=float, default=5.0)
    args = parser.parse_args()
    root = args.root.resolve()
    seen: set[str] = set()
    first = True
    while True:
        events = event_state(root, seen)
        if first:
            done = [key for key in events if key.startswith("done:")]
            running = [msg for key, msg in events.items() if key.startswith("start:")]
            append_line(root, f"STATUS done={len(done)}/9 now={running[0] if running else '-'}")
            first = False
        for key, message in events.items():
            if key in seen:
                continue
            seen.add(key)
            append_line(root, message)
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
