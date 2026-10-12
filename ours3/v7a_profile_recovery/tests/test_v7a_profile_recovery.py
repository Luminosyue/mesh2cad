import json
from pathlib import Path

import pytest

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v7a_profile_recovery")
SUMMARY = json.loads((OUT / "artifacts/pretest_summary.json").read_text())


def test_case09_profile_audit_complete():
    assert SUMMARY["CASE09_PROFILE_AUDIT_COMPLETE"]


def test_raw_profile_count_positive():
    assert sum(item["profile_count"] for item in SUMMARY["part_stats"].values()) == 36


def test_gate_is_truthful_partial():
    assert SUMMARY["CURRENT_GATE"] == "V7A_ROBUST_PROFILE_RECOVERY_PARTIAL"
    assert SUMMARY["NEW_TRUE_CLOSED_PROFILE_RATE"] < .60
    assert SUMMARY["TRUE_OR_SMALL_GAP_REPAIRED_RATE"] < .75


def test_no_fallback_profiles():
    assert SUMMARY["FALLBACK_PROFILE_RATE"] == 0


def test_no_bbox_or_hull_recovery_code():
    text = (OUT / "geometry/profile_recovery.py").read_text().lower()
    assert "convex_hull" not in text and "alpha_shape" not in text


def test_triangle_plane_profile_provenance():
    for path in (OUT / "04_measured_spec").glob("*/measured_cad_spec.json"):
        spec = json.loads(path.read_text())
        assert spec["profile_source"] == "HIGH_POLY_TRIANGLE_PLANE_INTERSECTION"
        assert all(profile["source"] == "HIGH_POLY_TRIANGLE_PLANE_INTERSECTION"
                   for profile in spec["profiles"])


def test_profile_provenance_fields_complete():
    for path in (OUT / "04_measured_spec").glob("*/measured_cad_spec.json"):
        spec = json.loads(path.read_text())
        for profile in spec["profiles"]:
            assert {"station_id", "requested_t", "actual_t", "raw_segment_count",
                    "true_closed", "repair_applied", "outer_loop", "inner_loops",
                    "resampling", "smooth_curve"} <= set(profile)


def test_orientation_and_resampling_contract():
    for path in (OUT / "04_measured_spec").glob("*/measured_cad_spec.json"):
        for profile in json.loads(path.read_text())["profiles"]:
            assert profile["outer_loop"]["orientation"] == "CCW"
            assert len(profile["points_2d"]) == 64
            assert profile["profile_polyline_is_sampling_only"]


def test_smooth_curves_valid():
    for path in (OUT / "04_measured_spec").glob("*/measured_cad_spec.json"):
        assert all(profile["smooth_curve"]["valid"]
                   for profile in json.loads(path.read_text())["profiles"])


def test_profile_dependency_counterfactual():
    assert SUMMARY["PROFILE_CONTRACT_PERTURBATION_EFFECTIVE"]


def test_profile_swap_counterfactual():
    assert SUMMARY["PROFILE_SWAP_PERTURBATION_EFFECTIVE"]


def test_invalid_profile_runtime_rejected():
    assert SUMMARY["INVALID_PROFILE_RUNTIME_REJECTED"]


def test_runtime_does_not_remeasure_profiles():
    text = (OUT / "scripts/v7a_runtime.py").read_text()
    assert "trimesh" not in text and ".section(" not in text
    assert SUMMARY["RUNTIME_PROFILE_REMEASUREMENT"] is False


def test_runtime_contract_fields():
    for path in (OUT / "06_candidates").glob("*/FRESH_PRIMARY/candidate_execution_contract.json"):
        contract = json.loads(path.read_text())
        assert not contract["runtime_profile_remeasurement"]
        assert not contract["runtime_axis_remeasurement"]
        assert not contract["runtime_station_regeneration"]
        assert contract["profile_polyline_is_sampling_only"]
        assert contract["smooth_profile_curve_consumed"]


def test_required_artifacts_exist():
    for key in ("FINAL_STEP", "PROFILE_QUALITY_CSV", "PROFILE_DEBUG_CONTACT_SHEET", "REPORT"):
        assert Path(SUMMARY[key]).is_file() and Path(SUMMARY[key]).stat().st_size > 0


def test_all_source_parts_truthfully_non_watertight():
    assert all(not stats["mesh_watertight"] for stats in SUMMARY["part_stats"].values())
