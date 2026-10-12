"""SPATIALLM_CURVE_TOKEN_V1 — inject frozen Curve Tokens into SpatialLM.

Three arms share one prompt structure so only the second geometry stream differs:

  B0  surface points only                        (= existing J0 recipe)
  B1  surface points + sharp EDGE POINTS         (= existing J2 sepedge recipe)
  M2  surface points + CURVE TOKENS  (ours)      (new second-stream payload)

B1 and M2 occupy the same sequence slot with the same marker tokens, so the only
difference between them is how the same sharp edges are represented: a voxelized
point cloud through Sonata, versus parametric Curve Tokens through the frozen C2
encoder.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = REPO_ROOT / "SpatialLM"
BASE_MODEL = SPATIALLM_ROOT / "models" / "SpatialLM1.1-Llama-1B"
PACK_ROOT = {
    "deepcad": REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "geometry_pack_v1",
    "fusion360": REPO_ROOT / "cad_spatial_dataset" / "Fusion360" / "geometry_pack_v1",
}
PACK_REL = {
    "deepcad": "DeepCAD/geometry_pack_v1",
    "fusion360": "Fusion360/geometry_pack_v1",
}
CURVE_DATA_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"
JOINT_DATASET_DIR = REPO_ROOT / "cad_spatial_dataset" / "joint_deepcad_fusion360_v1"
HEAD_RUNS = REPO_ROOT / "ours3" / "curve_token_head_v1" / "runs"
DEFAULT_CKPT = HEAD_RUNS / "D1_frozen_v1_seed0" / "best.pt"

OUTPUT_ROOT = REPO_ROOT / "ours3" / "spatiallm_curve_token_v1"
TOKEN_ROOT = OUTPUT_ROOT / "curve_tokens"
SUBSET_DIR = OUTPUT_ROOT / "subset100"
RUNS_DIR = OUTPUT_ROOT / "runs"
HELDOUT_BEST_V2 = RUNS_DIR / "heldout_best_v2"
SURFACE_IDX_CACHE = HELDOUT_BEST_V2 / "surface_idx4096.npz"
BASE_SPATIALLM = SPATIALLM_ROOT / "models" / "SpatialLM1.1-Llama-1B"

SCHEMA_VERSION = "spatiallm_curve_token_v1"

CURVE_TOKEN_DIM = 256  # frozen C2 output
LLM_HIDDEN_SIZE = 2048  # SpatialLM1.1-Llama-1B config.json::hidden_size
# Token budget: a CAD can have >1000 curves, which would blow past cutoff_len.
# Curves are ranked by polyline length (longest first) and truncated.
MAX_CURVE_TOKENS = 128

# Step 4: 100 CADs, mixed so both DSL dialects are represented.
SUBSET_N_DEEPCAD = 80
SUBSET_N_FUSION360 = 20
SUBSET_SEED = 0
