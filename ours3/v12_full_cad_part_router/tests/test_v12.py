import csv
import json
from pathlib import Path

import pytest

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v12_full_cad_part_router")
S = json.loads((ROOT / "artifacts/v12_summary.json").read_text())


@pytest.mark.parametrize("key", [
    "FULL_CAD_PART_ROUTER_IMPLEMENTED", "PART_STATUS_SCHEMA_USED", "CANDIDATE_ORCHESTRATOR_USED", "FIDELITY_AWARE_TTS_USED", "HISTORICAL_ARTIFACT_INDEPENDENCE_PASS",
    "V10_REGRESSION_PASS", "V11_REGRESSION_PASS", "V11B_REGRESSION_PASS", "V11C_REGRESSION_PASS", "V7D3_REGRESSION_PASS",
])
def test_required_true(key):
    assert S[key] is True


@pytest.mark.parametrize("key", [
    "INVALID_BUILDER_EXECUTED_COUNT", "LOFT_INVALID_EXECUTED_COUNT", "BSPLINE_INVALID_EXECUTED_COUNT", "EXECUTED_PARAMETER_WITHOUT_REF_COUNT", "UNMEASURED_PATTERN_PLACEMENT_COUNT", "DIRECT_PLAN_TO_OCC_BYPASS_COUNT", "RUNTIME_REMEASUREMENT_COUNT", "HISTORICAL_STEP_REUSE_COUNT", "GEOMETRY_EXPLOSION_COUNT", "BUILDER_ELIGIBILITY_CHANGED_BY_SEMANTICS_COUNT",
])
def test_safety_zero(key):
    assert S[key] == 0


@pytest.mark.parametrize("key", ["ALL_CASES_PART_ROUTE_COVERAGE", "CASE09_PART_ROUTE_COVERAGE", "TANK_PART_ROUTE_COVERAGE", "BUILDING_PART_ROUTE_COVERAGE"])
def test_coverage(key):
    assert S[key] == 1.0


def test_counts():
    assert S["PARTS_TOTAL"] == 42
    assert S["PARTS_WITH_TERMINAL_STATUS"] == 42
    assert S["CASE09_PARTS_TOTAL"] == 8
    assert S["TANK_PARTS_TOTAL"] == 13
    assert S["BUILDING_PARTS_TOTAL"] == 21


def test_main_wing_regression():
    assert S["CASE09_MAIN_WING_SELECTED_BUILDER"] == "LOFT"
    assert S["CASE09_MAIN_WING_SILHOUETTE_IOU"] >= 0.85
    assert S["CASE09_MAIN_WING_SECTION_PROFILE_ERROR"] <= 0.20


def test_wheel_evidence_is_honest():
    assert S["TANK_ROAD_WHEEL_CYLINDER_GEOMETRY_SUPPORTED_COUNT"] == 0
    assert S["TANK_ROAD_WHEEL_REVOLUTION_GEOMETRY_SUPPORTED_COUNT"] == 0
    assert S["TANK_ROAD_WHEEL_HIGH_FIDELITY_COUNT"] == 0


def test_open_shell_regression():
    assert S["OPEN_SHELL_FRESH_BREP_COUNT"] >= 1
    assert S["OPEN_SHELL_SHARED_OCC_EDGE_COUNT"] >= 1
    assert S["OPEN_SHELL_PCURVE_COUNT"] >= 2
    assert S["OPEN_SHELL_TRIMMED_FACE_COUNT"] >= 2


def test_counterfactuals():
    cf = S["counterfactuals"]
    assert cf["UNSAFE_CANDIDATE_EXECUTED"] is False
    assert cf["UNSAFE_CANDIDATE_STATUS"] == "BUILDER_REJECTED"
    assert cf["MISSING_CIRCULAR_EVIDENCE_DOES_NOT_ENABLE_CYLINDER"] is True
    assert cf["REASONING_TEXT_GEOMETRY_INVARIANCE_PASS"] is True


def test_terminal_schema_and_fresh_steps():
    rows = list(csv.DictReader((ROOT / "artifacts/v12_part_route_summary.csv").open()))
    assert len(rows) == 42
    assert all(row["STATUS"] and row["STATUS"] != "UNKNOWN_FAIL" for row in rows)
    for row in rows:
        if row["FRESH_BREP"] == "True":
            result = json.loads((ROOT / "cases" / row["CASE"] / "parts" / row["PART"] / "route_result.json").read_text())
            assert result["step_path"].startswith(str(ROOT))
            assert Path(result["step_path"]).is_file()


def test_required_artifacts():
    for name in ["v12_case_summary.csv", "v12_part_route_summary.csv", "v12_candidate_summary.csv", "v12_builder_coverage.csv", "v12_blocker_summary.csv", "v12_fidelity_summary.csv", "v12_pattern_summary.csv", "road_wheel_geometry_audit.csv", "v12_source_vs_selected_contact_sheet.png", "V12_FULL_CAD_PART_ROUTER_REPORT.md"]:
        path = ROOT / "artifacts" / name
        assert path.is_file() and path.stat().st_size > 0
