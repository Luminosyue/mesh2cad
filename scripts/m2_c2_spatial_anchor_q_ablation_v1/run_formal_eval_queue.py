#!/usr/bin/env python3
"""Wait for one formal arm to finish, then evaluate all ten epochs on dev50."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def write(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True)
    parser.add_argument("--train-dir", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--start-epoch", type=int, default=1)
    parser.add_argument("--end-epoch", type=int, default=10)
    args = parser.parse_args()
    train_dir, eval_dir = Path(args.train_dir), Path(args.eval_dir)
    eval_dir.mkdir(parents=True, exist_ok=False)
    status_path = eval_dir / "EVAL_QUEUE_STATUS.json"
    status = {
        "ARM": args.arm,
        "STATUS": "WAITING_FOR_TRAINING",
        "EPOCHS_COMPLETED": [],
        "START_EPOCH": args.start_epoch,
        "END_EPOCH": args.end_epoch,
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
    }
    write(status_path, status)
    while True:
        report_path = train_dir / "TRAINING_REPORT.json"
        if report_path.exists():
            report = json.loads(report_path.read_text())
            if report.get("STATUS") == "PASS" and len(report.get("EPOCHS", [])) == 10:
                break
            if str(report.get("STATUS", "")).startswith("HARD_STOP"):
                status["STATUS"] = "HARD_STOP_TRAINING_FAILED"
                status["TRAINING_STATUS"] = report.get("STATUS")
                write(status_path, status)
                raise SystemExit(2)
        time.sleep(60)
    status["STATUS"] = "RUNNING"
    write(status_path, status)
    script = Path("/data/home/cuiyuehan/project/mesh2cad/scripts/m2_c2_spatial_anchor_q_ablation_v1/evaluate_formal_checkpoint.py")
    for epoch in range(args.start_epoch, args.end_epoch + 1):
        checkpoint = train_dir / f"checkpoint_epoch_{epoch:02d}"
        output = eval_dir / f"epoch_{epoch:02d}"
        if output.exists() and (output / "SUMMARY.json").exists():
            summary = json.loads((output / "SUMMARY.json").read_text())
            if summary.get("STATUS") == "PASS" and summary.get("N") == 50:
                status["EPOCHS_COMPLETED"].append(epoch)
                write(status_path, status)
                continue
            raise RuntimeError(f"incomplete pre-existing output: {output}")
        log = eval_dir / f"epoch_{epoch:02d}.log"
        command = [
            sys.executable, str(script),
            "--arm", args.arm,
            "--checkpoint", str(checkpoint),
            "--epoch", str(epoch),
            "--output", str(output),
            "--device", args.device,
            "--max-new-tokens", "4096",
        ]
        with log.open("w") as handle:
            completed = subprocess.run(command, stdout=handle, stderr=subprocess.STDOUT)
        if completed.returncode != 0:
            status["STATUS"] = "HARD_STOP_EVALUATION_FAILED"
            status["FAILED_EPOCH"] = epoch
            status["RETURN_CODE"] = completed.returncode
            write(status_path, status)
            raise SystemExit(completed.returncode)
        status["EPOCHS_COMPLETED"].append(epoch)
        write(status_path, status)
    status["STATUS"] = "PASS"
    write(status_path, status)


if __name__ == "__main__":
    main()
