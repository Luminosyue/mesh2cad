# PARALLEL_PIPELINE_DIAGNOSTICS_V1

Gate: `PARALLEL_PIPELINE_DIAGNOSTICS_V1_PASS`

## Isolation

The diagnostic wrote only under `/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1`. It changed no shared code and generated no STEP. The separately running CASE09 task changed its own source/output during the observation window; this is explicitly recorded as concurrent external activity, not attributed to this diagnostic. CASE09 headline structure metrics are point-in-time because the live final changed from 137 to 92 faces between two read-only audit runs, although the selected 92-face file was stable during the final audit window.

## CAD structure audit

Six cases and fourteen unique STEP artifacts were fresh reloaded. CASE03 is a true analytic 6-plane BRep. CASE02/04/05/08 are fragmented spline BReps at their latest stable selected versions. CASE04 V1 is compact but spline-derived; its V2 has more feature-preserving faces yet remains a 322-patch spline BRep, so it is not mislabeled as structured. The CASE09 point-in-time final has 92 faces, 0.347826 BSpline ratio, 86 surface groups, and remains structurally UNKNOWN.

## CASE06 and CASE07 part discovery

Existing P3 and PhysX evidence was reused without inference. CASE06 source area is fully represented by two P3 segments, but both were C_FREEFORM/ready=0, so the old zero-accept result is a PART_CADABILITY_FAILURE. CASE07 has 30 P3 segments; three disconnected segments split into 33 graph parts. Coverage rises from 0.099514 to 1.0 at Part Graph scope. The old assembly omitted 90.0486% of source area because an area-unaware ready-part cap retained only a small subset, classified as ROUTER_FAILURE.

## CASE01 root cause

All three existing candidate STEP files fresh reload and are BRep valid. Candidate A smooth loft is Q3 and grossly mis-scaled after the frozen transform; candidates B ruled loft and C primitive are both Q1. The primary cause is OTHER: a stale candidate-A failure sentinel caused the old control flow to continue before QA/ranking valid B and C. Resource timeout and A-only geometry failure both occurred, but RESOURCE_TIMEOUT_ONLY is rejected. No rebuild was executed.

## Prohibitions

No shared pipeline edits, MAC, LLM API, P3/PhysX rerun, GPU use, unrestricted ICP, Loft/BSpline generation, STEP generation, or 10-case batch was performed.

## Verification

49 subtask tests plus 53 integration tests passed; 0 failed.
