"""Select CADFS STEP ids that have matching text annotations."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from .constants import CADFS_ANN_ROOT, CADFS_STEP_ROOT, MANIFEST_ROOT


def iter_cadfs_pairs(step_root: Path = CADFS_STEP_ROOT, ann_root: Path = CADFS_ANN_ROOT):
    step_root = Path(step_root)
    ann_root = Path(ann_root)
    for bucket in sorted(p for p in step_root.iterdir() if p.is_dir()):
        for step in sorted(bucket.glob("*.step")):
            ann = ann_root / bucket.name / f"{step.stem}.txt"
            yield {
                "sample_id": step.stem,
                "bucket": bucket.name,
                "step_path": str(step),
                "annotation_path": str(ann) if ann.is_file() else None,
                "has_annotation": ann.is_file(),
                "step_bytes": step.stat().st_size,
                "ann_bytes": ann.stat().st_size if ann.is_file() else 0,
            }


def select_cadfs(
    *,
    n: int,
    seed: int = 0,
    require_annotation: bool = True,
    min_ann_bytes: int = 200,
    max_step_bytes: int = 5_000_000,
    prefer_long_ann: bool = True,
) -> list[dict]:
    """Stratify across STEP buckets; bias toward longer annotations (more complex)."""
    rng = np.random.default_rng(seed)
    by_bucket: dict[str, list[dict]] = {}
    for rec in iter_cadfs_pairs():
        if require_annotation and not rec["has_annotation"]:
            continue
        if rec["ann_bytes"] < min_ann_bytes:
            continue
        if rec["step_bytes"] <= 0 or rec["step_bytes"] > max_step_bytes:
            continue
        by_bucket.setdefault(rec["bucket"], []).append(rec)

    buckets = sorted(by_bucket)
    if not buckets:
        return []

    # Round-robin across buckets for coverage; within bucket rank by ann length.
    ranked = {}
    for b in buckets:
        items = by_bucket[b]
        if prefer_long_ann:
            items = sorted(items, key=lambda r: (-r["ann_bytes"], r["sample_id"]))
        else:
            order = rng.permutation(len(items))
            items = [items[i] for i in order]
        ranked[b] = items

    selected: list[dict] = []
    ptr = {b: 0 for b in buckets}
    while len(selected) < n and any(ptr[b] < len(ranked[b]) for b in buckets):
        for b in buckets:
            if len(selected) >= n:
                break
            i = ptr[b]
            if i >= len(ranked[b]):
                continue
            selected.append(ranked[b][i])
            ptr[b] = i + 1
    return selected


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=Path, default=MANIFEST_ROOT / "manifests" / "cadfs_candidates_500.json")
    ap.add_argument("--min-ann-bytes", type=int, default=200)
    ap.add_argument("--max-step-bytes", type=int, default=5_000_000)
    args = ap.parse_args()

    selected = select_cadfs(
        n=args.n,
        seed=args.seed,
        min_ann_bytes=args.min_ann_bytes,
        max_step_bytes=args.max_step_bytes,
    )
    obj = {
        "dataset": "cadfs",
        "n_requested": args.n,
        "n_selected": len(selected),
        "seed": args.seed,
        "filters": {
            "require_annotation": True,
            "min_ann_bytes": args.min_ann_bytes,
            "max_step_bytes": args.max_step_bytes,
            "prefer_long_ann": True,
            "bucket_round_robin": True,
        },
        "sample_ids": [r["sample_id"] for r in selected],
        "records": selected,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out} n={len(selected)}")


if __name__ == "__main__":
    main()
