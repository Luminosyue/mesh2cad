import json
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1")
S = json.loads((ROOT / "artifacts/summary.json").read_text())
A = json.loads((ROOT / "task_a/artifacts/task_a_summary.json").read_text())
B = json.loads((ROOT / "task_b/artifacts/task_b_summary.json").read_text())
C = json.loads((ROOT / "task_c/artifacts/task_c_summary.json").read_text())
I = json.loads((ROOT / "isolation/isolation_verification.json").read_text())


def test_gate(): assert S["CURRENT_GATE"] == "PARALLEL_PIPELINE_DIAGNOSTICS_V1_PASS"
def test_no_blockers(): assert S["BLOCKERS"] == []
def test_case09_not_touched(): assert S["CASE09_TOUCHED"] is False and I["DIAGNOSTIC_CASE09_TOUCHED"] is False
def test_concurrent_case09_disclosed(): assert S["CONCURRENT_CASE09_ACTIVITY_OBSERVED"] is True and S["CASE09_POINT_IN_TIME_ONLY"] is True
def test_isolation_pass(): assert I["ISOLATION_PASS"] is True
def test_no_shared_code_changes(): assert I["SHARED_CODE_CHANGED"] == []
def test_no_step_generated_in_diagnostic(): assert I["STEP_FILES_INSIDE_DIAGNOSTIC_TASK"] == []
def test_no_preexisting_step_deleted(): assert I["PREEXISTING_STEPS_DELETED"] == []


@pytest.mark.parametrize("name", [
    "TASK_A_PASS", "TASK_B_PASS", "TASK_C_PASS", "CASE09_NOT_TOUCHED_BY_DIAGNOSTIC", "ISOLATION_PASS",
    "NO_SUBTASK_TEST_FAILURES", "NO_FORBIDDEN_GPU_INFERENCE", "NO_FORBIDDEN_CAD_GENERATION", "NO_MAC_OR_LLM", "NO_UNRESTRICTED_ICP",
])
def test_criterion(name): assert S["CRITERIA"][name] is True


@pytest.mark.parametrize("cid,expected", [
    ("02", "FRAGMENTED_SPLINE_BREP"), ("03", "ANALYTIC_FEATURE_BREP"),
    ("04", "FRAGMENTED_SPLINE_BREP"), ("05", "FRAGMENTED_SPLINE_BREP"),
    ("08", "FRAGMENTED_SPLINE_BREP"), ("09", "UNKNOWN"),
])
def test_structural_classes(cid, expected): assert S[f"CASE{cid}_STRUCTURAL_CLASS"] == expected


def test_six_structure_cases(): assert S["CASES_AUDITED"] == 6 and A["ARTIFACTS_AUDITED"] == 14
def test_case09_surface_accounting(): assert S["CASE09_TOTAL_FACES"] == 92 and 0 <= S["CASE09_BSPLINE_RATIO"] <= 1
def test_case09_group_accounting(): assert 1 <= S["CASE09_SURFACE_GROUPS"] <= S["CASE09_TOTAL_FACES"]
def test_case09_strip_accounting(): assert 0 <= S["CASE09_STRIP_EDGE_RATIO"] <= 1 and S["CASE09_STRIP_EDGE_COUNT"] >= 0
def test_contact_sheet():
    p = Path(S["STRUCTURE_CONTACT_SHEET"]); assert p.is_file() and Image.open(p).size[0] >= 1000


def test_case06_metrics(): assert S["CASE06_P3_SEGMENTS"] == 2 and S["CASE06_CAD_PARTS"] == 2 and S["CASE06_UNASSIGNED_AREA_RATIO"] == 0
def test_case06_rootcause(): assert S["CASE06_PRIMARY_ROOT_CAUSE"] == "PART_CADABILITY_FAILURE"
def test_case07_metrics(): assert S["CASE07_P3_SEGMENTS"] == 30 and S["CASE07_CAD_PARTS"] == 33
def test_case07_coverage_improved(): assert S["CASE07_OLD_COVERAGE"] < .11 and S["CASE07_PART_GRAPH_COVERAGE"] == 1.0
def test_case07_rootcause(): assert S["CASE07_PRIMARY_ROOT_CAUSE"] == "ROUTER_FAILURE" and S["CASE07_ROOT_CAUSE_DETAIL"] == "AREA_UNAWARE_MAX_READY_PARTS_TRUNCATION"
def test_task_b_no_inference(): assert B["P3_INFERENCE_RUNS"] == B["PHYSX_INFERENCE_RUNS"] == 0 and B["GPU_USED"] is False
def test_task_b_no_cad_generation(): assert B["LOFT_RUNS"] == B["BSPLINE_RUNS"] == B["STEP_GENERATED"] == 0


def test_case01_primary(): assert S["CASE01_PRIMARY_ROOT_CAUSE"] == "OTHER" and "STALE_CANDIDATE_A" in S["CASE01_PRIMARY_ROOT_CAUSE_DETAIL"]
def test_case01_secondary(): assert S["CASE01_SECONDARY_CAUSES"] == ["SURFACE_FIT_FAILURE", "BRep_VALID_BUT_GEOMETRY_Q3"]
def test_case01_failure_split(): assert S["CASE01_RESOURCE_FAILURE"] is True and S["CASE01_GEOMETRY_FAILURE"] is True and C["RESOURCE_TIMEOUT_ONLY_REJECTED"] is True
def test_case01_existing_q1(): assert S["CASE01_BEST_EXISTING_CANDIDATE_Q"] == "Q1" and C["CANDIDATE_Q1"] == 2 and C["CANDIDATE_Q3"] == 1
def test_case01_routes(): assert S["CASE01_RESCUE_ROUTE_A"] and S["CASE01_RESCUE_ROUTE_B"]
def test_case01_no_rebuild(): assert C["REBUILD_EXECUTED"] is False and C["UNRESTRICTED_ICP_USED"] is False


@pytest.mark.parametrize("rel", [
    "task_a/artifacts/task_a_summary.json", "task_a/task_a_report.md", "task_b/artifacts/task_b_summary.json",
    "task_b/artifacts/task_b_report.md", "task_c/artifacts/task_c_summary.json",
    "task_c/artifacts/case01_recovery_rootcause_report.md", "task_c/artifacts/case01_provenance_graph.json",
    "isolation/isolation_verification.json", "report.md",
])
def test_required_artifact(rel): assert (ROOT / rel).is_file()


def test_subtask_test_total(): assert S["SUBTASK_TESTS_PASSED"] == A["TESTS_PASSED"] + B["TESTS_PASSED"] + C["TESTS_PASSED"] == 49
def test_subtask_failures_zero(): assert A["TESTS_FAILED"] == B["TESTS_FAILED"] == C["TESTS_FAILED"] == 0
