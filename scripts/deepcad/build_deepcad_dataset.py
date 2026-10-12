#!/usr/bin/env python3
"""Batch-build DeepCAD spatial dataset from raw JSON or manifest."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_deepcad_sample import build_sample  # noqa: E402


def _iter_json_inputs(manifest: Path | None, json_dir: Path | None, limit: int | None) -> list[Path]:
    paths: list[Path] = []
    if manifest is not None:
        data = json.loads(manifest.read_text(encoding="utf-8"))
        raw_dir = Path(data["raw_json_dir"])
        for sample_id in data.get("sample_ids", []):
            safe = sample_id.replace("/", "_")
            paths.append(raw_dir / f"{safe}.json")
    elif json_dir is not None:
        paths = sorted(json_dir.glob("*.json"))
    else:
        raise ValueError("provide --manifest or --json-dir")

    if limit is not None:
        paths = paths[:limit]
    return paths


def main() -> int:
    parser = argparse.ArgumentParser(description="Batch DeepCAD → spatial dataset")
    parser.add_argument("--manifest", type=Path, default=None)
    parser.add_argument("--json-dir", type=Path, default=None)
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
        help="Stop after this many QA-passed samples",
    )
    args = parser.parse_args()

    json_paths = _iter_json_inputs(args.manifest, args.json_dir, args.limit)
    summary = {"total": len(json_paths), "ok": 0, "passed": 0, "skipped": 0, "qa_failed": [], "failed": []}

    required = ("features.npy", "program.dsl", "model.step", "model.obj", "qa.json")

    for i, json_path in enumerate(json_paths, start=1):
        if args.target_passed is not None and summary["passed"] >= args.target_passed:
            print(f"Reached target_passed={args.target_passed}", flush=True)
            break

        sample_id = json_path.stem
        sample_dir = args.output / "DeepCAD" / "train" / sample_id
        qa_path = sample_dir / "qa.json"
        if args.skip_existing and qa_path.exists():
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
            if qa.get("passed") and all((sample_dir / name).exists() for name in required):
                print(f"[{i}/{len(json_paths)}] {sample_id} SKIP (passed)", flush=True)
                summary["skipped"] += 1
                summary["ok"] += 1
                summary["passed"] += 1
                continue
        print(f"[{i}/{len(json_paths)}] {sample_id}", flush=True)
        try:
            report = build_sample(
                json_path,
                args.output,
                sample_id=sample_id,
                num_points=args.num_points,
            )
            summary["ok"] += 1
            if (report.get("qa") or {}).get("passed"):
                summary["passed"] += 1
            elif report.get("qa"):
                summary["qa_failed"].append(
                    {
                        "sample_id": sample_id,
                        "reason": report["qa"].get("reject_reason"),
                    }
                )
        except Exception as exc:
            summary["failed"].append({"sample_id": sample_id, "error": str(exc)})
            print(f"  FAILED: {exc}", flush=True)
            if args.fail_fast:
                break

    out_path = args.output / "DeepCAD" / "build_summary.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 1 if summary["failed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
