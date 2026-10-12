# V10 Geometry-Gated Builder Contract Closure

CURRENT_GATE=V10_GEOMETRY_GATED_BUILDER_CONTRACT_CLOSURE_PASS

## Gate fields

BUILDER_ELIGIBILITY_CONTRACT_USED=True
QWEN_CAN_OVERRIDE_INVALID_GEOMETRY=False
INVALID_BUILDER_REQUEST_COUNT=66
INVALID_BUILDER_EXECUTED_COUNT=0
LOFT_INVALID_REQUEST_COUNT=17
LOFT_INVALID_EXECUTED_COUNT=0
BSPLINE_INVALID_REQUEST_COUNT=44
BSPLINE_INVALID_EXECUTED_COUNT=0
UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT=20
UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT=0
DIRECT_OCC_BUILDER_BYPASS_COUNT=0
LOFT_PREFLIGHT_FAIL_COUNT=17
LOFT_PREFLIGHT_REJECTED_BUT_EXECUTED_COUNT=0
BSPLINE_GRID_PREFLIGHT_FAIL_COUNT=0
CONTROL_NET_GUARD_FAIL_COUNT=0
CONTROL_NET_GUARD_REJECTED_BUT_FACE_CREATED_COUNT=0
GEOMETRY_ALTERNATIVE_CANDIDATE_COUNT=28
EXPLODED_CANDIDATE_SELECTED_COUNT=0
YC4XCA_CADPART002_EXPLOSION_PREVENTED=True
CASE09_VALID_LOFT_COUNT_BEFORE=5
CASE09_VALID_LOFT_COUNT_AFTER=5
CASE09_VALID_BSPLINE_COUNT_BEFORE=8
CASE09_VALID_BSPLINE_COUNT_AFTER=8
CASE09_NEW_FALSE_REJECTION_COUNT=0

## Counterfactuals

{
  "INVALID_LOFT_EXECUTION_BLOCKED": true,
  "VALID_LOFT_OR_EXTRUSION_EXECUTED": true,
  "VALID_CONSTRUCTION_MODE": "LOFT",
  "CORRUPT_CORRESPONDENCE_PREFLIGHT_FAIL": true,
  "CONTROL_NET_REJECT_BEFORE_FACE": true,
  "UNMEASURED_NUMERIC_NOT_CONSUMED": true,
  "GEOMETRY_ALTERNATIVE_INDEPENDENT": true,
  "GRID_PREFLIGHT_ON_PATHOLOGICAL": true,
  "CONTROL_NET_RUNAWAY_TEST_PASS": true,
  "DIRECT_OCC_BUILDER_BYPASS_DETECTED": true,
  "details": {
    "A": {
      "schema_valid": true,
      "QWEN_REQUESTED_BUILDER": "LOFT",
      "GEOMETRY_ALLOWED_BUILDERS": [
        "EXTRUSION",
        "CYLINDER",
        "SWEEP",
        "GENERAL_BSPLINE"
      ],
      "PLAN_VALIDATION_DECISION": "REJECT_BUILDER_NOT_GEOMETRY_APPROVED",
      "PLAN_VALIDATION_STATUS": "REJECT_BUILDER_NOT_GEOMETRY_APPROVED",
      "PLAN_EXECUTABLE": false,
      "reasons": [
        "BUILDER_NOT_ALLOWED"
      ],
      "parameter_resolution": {
        "catalog": {
          "SPEC.AREA": 1.64,
          "SPEC.BBOX": [
            [
              -0.5,
              -0.2,
              -0.15
            ],
            [
              0.5,
              0.2,
              0.15
            ]
          ],
          "SPEC.CENTROID": [
            0.0,
            8.46206573647223e-18,
            5.288791085295143e-19
          ],
          "SPEC.EXTENTS": [
            1.0,
            0.4,
            0.3
          ],
          "SPEC.EXTENTS.longitudinal": 1.0,
          "SPEC.EXTRUSION.depth": 1.0,
          "SPEC.LONGITUDINAL_AXIS_INDEX": 0
        },
        "refs": [],
        "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": 0,
        "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0,
        "unmeasured": [],
        "unresolved_refs": [],
        "executable_parameters": {}
      },
      "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": 0,
      "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0,
      "representation": "GLOBAL_LOFT",
      "family": "LOFT"
    },
    "E": {
      "schema_valid": true,
      "QWEN_REQUESTED_BUILDER": "EXTRUSION",
      "GEOMETRY_ALLOWED_BUILDERS": [
        "EXTRUSION",
        "CYLINDER",
        "SWEEP",
        "LOFT",
        "GENERAL_BSPLINE"
      ],
      "PLAN_VALIDATION_DECISION": "REJECT_UNMEASURED_PARAMETER",
      "PLAN_VALIDATION_STATUS": "REJECT_UNMEASURED_PARAMETER",
      "PLAN_EXECUTABLE": false,
      "reasons": [
        "UNMEASURED_QWEN_GEOMETRY_PARAMETER"
      ],
      "parameter_resolution": {
        "catalog": {
          "SPEC.AREA": 1.64,
          "SPEC.BBOX": [
            [
              -0.5,
              -0.2,
              -0.15
            ],
            [
              0.5,
              0.2,
              0.15
            ]
          ],
          "SPEC.CENTROID": [
            0.0,
            8.46206573647223e-18,
            5.288791085295143e-19
          ],
          "SPEC.EXTENTS": [
            1.0,
            0.4,
            0.3
          ],
          "SPEC.EXTENTS.longitudinal": 1.0,
          "SPEC.EXTRUSION.depth": 1.0,
          "SPEC.LONGITUDINAL_AXIS_INDEX": 0
        },
        "refs": [],
        "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": 1,
        "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0,
        "unmeasured": [
          {
            "path": [
              "depth"
            ],
            "value": 99999,
            "key": "depth"
          }
        ],
        "unresolved_refs": [],
        "executable_parameters": {}
      },
      "UNMEASURED_QWEN_PARAMETER_PROPOSED_COUNT": 1,
      "UNMEASURED_QWEN_PARAMETER_CONSUMED_COUNT": 0,
      "representation": "EXTRUSION",
      "family": "EXTRUSION"
    },
    "F_source": "GEOMETRY_ALTERNATIVE"
  }
}

## Required audit answers

1. The Primitive Bank decision was advisory in the frozen V1 runtime; the runtime dispatched the Qwen representation string directly and never consumed builder eligibility.
2. The concrete bypasses were `case09_fullstack_mesh2cad_mac_v6/scripts/v6_runtime.py:89-112` and `v9_fullstack_architecture_closure/surface_primitives/fitters.py:20-72`, where OCC Loft/BSpline APIs were called without a geometry-authority gate.
3. Yes. V10 closes that production path with the registry capability token; DIRECT_OCC_BUILDER_BYPASS_COUNT=0 and the direct-bypass counterfactual is detected.
4. No. Qwen cannot overwrite an invalid geometry builder decision; QWEN_CAN_OVERRIDE_INVALID_GEOMETRY=false.
5. None of the 20 unmeasured Qwen geometry values was consumed; consumed=0.
6. Yes. CASE_YC4XCA CADPART_002's prior 22.806x explosion was prevented=True.
7. CADPART_002 stops at Builder Eligibility and then Plan Validator. Its measured-profile preflight marks Loft invalid (centroid/scale jump and crossing evidence), so Loft Preflight inside the builder, Control-Net Guard, and Post-build Guard are not reached.
8. CASE_5IHUMO CADPART_002, CADPART_013, and CADPART_019 all stop at Builder Eligibility / Plan Validator; their Loft and General-BSpline plans have PLAN_EXECUTABLE=false and BUILDER_EXECUTED=false. A geometry-approved Extrusion alternative is bounded for each.
9. No. LOFT_PREFLIGHT_REJECTED_BUT_EXECUTED_COUNT=0.
10. No. CONTROL_NET_GUARD_REJECTED_BUT_FACE_CREATED_COUNT=0.
11. Yes. Geometry-approved Extrusion alternatives produced bounded BReps: 28/28 valid.
12. Yes. CASE09 valid Loft executions are preserved: 5 before and 5 after.
13. No. Valid Loft was not globally disabled; CASE09_NEW_FALSE_REJECTION_COUNT=0.
14. Yes. V7D3 tail geometry and shared topology are unchanged; metric regression and artifact hashes pass=True.
15. Yes for the V10 builder-contract boundary: all three cases have zero V10 runaway geometry and the router can now consume only validated executable plans. Full-object reconstruction remains a separate downstream stage.
16. Not applicable: V10 is PASS and BLOCKERS is empty. No residual A-E blocker is being hidden.

