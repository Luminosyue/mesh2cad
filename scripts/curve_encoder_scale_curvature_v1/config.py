"""CURVE_ENCODER_SCALE_CURVATURE_V1 — disentangle shape vs scale.

Reuses frozen_v1 split + baseline cache. Does not touch Track A.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = REPO_ROOT / "ours3" / "curve_encoder_baseline_v1"
SPLIT_DIR = BASELINE_ROOT / "splits" / "frozen_v1"
CACHE_DIR = BASELINE_ROOT / "cache"
OUTPUT_ROOT = REPO_ROOT / "ours3" / "curve_encoder_scale_curvature_v1"
RUNS_DIR = OUTPUT_ROOT / "runs"

SCHEMA_VERSION = "curve_encoder_scale_curvature_v1"
SPLIT_NAME = "frozen_v1"
N_POINTS = 32
TOKEN_DIM = 256
SHAPE_DIM = 7  # local/object xyz(3)+tan(3)+s(1)
SCALE_DIM = 1  # log(length+eps)
CURV_DIM = 4  # chord_h, total_turn, mean_turn, max_turn (normalized)

PRIMARY_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
TYPE_TO_ID = {t: i for i, t in enumerate(PRIMARY_TYPES)}
ID_TO_TYPE = {i: t for t, i in TYPE_TO_ID.items()}
N_TYPES = 4

# C0 = P2 reference (object frame). C1–C3 = interventions.
EXPERIMENTS = {
    "C0": {
        "frame": "object",
        "use_scale_branch": False,
        "use_curvature": False,
        "use_straightness_head": False,
        "desc": "P2 reference: object xyz+tan+s",
    },
    "C1": {
        "frame": "curve_local",
        "use_scale_branch": False,
        "use_curvature": False,
        "use_straightness_head": False,
        "desc": "curve-local xyz+tan+s (no scale)",
    },
    "C2": {
        "frame": "curve_local",
        "use_scale_branch": True,
        "use_curvature": False,
        "use_straightness_head": False,
        "desc": "curve-local + log-length scale branch",
    },
    "C3": {
        "frame": "curve_local",
        "use_scale_branch": True,
        "use_curvature": True,
        "use_straightness_head": True,
        "desc": "curve-local + scale + curvature + straightness head",
    },
}

# Same budget as P0–T2 / P2
TRAIN = {
    "seed": 0,
    "epochs": 30,
    "batch_size": 256,
    "lr": 1e-3,
    "weight_decay": 1e-4,
    "grad_clip": 1.0,
    "warmup_epochs": 2,
    "samples_per_epoch": 65536,
    "num_workers": 4,
    "lambda_type": 1.0,
    "lambda_recon": 1.0,
    "lambda_param": 1.0,
    "lambda_straight": 0.5,  # C3 only
    "eval_every": 1,
}

# Root-cause targets (P2 test reference)
REF_P2 = {
    "line_to_circle_fp": 1248,
    "line_to_circle_rate": 0.073,
    "top_decile_line_to_circle_fp_rate": 0.46,
    "circle_recall": 0.905,
}
