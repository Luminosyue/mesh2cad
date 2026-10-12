"""Fixed experiment contract for CURVE_ENCODER_BASELINE_V1."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CURVE_DATA_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"
JOINT_SPLIT_ROOT = REPO_ROOT / "cad_spatial_dataset" / "joint_deepcad_fusion360_v1"
OUTPUT_ROOT = REPO_ROOT / "ours3" / "curve_encoder_baseline_v1"
SPLIT_DIR = OUTPUT_ROOT / "splits" / "frozen_v1"
CACHE_DIR = OUTPUT_ROOT / "cache"
RUNS_DIR = OUTPUT_ROOT / "runs"

SCHEMA_VERSION = "curve_encoder_baseline_v1"
SPLIT_NAME = "frozen_v1"
SPLIT_SOURCE = "joint_deepcad_fusion360_v1"  # CAD-level, frozen, no re-shuffle

# ---- fixed geometry / model contract ----
N_POINTS = 32
TOKEN_DIM = 256
PRIMARY_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
TYPE_TO_ID = {t: i for i, t in enumerate(PRIMARY_TYPES)}
ID_TO_TYPE = {i: t for t, i in TYPE_TO_ID.items()}
N_TYPES = len(PRIMARY_TYPES)

# Feature modes → experiment ids
EXPERIMENTS = {
    "P0": {"encoder": "pointnet", "features": ("xyz",)},
    "P1": {"encoder": "pointnet", "features": ("xyz", "tangent")},
    "P2": {"encoder": "pointnet", "features": ("xyz", "tangent", "s")},
    "T0": {"encoder": "transformer", "features": ("xyz",)},
    "T1": {"encoder": "transformer", "features": ("xyz", "tangent")},
    "T2": {"encoder": "transformer", "features": ("xyz", "tangent", "s")},
}

FEATURE_DIM = {
    ("xyz",): 3,
    ("xyz", "tangent"): 6,
    ("xyz", "tangent", "s"): 7,
}

# Param vector layout (normalized space). BSPLINE has no param regression.
# LINE:    direction[3]
# CIRCLE:  center[3] + normal[3] + radius[1]
# ELLIPSE: center[3] + major_axis[3] + minor_axis[3] + major_r[1] + minor_r[1]
PARAM_DIM = {
    "LINE": 3,
    "CIRCLE": 7,
    "ELLIPSE": 11,
    "BSPLINE": 0,
}
MAX_PARAM_DIM = max(PARAM_DIM.values())

# ---- shared training budget (must be identical across P0–T2) ----
TRAIN = {
    "seed": 0,
    "epochs": 30,
    "batch_size": 256,
    "lr": 1e-3,
    "weight_decay": 1e-4,
    "grad_clip": 1.0,
    "warmup_epochs": 2,
    "samples_per_epoch": 65536,  # type-aware draws; fixed budget
    "num_workers": 4,
    "lambda_type": 1.0,
    "lambda_recon": 1.0,
    "lambda_param": 1.0,
    "eval_every": 1,
}

# Dataset folder mapping from joint dataset name
DATASET_TO_CURVE_SPLIT = {
    "deepcad": "deepcad_train",
    "fusion360": "fusion360_train",
}
