# PART_TO_CAD_RECOVERY_FIX_V1

Status: **PART_TO_CAD_RECOVERY_FIX_V1_PASS**.

CASE01 finalized `candidate_B_loft` because it is Q1 and passes the feature guard (sharp/feature recall 1.0). The compact primitive is also Q1 geometrically but loses the source feature boundaries, so the frozen feature-first selection order correctly rejects it. The old stale Candidate-A failure sentinel is no longer allowed to bypass valid earlier candidates.

CASE06 routes both frozen part-graph nodes through all five backend slots and accepts 2/2 Q1 surface BReps, reaching area coverage 1.000000. CASE07 routes all 33 nodes (not only READY/capped nodes), accepts 33/33 Q1 surface BReps, and raises area coverage from 0.09951411358890397 to 1.000000.

Representation semantics: all 35 rescued parts selected the source-aware S1 surface-BRep backend, even though their frozen geometry metrics are Q1. This means high sampled geometric fidelity, not compact parametric reconstruction. Programmatic boxes/cylinders and two-region hybrid candidates were retained with QA; unsupported global NURBS fitting was recorded as an explicit failure instead of manufacturing strip lofts. V1/V2 ran per part only.

MAC was locally configured and the service endpoint was reachable, but the official graph received HTTP 403 `Free quota exhausted` before a token-bearing completion. Therefore MAC was not used for accepted geometry; deterministic fallback remained authorized. No raw mesh was supplied to MAC.

Fresh XCAF checks: CASE06 valid=True components=2; CASE07 valid=True components=33. No P3, PhysX, CASE09, shared code, global assembly refit, or unrestricted ICP was used.
