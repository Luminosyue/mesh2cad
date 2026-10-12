#!/usr/bin/env python3
"""Build a train-only balanced P1v2 fine-tuning set with corrected Fusion scale."""

from __future__ import annotations

import copy
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EXP = ROOT / "ours3/p1v2_cadfit_improvement_v1"
SOURCE = ROOT / "ours3/exact9998_v1/exact9998_train.json"
sys.path.insert(0, str(ROOT / "scripts/deepcad"))

from cad_canonical import canonicalize_features, compute_transform  # noqa: E402

SEED = 20260926
TRAIN_PER_SOURCE = 280
DEV_PER_SOURCE = 52


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def corrected_fusion_record(record: dict) -> tuple[dict, dict]:
    result = copy.deepcopy(record)
    source_surface = Path(record["point_clouds"][0])
    pack = source_surface.parent
    source_points_path = pack / "surface_points_source.npy"
    source_xyz = np.load(source_points_path).astype(np.float32)[:, :3]
    original_features = np.load(source_surface).astype(np.float32)
    if original_features.shape != (len(source_xyz), 6):
        raise ValueError(
            f"expected original (N,6) features for {record['id']}, got {original_features.shape}"
        )
    source_features = np.concatenate([source_xyz, original_features[:, 3:6]], axis=1)
    transform = compute_transform(source_xyz, target_diagonal=6.0)
    corrected = canonicalize_features(source_features, transform)
    if corrected.shape != (8192, 6) or not np.isfinite(corrected).all():
        raise ValueError(f"invalid corrected features for {record['id']}: {corrected.shape}")
    sample_id = record["sample_id"]
    out_dir = EXP / "corrected_features/Fusion360/geometry_pack_v2" / sample_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_surface = out_dir / "surface_points.npy"
    np.save(out_surface, corrected.astype(np.float32))
    (out_dir / "coordinate_transform.json").write_text(
        json.dumps(transform.to_json(), indent=2) + "\n"
    )
    result["point_clouds"] = [str(out_surface)]
    audit = {
        "id": record["id"],
        "source_surface": str(source_surface),
        "source_points": str(source_points_path),
        "corrected_surface": str(out_surface),
        "source_points_sha256": sha256(source_points_path),
        "corrected_surface_sha256": sha256(out_surface),
        "corrected_diagonal": float(
            np.linalg.norm(corrected[:, :3].max(0) - corrected[:, :3].min(0))
        ),
        "transform": transform.to_json(),
    }
    return result, audit


def main() -> int:
    records = json.loads(SOURCE.read_text())
    deepcad = [row for row in records if row["dataset"] == "deepcad"]
    fusion = [row for row in records if row["dataset"] == "fusion360"]
    if len(fusion) != TRAIN_PER_SOURCE + DEV_PER_SOURCE:
        raise RuntimeError(f"expected 332 Fusion train rows, found {len(fusion)}")
    rng = random.Random(SEED)
    rng.shuffle(deepcad)
    rng.shuffle(fusion)

    fusion_train_raw = fusion[:TRAIN_PER_SOURCE]
    fusion_dev_raw = fusion[TRAIN_PER_SOURCE:]
    deepcad_train = [copy.deepcopy(row) for row in deepcad[:TRAIN_PER_SOURCE]]
    deepcad_dev = [copy.deepcopy(row) for row in deepcad[TRAIN_PER_SOURCE : TRAIN_PER_SOURCE + DEV_PER_SOURCE]]

    audits = []
    fusion_fixed = {}
    for index, row in enumerate(fusion, 1):
        fixed, audit = corrected_fusion_record(row)
        fusion_fixed[row["id"]] = fixed
        audits.append(audit)
        if index % 50 == 0 or index == len(fusion):
            print(f"corrected Fusion features {index}/{len(fusion)}", flush=True)

    train = deepcad_train + [fusion_fixed[row["id"]] for row in fusion_train_raw]
    dev = deepcad_dev + [fusion_fixed[row["id"]] for row in fusion_dev_raw]
    rng.shuffle(train)
    rng.shuffle(dev)
    manifests = EXP / "manifests"
    manifests.mkdir(parents=True, exist_ok=True)
    (manifests / "balanced_train.json").write_text(json.dumps(train, indent=2) + "\n")
    (manifests / "balanced_dev.json").write_text(json.dumps(dev, indent=2) + "\n")
    dataset_info = {
        "p1v2_balanced_train": {
            "file_name": "balanced_train.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "point_clouds": "point_clouds"},
        },
        "p1v2_balanced_dev": {
            "file_name": "balanced_dev.json",
            "formatting": "sharegpt",
            "columns": {"messages": "conversations", "point_clouds": "point_clouds"},
        },
    }
    (manifests / "dataset_info.json").write_text(json.dumps(dataset_info, indent=2) + "\n")
    (EXP / "corrected_features/FUSION_FEATURE_AUDIT.json").write_text(
        json.dumps(audits, indent=2) + "\n"
    )
    summary = {
        "schema_version": "P1V2_BALANCED_FUSION_REPAIR_DATA_V1",
        "seed": SEED,
        "source": str(SOURCE),
        "train_N": len(train),
        "train_DeepCAD_N": TRAIN_PER_SOURCE,
        "train_Fusion360_N": TRAIN_PER_SOURCE,
        "dev_N": len(dev),
        "dev_DeepCAD_N": DEV_PER_SOURCE,
        "dev_Fusion360_N": DEV_PER_SOURCE,
        "formal_VAL1000_used_for_training_or_selection": False,
        "formal_TEST1000_used": False,
        "fusion_feature_corrections_N": len(audits),
        "fusion_corrected_diagonal_min": min(row["corrected_diagonal"] for row in audits),
        "fusion_corrected_diagonal_max": max(row["corrected_diagonal"] for row in audits),
    }
    (manifests / "PREPARATION_SUMMARY.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
