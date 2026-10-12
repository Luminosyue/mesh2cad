#!/usr/bin/env python3
"""Merge deterministic decode-dev50 evaluation shards without changing metrics."""
from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path


def mean_present(records: list[dict], key: str):
    values = [row[key] for row in records if row.get(key) is not None]
    return statistics.fmean(values) if values else None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", required=True)
    parser.add_argument("--epoch", type=int, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--dev-manifest", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("sources", nargs="+")
    args = parser.parse_args()

    records: list[dict] = []
    for source in args.sources:
        with Path(source).open() as handle:
            records.extend(json.loads(line) for line in handle if line.strip())

    expected_rows = json.loads(Path(args.dev_manifest).read_text())["records"]
    expected_ids = [row["cad_id"] for row in expected_rows]
    actual_ids = [row["cad_id"] for row in records]
    if len(records) != 50:
        raise RuntimeError(f"Expected 50 records, got {len(records)}")
    if len(set(actual_ids)) != 50:
        raise RuntimeError("Duplicate CAD IDs in merged records")
    if actual_ids != expected_ids:
        raise RuntimeError("Merged CAD ordering differs from frozen decode-dev50")
    if any(row.get("arm") != args.arm or row.get("epoch") != args.epoch for row in records):
        raise RuntimeError("Arm/epoch mismatch in shard records")

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=False)
    with (output / "per_cad.jsonl").open("w") as handle:
        for record in records:
            handle.write(json.dumps(record) + "\n")

    summary = {
        "ARM": args.arm,
        "EPOCH": args.epoch,
        "CHECKPOINT": args.checkpoint,
        "N": 50,
        "MAX_NEW_TOKENS": 4096,
        "EOS_COUNT": sum(row["eos_emitted"] for row in records),
        "RUNAWAY_COUNT": sum(row["unexpected_runaway"] for row in records),
        "PARSE_COUNT": sum(row["dsl_parse_success"] for row in records),
        "EXECUTE_COUNT": sum(row["dsl_execute_success"] for row in records),
        "BREP_VALID_COUNT": sum(row["brep_valid"] for row in records),
        "STEP_RELOAD_COUNT": sum(row["step_reload_success"] for row in records),
        "OP_F1": statistics.fmean(row["op_f1"] for row in records),
        "CHAMFER": mean_present(records, "chamfer_norm"),
        "HAUSDORFF95": mean_present(records, "hausdorff95_norm"),
        "BBOX_CENTER_ERROR": mean_present(records, "bbox_center_error_norm"),
        "BBOX_EXTENT_ERROR": mean_present(records, "bbox_extent_error_norm"),
        "BOX_ORIGIN_ERROR": mean_present(records, "box_origin_error"),
        "EXTRUDE_ORIGIN_ERROR": mean_present(records, "extrude_origin_error"),
        "EXTRUDE_DEPTH_ERROR": mean_present(records, "extrude_depth_error"),
        "CIRCLE_RADIUS_ERROR": mean_present(records, "circle_radius_error"),
        "MERGED_FROM": args.sources,
        "CAD_ID_UNIQUE": True,
        "FROZEN_ORDER_IDENTICAL": True,
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
        "STATUS": "PASS",
    }
    (output / "SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
