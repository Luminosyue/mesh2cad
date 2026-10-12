# P1 VAL1000 Qualitative Visualization V1

CURRENT_GATE = COMPLETE

TEST_TOUCHED = NO

## Selection
- OPERATION_RESCUE = 4
- STEP_RESCUE = 3
- GENERATION_RESCUE = 3
- GEOMETRY_RESCUE = 4
- P1_OUTLIER = 3
- PLACEMENT_FAILURE = 3
- CUT_UNION_LIMITATION = 3

## Visual protocol
- All geometry is re-tessellated from STEP with identical per-case tolerance.
- One GT-derived center and scale is shared across GT/A1/A3/P1.
- Camera, orthographic projection, zoom, clipping, and resolution are shared.
- Per-model auto-fit/recenter/rescale are disabled.

## Interpretation
- P1 visual strength: operation, STEP/execution, generation-completeness, and selected H95 rescue
- Failure pattern: local parameter, origin/translation, direction, scale/extent; Cut/Union regressions where available

## Integrity
- TEST_CASE_USED_N = 0
- PREDICTIONS_CHANGED = NO
- MODEL_CHANGED = NO
- EVALUATOR_CHANGED = NO
