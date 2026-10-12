# V11 Structured Plan To Executable Builder

CURRENT_GATE=V11_STRUCTURED_PLAN_TO_EXECUTABLE_BUILDER_PASS

## Gate fields

CURRENT_GATE=V11_STRUCTURED_PLAN_TO_EXECUTABLE_BUILDER_PASS
V11_PASS=True
PARTS_TESTED=6
STRUCTURED_PLAN_SCHEMA_IMPLEMENTED=True
PLAN_VALIDATOR_USED=True
PARAMETER_REF_RESOLVER_USED=True
BUILDER_REGISTRY_USED=True
REAL_QWEN_CALLS=1
REAL_QWEN_EXECUTABLE_PLAN_COUNT=0
GEOMETRY_ALTERNATIVE_EXECUTABLE_PLAN_COUNT=9
PLANS_GENERATED=26
PLANS_SCHEMA_VALID=25
PLANS_GEOMETRY_VALID=23
PLANS_REFERENCE_VALID=23
PLANS_EXECUTABLE=23
PLANS_EXECUTION_SUCCESS=20
FRESH_BREP_COUNT=20
FRESH_STEP_COUNT=20
PLANE_EXECUTABLE_PLAN_COUNT=6
EXTRUSION_EXECUTABLE_PLAN_COUNT=5
CYLINDER_EXECUTABLE_PLAN_COUNT=5
REVOLUTION_EXECUTABLE_PLAN_COUNT=0
LOFT_EXECUTABLE_PLAN_COUNT=3
SWEEP_EXECUTABLE_PLAN_COUNT=0
BSPLINE_EXECUTABLE_PLAN_COUNT=1
OPEN_SHELL_EXECUTABLE_PLAN_COUNT=0
QWEN_PLAN_PARSE_SUCCESS=1
QWEN_PLAN_SCHEMA_FAILURE=1
QWEN_PLAN_GEOMETRY_CONFLICT=0
QWEN_PLAN_BAD_REFERENCE_COUNT=0
QWEN_RAW_NUMERIC_HALLUCINATION_COUNT=0
EXECUTED_GEOMETRY_PARAMETER_COUNT=114
EXECUTED_PARAMETER_WITH_REF_COUNT=114
EXECUTED_PARAMETER_WITHOUT_REF_COUNT=0
REFERENCE_NOT_FOUND_COUNT=0
REFERENCE_TYPE_MISMATCH_COUNT=0
REFERENCE_FRAME_MISMATCH_COUNT=0
DIRECT_PLAN_TO_OCC_BYPASS_COUNT=0
HISTORICAL_STEP_REUSED=False
FALLBACK_USED=False
CASE09_VALID_LOFT_PLAN_EXECUTABLE=True
CASE09_VALID_LOFT_FRESH_BREP=True
YC4XCA_CADPART002_EXECUTABLE_PLAN=True
YC4XCA_CADPART002_FRESH_BREP=True
YC4XCA_CADPART002_EXPLOSION_PREVENTED=True
GEOMETRY_EXPLOSION_COUNT=0
GEOMETRY_EXPLOSION_GUARD_REJECT_COUNT=1
PLAN_ROUNDTRIP_EXECUTION_PASS=True
MEASURED_PARAMETER_DEPENDENCY_PASS=True
MEASURED_SPEC_TO_BREP_DEPENDENCY_PASS=True
FREEFORM_REASONING_NOT_EXECUTION_SOURCE=True
HISTORICAL_STEP_REUSE_TEST_PASS=True
V10_REGRESSION_PASS=True
V7D3_REGRESSION_PASS=True
PLAN_SUMMARY_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/plan_summary.csv
PARAMETER_PROVENANCE_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/parameter_provenance.csv
BUILDER_EXECUTION_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/builder_execution_summary.csv
QWEN_PLAN_AUDIT_CSV=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/qwen_plan_audit.csv
DEBUG_CONTACT_SHEET=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/v11_plan_to_brep_contact_sheet.png
TESTS_PASSED=9
TESTS_FAILED=0
BLOCKERS=[]
REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/v11_structured_plan_to_executable_builder/artifacts/V11_STRUCTURED_PLAN_TO_EXECUTABLE_BUILDER_REPORT.md

## Answers

1. Runtime requires a strict Structured CAD Plan (schema + refs). Real Qwen was called once; that output failed schema and was not executed. Deterministic fixtures are strict structured plans.
   REAL_QWEN_CALLS=1 REAL_QWEN_EXECUTABLE_PLAN_COUNT=0 QWEN_PLAN_SCHEMA_FAILURE=1

2. Does runtime parse Qwen free-form reasoning for geometry numbers? NO. Counterfactual F: FREEFORM_REASONING_NOT_EXECUTION_SOURCE=True

3. Every executed radius/depth/axis/profile has a Measured CAD Spec reference. EXECUTED_PARAMETER_WITH_REF_COUNT=114

4. EXECUTED_PARAMETER_WITHOUT_REF_COUNT > 0? NO. Count=0

5. Can an invalid builder requested by Qwen enter BuilderRegistry execute? NO. Eligibility validator rejects first. QWEN_CAN_OVERRIDE_INVALID_GEOMETRY=false. YC4XCA CADPART_002 loft probe: PLAN_GEOMETRY_REJECTED.

6. Parameter Ref Resolver converts MEASURED_SPEC.* references into authoritative values. PARAMETER_REF_RESOLVER_USED=true. Missing refs fail REFERENCE_NOT_FOUND; wrong types fail REFERENCE_TYPE_MISMATCH. No auto-correction.

7. Changing an authoritative Measured Spec value changes Fresh BRep. MEASURED_PARAMETER_DEPENDENCY_PASS=True MEASURED_SPEC_TO_BREP_DEPENDENCY_PASS=True

8. Changing only reasoning_summary leaves BRep unchanged. FREEFORM_REASONING_NOT_EXECUTION_SOURCE=True

9. CASE09 valid loft: Structured Plan → Ref Resolver → LoftBuilder → Fresh BRep. CASE09_VALID_LOFT_PLAN_EXECUTABLE=True CASE09_VALID_LOFT_FRESH_BREP=True

10. YC4XCA CADPART_002: invalid Loft geometry-rejected; independent Geometry Alternative EXTRUSION produced a structured plan and fresh bounded BRep. YC4XCA_CADPART002_EXECUTABLE_PLAN=True YC4XCA_CADPART002_FRESH_BREP=True YC4XCA_CADPART002_EXPLOSION_PREVENTED=True

11. Historical STEP reused? NO. HISTORICAL_STEP_REUSED=false HISTORICAL_STEP_REUSE_TEST_PASS=True

12. Fallback used to fake fresh reconstruction? NO. FALLBACK_USED=false

13. Builder plan schemas still missing or not executable: SWEEP (no valid representative / not dispatched), REVOLUTION (no safe representative; 360° hull revolts explode), PERIODIC_BSPLINE (schema only), OPEN_SHELL (schema present, registry returns OPEN_SHELL_PLAN_NOT_YET_EXECUTABLE).

14. OPEN_SHELL / V7D3 topology can be referenced in a Structured Plan (MASTER_BOUNDARIES / TOPOLOGY / SURFACE_PRIMITIVES / WIREFRAME) but cannot yet execute through BuilderRegistry. Status: OPEN_SHELL_PLAN_NOT_YET_EXECUTABLE. Historical V7D3 STEP is not reused.

15. Ready for V12_FULL_CAD_PART_ROUTER (all CADPARTs auto plan→resolve→execute→QA)? NO. Representative interface is proven; open-shell execution and Qwen schema conformance are not.

16. Remaining blockers: D. Qwen conformance (real call parsed but schema-invalid; REAL_QWEN_EXECUTABLE_PLAN_COUNT=0) and E. Open-shell representation (plan expressible, not executable). A/B/C (schema, resolver, core builder schemas for EXTRUSION/LOFT/CYLINDER/PLANE/BSPLINE) are in place. F does not apply if REAL_QWEN_CALLS>0.

## Notes

GEOMETRY_EXPLOSION_COUNT is exploded-and-selected (0). Guard rejects that never enter the success set: GEOMETRY_EXPLOSION_GUARD_REJECT_COUNT=1.
REVOLUTION_EXECUTABLE_PLAN_COUNT=0 and SWEEP_EXECUTABLE_PLAN_COUNT=0 are NO_VALID_REPRESENTATIVE, not forged success.
Qwen counts are not merged with Geometry Alternative counts.

