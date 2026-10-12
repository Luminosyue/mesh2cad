import hashlib
import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/parallel_pipeline_diagnostics_v1/task_c")

def load(name): return json.loads((ROOT / name).read_text())

def test_summary_gate_and_single_primary():
    s = load("artifacts/task_c_summary.json")
    assert s["CURRENT_GATE"] == "CASE01_RECOVERY_ROOTCAUSE_V1_PASS"
    assert s["PRIMARY_ROOT_CAUSE"] == "OTHER"
    assert s["PRIMARY_ROOT_CAUSE_DETAIL"] == "STALE_CANDIDATE_A_FAILURE_SENTINEL_SKIPPED_VALID_B_AND_C_QA_SELECTION"

def test_all_explicit_candidates_audited():
    s = load("artifacts/task_c_summary.json")
    assert s["CANDIDATE_STEP_COUNT"] == s["CANDIDATE_RELOAD_SUCCESS"] == s["CANDIDATE_BREP_VALID"] == 3
    assert s["CANDIDATE_Q1"] == 2 and s["CANDIDATE_Q3"] == 1
    assert s["RECOVERABLE_EXISTING_CANDIDATES"] == ["candidate_B_loft", "candidate_C_primitive"]

def test_resource_vs_geometry_separated():
    r = load("artifacts/case01_rootcause.json")
    assert r["CASE01_RESOURCE_FAILURE"] and r["CASE01_GEOMETRY_FAILURE"] and r["RESOURCE_TIMEOUT_ONLY_REJECTED"]

def test_no_rebuild_or_provider_or_icp():
    r = load("artifacts/case01_rootcause.json")
    assert not r["REBUILD_EXECUTED"] and r["MAC_LLM_CALLS"] == 0 and not r["UNRESTRICTED_ICP_USED"]

def test_exactly_two_plan_only_rescues():
    r = load("artifacts/case01_rootcause.json")
    assert r["RESCUE_ROUTE_A"]["plan_only"] and r["RESCUE_ROUTE_B"]["plan_only"]
    assert not any(k.startswith("RESCUE_ROUTE_") for k in r if k not in {"RESCUE_ROUTE_A", "RESCUE_ROUTE_B"})

def test_transform_is_saved_and_no_icp():
    t = load("transforms/transform_used.json")
    assert t["matrix_finite"] and t["inverse_roundtrip_max_abs_error"] < 1e-6
    assert t["ledger_roundtrip_pass"] and not t["ledger_icp_used"] and not t["unrestricted_icp_used"]

def test_candidate_step_inputs_unchanged():
    for c in load("artifacts/task_c_summary.json")["CANDIDATES"]:
        p = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/batch_real_mesh2cad_v1/cases/CASE_01/cad_recovery/CADPART_000") / c["candidate"] / "candidate.step"
        assert hashlib.sha256(p.read_bytes()).hexdigest() == c["sha256"]

def test_provenance_graph_case01_only():
    g = load("artifacts/case01_provenance_graph.json")
    assert g["schema"] == "CASE01_PROVENANCE_GRAPH_V1"
    assert "CASE_09" not in json.dumps(g)
    assert sum(n["type"] == "CANDIDATE_STEP" for n in g["nodes"]) == 3

def test_geometry_metric_protocol():
    for c in load("artifacts/task_c_summary.json")["CANDIDATES"]:
        assert c["sample_count_each"] == 50000 and c["seed_source"] == 20260811
        assert c["normalized_symmetric_chamfer"] >= 0 and c["normalized_p95"] >= 0

def test_reports_exist():
    for p in ["artifacts/case01_recovery_rootcause_report.md", "artifacts/case01_candidate_audit.json", "artifacts/case01_geometry_hypothesis_audit.json", "artifacts/case01_log_resource_evidence.json", "artifacts/case01_control_flow_evidence.json"]:
        assert (ROOT / p).is_file()

def test_control_flow_evidence_is_read_only_source_snapshot():
    e = load("artifacts/case01_control_flow_evidence.json")
    assert e["line_range_1_based"] == [146, 149]
    assert any("continue" in x["text"] for x in e["source_lines"])

def test_a_is_geometry_failure_b_and_c_are_recoverable():
    by = {x["candidate"]: x for x in load("artifacts/task_c_summary.json")["CANDIDATES"]}
    assert by["candidate_A_loft"]["geometry_q"] == "Q3"
    assert by["candidate_A_loft"]["mapped_bbox_diagonal"] / 2.604775954723862 > 10000
    assert by["candidate_B_loft"]["geometry_q"] == by["candidate_C_primitive"]["geometry_q"] == "Q1"
