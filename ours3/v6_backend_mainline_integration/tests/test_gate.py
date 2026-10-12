import csv
import json
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v6_backend_mainline_integration")


def summary():
    return json.loads((ROOT / "artifacts/final_summary.json").read_text())


def test_v6_registered_and_fresh():
    value = summary()
    assert value["V6_GEOMETRY_BACKEND_REGISTERED"]
    assert value["V6_GEOMETRY_BACKEND_USED_IN_MAINLINE"]
    assert value["V6_MAINLINE_FRESH_EXECUTION_COUNT"] == 6
    assert value["V6_BACKEND_FRESH_BREP_COUNT"] == 6
    assert value["V6_BACKEND_RELOAD_VALID_COUNT"] == 6


def test_no_historical_geometry_reuse():
    value = summary()
    assert value["V6_MAINLINE_HISTORICAL_STEP_REUSE_COUNT"] == 0
    assert value["CURRENT_HISTORICAL_STEP_REUSE_COUNT"] == 0
    assert value["V7D3_HISTORICAL_FINAL_STEP_REUSE_COUNT"] == 0
    manifest = json.loads((ROOT / "artifacts/mainline_selected_artifact_manifest.json").read_text())
    assert len(manifest["parts"]) == 8
    for part in manifest["parts"]:
        assert "v6_geometry_backend_restore" not in part["selected_step_path"]
        assert "v12_full_cad_part_router" not in part["selected_step_path"]
        assert Path(part["selected_step_path"]).is_file()


def test_external_safety_wrapper():
    rows = list(csv.DictReader((ROOT / "artifacts/v6_backend_safety_wrapper_summary.csv").open()))
    assert len(rows) == 6
    assert all(row["fresh_brep"] == "True" for row in rows)
    assert all(row["reload_valid"] == "True" for row in rows)
    assert all(row["geometry_explosion"] == "False" for row in rows)


def test_v6_selection_gate():
    value = summary()
    assert value["V6_BACKEND_SELECTED_PART_COUNT"] >= 3
    assert value["V6_BACKEND_INVALID_SELECTED_COUNT"] == 0
    assert value["DIRECT_PLAN_TO_OCC_BYPASS_COUNT"] == 0


def test_vertical_tail_hybrid_contract():
    value = summary()
    assert value["VERTICAL_TAIL_HYBRID_IMPLEMENTED"]
    assert value["VERTICAL_TAIL_HYBRID_SHARED_EDGE"] >= 1
    assert value["VERTICAL_TAIL_HYBRID_PCURVE"] >= 2
    assert value["VERTICAL_TAIL_HYBRID_TRIMMED_FACE"] >= 2
    assert value["VERTICAL_TAIL_HYBRID_PASS"]
    row = next(csv.DictReader((ROOT / "artifacts/vertical_tail_hybrid_audit.csv").open()))
    assert row["pre_export_post_reload_topology_match"] == "True"
    assert row["geometry_fidelity_over_current"] == "True"


def test_current_builder_mesh_read_contract():
    value = summary()
    assert value["CURRENT_BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT"] == 0
    assert value["INVALID_CURRENT_BUILDER_EXECUTED_COUNT"] == 0


def test_whole_object_and_v13():
    value = summary()
    assert value["CASE09_FINAL_SELECTION_COMPLETE"]
    assert value["CASE09_WHOLE_OBJECT_FIDELITY_IMPROVED"]
    assert value["V13_RERUN_STARTED"]
    assert value["V13_RERUN_PASS"]
    assert value["V13_CONSUMED_SELECTED_ARTIFACT_MATCH"]


def test_required_artifacts():
    for name in (
        "v6_mainline_candidate_summary.csv",
        "v6_mainline_selection_summary.csv",
        "vertical_tail_hybrid_audit.csv",
        "v6_backend_safety_wrapper_summary.csv",
        "mainline_selected_artifact_manifest.json",
        "case09_mainline_v6_integration_shaded.png",
        "case09_mainline_v6_integration_true_edges.png",
        "case09_mainline_v6_selected_parts_preview.png",
        "case09_current_vs_v6_integrated_whole_object.png",
        "V6_BACKEND_MAINLINE_INTEGRATION_REPORT.md",
    ):
        assert (ROOT / "artifacts" / name).is_file()
