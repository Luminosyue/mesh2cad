# TANK V4 FROZEN GENERALIZATION V1 REPORT

## Direct answers

1. V4 direct generalization: `TANK_V4_FROZEN_GENERALIZATION_V1_GEOMETRY_FAIL`. Frozen V4 selected `0/6` parts and STEP reload is `False`.
2. Successful CAD parts: `NONE`.
3. Failed parts: `CADPART_000:FP_OCCUPANCY_FAIL, CADPART_001:FP_OCCUPANCY_FAIL, CADPART_002:FP_OCCUPANCY_FAIL, CADPART_003:FP_OCCUPANCY_FAIL, CADPART_004:FP_OCCUPANCY_FAIL, CADPART_005:FP_OCCUPANCY_FAIL`.
4. Next module to fix: `GEOMETRY_QA_FAIL`.

## Freeze audit

- V4 core modules were imported from `generalization/topology_aware_routing_trimmed_surface_fidelity_v4` without editing them.
- P3, PhysX, and CAD Part Graph were freshly re-executed on the tank OBJ.
- SuperFit was not used.
- PhysX global semantics misidentified the object as Furniture/Armchair; per-part semantic priors were left UNKNOWN rather than manually corrected.

## Final status

CURRENT_GATE=TANK_V4_FROZEN_GENERALIZATION_V1_GEOMETRY_FAIL
INPUT_OBJ=/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj
INPUT_SHA256=fe012b4ce1cb1262e1b82651b4e3ae0845437cf4d54f45808be21bc0603da3b2
V4_CODE_FROZEN=True
V4_QA_THRESHOLDS_UNCHANGED=True
P3_REEXECUTED=True
PHYSX_REEXECUTED=True
SUPERFIT_USED=False
INPUT_TRIANGLES=367466
P3_SEGMENT_COUNT=6
P3_TRIANGLE_COVERAGE=1.0
CAD_PART_COUNT=6
REFINED_PART_COUNT=6
STRUCTURAL_SPLIT_COUNT=0
TOPOLOGY_VOLUMETRIC_COUNT=0
TOPOLOGY_THIN_SHEET_COUNT=4
TOPOLOGY_OPEN_SURFACE_COUNT=0
TOPOLOGY_MULTI_PATCH_COUNT=2
TOPOLOGY_UNKNOWN_COUNT=0
REVOLUTION_HARD_REJECT_COUNT=6
BOX_PRISM_HARD_REJECT_COUNT=6
EXTRUSION_HARD_REJECT_COUNT=6
TRIMMED_FACE_ATTEMPTS=0
TRIMMED_FACE_SUCCESS=0
OUTER_LOOPS_RECOVERED=6
INNER_LOOPS_RECOVERED=48
NEGATIVE_SPACE_REGIONS_RECOVERED=0
TOTAL_CANDIDATES=6
OCC_VALID_CANDIDATES=6
GEOMETRY_QA_PASS_COUNT=0
PARTS_SELECTED=0
PARTS_UNRESOLVED=6
PART_SELECTION_RATE=0.0
QA_PASS_TRIANGLE_COVERAGE=0.0
BEST_CHAMFER=0.03216110650711423
BEST_HAUSDORFF=0.17145138732247206
BEST_COVERAGE=0.8926081730769231
BEST_FP_OCCUPANCY=0.369022869022869
PLANAR_FACE_QA_PASS=0
PROFILE_EXTRUSION_QA_PASS=0
REVOLUTION_QA_PASS=0
RULED_SURFACE_QA_PASS=0
LOFT_SURFACE_QA_PASS=0
BSPLINE_SURFACE_QA_PASS=0
BOOLEAN_QA_PASS=0
FINAL_STEP_PATH=None
FINAL_STEP_RELOAD=False
FINAL_STEP_OCC_VALID=False
TESTS_PASSED=0
TESTS_FAILED=1
PRIMARY_GENERALIZATION_BLOCKER=GEOMETRY_QA_FAIL
NEXT_PRIMARY_BLOCKER=GEOMETRY_QA_FAIL
BLOCKERS=["NO_SELECTED_V4_CANDIDATE"]

## Artifact index
- input audit: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_v4_frozen_generalization_v1/artifacts/input_audit.json`
- per-part table: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_v4_frozen_generalization_v1/artifacts/tank_part_generalization.csv`
- all candidates: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_v4_frozen_generalization_v1/artifacts/tank_all_candidates_contact_sheet.png`
- QA pass only: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_v4_frozen_generalization_v1/artifacts/tank_qa_pass_parts_contact_sheet.png`
- source vs best CAD: `/data/home/cuiyuehan/project/mesh2cad/ours3/tank_v4_frozen_generalization_v1/artifacts/tank_source_vs_best_cad_contact_sheet.png`
- final STEP: `None`
