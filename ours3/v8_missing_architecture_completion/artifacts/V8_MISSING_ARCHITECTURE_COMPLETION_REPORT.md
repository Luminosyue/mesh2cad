# V8 Missing Architecture Completion — Audit-first Report

## Outcome

This run produced a fresh, valid **main-wing experimental STEP** and real dependency evidence for Steps 5, 6, 7, 13, and 17. It did not complete the full eight-type primitive bank, fuselage/vertical-tail construction experiments, generic feature graph, or MAC repair. No historical STEP or fallback result was used.

## Sequential gates

V8A=PARTIAL, V8B=PARTIAL, V8C=PARTIAL, V8D=PARTIAL, V8E=PARTIAL, V8F=PARTIAL. Later gates are not marked PASS because V8A is not fully complete. Step 13 is nevertheless independently FULLY_OPERATIONAL as a scoped module.

## Quantitative evidence

- Fresh STEP: `/data/home/cuiyuehan/project/mesh2cad/ours3/v8_missing_architecture_completion/19_final/CASE09_v8_main_wing_fresh.step`
- STEP SHA256: `bf7ce0ed81c1e086ba4eb61186e46982d50b7f277970fc13e214288cc7909053`
- OCC readback valid: `True`
- Shared OCC edges: 12 / expected 12
- Pcurves: 24; mean/p95 consistency error 7.29659e-17 / 1.50871e-16
- Optimizer: 20 executed-BRep objective evaluations; two parameters changed
- Chamfer: 0.016587224 -> 0.014875077
- Hausdorff p99: 0.070759319 -> 0.038569877
- Grounding: 1 FACE and 2 EDGE queries resolved; ambiguous query unresolved
- MAC: request sent, provider response not received, blocker `MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403`

## Required answers

1. Step 5: PARTIAL. It is not merely a builder-name wrapper: PLANE fitting uses real extreme-quantile mesh samples, SVD parameters, residual metrics and a BRep perturbation test. But CYLINDER/REVOLUTION/EXTRUSION/SWEEP/LOFT/PERIODIC_BSPLINE/GENERAL_BSPLINE are not real fitters yet, so the bank is not complete.
2. Step 6: PARTIAL. The main-wing graph contains 8 typed loop vertices and 12 design boundaries derived from fitted-plane intersections; mesh-triangle imports and profile-sample design-edge imports are both zero. Other part families are untested.
3. Step 7: PARTIAL overall, operational for the planar main-wing experiment. It reuses 12 OCC edges across six faces, verifies 24 pcurves, builds six closed trimmed faces, and reads back a valid solid. pcurve mean/p95 3D errors are 7.29659e-17 / 1.50871e-16.
4. No. The V8 main-wing STEP edges come from intersections of fitted design planes, not section-sampling segments. Section profiles are retained as measured constraints in Step 9 only.
5. Yes for the scoped optimizer. Construction family, builder, feature sequence and topology graph stay fixed. Two offsets are optimized against freshly executed BReps; composite improves 0.270739088 -> 0.262589052 and a shifted source changes the optimum. Step 13 is FULLY_OPERATIONAL as a module.
6. Step 17 returns real OCC Face/Edge fingerprints for main-wing upper/leading/trailing queries and returns UNRESOLVED for an ambiguous fillet query. It is not nearest-only. It remains PARTIAL because descriptors do not yet include orientation, adjacency, or feature membership.
7. No completed MAC repair occurred. A real grounded leading-edge ID was sent in a local-only MAC request, but DashScope returned 403 free-tier quota exhausted. The system executed zero repair attempts and did not substitute deterministic regeneration.
8. Steps 4, 8 and 9 all remain PARTIAL: Step 4 is wing-specific; Step 8 lacks general executable feature detectors; Step 9 now aggregates dimensions, profiles, primitives, wireframe and feature fields but inherits the partial feature graph and is tested only on the main wing.
9. PhysX remains OPTIONAL_SEMANTIC_PRIOR. No dependency proves that it changes BRep construction.
10. CAD Part Graph remains PARTIAL: flat/identity placements and no demonstrated automatic merge dependency.
11. Only Step 13 qualifies as FULLY_OPERATIONAL at module level. Steps 5/6/7/17 made real scoped progress but remain PARTIAL; Step 18 is provider-blocked. Sequential V8A-V8F gates are therefore all PARTIAL.
12. Dependency evidence: Step 5 plane perturb changed STEP SHA; Step 6 boundary removal caused an invalid-trim failure; Step 7 intersection-plane perturb changed trimmed BRep SHA; Step 13 optimization changed executed BRep and shifted-source optimum; Step 17 leading/trailing queries changed OCC fingerprints. Step 18 failed because no provider response/local patch existed.

## Scope caveat

The fresh STEP is the CASE09 MAIN_WING V8 architecture experiment, not a complete CASE09 aircraft assembly. FUSELAGE and VERTICAL_TAIL contributed source-derived plane evidence only; their required loft/BSpline/open/freeform topology experiments remain blockers.

## Test summary

TESTS_PASSED=45

TESTS_FAILED=0
