"""Frozen Method-B clean pack contracts (Jerry Steps 1–6).

Three sources stay in separate buckets. CAD-level mix target is 50/30/20
(DeepCAD / Fusion360 / CADFS); curve-type mix is controlled separately.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = "method_b_clean_v1"

# --- tessellation (OCC) ---
LINEAR_DEFLECTION_RELATIVE = 0.01
LINEAR_DEFLECTION_MIN = 1.0e-6
ANGULAR_DEFLECTION_DEG = 10.0
TESSELLATION_IS_RELATIVE = False
TESSELLATION_PARALLEL = False

# --- sampling ---
NUM_SURFACE_POINTS = 4096
NUM_EDGE_POINTS = 1024
SURFACE_CHANNELS = 6  # xyz + normal; never edge_score
SHARP_ANGLE_DEG = 30.0
TARGET_DIAGONAL = 6.0
DEFAULT_SEED = 0

# --- mesh noise levels (vertex-wise Gaussian in source mesh frame) ---
NOISE_SIGMAS = {
    "001": 0.001,
    "005": 0.005,
    "01": 0.01,
}

# --- paths ---
OUTPUT_ROOT = REPO_ROOT / "cad_spatial_dataset" / "method_b_pack_v1"
MANIFEST_ROOT = REPO_ROOT / "cad_spatial_dataset" / "method_b_clean_v1"
STATS_DIR = MANIFEST_ROOT / "statistics"

CADFS_STEP_ROOT = REPO_ROOT / "CADFS" / "step"
CADFS_ANN_ROOT = REPO_ROOT / "CADFS" / "text_annotations"

SOURCE_ROOTS = {
    "deepcad": {
        "step_root": REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "train",
        "step_name": "model.step",
        "track_a_pack": REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "geometry_pack_v1",
        "curve_ready": REPO_ROOT / "ours3" / "curve_token_data_v1" / "deepcad_train",
        "role": "main_train",
        "budget_frac": 0.50,
    },
    "fusion360": {
        "step_root": REPO_ROOT / "cad_spatial_dataset" / "Fusion360" / "train",
        "step_name": "model.step",
        "track_a_pack": REPO_ROOT / "cad_spatial_dataset" / "Fusion360" / "geometry_pack_v1",
        "curve_ready": REPO_ROOT / "ours3" / "curve_token_data_v1" / "fusion360_train",
        "role": "geometry_augment",
        "budget_frac": 0.30,
    },
    "cadfs": {
        "step_root": CADFS_STEP_ROOT,
        "step_name": None,  # <bucket>/<id>.step
        "track_a_pack": None,
        "curve_ready": None,
        "role": "hard_set",
        "budget_frac": 0.20,
    },
}

# CAD-level budget for the formal 10k round (half of CADFS held out as test).
SCALE_TARGETS = {
    "overfit100": {"deepcad": 50, "fusion360": 30, "cadfs_train": 10, "cadfs_test": 10},
    "mid1k": {"deepcad": 500, "fusion360": 300, "cadfs_train": 100, "cadfs_test": 100},
    "full10k": {"deepcad": 5000, "fusion360": 3000, "cadfs_train": 1000, "cadfs_test": 1000},
}

PRIMARY_CURVE_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")

REQUIRED_PACK_FILES = (
    "mesh_clean.obj",
    "mesh_noise_001.obj",
    "mesh_noise_005.obj",
    "mesh_noise_01.obj",
    "surface_points.npy",
    "sharp_edges.npy",
    "edge_points.npy",
    "curves.json",
    "normalization.json",
    "metadata.json",
    "qa.json",
)
