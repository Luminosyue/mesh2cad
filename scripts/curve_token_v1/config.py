"""Track B / Method 2 (Parametric Curve Token) configuration.

Track A is a frozen baseline: this package only ever READS Track A artifacts and
writes into OUTPUT_ROOT. Nothing here may import or mutate Track A modules.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATASET_ROOT = REPO_ROOT / "cad_spatial_dataset"
OUTPUT_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"

SCHEMA_VERSION = "curve_token_v1"
NORMALIZATION_VERSION = "curve_token_v1"

# ---------------------------------------------------------------- sampling ---
N_SAMPLE_DEFAULT = 32
N_SAMPLE_EXTRA = (64,)

# ------------------------------------------------------------- curve types ---
# GeomAbs_CurveType enum -> Track B canonical name. Track A used mixed-case
# names ("Line"/"Circle"); Track B uses upper case and keeps the raw OCC name
# separately so the two vocabularies never get confused.
GEOMABS_TO_NAME = {
    0: "LINE",
    1: "CIRCLE",
    2: "ELLIPSE",
    3: "HYPERBOLA",
    4: "PARABOLA",
    5: "BEZIER",
    6: "BSPLINE",
    7: "OFFSET",
    8: "OTHER",
}

# Stable ids for curve_type_id in the npz. Never renumber: downstream token
# embeddings will be indexed by these.
CURVE_TYPE_IDS = {
    "LINE": 0,
    "CIRCLE": 1,
    "ELLIPSE": 2,
    "BSPLINE": 3,
    "BEZIER": 4,
    "HYPERBOLA": 5,
    "PARABOLA": 6,
    "OFFSET": 7,
    "OTHER": 8,
}
ID_TO_CURVE_TYPE = {v: k for k, v in CURVE_TYPE_IDS.items()}

# Types this version extracts exact parameters for.
PRIMARY_TYPES = ("LINE", "CIRCLE", "ELLIPSE", "BSPLINE")
# Types kept with full raw geometry but no analytic parameter block.
SECONDARY_TYPES = ("BEZIER", "HYPERBOLA", "PARABOLA", "OFFSET", "OTHER")

# ------------------------------------------------------------- tolerances ----
# Reconstruction tolerances are relative to the object bbox diagonal so they
# behave the same for a 3 mm part and a 300 mm part.
RECON_REL_TOL = 1e-6
RECON_ABS_TOL_MIN = 1e-9
TANGENT_ANGLE_TOL_DEG = 1.0
DEGENERATE_LENGTH_REL = 1e-9

# --------------------------------------------------------------- datasets ----
# split name -> (STEP source dir, Track A geometry_pack dir used only for the
# cad_id whitelist and the frozen coordinate_transform.json).
SPLITS: dict[str, dict[str, Path]] = {
    "deepcad_train": {
        "step_root": DATASET_ROOT / "DeepCAD" / "train",
        "track_a_pack": DATASET_ROOT / "DeepCAD" / "geometry_pack_v1",
        "dataset": "DeepCAD",
    },
    "fusion360_train": {
        "step_root": DATASET_ROOT / "Fusion360" / "train",
        "track_a_pack": DATASET_ROOT / "Fusion360" / "geometry_pack_v1",
        "dataset": "Fusion360",
    },
}

STEP_FILENAME = "model.step"

# --------------------------------------------------------- output subdirs ----
AUDIT_MD = OUTPUT_ROOT / "audit_existing_data.md"
GUARD_DIR = OUTPUT_ROOT / "track_a_guard"
STATS_DIR = OUTPUT_ROOT / "statistics"
VALIDATION_DIR = OUTPUT_ROOT / "validation"
ARTIFACTS_DIR = OUTPUT_ROOT / "artifacts"
VISUAL_QA_DIR = ARTIFACTS_DIR / "visual_qa"
FITTING_DIR = OUTPUT_ROOT / "curve_fitting_baseline"
RUNS_DIR = OUTPUT_ROOT / "runs"


def split_dir(split: str) -> Path:
    return OUTPUT_ROOT / split


def cad_dir(split: str, cad_id: str) -> Path:
    return split_dir(split) / cad_id
