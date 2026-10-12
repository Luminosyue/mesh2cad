"""Frozen geometry-pack v1 contracts.

CAD target is never derived from mesh / surface / edge inputs.
Tessellation and sampling knobs are fixed so the same STEP always
yields the same canonical mesh and the same surface seed.
"""

from __future__ import annotations

EXPERIMENT = "geometry_pack_v1"

NUM_SURFACE_POINTS = 8192
NUM_EDGE_POINTS = 1024
SURFACE_CHANNELS = 6  # xyz + normal; no edge_score on the surface branch
EDGE_CHANNELS = 6

# Mesh sharp-edge detector (first overfit round). Later ablate 15/30/45.
SHARP_ANGLE_DEG = 30.0

# OCC BRepMesh_IncrementalMesh — frozen, not per-sample random.
# Absolute linear deflection = max(rel * AABB_diag, min).
LINEAR_DEFLECTION_RELATIVE = 1.0e-3
LINEAR_DEFLECTION_MIN = 1.0e-6
ANGULAR_DEFLECTION_DEG = 20.0
TESSELLATION_IS_RELATIVE = False
TESSELLATION_PARALLEL = False  # serial mesh is deterministic

DEFAULT_SEED = 0
DEFAULT_TARGET_DIAGONAL = 6.0
