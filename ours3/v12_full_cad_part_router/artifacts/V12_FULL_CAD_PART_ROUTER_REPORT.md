# V12 Full CAD Part Router Report

CURRENT_GATE=V12_FULL_CAD_PART_ROUTER_PASS

## Metrics

CURRENT_GATE=V12_FULL_CAD_PART_ROUTER_PASS
V12_PASS=True
FULL_CAD_PART_ROUTER_IMPLEMENTED=True
CASES_ROUTED=3
PARTS_TOTAL=42
PARTS_WITH_TERMINAL_STATUS=42
ALL_CASES_PART_ROUTE_COVERAGE=1.0
CASE09_PARTS_TOTAL=8
CASE09_PARTS_ROUTED=8
CASE09_PART_ROUTE_COVERAGE=1.0
TANK_PARTS_TOTAL=13
TANK_PARTS_ROUTED=13
TANK_PART_ROUTE_COVERAGE=1.0
BUILDING_PARTS_TOTAL=21
BUILDING_PARTS_ROUTED=21
BUILDING_PART_ROUTE_COVERAGE=1.0
PARTS_WITH_FRESH_BREP=36
FRESH_BREP_COVERAGE=0.8571428571428571
SUCCESS_HIGH_FIDELITY_COUNT=2
SUCCESS_ACCEPTABLE_COUNT=8
SAFE_BUT_LOW_FIDELITY_COUNT=13
NO_HIGH_FIDELITY_BUILDER_COUNT=0
NO_EXECUTABLE_PLAN_COUNT=0
UNSUPPORTED_FEATURE_COUNT=0
GEOMETRY_EVIDENCE_INSUFFICIENT_COUNT=5
SEMANTIC_UNCERTAIN_COUNT=1
BUILDER_REJECTED_COUNT=0
QA_REJECTED_COUNT=13
EXECUTION_FAILED_COUNT=0
QWEN_CANDIDATE_COUNT=39
MAC_CANDIDATE_COUNT=0
GEOMETRY_CANDIDATE_COUNT=107
CANDIDATES_TOTAL=146
CANDIDATES_EXECUTABLE=146
CANDIDATES_EXECUTION_SUCCESS=70
CANDIDATES_HIGH_FIDELITY=2
CANDIDATES_SAFE_LOW_FIDELITY=13
REAL_QWEN_CALLS=48
REAL_QWEN_EXECUTABLE_PLAN_COUNT=39
REAL_MAC_CALLS=1
MAC_EXTERNAL_RESOURCE_FAILURE=True
MAC_PROVIDER_AVAILABLE=False
MAC_SKIPPED_DUE_TO_PROVIDER_FAILURE_COUNT=42
PLANE_SELECTED_COUNT=3
EXTRUSION_SELECTED_COUNT=24
CYLINDER_SELECTED_COUNT=7
REVOLUTION_SELECTED_COUNT=0
LOFT_SELECTED_COUNT=1
SWEEP_SELECTED_COUNT=0
BSPLINE_SELECTED_COUNT=0
OPEN_SHELL_SELECTED_COUNT=1
TANK_ROAD_WHEEL_CYLINDER_GEOMETRY_SUPPORTED_COUNT=0
TANK_ROAD_WHEEL_REVOLUTION_GEOMETRY_SUPPORTED_COUNT=0
TANK_ROAD_WHEEL_HIGH_FIDELITY_COUNT=0
TANK_GUN_BARREL_SELECTED_BUILDER=NONE
TANK_GUN_BARREL_STATUS=NO_HIGH_FIDELITY_BUILDER:PART_GRAPH_TOO_COARSE
TANK_HULL_STATUS=SAFE_BUT_LOW_FIDELITY
TANK_TRACK_HIGH_FIDELITY_COUNT=0
CASE09_MAIN_WING_STATUS=SUCCESS_HIGH_FIDELITY
CASE09_MAIN_WING_SELECTED_BUILDER=LOFT
CASE09_MAIN_WING_SILHOUETTE_IOU=0.8779582157983441
CASE09_MAIN_WING_SECTION_PROFILE_ERROR=0.060604815548632375
BBOX_PROXY_RECONSTRUCTION_COUNT=3
CIRCULAR_FEATURE_FIDELITY_PASS_COUNT=0
PATTERN_FIDELITY_PASS_COUNT=0
SILHOUETTE_IOU_MEAN=0.4521158592002393
SECTION_PROFILE_ERROR_MEAN=0.7651338744896362
PATTERN_PROTOTYPE_REUSE_COUNT=0
INVALID_BUILDER_EXECUTED_COUNT=0
LOFT_INVALID_EXECUTED_COUNT=0
BSPLINE_INVALID_EXECUTED_COUNT=0
EXECUTED_PARAMETER_WITHOUT_REF_COUNT=0
UNMEASURED_PATTERN_PLACEMENT_COUNT=0
DIRECT_PLAN_TO_OCC_BYPASS_COUNT=0
RUNTIME_REMEASUREMENT_COUNT=0
HISTORICAL_STEP_REUSE_COUNT=0
GEOMETRY_EXPLOSION_COUNT=0
PART_STATUS_SCHEMA_USED=True
CANDIDATE_ORCHESTRATOR_USED=True
FIDELITY_AWARE_TTS_USED=True
BUILDER_ELIGIBILITY_CHANGED_BY_SEMANTICS_COUNT=0
HISTORICAL_ARTIFACT_INDEPENDENCE_PASS=True
ASSEMBLY_READY_CASE_COUNT=3
OPEN_SHELL_FRESH_BREP_COUNT=1
OPEN_SHELL_SHARED_OCC_EDGE_COUNT=1
OPEN_SHELL_PCURVE_COUNT=2
OPEN_SHELL_TRIMMED_FACE_COUNT=2
V10_REGRESSION_PASS=True
V11_REGRESSION_PASS=True
V11B_REGRESSION_PASS=True
V11C_REGRESSION_PASS=True
V7D3_REGRESSION_PASS=True
PART_ROUTE_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_part_route_summary.csv
CANDIDATE_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_candidate_summary.csv
BUILDER_COVERAGE_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_builder_coverage.csv
BLOCKER_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_blocker_summary.csv
FIDELITY_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_fidelity_summary.csv
DEBUG_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/v12_source_vs_selected_contact_sheet.png
REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router/artifacts/V12_FULL_CAD_PART_ROUTER_REPORT.md
TESTS_PASSED=0
TESTS_FAILED=0
V13_ENTRY_READY=True
RUN_SECONDS=344.4496719837189

## Required answers

1. YES. FullCADPartRouter traversed all frozen CAD Parts in all three representative whole objects.
2. YES. Every one of 42 parts has a formal terminal status.
3. YES. Routing coverage is 1.000; this includes explained blockers and is not success coverage.
4. Fresh BRep coverage is 0.857, kept separate from routing coverage.
5. SUCCESS_HIGH_FIDELITY parts: 2.
6. SAFE_BUT_LOW_FIDELITY parts: 13.
7. NO_HIGH_FIDELITY_BUILDER parts: 0.
8. V11C did not enable wheel Cylinder/Revolution because the frozen V10 eligibility exposed only PLANE/EXTRUSION for those segments.
9. V12 measured audit shows geometry-evidence insufficiency, not a safe eligibility coverage fix: all three wheel candidates fail the circular residual/radial consistency thresholds.
10. NO. Safely upgraded road-wheel count is 0; no cylinder is fabricated.
11. YES. The router retains an evidence-based GEOMETRY_EVIDENCE_INSUFFICIENT/NO_HIGH_FIDELITY status instead of rectangular wheel CAD.
12. Track blocker is missing measured closed-path and cross-section evidence; Sweep runtime is therefore not activated.
13. YES. CASE09 main wing remains LOFT with silhouette IoU=0.877958.
14. YES. Vertical-tail OpenShell is freshly executed through the V11B registry path and retains shared topology/pcurves/trimmed faces.
15. NO historical selected STEP is used for any final Part.
16. NO runtime remeasurement is used to fill plan parameters; the router consumes hash-checked frozen evidence. Post-build QA and the versioned wheel audit are explicit measurements, not parameter fallbacks.
17. NO. PhysX/Qwen/MAC never changes V10 eligibility; only geometry evidence can qualify a targeted coverage fix.
18. NO invalid Builder is executed for coverage.
19. YES. The formal schema distinguishes high fidelity, safe low fidelity, missing builder, unsupported feature, and insufficient evidence.
20. YES. V13 entry requires all routes terminal and every successful part to have a fresh BRep plus transform metadata.

## Interpretation

V12 PASS means complete, explicit routing coverage. It does not mean every part has a high-fidelity BRep. No historical selected STEP, raw mesh-to-STEP wrapper, semantic eligibility override, or arbitrary track/wheel extrusion is accepted.
## Final validation

CURRENT_GATE=V12_FULL_CAD_PART_ROUTER_PASS

TESTS_PASSED=31

TESTS_FAILED=0
