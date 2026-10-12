# CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1

CURRENT_GATE=CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_PASS

## Gate fields

CASES_TOTAL=3
CASES_WITH_GEOMETRY_EXPLOSION=3
EXPLODED_CANDIDATE_COUNT=26
EXPLODED_CANDIDATE_SELECTED_COUNT=0
CASE09_FALSE_POSITIVE_REJECT_COUNT=0
PARTS_AUDITED=42
PARTS_WITH_EXPLOSION=6
FIRST_EXPLOSION_STAGE_COUNTS={"STAGE_7_BUILDER_RAW_OUTPUT": 6}
FAILURE_CLASS_COUNTS={"BSPLINE_CONTROL_NET_ERROR": 5, "PROFILE_CORRESPONDENCE_ERROR": 1}
PER_CASE_PRIMITIVE_HISTOGRAM={"CASE_5IHUMO": {"PLANE": 21}, "CASE_YC4XCA": {"PLANE": 13}, "CASE09": {"CYLINDER": 3, "PLANE": 5}}
PER_CASE_ROUTE_HISTOGRAM={"CASE_5IHUMO": {"LOFT": 29, "GENERAL_BSPLINE": 12, "REVOLUTION": 5, "SWEEP": 5, "PERIODIC_BSPLINE": 5, "EXTRUSION": 7}, "CASE_YC4XCA": {"LOFT": 20, "GENERAL_BSPLINE": 10, "REVOLUTION": 3, "SWEEP": 3, "PERIODIC_BSPLINE": 3}, "CASE09": {"LOFT": 15, "PERIODIC_BSPLINE": 1, "EXTRUSION": 4, "UNSUPPORTED": 2, "REVOLUTION": 1, "GENERAL_BSPLINE": 1}}
FRAME_MISMATCH_COUNT=0
SILENT_GENERAL_BSPLINE_FALLBACK_COUNT=0
selection_by_case={"CASE_5IHUMO": "CAD_BEST_AVAILABLE_EXPLOSION_FILTERED", "CASE_YC4XCA": "CAD_BEST_AVAILABLE_EXPLOSION_FILTERED", "CASE09": "CAD_BEST_AVAILABLE_EXPLOSION_FILTERED"}

## Answers

1. CASE_5IHUMO first explosion stage: STAGE_7_BUILDER_RAW_OUTPUT (dominant class BSPLINE_CONTROL_NET_ERROR)
2. CASE_YC4XCA first explosion stage: STAGE_7_BUILDER_RAW_OUTPUT (dominant class BSPLINE_CONTROL_NET_ERROR)
3. Same root cause? YES (stage STAGE_7_BUILDER_RAW_OUTPUT vs STAGE_7_BUILDER_RAW_OUTPUT, class BSPLINE_CONTROL_NET_ERROR vs BSPLINE_CONTROL_NET_ERROR)
4. Coordinate/transform mix? FRAME_MISMATCH_COUNT=0; TRANSFORM_CAUSAL_COUNT=0
5. Wrong CAD Part merge? PART_MERGE_ERROR_COUNT=0
6. Loft profile correspondence error? PROFILE_CORRESPONDENCE_ERROR_COUNT=1; causal=4
7. BSpline control points outside part bbox? BSPLINE_CONTROL_NET_ERROR_COUNT=5
8. Untrimmed infinite intersection as long Edge? WIREFRAME_TOPOLOGY_ERROR_COUNT=0 (wireframe stage was declared absent for these runs; long edges are from builder faces/edges)
9. Primitive selector routing mechanical parts to Loft/BSpline? See PER_CASE_ROUTE_HISTOGRAM vs PER_CASE_PRIMITIVE_HISTOGRAM. Qwen/builder route is independent of plane-bank selection.
10. Tank-like case primitive histogram: {"PLANE": 13}
11. Reference vs tank primitive histogram: ref={"CYLINDER": 3, "PLANE": 5} tank={"PLANE": 13}
12. Qwen plan vs geometry conflict count=89; unmeasured params=20
13. Explosion before builder? NO — first reject is at/after builder for the dominant path
14. Explosion only after assembly placement? NO
15. Will exploded CAD still be labeled best-available? NO. REJECT => ELIGIBLE_FOR_BEST_AVAILABLE=false; if none eligible the output is NO_VALID_CAD_CANDIDATE. EXPLODED_CANDIDATE_SELECTED_COUNT=0
16. Next fix (from first-explosion evidence): **E** (Loft/BSpline builder). Stages 0–6 stay PASS; explosion starts at STAGE_7. Counterfactual B: swapping to EXTRUSION removes the explosion (PRIMITIVE_SELECTION_CAUSAL=5), so the loft/skin family is the exploding operator. The plane bank did not select Loft — design-intent/runtime ignored it. Do not start with merge/transform/assembly.

TESTS_PASSED=8
TESTS_FAILED=0
BLOCKERS=[]

REPORT=/data/home/cuiyuehan/project/mesh2cad/ours3/cross_case_geometry_explosion_audit_v1/artifacts/CROSS_CASE_GEOMETRY_EXPLOSION_AUDIT_V1_REPORT.md
