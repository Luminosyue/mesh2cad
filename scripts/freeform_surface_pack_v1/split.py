"""Part-level stratified split by num_bspline_faces."""

from __future__ import annotations

import numpy as np

from .constants import N_TEST_PARTS, N_TRAIN_PARTS, N_VAL_PARTS, SPLIT_SEED


def stratified_part_split(
    part_ids: list[str],
    n_bspline: dict[str, int],
    *,
    n_train: int = N_TRAIN_PARTS,
    n_val: int = N_VAL_PARTS,
    n_test: int = N_TEST_PARTS,
    seed: int = SPLIT_SEED,
) -> dict[str, list[str]]:
    """Greedy stratified assignment to balance BSpline face counts across splits."""
    parts = sorted(part_ids)
    if len(parts) != n_train + n_val + n_test:
        raise ValueError(
            f"expected {n_train}+{n_val}+{n_test}={n_train + n_val + n_test} parts, got {len(parts)}"
        )
    rng = np.random.default_rng(int(seed))
    # Sort by count then shuffle within equal-count buckets for stability.
    counts = np.array([int(n_bspline[p]) for p in parts], dtype=np.int64)
    order = np.argsort(-counts, kind="stable")
    # Secondary random permute among ties
    buckets: dict[int, list[str]] = {}
    for p in parts:
        buckets.setdefault(int(n_bspline[p]), []).append(p)
    ordered: list[str] = []
    for c in sorted(buckets.keys(), reverse=True):
        ids = buckets[c]
        rng.shuffle(ids)
        ordered.extend(ids)

    targets = {
        "train": n_train,
        "val": n_val,
        "test": n_test,
    }
    splits: dict[str, list[str]] = {"train": [], "val": [], "test": []}
    load = {"train": 0, "val": 0, "test": 0}
    for p in ordered:
        # Prefer split that still needs parts and currently has lowest face load
        # among those with remaining slots.
        cands = [s for s in ("train", "val", "test") if len(splits[s]) < targets[s]]
        # Weight: pick lowest load; tie-break by remaining slots then name order
        best = min(cands, key=lambda s: (load[s], - (targets[s] - len(splits[s])), s))
        splits[best].append(p)
        load[best] += int(n_bspline[p])

    for s in splits:
        splits[s] = sorted(splits[s])
    return splits
