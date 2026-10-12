#!/usr/bin/env python3
"""Batch-build Fusion360 spatial dataset from manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_fusion360_sample import build_sample  # noqa: E402


def _iter_sample_ids(manifest: Path, limit: int | None) -> list[str]:
    data = json.loads(manifest.read_text(encoding="utf-8"))
    ids = list(data.get("sample_ids", []))
    if limit is not None:
        ids = ids[:limit]
    return ids


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch Fusion360 → spatial dataset")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=ROOT / "cad_spatial_dataset/Fusion360/manifest_train200.json",
    )
    parser.add_argument("--output", type=Path, default=ROOT / "cad_spatial_dataset")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--num-points", type=int, default=8192)
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip samples that already have qa.json with passed=true",
    )
    parser.add_argument(
        "--target-passed",
        type=int,
        default=None,
        help="Stop after this many QA-passed samples (scan manifest in order)",
    )
    args = parser.parse_args()

    sample_ids = _iter_sample_ids(args.manifest, args.limit)
    summary = {
        "total": len(sample_ids),
        "built": 0,
        "passed": 0,
        "skipped": 0,
        "filtered": [],
        "qa_failed": [],
        "failed": [],
    }

    for i, sample_id in enumerate(sample_ids, start=1):
        if args.target_passed is not None and summary["passed"] >= args.target_passed:
            print(f"Reached target_passed={args.target_passed}", flush=True)
            break

        sample_dir = args.output / "Fusion360" / "train" / sample_id
        qa_path = sample_dir / "qa.json"
        if args.skip_existing and qa_path.exists():
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
            if qa.get("passed"):
                print(f"[{i}/{len(sample_ids)}] {sample_id} SKIP (passed)", flush=True)
                summary["skipped"] += 1
                summary["passed"] += 1
                continue

        print(f"[{i}/{len(sample_ids)}] {sample_id}", flush=True)
        try:
            report = build_sample(
                sample_id,
                args.output,
                num_points=args.num_points,
                run_qa=True,
            )
            summary["built"] += 1
            if report.get("filter_reason"):
                summary["filtered"].append({"sample_id": sample_id, "reason": report["filter_reason"]})
            elif report.get("qa", {}).get("passed"):
                summary["passed"] += 1
            else:
                reason = (report.get("qa") or {}).get("reject_reason") or "qa_failed"
                summary["qa_failed"].append({"sample_id": sample_id, "reason": reason})
        except Exception as exc:
            summary["failed"].append({"sample_id": sample_id, "error": str(exc)})
            print(f"  FAILED: {exc}", flush=True)
            if args.fail_fast:
                break

    out_path = args.output / "Fusion360" / "build_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
