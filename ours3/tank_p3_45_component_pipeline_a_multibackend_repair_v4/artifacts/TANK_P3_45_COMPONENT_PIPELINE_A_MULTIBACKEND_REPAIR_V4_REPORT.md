# TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4

CURRENT_GATE=TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4_CANDIDATE_ACTIVATION_FAIL
NEXT_PRIMARY_BLOCKER=MAC_CONSTRUCTION_GENERALIZATION
SOURCE_OBJ=/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj
FROZEN_P3_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_rerun_v1/p3_max_367k_4000
P3_REEXECUTED=False
P3_COMPONENT_COUNT=45
CROSS_P3_COMPONENT_MERGE_COUNT=0
CANARY_COMPONENT_COUNT=9
PIPELINE_A_FULLSTACK_RESTORED=True

## Pipeline A reuse audit
{
  "candidate_contract_reused": false,
  "dual_modal_adapter_reused": true,
  "feature_graph_reused": true,
  "finalize_module": "/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD/multi_agent_cad/graph.py",
  "geometry_analyzer_reused": true,
  "mac_module": "/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD/multi_agent_cad/nodes.py",
  "prepare_module": "/data/home/cuiyuehan/project/mesh2cad/scripts/tank_p3_45_component_pipeline_a_multibackend_repair_v4.py",
  "ranking_reused": false,
  "repair_module": "/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD/multi_agent_cad/nodes.py",
  "runtime_fitter_reused": false,
  "runtime_module": "/data/home/cuiyuehan/project/mesh2cad/Multi-Agent-CAD/multi_agent_cad/nodes.py",
  "semantic_surface_reused": true,
  "targeted_repair_reused": false,
  "v3_summary": {
    "CURRENT_GATE": "TANK_P3_45_COMPONENT_MIXED_CAD_RECOVERY_V3_CAD_NATIVE_FAIL",
    "CURRENT_V6_COMPONENTS_ROUTED": 4,
    "CURRENT_V6_COMPONENTS_SELECTED": 0,
    "FACETED_FALLBACK_COMPONENTS": 45,
    "POINT2CAD_COMPONENTS_SELECTED": 0,
    "SUPERFIT_COMPONENTS_SELECTED": 0
  }
}

## Pipeline correspondence
{
  "airplane_pipeline": {
    "finalize": "v6_finalize.py",
    "mac": "v6_mac.py",
    "prepare": "v6_prepare.py",
    "repair": "v6_repair.py",
    "runtime": "v6_runtime"
  },
  "reused_modules": {
    "geometry_analyzer": "tank_p3_45_component_mixed_cad_recovery_v3.py",
    "local_qa": "tank_p3_point2cad_component_local_qa_v2.py",
    "mac_graph": "Multi-Agent-CAD/multi_agent_cad/graph.py",
    "mac_nodes": "Multi-Agent-CAD/multi_agent_cad/nodes.py"
  },
  "tank_pipeline": {
    "finalize": "component ranking + assembly",
    "mac": "Multi-Agent-CAD graph original workflow",
    "prepare": "component_geometry_analyzer + semantic_surface + feature_graph + dual_modal",
    "repair": "autonomous_skill_loop",
    "runtime": "per-component build123d / STEP / STL execution"
  }
}

## Final summary
```text
CURRENT_GATE=TANK_P3_45_COMPONENT_PIPELINE_A_MULTIBACKEND_REPAIR_V4_CANDIDATE_ACTIVATION_FAIL
NEXT_PRIMARY_BLOCKER=MAC_CONSTRUCTION_GENERALIZATION
PIPELINE_A_FULLSTACK_RESTORED=True
SOURCE_OBJ=/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj
FROZEN_P3_ROOT=/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_rerun_v1/p3_max_367k_4000
P3_REEXECUTED=False
P3_COMPONENT_COUNT=45
CROSS_P3_COMPONENT_MERGE_COUNT=0
CANARY_COMPONENT_COUNT=9
CURRENT_V3_MAC_GENERATED_CANDIDATES=0
CURRENT_V3_MAC_GENERATED_STEP_SUCCESS=0
CURRENT_V3_CURRENT_V6_CANDIDATES=4
CURRENT_V3_SUPERFIT_CANDIDATES=0
CURRENT_V3_POINT2CAD_CANDIDATES=0
CURRENT_V3_HYBRID_CANDIDATES=0
CURRENT_V3_FACETED_FALLBACK_COMPONENTS=45
PIPELINE_A_WAS_NOT_FULLY_EXECUTED=True
MAC_CANDIDATES_CREATED=9
MAC_STEP_SUCCESS=0
MAC_QA_PASS=0
CURRENT_V6_CANDIDATES_CREATED=3
CURRENT_V6_STEP_SUCCESS=3
CURRENT_V6_QA_PASS=0
SUPERFIT_CANDIDATES_CREATED=3
SUPERFIT_STEP_SUCCESS=3
SUPERFIT_QA_PASS=0
POINT2CAD_REAL_EXECUTED_COMPONENTS=3
POINT2CAD_CANDIDATES_CREATED=3
POINT2CAD_SURFACE_SUCCESS=0
POINT2CAD_TOPOLOGY_SUCCESS=0
HYBRID_CANDIDATES_CREATED=0
CAD_NATIVE_QA_PASS_COMPONENTS=0
FACETED_FALLBACK_COMPONENTS=45
PURE_CAD_NATIVE_COMPONENTS=0
HYBRID_WITH_FACETED_RESIDUAL_COMPONENTS=0
PURE_FACETED_COMPONENTS=45
CAD_NATIVE_RECOVERY_RATE=0.0
CAD_NATIVE_TRIANGLE_SUPPORT=0
CAD_NATIVE_TRIANGLE_SUPPORT_RATIO=0.0
FACETED_TRIANGLE_SUPPORT=367466
FINAL_COMPONENT_COUNT=45
FINAL_SOLID_COUNT=0
FINAL_CLOSED_SHELL_COUNT=0
FINAL_OPEN_SHELL_COUNT=45
FINAL_FACE_COUNT=None
GLOBAL_DENSE_MESH_CONTAINS_USED=False
BASELINE_FACETED_STEP=/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_45_component_mixed_cad_recovery_v3/14_assembly/tank_p3_45_component_assembly.step
MIXED_CAD_STEP=None
MIXED_CAD_STEP_RELOAD=False
TESTS_PASSED=0
TESTS_FAILED=0
```
