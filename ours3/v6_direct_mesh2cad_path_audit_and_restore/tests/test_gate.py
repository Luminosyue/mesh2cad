import json
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/v6_direct_mesh2cad_path_audit_and_restore")
SUMMARY = json.loads((ROOT / "artifacts/final_summary.json").read_text())


def test_v6_path_truthful():
    assert SUMMARY["V6_MESH2CAD_STYLE_PATH_FOUND"] is True
    assert SUMMARY["V6_DIRECT_VLM_CADQUERY_PATH_FOUND"] is False
    assert SUMMARY["V6_MESH_GUIDED_FITTING_PATH_FOUND"] is True


def test_branch_and_adapter_present():
    assert SUMMARY["MESH2CAD_STYLE_BRANCH_IMPLEMENTED"] is True
    assert SUMMARY["MESH2CAD_TO_V11_ADAPTER_IMPLEMENTED"] is True
    assert (ROOT / "candidate_generators/mesh2cad_program_parser.py").is_file()


def test_dual_modal_artifacts():
    assert SUMMARY["DUAL_MODAL_OBJ_USED_COUNT"] == 5
    assert SUMMARY["DUAL_MODAL_RENDER_USED_COUNT"] == 5
    for part in ("CADPART_000", "CADPART_001", "CADPART_002", "CADPART_003", "CADPART_005"):
        base = ROOT / "cases/CASE09" / part / "dual_modal"
        assert (base / "canonical_obj_tokens.txt").stat().st_size > 0
        assert (base / "part_isometric_render.png").stat().st_size > 0
        assert (base / "source_object_context_render.png").stat().st_size > 0


def test_safety_zeroes():
    for key in (
        "MESH2CAD_RAW_PARAMETER_CONSUMED_FINAL_COUNT",
        "MESH2CAD_DIRECT_FINAL_OCC_BYPASS_COUNT",
        "INVALID_BUILDER_EXECUTED_COUNT",
        "BUILDER_RUNTIME_SOURCE_MESH_READ_COUNT",
        "HISTORICAL_STEP_REUSE_COUNT",
        "GEOMETRY_EXPLOSION_COUNT",
    ):
        assert SUMMARY[key] == 0, (key, SUMMARY[key])


def test_outputs_exist():
    for key in ("REPORT", "V6_AUDIT_CSV", "AB_COMPARISON_CSV", "CONTACT_SHEET", "TRUE_EDGE_CONTACT_SHEET"):
        assert Path(SUMMARY[key]).is_file(), key


def test_vertical_tail_independent_reload():
    assert SUMMARY["CASE09_VERTICAL_TAIL_SELECTED_ARTIFACT_MATCH"] is True

