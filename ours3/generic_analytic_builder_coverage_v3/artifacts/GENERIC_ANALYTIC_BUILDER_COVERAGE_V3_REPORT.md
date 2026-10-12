# GENERIC ANALYTIC BUILDER COVERAGE V3

CURRENT_GATE=GENERIC_ANALYTIC_BUILDER_COVERAGE_V3_FAIL
V6_ELIGIBLE=5
V6_SELECTED=0
NEXT_PRIMARY_BLOCKER=PARAMETER_FITTING

## Policy

- V2 refined meshes are read-only inputs.
- P3 and PhysX were not rerun.
- Every candidate is a real OCC analytic construction; no mesh-to-STEP proxy is used.
- QA thresholds are inherited from V2 and were not widened.

## Diagnosis

- V6 eligible parts diagnosed: `5`.
- Local frame success: `5`.
- Candidates created: `21`.
- OCC-valid candidates: `21`.
- V6 selected: `0`.
- Best diagnostic candidate: `CADPART_008_PLANAR_PATCH_e47f854e09__V6_GEOMETRY`.
- Best diagnostic Chamfer / Hausdorff: `0.02722590147215699` / `0.26159573119281826`.
- Best diagnostic FP occupancy / coverage: `0.5251727541954591` / `0.9622210753741591`.
- OCC-invalid candidates: `4`.
- Geometry-QA failures: `21`.
- Tests passed / failed: `17` / `0`.
- Next primary blocker: `PARAMETER_FITTING`.
