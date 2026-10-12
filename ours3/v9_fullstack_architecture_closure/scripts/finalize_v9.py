#!/usr/bin/env python3
"""Freeze the evidence-backed V9 audit without executing any CAD recovery."""

import csv
import json
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v9_fullstack_architecture_closure"
ART = OUT / "artifacts"


def load(name):
    return json.loads((ART / name).read_text())


def dump_json(name, value):
    (ART / name).write_text(json.dumps(value, indent=2) + "\n")


def write_csv(name, rows, fields):
    with (ART / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


ART.mkdir(parents=True, exist_ok=True)
a = load("v9a_summary.json")
bc = load("v9bc_summary.json")
d = load("v9d_summary.json")
e = load("v9e_qwen_ablation.json")
f = load("v9f_summary.json")
g = load("v9g_summary.json")
h = load("v9h_summary.json")
pg = load("v9_part_graph_summary.json")

status_rows = [
    {
        "STEP": 1,
        "STATUS": "CONNECTED_BUT_NOT_GEOMETRY_EFFECTIVE",
        "REAL_MODULE": "P3_conditioned_PhysX_fusion",
        "REAL_INPUT": "existing CASE09 P3 artifacts; PhysX optional prior",
        "REAL_OUTPUT": "semantic/reliability evidence",
        "REAL_CONSUMER": "none in V9 reconstruction geometry",
        "GEOMETRY_EFFECTIVE": False,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": False,
        "CASE09_COVERAGE": "optional; not consumed",
        "BLOCKER": "NO_V9_GEOMETRY_CONSUMER",
    },
    {
        "STEP": 2,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "automatic_graph.py",
        "REAL_INPUT": "10 P3 OBJ segments and triangle maps",
        "REAL_OUTPUT": "8-node geometry/contact part graph",
        "REAL_CONSUMER": "V9 audit only; no full router execution",
        "GEOMETRY_EFFECTIVE": False,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": False,
        "CASE09_COVERAGE": "10/10 segments; hierarchy partial",
        "BLOCKER": "HIERARCHY_SEMANTIC_ROLES_NOT_RELIABLY_INFERRED",
    },
    {
        "STEP": 4,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "surface_wireframe.py",
        "REAL_INPUT": "fitted OCC surfaces for 3 core parts",
        "REAL_OUTPUT": "10 semantic surfaces and 40 CAD boundaries",
        "REAL_CONSUMER": "V9C main wing only; fuselage/tail not shared-topology consumers",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": "MAIN_WING_ONLY",
        "COUNTERFACTUAL_PASS": False,
        "CASE09_COVERAGE": "3/8 inferred parts",
        "BLOCKER": "FUSELAGE_TAIL_WIREFRAME_NOT_CONSUMED_BY_SHARED_TOPOLOGY",
    },
    {
        "STEP": 5,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "fitters.py",
        "REAL_INPUT": "measured points/profiles/control nets",
        "REAL_OUTPUT": "8 executable OCC primitive examples",
        "REAL_CONSUMER": "V9B/V9D capability evidence",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": True,
        "CASE09_COVERAGE": "fitter suite only; no per-surface candidate selection",
        "BLOCKER": "PER_SEMANTIC_SURFACE_PRIMITIVE_SELECTOR_NOT_EXECUTED",
    },
    {
        "STEP": 6,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "surface_wireframe.py and wireframe_graph.py",
        "REAL_INPUT": "10 real semantic surfaces",
        "REAL_OUTPUT": "40 design edges; zero mesh/profile-sample imports",
        "REAL_CONSUMER": "main-wing topology plus descriptive f/t QA",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": "MAIN_WING_ONLY",
        "COUNTERFACTUAL_PASS": "MAIN_WING_BASELINE_ONLY",
        "CASE09_COVERAGE": "3 core parts, topology dependency 1/3",
        "BLOCKER": "WIRE_FRAME_DEPENDENCY_PASS_FALSE",
    },
    {
        "STEP": 7,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "global_topology_builder.py and topology/qa.py",
        "REAL_INPUT": "main-wing shared curves plus three-part face sets",
        "REAL_OUTPUT": "12 shared OCC edges, 40 pcurves, 10 trimmed faces",
        "REAL_CONSUMER": "V9D measured specs",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": "MAIN_WING_ONLY",
        "COUNTERFACTUAL_PASS": "MAIN_WING_BASELINE_ONLY",
        "CASE09_COVERAGE": "main wing pass; fuselage/tail fail",
        "BLOCKER": "FUSELAGE_AND_TAIL_COMMON_BOUNDARY_CONTROL_NETS_MISSING",
    },
    {
        "STEP": 8,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "run_v9d.py feature graph",
        "REAL_INPUT": "geometry, primitives, wireframe, topology",
        "REAL_OUTPUT": "3 evidence-backed feature instances",
        "REAL_CONSUMER": "three V9 measured specs and Qwen prompt inputs",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": True,
        "CASE09_COVERAGE": "3/8 inferred parts",
        "BLOCKER": "FULL_CASE09_FEATURE_GRAPH_NOT_EXECUTED",
    },
    {
        "STEP": 9,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "MeasuredCADSpecV9 writer",
        "REAL_INPUT": "geometry, primitive, wireframe, topology, feature graph",
        "REAL_OUTPUT": "3 provenance-linked measured specs",
        "REAL_CONSUMER": "V9E Qwen ablations",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": True,
        "CASE09_COVERAGE": "3/8 inferred parts",
        "BLOCKER": "FULL_CASE09_MEASURED_SPEC_NOT_EXECUTED",
    },
    {
        "STEP": 13,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "V8 frozen-logic optimizer evidence",
        "REAL_INPUT": "main-wing executed BRep metrics",
        "REAL_OUTPUT": "2 optimized main-wing parameters",
        "REAL_CONSUMER": "V9F audit",
        "GEOMETRY_EFFECTIVE": True,
        "TOPOLOGY_EFFECTIVE": True,
        "COUNTERFACTUAL_PASS": True,
        "CASE09_COVERAGE": "main wing only; V8 result read, not rerun for all core parts",
        "BLOCKER": "FUSELAGE_AND_TAIL_OPTIMIZATION_NOT_RUN",
    },
    {
        "STEP": 17,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "grounding/v2.py",
        "REAL_INPUT": "main-wing OCC faces/edges plus semantic descriptors",
        "REAL_OUTPUT": "2 face and 2 edge resolutions with uncertainty",
        "REAL_CONSUMER": "V9H repair request target",
        "GEOMETRY_EFFECTIVE": False,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": True,
        "CASE09_COVERAGE": "main wing only",
        "BLOCKER": "FULL_CASE09_GROUNDING_NOT_EXECUTED",
    },
    {
        "STEP": 18,
        "STATUS": "PARTIAL",
        "REAL_MODULE": "V9H targeted repair driver",
        "REAL_INPUT": "grounded main-wing edge and real QA context",
        "REAL_OUTPUT": "provider request plus truthful 403 resource failure",
        "REAL_CONSUMER": "none; no patch returned",
        "GEOMETRY_EFFECTIVE": False,
        "TOPOLOGY_EFFECTIVE": False,
        "COUNTERFACTUAL_PASS": False,
        "CASE09_COVERAGE": "0 repair executions",
        "BLOCKER": "MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403",
    },
]
status_fields = [
    "STEP",
    "STATUS",
    "REAL_MODULE",
    "REAL_INPUT",
    "REAL_OUTPUT",
    "REAL_CONSUMER",
    "GEOMETRY_EFFECTIVE",
    "TOPOLOGY_EFFECTIVE",
    "COUNTERFACTUAL_PASS",
    "CASE09_COVERAGE",
    "BLOCKER",
]
write_csv("v9_architecture_status.csv", status_rows, status_fields)

dependency_rows = [
    {
        "STEP": 5,
        "PERTURBATION": "cylinder radius 0.8 and loft profile scale 0.9",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": True,
        "TOPOLOGY_CHANGED": "NOT_ASSERTED",
        "DEPENDENCY_PASS": True,
        "COVERAGE": "fitter artifacts, not final CASE09 assembly",
    },
    {
        "STEP": 6,
        "PERTURBATION": "design edge remove",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": True,
        "TOPOLOGY_CHANGED": True,
        "DEPENDENCY_PASS": True,
        "COVERAGE": "V8/main wing baseline only; V9 global dependency false",
    },
    {
        "STEP": 7,
        "PERTURBATION": "shared edge perturb",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": True,
        "TOPOLOGY_CHANGED": True,
        "DEPENDENCY_PASS": True,
        "COVERAGE": "V8/main wing baseline only",
    },
    {
        "STEP": 9,
        "PERTURBATION": "LOFT profile_scale 1.0 to 0.9",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": True,
        "TOPOLOGY_CHANGED": "NOT_ASSERTED",
        "DEPENDENCY_PASS": True,
        "COVERAGE": "main-wing feature/spec parameter",
    },
    {
        "STEP": 13,
        "PERTURBATION": "optimization target change",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": True,
        "TOPOLOGY_CHANGED": True,
        "DEPENDENCY_PASS": True,
        "COVERAGE": "V8/main wing baseline only",
    },
    {
        "STEP": 17,
        "PERTURBATION": "lower-leading query to upper-trailing query",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": True,
        "GEOMETRY_CHANGED": False,
        "TOPOLOGY_CHANGED": False,
        "DEPENDENCY_PASS": True,
        "COVERAGE": "different real main-wing OCC edge selected",
    },
    {
        "STEP": 18,
        "PERTURBATION": "repair target change",
        "REAL_INPUT_CHANGED": True,
        "DOWNSTREAM_REEXECUTED": False,
        "GEOMETRY_CHANGED": False,
        "TOPOLOGY_CHANGED": False,
        "DEPENDENCY_PASS": False,
        "COVERAGE": "blocked before patch by provider 403",
    },
]
write_csv(
    "e2e_dependency_matrix.csv",
    dependency_rows,
    [
        "STEP",
        "PERTURBATION",
        "REAL_INPUT_CHANGED",
        "DOWNSTREAM_REEXECUTED",
        "GEOMETRY_CHANGED",
        "TOPOLOGY_CHANGED",
        "DEPENDENCY_PASS",
        "COVERAGE",
    ],
)

pipeline = """ACTUAL V9 RUNTIME DEPENDENCY (evidence only)

CASE09 original high-poly OBJ
  -> existing verified P3 artifacts (10 segments; P3 not rerun by V9)
  -> automatic geometry/contact part graph (8 inferred groups; hierarchy PARTIAL)
  -> [STOP: no generic full-part router/reconstruction executed]

Independent scoped branch for CADPART_001 / CADPART_000 / CADPART_005:
  measured geometry/profiles
  -> V9A OCC fitter capability suite (8 types; no per-semantic-surface selector)
  -> V9B semantic surfaces + CAD boundary curves (3 core parts)
  -> V9C topology
       CADPART_001: shared OCC edges -> pcurves -> trimmed faces [PASS]
       CADPART_000: independent FACE_SET [no shared topology]
       CADPART_005: independent FACE_SET [no shared topology]
  -> V9D feature graph + measured CAD spec (3 core parts)
  -> V9E local Qwen3-VL ablation
       OBJ tokens + pixels + measured spec requests sent
       executable Qwen construction plan not produced
  -> V9F reads V8 main-wing optimizer evidence only
  -> V9G main-wing BRep grounding V2
  -> V9H real Multi-Agent-CAD provider request
       MAC unavailable: HTTP 403 free-tier quota exhausted
  -> [STOP: no local patch, no post-repair QA, no V9I XCAF assembly]

PhysX: optional prior; not a geometry membership or design-intent consumer.
Historical STEP: not used as a final V9 part; no final V9 assembly exists.
Fallback: none executed.
"""
(ART / "v9_actual_runtime_pipeline.txt").write_text(pipeline)

blockers = [
    "PER_SEMANTIC_SURFACE_PRIMITIVE_SELECTOR_NOT_EXECUTED",
    "HIERARCHY_SEMANTIC_ROLES_NOT_RELIABLY_INFERRED",
    "FUSELAGE_COMMON_BOUNDARY_CONTROL_NET_NOT_CONSTRUCTED",
    "VERTICAL_TAIL_COMMON_BOUNDARY_CONTROL_NET_NOT_CONSTRUCTED",
    "V9B_FUSELAGE_TAIL_WIREFRAME_NOT_CONSUMED_BY_SHARED_TOPOLOGY",
    "FULL_CASE09_ROUTER_AND_RECONSTRUCTION_NOT_EXECUTED",
    "LOCAL_QWEN_PLAN_BUILDER_NOT_EXECUTABLE",
    "FUSELAGE_CONTINUOUS_BREP_OPTIMIZATION_NOT_RUN",
    "VERTICAL_TAIL_CONTINUOUS_BREP_OPTIMIZATION_NOT_RUN",
    "MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403",
    "V9I_XCAF_ASSEMBLY_NOT_WRITTEN",
]

summary = {
    "CURRENT_GATE": "V9_FULLSTACK_ARCHITECTURE_CLOSURE_PARTIAL",
    "CASE09_FULLSTACK_COMPLETE": False,
    "STEP_1_STATUS": "CONNECTED_BUT_NOT_GEOMETRY_EFFECTIVE",
    "STEP_2_STATUS": "PARTIAL",
    "STEP_4_STATUS": "PARTIAL",
    "STEP_5_STATUS": "PARTIAL",
    "STEP_6_STATUS": "PARTIAL",
    "STEP_7_STATUS": "PARTIAL",
    "STEP_8_STATUS": "PARTIAL",
    "STEP_9_STATUS": "PARTIAL",
    "STEP_13_STATUS": "PARTIAL",
    "STEP_17_STATUS": "PARTIAL",
    "STEP_18_STATUS": "PARTIAL",
    "REAL_SURFACE_FITTER_COUNT": a["REAL_SURFACE_FITTER_COUNT"],
    "SEMANTIC_SURFACE_COUNT": bc["SEMANTIC_SURFACE_COUNT"],
    "SURFACE_PRIMITIVE_COUNT": bc["SEMANTIC_SURFACE_COUNT"],
    "REAL_DESIGN_EDGE_COUNT": bc["REAL_DESIGN_EDGE_COUNT"],
    "SHARED_OCC_EDGE_COUNT": bc["SHARED_OCC_EDGE_COUNT"],
    "PCURVE_EDGE_COUNT": bc["PCURVE_EDGE_COUNT"],
    "TRIMMED_FACE_COUNT": bc["TRIMMED_FACE_COUNT"],
    "FUSELAGE_RESULT_TYPE": bc["FUSELAGE_RESULT_TYPE"],
    "VERTICAL_TAIL_RESULT_TYPE": bc["VERTICAL_TAIL_RESULT_TYPE"],
    "FEATURE_INSTANCE_COUNT": d["FEATURE_INSTANCE_COUNT"],
    "MEASURED_SPEC_SURFACE_PRIMITIVES_INCLUDED": d["MEASURED_SPEC_SURFACE_PRIMITIVES_INCLUDED"],
    "MEASURED_SPEC_WIREFRAME_INCLUDED": d["MEASURED_SPEC_WIREFRAME_INCLUDED"],
    "MEASURED_SPEC_FEATURE_PARAMETERS_INCLUDED": d["MEASURED_SPEC_FEATURE_PARAMETERS_INCLUDED"],
    "QWEN3_VL_DUAL_MODAL_USED": e["QWEN3_VL_DUAL_MODAL_USED"],
    "REAL_MAC_CALLS": h["REAL_MAC_CALLS"],
    "MAC_RESOURCE_FAILURES": h["MAC_RESOURCE_FAILURES"],
    "PARAMETERS_OPTIMIZED": f["PARAMETERS_OPTIMIZED"],
    "GROUNDING_FACE_SUCCESS_COUNT": g["GROUNDING_FACE_SUCCESS_COUNT"],
    "GROUNDING_EDGE_SUCCESS_COUNT": g["GROUNDING_EDGE_SUCCESS_COUNT"],
    "TARGETED_REPAIR_ATTEMPTS": h["TARGETED_REPAIR_ATTEMPTS"],
    "TARGETED_REPAIR_ACCEPTED": h["TARGETED_REPAIR_ACCEPTED"],
    "STEP18_DEPENDENCY_PASS": h["STEP18_DEPENDENCY_PASS"],
    "P3_SEGMENT_COUNT": pg["P3_SEGMENT_COUNT"],
    "FINAL_CAD_PART_COUNT": pg["FINAL_CAD_PART_COUNT"],
    "AUTOMATIC_PART_MERGE_USED": pg["AUTOMATIC_PART_MERGE_USED"],
    "PART_HIERARCHY_STATUS": pg["PART_HIERARCHY_STATUS"],
    "TRANSFORM_STATUS": pg["TRANSFORM_STATUS"],
    "ALL_FINAL_PARTS_FRESH": False,
    "HISTORICAL_STEP_REUSED": False,
    "FALLBACK_COUNT": 0,
    "FULL_CASE09_ASSEMBLY": False,
    "FINAL_STEP": "NONE",
    "FINAL_STEP_OCC_VALID": False,
    "FINAL_CHAMFER": "NOT_AVAILABLE",
    "FINAL_HAUSDORFF": "NOT_AVAILABLE",
    "FINAL_ARTIFICIAL_EDGE_RATIO": "NOT_AVAILABLE",
    "FINAL_MESH_LIKE_SCORE": "NOT_AVAILABLE",
    "ARCHITECTURE_STATUS_CSV": str(ART / "v9_architecture_status.csv"),
    "E2E_DEPENDENCY_MATRIX": str(ART / "e2e_dependency_matrix.csv"),
    "ACTUAL_RUNTIME_PIPELINE": str(ART / "v9_actual_runtime_pipeline.txt"),
    "REPORT": str(ART / "V9_FULLSTACK_ARCHITECTURE_CLOSURE_REPORT.md"),
    "TESTS_PASSED": 99,
    "TESTS_FAILED": 0,
    "BLOCKERS": blockers,
}

test_results = {
    "current_run": [
        {"suite": "v7_contract_closed_runtime", "passed": 35, "failed": 0},
        {"suite": "v7a_profile_recovery", "passed": 16, "failed": 0},
        {"suite": "v7b_profile_type_aware_open_shell_reconstruction", "passed": 23, "failed": 0},
        {"suite": "v9_fullstack_architecture_closure", "passed": 5, "failed": 0},
        {"suite": "physx_grounded_v2_1", "passed": 20, "failed": 0},
    ],
    "V7C_TEST_SUITE_AVAILABLE": False,
    "V8_TEST_SUITE_AVAILABLE": False,
    "V8_EXISTING_AUDIT_TESTS_PASSED": 45,
    "V8_EXISTING_AUDIT_TESTS_FAILED": 0,
    "PHYSX_V2_2_AVAILABLE": False,
    "PHYSX_V2_1_RUN_INSTEAD": True,
    "TESTS_PASSED": 99,
    "TESTS_FAILED": 0,
    "note": "An initial combined pytest invocation had one collection error because V7B requires its module directory on sys.path; every suite was then run from its required cwd and passed.",
}
dump_json("test_results.json", test_results)
dump_json("final_summary.json", summary)

report = f"""# V9 Fullstack Architecture Closure — Evidence Audit

## Outcome

`CURRENT_GATE=V9_FULLSTACK_ARCHITECTURE_CLOSURE_PARTIAL`

CASE09 did **not** reach a fresh complete XCAF assembly. The internal pipeline has multiple blockers in addition to the external MAC quota: per-surface primitive selection was not executed; fuselage and vertical-tail shared topology is absent; full-part routing/reconstruction was not executed; Qwen produced no executable construction plan; and optimization/grounding coverage is incomplete. Therefore the external-resource exception status is not applicable.

The V9I gate was stopped rather than substituting the old CASE09 hard-coded `PART_SPECS` path, a historical STEP, convex-hull/bbox fallback, or a main-wing-only STEP.

## Evidence summary

- Eight primitive fitter implementations generate executable OCC geometry and expose geometry parameters, support/domain and residual evidence. Radius/profile-scale perturbations change freshly written fitter STEP files. The CASE09 per-semantic-surface candidate selector was not run, so Step 5 remains PARTIAL.
- Automatic geometry/contact grouping covers all 10 P3 segments and emits 8 groups without old `PART_SPECS` or GT semantic labels. Hierarchy remains PARTIAL.
- Main wing has shared OCC topology. Fuselage and vertical tail each have real BSpline FACE_SET output and real CAD boundary curves, but their independently fitted tracks do not provide a common boundary control net; they do not have shared-edge topology.
- Three evidence-backed feature instances and three provenance-linked measured specs were produced for the core parts. This is 3/8 inferred-part coverage, not full CASE09 coverage.
- Local Qwen3-VL received the requested OBJ/pixel/spec ablation inputs. Its full multimodal request failed HTTP 500 and the other responses did not yield an executable permitted builder; `QWEN_PLAN_EXECUTED=false`.
- One real Multi-Agent-CAD provider request was sent. DashScope returned HTTP 403 `AllocationQuota.FreeTierOnly`; no repair patch, post-QA, or acceptance/rollback occurred.
- No hidden fallback was executed. No historical STEP was used as a final V9 part. There is no final V9 STEP.

## Gate metrics

```text
REAL_SURFACE_FITTER_COUNT={summary['REAL_SURFACE_FITTER_COUNT']}
SEMANTIC_SURFACE_COUNT={summary['SEMANTIC_SURFACE_COUNT']}
REAL_DESIGN_EDGE_COUNT={summary['REAL_DESIGN_EDGE_COUNT']}
SHARED_OCC_EDGE_COUNT={summary['SHARED_OCC_EDGE_COUNT']}
PCURVE_EDGE_COUNT={summary['PCURVE_EDGE_COUNT']}
TRIMMED_FACE_COUNT={summary['TRIMMED_FACE_COUNT']}
FEATURE_INSTANCE_COUNT={summary['FEATURE_INSTANCE_COUNT']}
PARAMETERS_OPTIMIZED={summary['PARAMETERS_OPTIMIZED']}
GROUNDING_FACE_SUCCESS_COUNT={summary['GROUNDING_FACE_SUCCESS_COUNT']}
GROUNDING_EDGE_SUCCESS_COUNT={summary['GROUNDING_EDGE_SUCCESS_COUNT']}
REAL_MAC_CALLS={summary['REAL_MAC_CALLS']}
TARGETED_REPAIR_ATTEMPTS={summary['TARGETED_REPAIR_ATTEMPTS']}
P3_SEGMENT_COUNT={summary['P3_SEGMENT_COUNT']}
FINAL_CAD_PART_COUNT={summary['FINAL_CAD_PART_COUNT']}
FULL_CASE09_ASSEMBLY=false
```

`FINAL_CAD_PART_COUNT=8` is the automatic part-graph group count, not the count of successfully reconstructed V9 CAD BReps.

## Required 20 answers

1. **Are all eight Step 5 fitters real implementations?** Yes as fitter capabilities: all eight construct executable OCC geometry with real parameters. No for the full Step 5 gate: the required per-semantic-surface candidate comparison/selection was not executed.
2. **Did fuselage traverse primitive → wireframe → shared edge → pcurve → trimmed Face?** No. It reached real GENERAL_BSPLINE faces and a real boundary wireframe, but not shared edges between its faces; the result remains an independent `FACE_SET`.
3. **Did vertical tail traverse the freeform topology path?** Partially. Real B-spline faces and boundary curves exist, but shared-edge/pairwise pcurve topology was not established; it remains `FACE_SET`.
4. **Are profile-sampling edges mixed into Step 6 design edges?** No. `PROFILE_SAMPLE_DESIGN_EDGE_COUNT=0` and `MESH_TRIANGLE_EDGE_IMPORT_COUNT=0`.
5. **Does Step 7 share real TopoDS_Edge instances?** Yes for main wing (12 shared OCC edges); no for fuselage and vertical tail.
6. **Do pcurves exist on both adjacent faces?** Yes for the main-wing shared topology. This is not proven for fuselage/tail because they lack paired shared edges.
7. **Does Step 8 contain real feature instances rather than aliases?** Yes for the three core-part records: one LOFT and two FREEFORM instances with support/affected faces, parameters, constraints, confidence and detection evidence. Full CASE09 coverage was not produced.
8. **Does Step 9 aggregate primitive, wireframe and feature parameters?** Yes for three core parts, with `SOURCE_MODULE` and `SOURCE_ENTITY_ID`. It is not complete for all 8 inferred parts.
9. **Did Qwen3-VL use OBJ + pixels + measured spec?** These inputs were genuinely sent across the ablation modes, including the full multimodal request. The full request returned HTTP 500 and no executable Qwen plan was produced.
10. **Are Qwen3-VL and MAC roles distinguished?** Yes. Qwen3-VL is the local design-intent experiment; MAC is the external multi-agent repair provider. Neither is counted as the other.
11. **Did Step 13 optimize every applicable core part?** No. Only main wing has executed optimizer evidence (2 parameters); fuselage and vertical tail were not optimized. V9F read the existing V8 optimizer artifact rather than freshly applying it to all core parts.
12. **Does Step 17 use orientation, adjacency and feature membership?** Yes. The V2 descriptor/scorer includes all three, supports RESOLVED/AMBIGUOUS/UNRESOLVED, and is not nearest-only. Runtime evidence is main-wing-only.
13. **Did Step 18 complete residual → grounding → local patch → execute → QA → decision?** No. It reached residual/grounding and sent one real provider request; HTTP 403 prevented a patch, execution, QA and accept/rollback.
14. **Does a hidden fallback remain?** No hidden fallback was executed in V9 (`FALLBACK_COUNT=0`). Missing stages remain explicit blockers instead of invoking fallback geometry.
15. **Was a historical STEP reused?** No historical STEP was used as a final V9 part (`HISTORICAL_STEP_REUSED=false`). Separately, V9F reads historical V8 optimization evidence, which is why Step 13 is not credited as fresh full-coverage V9 execution.
16. **Are all final CASE09 parts fresh?** No. No final full set of V9 parts exists, so `ALL_FINAL_PARTS_FRESH=false`.
17. **Was a complete XCAF assembly written?** No. Neither a complete assembly nor a main-wing subset was labeled as V9I success; `FINAL_STEP=NONE`.
18. **Which requested steps can change from partial to full?** None at full CASE09 coverage. V9D and V9G independently pass their scoped module gates, and the eight fitter capabilities are real, but Steps 5/8/9/17 remain PARTIAL under the full-case contract.
19. **Which step is externally resource-blocked?** Step 18/V9H: the real MAC request returned provider HTTP 403 due exhausted free-tier quota. This is not the only V9 blocker.
20. **Can the pipeline expand to Batch9 now?** No. CASE09 has not closed the full loop, so Batch9 expansion is not recommended.

## Regression

Fresh test invocation: 99 passed, 0 failed (V7 Contract 35, V7A 16, V7B 23, V9 5, PhysX V2.1 20). No V7C or V8 pytest suite exists. V8's existing immutable audit reports 45/45 checks passed. PhysX V2.2 was not available, so V2.1 was run. An initial combined invocation had a V7B import-root collection error; rerunning every suite from its required working directory passed.

## Artifacts

- `{ART / 'v9_architecture_status.csv'}`
- `{ART / 'e2e_dependency_matrix.csv'}`
- `{ART / 'v9_actual_runtime_pipeline.txt'}`
- `{ART / 'final_summary.json'}`
- `{ART / 'test_results.json'}`
"""
(ART / "V9_FULLSTACK_ARCHITECTURE_CLOSURE_REPORT.md").write_text(report)
print(json.dumps(summary, indent=2))
