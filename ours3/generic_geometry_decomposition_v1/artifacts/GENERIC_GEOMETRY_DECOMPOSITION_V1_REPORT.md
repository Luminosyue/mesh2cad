# GENERIC GEOMETRY DECOMPOSITION V1 REPORT

CURRENT_GATE=GENERIC_GEOMETRY_DECOMPOSITION_V1_PASS
PASS=True
TARGET_OBJ=/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj
TARGET_SHA256=f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61

## Summary

- Coarse P3/CAD: `12` / `12`
- Refined CAD parts: `15`
- Actual split/fusion: `3` / `0`
- Mixed sent directly to V6: `0`
- QA false accepts accepted: `0`
- Final STEP reload valid: `True`

## Required Answers

1. The old 12 P3 segments -> 12 CAD Parts relation was broken: `True`.
2. Refined CAD Part count: `15`.
3. Split/fusion counts: `3` / `0`.
4. Mixed geometry direct to V6: `0`.
5. CADPART_000 repetition detected: `False`; freeform keep: `True`; diagnostic fail: `True`. The generic connected-component/regime detector did not recover rail/post-level regions, so this is an under-decomposition finding, not a semantic hardcode.
6. CADPART_004 old loop avoided by decomposition/QA: `True`.
7. CADPART_008 body/rod split: `False`; mixed direct V6: `False`. The current detector kept it as one planar region, so it remains a next-round under-decomposition target.
8. CADPART_009 analytic opportunity recovered: `True`.
9. Current analytic selected coarse/refined: `0` / `14`.
10. Analytic missed opportunity baseline/V2: `6` / `0`.
11. V6 decomposition failure baseline/V2: `10` / `0`.
12. QA does not accept reload-valid but exploding/out-of-support/loop-like candidates.
13. Case-specific 5iHumo hardcode: `NO`; modules operate on connectivity, normals, PCA, scale, support, and repetition.
14. Geometry fidelity improved: `True`.
15. NEXT_PRIMARY_BLOCKER=`UNDER_DECOMPOSITION`.
16. Run MAC next: `NO`.
