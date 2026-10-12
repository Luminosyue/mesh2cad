#!/usr/bin/env python3
"""Freeze data, initialization, visualization, and selection contracts before formal training."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DATA = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data"
OUT = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/formal_train800_v1"
WEIGHTS = Path("/var/tmp/cuiyuehan_mesh2cad/m2_spatial_anchor_q_ablation_formal_train800_v1")
BASE = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/c2_frozen_v2_rewire/OFFICIAL_LLAMA_GEOMETRY_BASE_V1"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


OUT.mkdir(parents=True, exist_ok=False)
WEIGHTS.mkdir(parents=True, exist_ok=False)
train_path = DATA / "v3_1k_train.json"
dev_path = DATA / "v3_decode_dev_50.json"
train = json.loads(train_path.read_text())["records"]
dev = json.loads(dev_path.read_text())["records"]
assert len(train) == 800 and len(dev) == 50

# Freeze qualitative IDs before any formal result exists. Hash ordering avoids file-order bias.
ranked = sorted(dev, key=lambda row: (hashlib.sha256(row["cad_id"].encode()).hexdigest(), row["cad_id"]))
visual_ids = [row["cad_id"] for row in ranked[:10]]
(OUT / "VISUALIZATION_DEV_IDS_V1.json").write_text(json.dumps({
    "selection_time": "BEFORE_FORMAL_RESULTS",
    "algorithm": "ascending SHA256(cad_id), tie by cad_id",
    "count": len(visual_ids),
    "cad_ids": visual_ids,
}, indent=2) + "\n")

contract = {
    "CONTRACT": "M2_SPATIAL_ANCHOR_Q_ABLATION_FORMAL_TRAIN800_V1",
    "CURRENT_GATE": "FORMAL_TRAIN800_CONTRACT_FROZEN",
    "ARMS": {
        "A0_NOANCHOR_Q8": {"use_anchor": False, "num_queries": 8},
        "A1_ANCHOR_Q8": {"use_anchor": True, "num_queries": 8},
        "A2_ANCHOR_Q16": {"use_anchor": True, "num_queries": 16},
        "A3_ANCHOR_Q32": {"use_anchor": True, "num_queries": 32},
    },
    "FRESH_INITIALIZATION": str(BASE),
    "SMOKE_CHECKPOINT_USED_FOR_FORMAL_TRAINING": False,
    "TRAIN_PATH": str(train_path),
    "TRAIN_SHA256": sha256(train_path),
    "TRAIN_COUNT": 800,
    "DECODE_DEV_PATH": str(dev_path),
    "DECODE_DEV_SHA256": sha256(dev_path),
    "DECODE_DEV_COUNT": 50,
    "WEIGHT_OUTPUT_ROOT": str(WEIGHTS),
    "TRAINING": {
        "seed": 42,
        "epochs": 10,
        "micro_batch_size": 1,
        "gradient_accumulation": 4,
        "optimizer": "AdamW",
        "learning_rate": 2e-5,
        "weight_decay": 0.0,
        "scheduler": "cosine",
        "warmup_ratio": 0.03,
        "precision": "bfloat16",
        "max_sequence_length": 4096,
        "target_norm": 1.9414,
        "epoch_order": "random.Random(42 + epoch).shuffle(range(800))",
    },
    "FROZEN": {
        "Sonata": True,
        "SurfaceProjector": True,
        "C2": True,
        "C2_SHA256": "553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9",
    },
    "DECODE": {"split": "decode-dev50", "greedy": True, "max_new_tokens": 4096},
    "SELECTION_RULE": [
        "unexpected_runaway_rate <= 0.10",
        "maximize STEP reload",
        "maximize Op F1",
        "minimize common-valid Chamfer",
        "minimize validation CE",
    ],
    "COMMON_VALID_DEFINITION": "For epoch e, intersection of STEP-success CAD IDs across all four arm epoch-e predictions.",
    "FORBIDDEN": {
        "ANCHOR_EVAL_100_MODEL_READ": False,
        "PILOT150_MODEL_READ": False,
        "OFFICIAL_TEST_READ": False,
    },
}
(OUT / "FORMAL_TRAIN800_CONTRACT_V1.json").write_text(json.dumps(contract, indent=2) + "\n")
(OUT / "WEIGHT_OUTPUT_ROOT.txt").write_text(str(WEIGHTS) + "\n")
manifest = {}
for path in sorted(OUT.iterdir()):
    if path.is_file():
        manifest[path.name] = {"size": path.stat().st_size, "sha256": sha256(path)}
(OUT / "CONTRACT_FILE_SHA256_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(json.dumps({"CURRENT_GATE": contract["CURRENT_GATE"], "TRAIN_COUNT": 800, "DEV_COUNT": 50, "VISUAL_IDS": visual_ids, "WEIGHT_OUTPUT_ROOT": str(WEIGHTS)}, indent=2))
