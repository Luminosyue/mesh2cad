# TARGET 5iHumo Geometry Decomposition and Backend Failure Audit V1

TARGET_OBJ=/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj
TARGET_OBJ_SHA256=f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61
CURRENT_GATE=TARGET_5iHumo_GEOMETRY_DECOMPOSITION_AND_BACKEND_FAILURE_AUDIT_V1_PASS

## Core Finding

The current CAD Part Graph is effectively the P3 segment graph: `True`.
First divergence stage: `CAD_PART_DECOMPOSITION_MISSING`.
Primary blocker: `CAD_PART_DECOMPOSITION_MISSING`.

## Counts

- P3 segments / CAD parts: `12` / `12`
- One-to-one P3 to CAD Part: `12`
- Split recommended parts: `5`
- Analytic missed opportunities: `6`
- V6 input decomposition failures: `10`
- V6 algorithm failures: `1`
- QA false accepts: `5`

## Required Answers

1. P3 segments are effectively used 1:1 as CAD Parts when p3_to_cadpart_relation.csv shows ONE_TO_ONE for nearly all parts.
2. Mixed geometry and decomposition-missing evidence appear before backend fitting, so the next first-order fix should be Generic Geometry Decomposition, not MAC or lower QA thresholds.
3. V6 failures are split between unsuitable mixed inputs and true fitting/topology failures; selected loop-like edge suspects are real BRep/geometry candidates, not only tessellation debug.

## Final Required Answers

1. P3 12 / CAD 12 does mean the CAD Part Graph is effectively P3 1:1 here: `True` with `12` one-to-one rows and no split/fusion operations.
2. Significant multi-component CAD Parts: `3`.
3. Mixed geometry parts: `5`; split recommended parts: `5`.
4. Fusion recommendations: `0`.
5. CADPART_000 recommendation: `FIX_QA_FALSE_ACCEPT`; audit did not find a strong repeated-post group for it in this run.
6. CADPART_001 / CADPART_006 recommendations: `FIX_QA_FALSE_ACCEPT` / `FIX_QA_FALSE_ACCEPT`; both have linear or analytic opportunity evidence, but selected results are flagged by QA.
7. CADPART_004 recommendation: `FIX_QA_FALSE_ACCEPT`; its V6 issue is attributed to decomposition-unfriendly mixed/multi-component input with loop-like/BBox abnormality evidence.
8. CADPART_008 recommendation: `FIX_ANALYTIC_CLASSIFIER`; it is a planar analytic missed opportunity rather than a reason to run MAC.
9. CADPART_009 recommendation: `FIX_QA_FALSE_ACCEPT`; it has planar analytic opportunity evidence and selected-candidate QA risk.
10. Current Analytic generated candidates for `12` parts, selected `0`, and failed fidelity on `12`.
11. Analytic missed opportunities: `6`.
12. V6 input decomposition failures / algorithm failures: `10` / `1`.
13. QA false accept suspects: `5`; reload-valid alone is too permissive for this run.
14. Generic Geometry Decomposition is needed: `True`.
15. Directly tuning V6 next is recommended only if V6 algorithm failures dominate; here they do not, so the answer is `NO`.
16. Running MAC next: `NO`.
17. Lowering fidelity threshold next: `NO`.
18. Primary blocker: `CAD_PART_DECOMPOSITION_MISSING`.
19. First-order fix: implement a generic geometry decomposition layer before routing analytic/V6 backends.
