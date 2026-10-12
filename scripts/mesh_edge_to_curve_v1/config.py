"""MESH_EDGE_TO_CURVE_V1 — Step 6.1: mesh sharp edge points → Curve Token.

Reads (read-only):
  * ``cad_spatial_dataset/{DeepCAD,Fusion360}/geometry_pack_v1/<sample_id>/``
      mesh_sharp_edges.npz  (mesh triangle edges with dihedral > 30°, world coords)
      metadata.json         (canonical scale/translation: p_canon = s*p + t)
  * ``ours3/curve_token_data_v1/<cad_dir>/``
      curve_samples_64.npz / curve_samples.npz, curves.json   (B-Rep GT)
  * ``ours3/curve_encoder_baseline_v1/splits/frozen_v1/``      (frozen split)
  * ``ours3/curve_token_head_v1/runs/D1_frozen_v1_seed*/best.pt`` (frozen C2 + heads)

Writes only under ``ours3/mesh_edge_to_curve_v1/``.
"""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_ROOT = {
    "deepcad": REPO_ROOT / "cad_spatial_dataset" / "DeepCAD" / "geometry_pack_v1",
    "fusion360": REPO_ROOT / "cad_spatial_dataset" / "Fusion360" / "geometry_pack_v1",
}
CURVE_DATA_ROOT = REPO_ROOT / "ours3" / "curve_token_data_v1"
SPLIT_DIR = REPO_ROOT / "ours3" / "curve_encoder_baseline_v1" / "splits" / "frozen_v1"
HEAD_RUNS = REPO_ROOT / "ours3" / "curve_token_head_v1" / "runs"
OUTPUT_ROOT = REPO_ROOT / "ours3" / "mesh_edge_to_curve_v1"
CACHE_DIR = OUTPUT_ROOT / "cache"
RUNS_DIR = OUTPUT_ROOT / "runs"

SCHEMA_VERSION = "mesh_edge_to_curve_v1"
SPLIT_NAME = "frozen_v1"
N_POINTS = 32

# Oracle grouping: a mesh sharp segment is attached to a B-Rep curve when both
# endpoints are closer to that curve than ASSIGN_TOL_FRAC * canonical diagonal.
# The canonical frame has a fixed target diagonal of 6.0 (see curve_token_v1).
CANON_DIAGONAL = 6.0
ASSIGN_TOL_FRAC = 0.01
GT_REF_POINTS = 64  # curve_samples_64.npz, used as the GT reference polyline
KNN_CANDIDATES = 8  # candidate curves per query point before exact distance
MIN_MESH_POINTS = 2  # a polyline needs at least two distinct points
