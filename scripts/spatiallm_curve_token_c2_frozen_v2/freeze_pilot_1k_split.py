#!/usr/bin/env python3
"""Freeze a deterministic stratified 800/200 split from the gated V2-1k cohort."""
from __future__ import annotations

import hashlib
import json
import pathlib
import random
from collections import Counter, defaultdict

ROOT = pathlib.Path("/data/home/cuiyuehan/project/mesh2cad")
SOURCE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/v2_1k_corrected/runs/run1/MANIFEST.json"
OUT = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/pilot_1k_formal_v1/data"
SEED = 20260827


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def k_bin(k: int) -> str:
    if k <= 8:
        return "low"
    if k < 64:
        return "mid"
    return "high"


def distribution(rows: list[dict]) -> dict:
    return {
        "count": len(rows),
        "source_dataset": dict(sorted(Counter(r["source_dataset"] for r in rows).items())),
        "difficulty_bin": dict(sorted(Counter(r["difficulty_bin"] for r in rows).items())),
        "k_bin": dict(sorted(Counter(k_bin(int(r["k_valid"])) for r in rows).items())),
        "joint_stratum": dict(sorted(Counter(
            f'{r["source_dataset"]}|{r["difficulty_bin"]}|{k_bin(int(r["k_valid"]))}' for r in rows
        ).items())),
    }


def main() -> None:
    if OUT.exists():
        raise FileExistsError(f"refusing to overwrite frozen output: {OUT}")
    manifest = json.loads(SOURCE.read_text())
    rows = manifest["rows"]
    if len(rows) != 1000 or any(r["split"] != "train" for r in rows):
        raise RuntimeError("source must be the gated 1000-record training cohort")

    strata: dict[tuple[str, str, str], list[dict]] = defaultdict(list)
    for row in rows:
        strata[(row["source_dataset"], row["difficulty_bin"], k_bin(int(row["k_valid"])))].append(row)

    train, val = [], []
    allocation = {}
    for key in sorted(strata):
        group = sorted(strata[key], key=lambda r: r["cad_id"])
        rng = random.Random(f"{SEED}|{'|'.join(key)}")
        rng.shuffle(group)
        # Largest-remainder allocation is resolved globally below; begin with floor(20%).
        n_val = len(group) // 5
        val.extend(group[:n_val])
        train.extend(group[n_val:])
        allocation[key] = {"size": len(group), "val": n_val, "remainder": len(group) % 5}

    # Assign remaining validation slots to strata with the largest fractional remainder.
    need = 200 - len(val)
    candidates = sorted(allocation, key=lambda key: (-allocation[key]["remainder"], key))
    if need < 0 or need > len(candidates):
        raise RuntimeError(f"unexpected remainder allocation: need={need}")
    for key in candidates[:need]:
        # Move one deterministic record from this stratum's train portion to val.
        candidates_in_train = sorted(
            (r for r in train if (r["source_dataset"], r["difficulty_bin"], k_bin(int(r["k_valid"]))) == key),
            key=lambda r: r["cad_id"],
        )
        moved = candidates_in_train[0]
        train.remove(moved)
        val.append(moved)
        allocation[key]["val"] += 1

    train.sort(key=lambda r: r["cad_id"])
    val.sort(key=lambda r: r["cad_id"])
    if len(train) != 800 or len(val) != 200:
        raise RuntimeError((len(train), len(val)))
    if {r["cad_id"] for r in train} & {r["cad_id"] for r in val}:
        raise RuntimeError("train/val overlap")
    if {r["cad_id"] for r in train + val} != {r["cad_id"] for r in rows}:
        raise RuntimeError("split does not exactly cover source cohort")

    OUT.mkdir(parents=True, exist_ok=False)
    common = {
        "protocol": "pilot_1k_formal_v1_deterministic_joint_stratified",
        "seed": SEED,
        "source_manifest": str(SOURCE),
        "source_manifest_sha256": hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        "source_content_sha256": manifest["content_sha256"],
        "official_test_read": False,
    }
    hashes = {}
    for name, selected in (("train", train), ("val", val)):
        payload = {**common, "split": name, "records": selected, "distribution": distribution(selected)}
        data = canonical_bytes(payload)
        path = OUT / f"pilot_1k_{name}.json"
        path.write_bytes(data)
        hashes[name] = sha256_bytes(data)
    summary = {
        **common,
        "train_count": len(train),
        "val_count": len(val),
        "train_sha256": hashes["train"],
        "val_sha256": hashes["val"],
        "cohort_identity_sha256": sha256_bytes(canonical_bytes(sorted(r["cad_id"] for r in train + val))),
        "train_distribution": distribution(train),
        "val_distribution": distribution(val),
        "cross_split_overlap": 0,
        "status": "FROZEN",
    }
    (OUT / "SPLIT_FREEZE.json").write_bytes(canonical_bytes(summary))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
