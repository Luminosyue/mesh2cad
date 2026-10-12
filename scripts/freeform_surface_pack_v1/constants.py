"""FREEFORM_SURFACE_PACK_V1 frozen constants."""

from __future__ import annotations

EXPERIMENT = "freeform_surface_pack_v1"

N_PATCH_POINTS = 1024
N_BOUNDARY_POINTS = 256
PATCH_CHANNELS = 6  # xyz + normal
BOUNDARY_CHANNELS = 6

# Tessellation (same contract family as geometry_pack_v1)
LINEAR_DEFLECTION_RELATIVE = 1.0e-3
LINEAR_DEFLECTION_MIN = 1.0e-6
ANGULAR_DEFLECTION_DEG = 20.0
TESSELLATION_IS_RELATIVE = False
TESSELLATION_PARALLEL = False

# Canonical cubic control grid (fixed output budget for reconstruction)
# Audit (729 faces): 4x4 << 8x8 under UV-sample-as-cubic-poles semantics.
# See freeform_surface_pack_v1/canonical_grid_audit.md
CANONICAL_DEGREE = 3
CANONICAL_NU = 4
CANONICAL_NV = 4

# QA
MIN_FACE_AREA_FRAC = 1e-12  # relative to bbox_diag^2
MIN_TRIANGLES = 1

# Split (part-level)
SPLIT_SEED = 42
N_TRAIN_PARTS = 25
N_VAL_PARTS = 6
N_TEST_PARTS = 6

# Analytic control quotas (classification negatives)
N_PLANE_TARGET = 700
N_CYLINDER_TARGET = 650

DEFAULT_SEED = 0
