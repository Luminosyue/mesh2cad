# COMPLEXITY_AWARE_COMPACT_CAD_V1

Gate: `COMPLEXITY_AWARE_COMPACT_CAD_V1_PASS`

## Method

True TopoDS face adjacency and edge semantics feed SurfaceCandidates. OCC UnifySameDomain is retained as a baseline. The successful branch reconstructs from frozen measured section programs: global non-ruled refit for CASE_04/09 and complexity-aware section selection for CASE_05. No source mesh, baseline STEP, P3, PhysX, or MAC artifact was modified.

Complexity weights are fixed and interpretable: face=.35, edge=.25, patch=.20, control points=.15, degree=.05. Invalid, Q3, and topology-regressed candidates are filtered before complexity ranking.

CASE_05 main selection is the 7-section-per-component Q1 candidate; the 5-section Q2 candidate is retained as MOST_COMPACT_VALID but not selected because its Coverage02 is below the stricter CASE_05 success floor of 0.95.

## Verification

- Tests passed: 19
- Tests failed: 0
- Visual QA: PASS
