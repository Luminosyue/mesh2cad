"""Track B Curve Encoder Baseline V1 configuration.

Reads Track B curve_token_data_v1 (and Track A only via that frozen data).
Writes exclusively under ENCODER_OUTPUT_ROOT. Never mutates Track A.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"
ENCODER_OUTPUT_ROOT = REPO_ROOT / "ours3" / "curve_encoder_baseline_v1"

SCHEMA_VERSION = "curve_encoder_baseline_v1"
TOKEN_DIM = 256
N_SAMPLE = 32

# Geometry-only input ablations (curve_type is NEVER an input here).
ABLATIONS = {
    "B0_xyz": {"use_tangent": False, "use_scalars": False},
    "B1_xyz_tangent": {"use_tangent": True, "use_scalars": False},
    "B2_xyz_tangent_scalars": {"use_tangent": True, "use_scalars": True},
}

CURVE_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
CURVE_TYPE_IDS = {"LINE": 0, "CIRCLE": 1, "ELLIPSE": 2, "BSPLINE": 3}
ID_TO_CURVE_TYPE = {v: k for k, v in CURVE_TYPE_IDS.items()}
N_TYPES = 4

# Noise σ relative to Track-A target_diagonal (normalized-space units ≈ σ * 6).
NOISE_LEVELS = (0.0, 1e-4, 1e-3, 5e-3)
PARTIAL_FRACS = (1.0, 0.75, 0.5, 0.25)

# Arc-coverage buckets (degrees) for CIRCLE / ELLIPSE evaluation.
ARC_BUCKETS = (
    ("lt15", 0.0, 15.0),
    ("15_45", 15.0, 45.0),
    ("45_90", 45.0, 90.0),
    ("gt90", 90.0, 360.0),
    ("closed", None, None),  # is_closed override
)

# CAD-level split ratios (by CAD / family, never by curve).
SPLIT_RATIOS = {"train": 0.80, "val": 0.10, "test": 0.10}
SPLIT_SEED = 42

# Training defaults (CPU-friendly; override via CLI).
DEFAULT_EPOCHS = 20
DEFAULT_BATCH = 1024
DEFAULT_LR = 1e-3
DEFAULT_NUM_WORKERS = 4
DEFAULT_WEIGHT_DECAY = 1e-4

# Loss weights
W_TYPE = 1.0
W_RECON = 1.0
W_PARAM = 1.0

SPLITS_DATA = ("deepcad_train", "fusion360_train")

CACHE_DIR = ENCODER_OUTPUT_ROOT / "cache"
SPLITS_DIR = ENCODER_OUTPUT_ROOT / "splits"
RUNS_DIR = ENCODER_OUTPUT_ROOT / "runs"
CKPT_DIR = ENCODER_OUTPUT_ROOT / "checkpoints"
EVAL_DIR = ENCODER_OUTPUT_ROOT / "eval"
EMBED_DIR = ENCODER_OUTPUT_ROOT / "embeddings"
REPORTS_DIR = ENCODER_OUTPUT_ROOT / "reports"
GUARD_DIR = ENCODER_OUTPUT_ROOT / "track_a_guard"

# Param vector layout (normalized space). BSPLINE uses recon only in V1.
# LINE:     origin(3) + direction(3) = 6 @ [0:6]
# CIRCLE:   center(3) + normal(3) + radius(1) = 7 @ [0:7]
# ELLIPSE:  center(3) + normal(3) + major_axis(3) + ra(1) + rb(1) = 11 @ [0:11]
PARAM_DIM = 11
