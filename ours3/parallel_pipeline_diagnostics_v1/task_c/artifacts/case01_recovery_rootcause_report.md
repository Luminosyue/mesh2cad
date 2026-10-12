# CASE01_RECOVERY_ROOTCAUSE_V1

Gate: `CASE01_RECOVERY_ROOTCAUSE_V1_PASS`

## Finding

Primary enum: `OTHER`

Detail: `STALE_CANDIDATE_A_FAILURE_SENTINEL_SKIPPED_VALID_B_AND_C_QA_SELECTION`

CASE01's recorded failure is primarily a control-flow/resume defect, not a geometry-wide failure. `batch_pipeline.py:146-149` treats the mere existence of candidate A STEP as a terminal failure sentinel and executes `continue`, bypassing the normal QA/ranking path. Fresh independent QA shows the already-existing ruled B and primitive C candidates are both valid Q1.

## Fresh candidate evidence

- `candidate_A_loft`: valid=True; faces=66; Q=Q3; Chamfer=877.806255294; P95=2851.113984090; Coverage@2%=0.000000; mapped/source diag ratio=10046.341872.
- `candidate_B_loft`: valid=True; faces=3522; Q=Q1; Chamfer=0.002764263; P95=0.005369534; Coverage@2%=1.000000; mapped/source diag ratio=0.999464.
- `candidate_C_primitive`: valid=True; faces=6; Q=Q1; Chamfer=0.006343335; P95=0.010404530; Coverage@2%=1.000000; mapped/source diag ratio=1.003955.

## Cause separation

- Resource event: true; the historical smooth-loft retessellation timeout is evidenced.
- Geometry failure: true but limited to A; A's valid BSpline BRep explodes to ~10,046x source diagonal.
- `RESOURCE_TIMEOUT_ONLY`: rejected because A can now be retessellated and Q1 B/C were already present but skipped.
- `TRANSFORM_FAILURE`: rejected because the same finite inverse-consistent transform maps B/C to source scale.
- Section-order/twist failure: rejected; z is monotonic, orientation changes=0, self-intersecting profiles=0, large shifts=0, reversals=0.

## Secondary causes

- `SURFACE_FIT_FAILURE`: smooth A is numerically pathological while ruled B from identical sections is Q1.
- `BRep_VALID_BUT_GEOMETRY_Q3`: A is topologically valid yet geometrically catastrophic.

## Rescue plans — not executed

- Route A `COMPLETE_EXISTING_CANDIDATE_RANKING`: resume candidate inventory and normal QA/ranking; select existing B when it remains Q1.
- Route B `STABILIZE_SMOOTH_LOFT_THEN_FALL_BACK_TO_RULED`: guard smooth-loft bounds/poles, remove degenerate end profiles, and fall through to ruled B on A failure.

No reconstruction, MAC/LLM call, unrestricted ICP, CASE09 work, shared-code edit, or input STEP overwrite was performed.
