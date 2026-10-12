# Stage 1 Gate Report

Baseline: /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_val1000_baseline_v1

## Provenance and environment
- Official repository commit: fb31f63b79805fff4c5a5c6fa5f8b2f00fe86536.
- Existing dirty repository status was preserved in provenance/CADFIT_GIT_STATUS.
- Independent cadfit-env imports passed for cadquery, numpy, trimesh, scipy, and torch.

## Alignment
- CADFIT_TARGET_N=1000
- CADFIT_UNIQUE_TARGET_IDS=1000
- P1_CADFIT_INTERSECTION_N=1000
- CAD_RECODE_CADFIT_INTERSECTION_N=1000
- CADFIT_ONLY_N=0
- P1_ONLY_N=0

## Input compatibility
- 253 source STL paths were found for the frozen VAL1000 IDs.
- 747 source mesh paths could not be located in existing dataset artifacts.
- All 253 available STL meshes were reported non-watertight by trimesh.
- No repair, remesh, smoothing, rescale, recenter, or denominator removal was performed.
- VAL5 and Canary20 were not started because the frozen VAL1000 input set cannot currently be materialized under the required protocol.

## Gate
OFFICIAL_SMOKE=PASS
VAL5_SMOKE=BLOCKED_INPUT_COMPATIBILITY
CANARY20=BLOCKED_INPUT_COMPATIBILITY
CURRENT_GATE=CADFIT_VAL1000_INPUT_COMPATIBILITY_BLOCKED
NEXT_ALLOWED_STAGE=RECOVER_OR_IDENTIFY_FROZEN_VAL1000_SOURCE_MESHES
FULL_VAL1000_STARTED=NO
