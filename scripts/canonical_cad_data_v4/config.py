"""Single source of thresholds / paths for CANONICAL_CAD_DATA_V4.

Do not hard-code these values in other modules.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = REPO_ROOT / "scripts"
DATA_ROOT = REPO_ROOT / "ours3" / "canonical_cad_data_v4"

PIPELINE_VERSION = "canonical_cad_data_v4"
SEED = 42

# ---------------------------------------------------------------------------
# Source roots (read-only)
# ---------------------------------------------------------------------------
DEEPCAD_RAW_JSON = REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "raw_json"
DEEPCAD_TRAIN = REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "train"
FUSION360_RECON = (
    REPO_ROOT
    / "cad_spatial_dataset"
    / "Fusion360"
    / "reconstruction"
    / "reconstruction"
)
FUSION360_TRAIN = REPO_ROOT / "cad_spatial_dataset" / "Fusion360" / "train"
FUSION360_570_PASS = (
    REPO_ROOT
    / "cad_spatial_dataset"
    / "geometry_pack_v2_mesh2cad"
    / "placement_fix_retest_v3"
    / "STRICT_LABEL_PASS_CANDIDATES.json"
)
FUSION360_FAILURES = (
    REPO_ROOT
    / "cad_spatial_dataset"
    / "geometry_pack_v2_mesh2cad"
    / "placement_fix_retest_v3"
    / "REMAINING_FAILURES.json"
)
CADFS_FEATURESCRIPT = REPO_ROOT / "CADFS" / "featurescript_rp"
CADFS_STEP = REPO_ROOT / "CADFS" / "step"
CADFS_TEXT = REPO_ROOT / "CADFS" / "text_annotations"

C2_CHECKPOINT = (
    REPO_ROOT
    / "ours3"
    / "curve_encoder_scale_curvature_v1"
    / "runs"
    / "C2_frozen_v1"
    / "best.pt"
)

# ---------------------------------------------------------------------------
# Canary / scale-up quotas (do not jump to 10k)
# ---------------------------------------------------------------------------
CANARY = {
    "DEEPCAD": 100,
    "FUSION360": 100,
    "CADFS": 300,
    "CADFS_AUDIT": 1000,
}
TARGET_10K = {"CADFS": 5000, "DEEPCAD": 3000, "FUSION360": 2000}

# ---------------------------------------------------------------------------
# Geometry / sampling
# ---------------------------------------------------------------------------
SURFACE_N_POINTS = 4096
SURFACE_SEED = 42
EDGE_SEED = 42
CURVE_N_SAMPLES = 32
C2_TOKEN_DIM = 256
C2_PROVENANCE_N = 20
C2_ABS_DIFF_TOL = 1e-5  # expected ~0; document backend noise if not

VOLUME_EPS = 1e-12
BBOX_DIAG_EPS = 1e-8
NORMAL_NORM_MIN = 0.5  # after unit-normalization, reject collapsed normals

# ---------------------------------------------------------------------------
# Complexity (deterministic)
# ---------------------------------------------------------------------------
ADVANCED_OPS = frozenset(
    {"revolve", "loft", "sweep", "fillet", "chamfer", "shell", "mirror", "pattern"}
)
COMPLEXITY = {
    "simple_max_ops": 5,
    "medium_max_ops": 15,
    "hard_advanced_min": 2,
}

# ---------------------------------------------------------------------------
# Split (only after dedup)
# ---------------------------------------------------------------------------
SPLIT_RATIOS = {"train": 0.8, "val": 0.1, "test": 0.1}

# ---------------------------------------------------------------------------
# Fingerprint quantization
# ---------------------------------------------------------------------------
FINGERPRINT = {
    "bbox_decimals": 4,
    "metric_decimals": 4,
    "xyz_quant": 1e-3,
}

# ---------------------------------------------------------------------------
# Output layout
# ---------------------------------------------------------------------------
RECORDS_DIR = DATA_ROOT / "records"
MANIFESTS_DIR = DATA_ROOT / "manifests"
REPORTS_DIR = DATA_ROOT / "reports"
HASHES_DIR = DATA_ROOT / "hashes"
AUDIT_DIR = DATA_ROOT / "audit"
