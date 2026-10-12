# Task B — CASE06/CASE07 Part Discovery Rescue

Status: **PASS**. Frozen source OBJ files were resolved from `/data/home/cuiyuehan/project/mesh2cad/ours3/batch_real_mesh2cad_v1/manifest/batch_10_case_manifest.json` and their SHA-256 hashes were verified. Existing P3 triangle maps and PhysX outputs were reused; no GPU inference ran and no STEP was used as segmentation input.

## CASE06

P3 already partitions all 310960 triangles into 2 source-aligned connected parts, matching both the two source connected components and the two-part PhysX prior. The rescued part graph covers 1.000000 of source area with zero overlap and zero unassigned area. The old pipeline produced no accepted CAD because both parts were classified `C_FREEFORM_DOMINANT` and no part was routed for reconstruction. Primary cause: **PART_CADABILITY_FAILURE**, not segmentation or PhysX failure.

## CASE07

P3 already assigns all 274684 triangles across 30 segments. The rescued graph retains every source-area assignment and reaches 1.000000 coverage, versus old accepted-CAD coverage 0.099514. The old graph marked 27 nodes ready but its `MAX_READY_PARTS_PER_OBJECT=6` cap forwarded only six; five accepted small parts accounted for roughly 10% of area and the remainder was not requeued as residual. Primary cause: **ROUTER_FAILURE / AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION**.

Residual catalogs are defined against old accepted P3 part IDs, never STEP geometry. They include connected source-mesh regions, exact areas, P3 memberships, geometry-continuity notes, and split/merge hypotheses. The new graph itself has zero unassigned area.

No Loft, BSpline reconstruction, MAC, LLM, CAD/STEP generation, shared-code edit, CASE09 edit, or P3/PhysX rerun occurred.

Tests: 17 passed, 0 failed.
