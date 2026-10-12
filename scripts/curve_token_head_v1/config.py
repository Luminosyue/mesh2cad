"""CURVE_TOKEN_HEAD_V1 — frozen C2 backbone + type / recon / parameter heads.

Step 1 contract: the encoder is FROZEN as C2 and must not change.
    shape  = curve-local xyz(3) + tangent(3) + s(1)      [32, 7]
    scale  = log(polyline_length + 1e-6)                 [1]
    fusion = PointNet(shape) ⊕ MLP(scale) → 256-D Curve Token
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE_ROOT = REPO_ROOT / "ours3" / "curve_encoder_baseline_v1"
SPLIT_DIR = BASELINE_ROOT / "splits" / "frozen_v1"
CACHE_DIR = BASELINE_ROOT / "cache"
CURVE_DATA_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"
OUTPUT_ROOT = REPO_ROOT / "ours3" / "curve_token_head_v1"
RUNS_DIR = OUTPUT_ROOT / "runs"
EXPORT_DIR = OUTPUT_ROOT / "curve_token_format"

SCHEMA_VERSION = "curve_token_head_v1"
SPLIT_NAME = "frozen_v1"

# ---- FROZEN backbone (C2). Do not edit. ----
BACKBONE = {
    "name": "C2",
    "frame": "curve_local",
    "shape_features": ("xyz_local", "tangent", "s"),
    "shape_dim": 7,
    "scale_features": ("log_length",),
    "scale_dim": 1,
    "encoder": "pointnet",
    "fusion": "concat+mlp",
    "token_dim": 256,
    "n_points": 32,
    "source": "scripts/curve_encoder_scale_curvature_v1 (exp C2)",
}
N_POINTS = 32
TOKEN_DIM = 256

PRIMARY_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
TYPE_TO_ID = {t: i for i, t in enumerate(PRIMARY_TYPES)}
ID_TO_TYPE = {i: t for t, i in TYPE_TO_ID.items()}
N_TYPES = 4

# ---- per-type parameter head layouts (curve-LOCAL frame) ----
# Translation+uniform-scale normalized: p_local = (p_norm - centroid) / curve_scale
# Directions are rotation-free, so they are used as-is (unit).
LINE_PARAM = ("origin_local[3]", "direction[3]", "length_local[1]")
CIRCLE_PARAM = (
    "center_local[3]",
    "normal[3]",
    "radius_local[1]",
    "cos_u0",
    "sin_u0",
    "cos_u1",
    "sin_u1",
    "span_frac",
)
ELLIPSE_PARAM = (
    "center_local[3]",
    "major_axis[3]",
    "minor_axis[3]",
    "normal[3]",
    "major_r_local",
    "minor_r_local",
    "cos_u0",
    "sin_u0",
    "span_frac",
)
# BSPLINE: no control-point regression (variable length, P95=34, max=95).
BSPLINE_PARAM = ("degree_logits[6]", "log_num_cp[1]")
BSPLINE_DEGREES = (3, 4, 5, 6, 7, 8)

LINE_DIM = 7
CIRCLE_DIM = 12
ELLIPSE_DIM = 17
BSPLINE_DEGREE_CLASSES = len(BSPLINE_DEGREES)

# ---- experiments (Step 4) ----
EXPERIMENTS = {
    "D0": {
        "use_recon": False,
        "use_param": False,
        "desc": "frozen C2 backbone + type head only (classification baseline)",
    },
    "D1": {
        "use_recon": True,
        "use_param": True,
        "desc": "frozen C2 backbone + type + reconstruction + parameter heads",
    },
}

# L = CE + 1.0 * Chamfer + 0.1 * parameter
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
    "lambda_param": 0.1,
    "eval_every": 1,
}
