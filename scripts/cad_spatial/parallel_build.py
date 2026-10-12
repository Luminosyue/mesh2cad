#!/usr/bin/env python3
"""Parallel batch builder for DeepCAD / Fusion360 / CADFS cad_spatial datasets."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PYTHON = Path("/data/miniconda3/envs/cadfit-env/bin/python3")
PYTHON = str(DEFAULT_PYTHON if DEFAULT_PYTHON.exists() else Path(sys.executable))


def _count_passed(train_dir: Path) -> int:
    if not train_dir.exists():
        return 0
    n = 0
    for qa in train_dir.glob("*/qa.json"):
        try:
            if json.loads(qa.read_text(encoding="utf-8")).get("passed"):
                n += 1
        except Exception:
            pass
    return n


def _should_skip(sample_dir: Path, skip_existing: bool) -> bool:
    if not skip_existing:
        return False
    qa = sample_dir / "qa.json"
    if not qa.exists():
        return False
    try:
        return bool(json.loads(qa.read_text(encoding="utf-8")).get("passed"))
    except Exception:
        return False


def _run_one(
    dataset: str,
    sample_key: str,
    output: str,
    num_points: int,
    timeout: int,
    no_vis: bool,
) -> dict:
    """Run one sample in an isolated subprocess (memory + timeout safe)."""
    t0 = time.time()
    if dataset == "deepcad":
        cmd = [
            PYTHON,
            str(ROOT / "scripts/deepcad/build_deepcad_sample.py"),
            "--json",
            sample_key,
            "--output",
            output,
            "--num-points",
            str(num_points),
        ]
        sample_id = Path(sample_key).stem
    elif dataset == "fusion360":
        cmd = [
            PYTHON,
            str(ROOT / "scripts/fusion360/build_fusion360_sample.py"),
            "--sample-id",
            sample_key,
            "--output",
            output,
            "--num-points",
            str(num_points),
        ]
        sample_id = sample_key
    elif dataset == "cadfs":
        cmd = [
            PYTHON,
            str(ROOT / "scripts/cadfs/build_cadfs_sample.py"),
            "--sample-id",
            sample_key,
            "--output",
            output,
            "--num-points",
            str(num_points),
        ]
        sample_id = sample_key
    else:
        raise ValueError(dataset)

    if no_vis:
        cmd.append("--no-vis")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - t0
        if dataset == "deepcad":
            qa_path = Path(output) / "DeepCAD" / "train" / sample_id / "qa.json"
        elif dataset == "fusion360":
            qa_path = Path(output) / "Fusion360" / "train" / sample_id / "qa.json"
        else:
            qa_path = Path(output) / "CADFS" / "train" / sample_id / "qa.json"

        if proc.returncode == 2:
            return {"sample_id": sample_id, "status": "filtered", "passed": False, "elapsed_s": round(elapsed, 1)}

        if qa_path.exists():
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
            passed = bool(qa.get("passed"))
            return {
                "sample_id": sample_id,
                "status": "passed" if passed else "qa_failed",
                "passed": passed,
                "reject_reason": qa.get("reject_reason"),
                "elapsed_s": round(elapsed, 1),
            }

        if proc.returncode == 0:
            return {"sample_id": sample_id, "status": "passed", "passed": True, "elapsed_s": round(elapsed, 1)}

        err = (proc.stderr or proc.stdout or "")[-500:]
        return {"sample_id": sample_id, "status": "failed", "passed": False, "error": err, "elapsed_s": round(elapsed, 1)}
    except subprocess.TimeoutExpired:
        return {"sample_id": sample_id, "status": "timeout", "passed": False, "elapsed_s": timeout}


def _load_jobs(dataset: str, manifest: Path, output: Path, skip_existing: bool) -> tuple[list[str], int]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    skipped = 0
    jobs: list[str] = []
    if dataset == "deepcad":
        raw_dir = Path(data["raw_json_dir"])
        train_dir = output / "DeepCAD" / "train"
        for sid in data.get("sample_ids", []):
            safe = sid.replace("/", "_")
            json_path = raw_dir / f"{safe}.json"
            sample_dir = train_dir / safe
            if _should_skip(sample_dir, skip_existing):
                skipped += 1
                continue
            if json_path.exists():
                jobs.append(str(json_path))
    elif dataset == "fusion360":
        train_dir = output / "Fusion360" / "train"
        for sid in data.get("sample_ids", []):
            sample_dir = train_dir / sid
            if _should_skip(sample_dir, skip_existing):
                skipped += 1
                continue
            jobs.append(sid)
    else:
        train_dir = output / "CADFS" / "train"
        for sid in data.get("sample_ids", []):
            sample_dir = train_dir / sid
            if _should_skip(sample_dir, skip_existing):
                skipped += 1
                continue
            jobs.append(sid)
    return jobs, skipped


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel cad_spatial dataset builder")
    parser.add_argument("--dataset", choices=["deepcad", "fusion360", "cadfs"], required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "cad_spatial_dataset")
    parser.add_argument("--workers", type=int, default=32, help="Parallel worker count (default 32)")
    parser.add_argument("--target-passed", type=int, default=1000)
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument("--timeout", type=int, default=600, help="Per-sample timeout seconds")
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--no-vis", action="store_true", help="Skip Dora visualization PNGs")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    _TRAIN = {"deepcad": "DeepCAD", "fusion360": "Fusion360", "cadfs": "CADFS"}
    train_dir = args.output / _TRAIN[args.dataset] / "train"
    already_passed = _count_passed(train_dir)
    jobs, skipped = _load_jobs(args.dataset, args.manifest, args.output, args.skip_existing)
    if args.limit is not None:
        jobs = jobs[: args.limit]

    print(f"=== parallel build {args.dataset} ===")
    print(f"workers={args.workers}  target_passed={args.target_passed}  already_passed={already_passed}")
    print(f"jobs={len(jobs)}  skipped={skipped}")

    summary = {
        "dataset": args.dataset,
        "workers": args.workers,
        "target_passed": args.target_passed,
        "already_passed": already_passed,
        "passed": already_passed,
        "built": 0,
        "qa_failed": 0,
        "filtered": 0,
        "failed": 0,
        "timeout": 0,
        "skipped": skipped,
    }

    if already_passed >= args.target_passed:
        print(f"Already reached target_passed={args.target_passed}")
        return 0

    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(
                _run_one,
                args.dataset,
                job,
                str(args.output),
                args.num_points,
                args.timeout,
                args.no_vis,
            ): job
            for job in jobs
        }
        done = 0
        for fut in as_completed(futures):
            done += 1
            rec = fut.result()
            summary["built"] += 1
            status = rec["status"]
            if status == "passed":
                summary["passed"] += 1
            elif status == "qa_failed":
                summary["qa_failed"] += 1
            elif status == "filtered":
                summary["filtered"] += 1
            elif status == "timeout":
                summary["timeout"] += 1
            else:
                summary["failed"] += 1

            mark = "PASS" if rec.get("passed") else status.upper()
            print(
                f"[{done}/{len(jobs)}] {rec['sample_id']} {mark} "
                f"({rec.get('elapsed_s', '?')}s) passed={summary['passed']}/{args.target_passed}",
                flush=True,
            )

            if summary["passed"] >= args.target_passed:
                print(f"Reached target_passed={args.target_passed}, cancelling remaining...", flush=True)
                for f in futures:
                    f.cancel()
                break

    out = args.output / _TRAIN[args.dataset] / "build_summary_parallel.json"
    out.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
