# Batch9 MAC Resume V6.1

## Result

`BATCH9_MAC_RESUME_V6_1_FAIL`

The first CASE01 canary reached the endpoint but the text MAC request returned HTTP 403 `AllocationQuota.FreeTierOnly`. The resume stopped before CASE04/CASE07 canaries and before the 393-candidate batch.

The visual-context call consumed the canonical OBJ and rendered image successfully. The text MAC request included measured CAD spec, semantic surface graph, CAD feature graph, design hypothesis, canonical OBJ context, and rendered visual analysis, but no successful MAC candidate was returned.

The reused `mac.call` helper made three finite attempts before surfacing the 403. Accounting records one successful visual-context call plus three failed text-MAC attempts.

No fallback batch was started. No existing candidate, STEP, assembly, upstream artifact, or CASE09 result was modified.

## Reuse

- P3 cases reused: 9; rerun: none.
- PhysX cases reused: 9; rerun: none.
- Semantic artifacts reused: 132.
- Dual-modal artifacts reused: 132.
- Historical STEP used as reconstruction input: false.

## Accounting

- Real MAC candidates before/after: 3/3.
- Candidates still blocked: 393.
- Quota fallback candidates replaced: 0.
- New real MAC programs executed: 0.
- TTS actually used for this resume: false.

Canary evidence: `/data/home/cuiyuehan/project/mesh2cad/ours3/batch9_mac_resume_v6_1/artifacts/canary_summary.json`
Summary: `/data/home/cuiyuehan/project/mesh2cad/ours3/batch9_mac_resume_v6_1/artifacts/final_summary.json`
