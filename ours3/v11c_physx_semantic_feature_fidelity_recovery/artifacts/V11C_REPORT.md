# V11C PhysX Semantic Feature Fidelity Recovery

CURRENT_GATE=V11C_PHYSX_SEMANTIC_FEATURE_FIDELITY_RECOVERY_PASS

## Summary

CURRENT_GATE=V11C_PHYSX_SEMANTIC_FEATURE_FIDELITY_RECOVERY_PASS
V11C_PASS=True
PARTS_ANALYZED=42
PHYSX_SEMANTIC_FEATURE_PRIOR_IMPLEMENTED=True
GLOBAL_OBJECT_SEMANTIC_CONTEXT_USED=True
SEMANTIC_FEATURE_GRAPH_IMPLEMENTED=True
PART_RELATION_GRAPH_IMPLEMENTED=True
PATTERN_RECOVERY_IMPLEMENTED=True
CAD_CONSTRUCTION_PRIOR_IMPLEMENTED=True
FIDELITY_AWARE_RANKING_USED=True
FIDELITY_QA_IMPLEMENTED=True
BBOX_PROXY_DETECTOR_IMPLEMENTED=True
PHYSX_SEMANTIC_PRIOR_USED_COUNT=8
PHYSX_ROLE_GEOMETRY_CONFLICT_COUNT=2
SEMANTIC_ROLE_ACCEPTED_COUNT=41
UNKNOWN_ROLE_COUNT=1
PART_RELATION_COUNT=67
PATTERN_GROUP_COUNT=5
SYMMETRY_GROUP_COUNT=2
BUILDER_RANKING_CHANGED_BY_SEMANTICS_COUNT=17
BUILDER_ELIGIBILITY_CHANGED_BY_SEMANTICS_COUNT=0
BBOX_PROXY_RECONSTRUCTION_COUNT=4
SAFE_BUT_LOW_FIDELITY_COUNT=19
NO_HIGH_FIDELITY_BUILDER_COUNT=9
SILHOUETTE_IOU_MEAN_BEFORE=0.7635763794864155
SILHOUETTE_IOU_MEAN_AFTER=0.8769801945638075
SECTION_PROFILE_ERROR_BEFORE=1.0
SECTION_PROFILE_ERROR_AFTER=0.15551423501945166
CIRCULAR_FEATURE_FIDELITY_PASS_COUNT=0
PATTERN_FIDELITY_PASS_COUNT=1
CASE09_MAIN_WING_ROLE_RECOVERED=True
CASE09_MAIN_WING_SELECTED_BUILDER=LOFT
CASE09_MAIN_WING_BBOX_PROXY_REJECTED=True
CASE09_MAIN_WING_SILHOUETTE_IOU_BEFORE=0.7635763794864155
CASE09_MAIN_WING_SILHOUETTE_IOU_AFTER=0.8769801945638075
TANK_HULL_ROLE_RECOVERED=True
TANK_TURRET_ROLE_RECOVERED=True
TANK_GUN_BARREL_ROLE_RECOVERED=True
ROAD_WHEEL_PATTERN_RECOVERED=True
ROAD_WHEEL_GROUP_COUNT=3
TRACK_ROLE_CANDIDATE_COUNT=2
PHYSX_SEMANTIC_PRIOR_DEPENDENCY_PASS=True
WRONG_PHYSX_ROLE_CANNOT_OVERRIDE_GEOMETRY=True
SEMANTIC_PRIOR_RESPECTS_V10_GATE=True
GEOMETRY_ONLY_PATH_REMAINS_AVAILABLE=True
CIRCULAR_SOURCE_VS_RECTANGULAR_CAD_PASS=False
PATTERN_COLLAPSE_REJECTED=True
BBOX_PROXY_COUNTERFACTUAL_PASS=True
PHYSX_CONFLICT_GATED=True
INVALID_BUILDER_EXECUTED_COUNT=0
LOFT_INVALID_EXECUTED_COUNT=0
BSPLINE_INVALID_EXECUTED_COUNT=0
EXECUTED_PARAMETER_WITHOUT_REF_COUNT=0
DIRECT_PLAN_TO_OCC_BYPASS_COUNT=0
GEOMETRY_EXPLOSION_COUNT=0
REAL_QWEN_CALLS=7
REAL_QWEN_EXECUTABLE_PLAN_COUNT=1
REAL_MAC_CALLS=1
MAC_EXTERNAL_RESOURCE_FAILURE=True
PART_ID_HARDCODE_COUNT=0
CASE_ID_HARDCODE_COUNT=0
V10_REGRESSION_PASS=True
V11_REGRESSION_PASS=True
V11B_REGRESSION_PASS=True
V7D3_REGRESSION_PASS=True
SEMANTIC_ROLE_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/semantic_part_roles.csv
PATTERN_GROUP_JSON=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/pattern_groups.json
BUILDER_RANKING_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/builder_ranking_before_after.csv
FIDELITY_QA_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/fidelity_qa.csv
DEBUG_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/v11c_source_vs_cad_contact_sheet.png
REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v11c_physx_semantic_feature_fidelity_recovery/artifacts/V11C_REPORT.md
TESTS_PASSED=29
TESTS_FAILED=0

## Required answers

1. YES. PhysX grounded evidence is now normalized into a gated Semantic Feature Prior with function, relations, patterns, geometry expectations and soft construction priors.
2. YES, with reliability qualification: object category, accepted part roles/functions, geometry-checked relations, and deterministic pattern semantics are represented; ambiguous evidence remains UNKNOWN.
3. NO. PhysX never changes Builder Eligibility; the observed eligibility change count is 0.
4. YES. It changes ranking only among builders already approved by V10.
5. NO. Wrong roles cannot introduce or execute a builder absent from the V10 allowed set.
6. The main wing previously favored a stable coarse board/skin candidate because ranking had no lifting-surface or taper fidelity term.
7. With MAIN_WING prior, LOFT/GENERAL_BSPLINE outrank EXTRUSION/PLANE when eligible; selected=LOFT.
8. Measured fixed-camera silhouette changed 0.7636 -> 0.8770; section error changed 1.0000 -> 0.1555.
9. YES. Geometry detected road-wheel pattern membership count=3.
10. YES. Cylindrical/revolution wheel candidates outrank rectangular extrusion where V10 permits them; passes=0.
11. The barrel role is recovered as an elongated child feature inside the frozen turret CADPART, but no boundary is invented; if Cylinder is not eligible it is reported as no high-fidelity builder.
12. YES. Hull bbox-like candidates rejected by Fidelity QA count=4.
13. YES. OCC-valid but SAFE_BUT_LOW_FIDELITY candidates count=19.
14. YES. NO_HIGH_FIDELITY_BUILDER_AVAILABLE count=9; wrong safe CAD is not promoted.
15. YES. Qwen/MAC candidates remain V11 Structured Plan -> Validator -> Resolver -> BuilderRegistry; MAC 403 is external and non-blocking.
16. YES for V12 router entry: semantic/fidelity ranking changes across aircraft, tank-like and building-like representatives while geometry authority remains frozen.

## Limitations

The frozen tank P3 merges some semantic subfeatures (notably turret and barrel). V11C records this instead of inventing new segmentation. Whole-object legacy PhysX misclassified two non-aircraft cases as lamps; these raw outputs are retained but gated out when they conflict with real Qwen global context and geometry.
