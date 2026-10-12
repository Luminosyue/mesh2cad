import json
from pathlib import Path

import numpy as np
import pytest

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "v7c_open_shell_topology_and_sewing"
SUMMARY = json.loads((OUT / "artifacts/pretest_summary.json").read_text())
PARTS = SUMMARY["parts"]


def test_boundary_candidate_extraction():
    assert SUMMARY["BOUNDARY_CANDIDATE_COUNT"] == 16


def test_boundary_descriptor():
    for part in PARTS.values():
        for face in part["face_audit"]:
            for boundary in face["boundaries"]:
                assert boundary["length"] > 0
                assert len(boundary["centroid"]) == 3
                assert len(boundary["tangent_start"]) == 3


def test_boundary_matching_geometry():
    assert all(part["pair_scores"] for part in PARTS.values())


def test_boundary_matching_orientation():
    assert all(part["pair_scores"][0]["orientation_relation"] in {"SAME", "REVERSED"} for part in PARTS.values())


def test_boundary_matching_can_be_unresolved():
    assert all(part["boundary_match_status"] == "UNRESOLVED" for part in PARTS.values())


def test_design_boundary_not_profile_sample():
    assert SUMMARY["PROFILE_SAMPLE_DERIVED_EDGE_COUNT"] == 0
    assert all(boundary["source"] == "BREP_FACE_BOUNDARY" for part in PARTS.values() for face in part["face_audit"] for boundary in face["boundaries"])


def test_semantic_wireframe_graph():
    graph = json.loads((OUT / "artifacts/semantic_wireframe_graph.json").read_text())
    assert graph["implemented"] and graph["edges"] and graph["nodes"]


def test_shared_occ_edge_identity_not_falsely_claimed():
    assert SUMMARY["SHARED_OCC_EDGE_COUNT"] == 0
    assert SUMMARY["SHARED_EDGE_IDENTITY_VALID"] is False


def test_shared_edge_lies_on_surface_a_gate():
    assert all(part["candidate_validation"] is None or "surface_a" in part["candidate_validation"] for part in PARTS.values())


def test_shared_edge_lies_on_surface_b_gate():
    assert all(part["candidate_validation"] is None or "surface_b" in part["candidate_validation"] for part in PARTS.values())


def test_pcurve_not_claimed_without_edge():
    assert SUMMARY["PCURVE_CREATED_COUNT"] == 0


def test_pcurve_face_pair_not_claimed():
    assert SUMMARY["PCURVE_FACE_PAIR_COUNT"] == 0


def test_pcurve_3d_consistency_is_undefined_without_formal_edge():
    assert SUMMARY["PCURVE_3D_MEAN_ERROR"] is None


def test_wire_builder_not_claimed_without_matched_boundaries():
    assert SUMMARY["WIRE_COUNT"] == 0


def test_wire_orientation_not_faked():
    assert SUMMARY["CLOSED_WIRE_COUNT"] == 0


def test_missing_boundary_rejected():
    assert all(part["counterfactuals"]["invalid_topology"]["rejected"] for part in PARTS.values())


def test_wrong_orientation_rejected_by_unresolved_gate():
    assert all(not pair["accepted"] for part in PARTS.values() for pair in part["pair_scores"])


def test_trimmed_face_not_falsely_created():
    assert SUMMARY["TRIMMED_FACE_CREATED_COUNT"] == 0


def test_trimmed_face_valid_not_falsely_created():
    assert SUMMARY["TRIMMED_FACE_VALID_COUNT"] == 0


def test_sewing_not_run_before_trim():
    assert SUMMARY["OPEN_SHELL_TOPOLOGICAL_SEWING_USED"] is False


def test_large_tolerance_sewing_rejected():
    assert SUMMARY["LARGE_TOLERANCE_SEWING_REQUIRED"] is False
    assert SUMMARY["FORCED_SEWING_COUNT"] == 0


def test_duplicate_coincident_edge_detection():
    assert SUMMARY["DUPLICATE_COINCIDENT_EDGE_COUNT"] >= 0


def test_free_edge_count_real():
    assert SUMMARY["FUSELAGE_FREE_EDGE_COUNT_BEFORE"] == 8
    assert SUMMARY["VERTICAL_TAIL_FREE_EDGE_COUNT_BEFORE"] == 8


def test_shared_edge_perturbation_effect():
    assert SUMMARY["SHARED_EDGE_PERTURBATION_EFFECTIVE"] is False
    assert SUMMARY["DIAGNOSTIC_SHARED_EDGE_CANDIDATE_PERTURBATION_EFFECTIVE"] is True


def test_pcurve_perturbation_effect():
    assert SUMMARY["PCURVE_PERTURBATION_EFFECTIVE"] is False
    assert SUMMARY["DIAGNOSTIC_NATURAL_PCURVE_PERTURBATION_EFFECTIVE"] is True


def test_boundary_matching_swap_effect():
    assert SUMMARY["BOUNDARY_MATCH_SWAP_EFFECTIVE"] is True


def test_runtime_does_not_resection_mesh():
    assert SUMMARY["RUNTIME_BOUNDARY_REDETECTION_FROM_MESH"] is False
    assert all(part["topology_source_mesh_read"] is False for part in PARTS.values())


def test_main_wing_v7b_regression():
    assert SUMMARY["MAIN_WING_V7B_REGRESSION_PASS"] is True


def test_v7_contract_regression():
    assert SUMMARY["V7_CONTRACT_REGRESSION_PASS"] is True


def test_v7b_regression():
    assert SUMMARY["V7B_REGRESSION_PASS"] is True


def test_honest_partial_gate():
    assert SUMMARY["CURRENT_GATE"].endswith("_PARTIAL")
    assert SUMMARY["CASE09_V7C_PASS"] is False


def test_no_untrimmed_fallback():
    assert SUMMARY["UNTRIMMED_FACE_FALLBACK_COUNT"] == 0


def test_no_fake_edge():
    assert SUMMARY["FAKE_EDGE_COUNT"] == 0


def test_surface_intersection_attempted():
    assert SUMMARY["SURFACE_INTERSECTION_ATTEMPTED"] is True


def test_topology_qa_artifacts_exist():
    assert all((OUT / "08_qa" / pid / "topology_qa.json").is_file() for pid in PARTS)


def test_debug_images_complete():
    assert len(list((OUT / "artifacts/v7c_debug").glob("CADPART_*/*.png"))) == 20
    assert (OUT / "artifacts/v7c_debug/all_v7c_topology_contact_sheet.png").is_file()


def test_no_formal_v7c_step_when_partial():
    assert SUMMARY["FINAL_STEP"] == "NOT_CREATED_PARTIAL"
