import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import trimesh
from PIL import Image


OURS3 = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
ROOT = OURS3 / "whole_machine_hybrid_preview_gate0"
HYBRID = ROOT / "hybrid"
ART = ROOT / "artifacts"
ACCEPTED = OURS3 / "real03_high_fidelity_parts_v2"
GRAPH = OURS3 / "cad_part_graph_gate1/cases"
FULL = OURS3 / "meshes/30_CONSTRUCTION_SET.obj"
PARTS = ["CADPART_000", "CADPART_004"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@pytest.fixture(scope="session")
def summary():
    return load(ART / "summary.json")


@pytest.fixture(scope="session")
def provenance():
    return load(HYBRID / "hybrid_provenance.json")


def test_gate_pass(summary):
    assert summary["CURRENT_GATE"] == "WHOLE_MACHINE_HYBRID_PREVIEW_GATE_0_PASS"


def test_scientific_semantics(summary, provenance):
    assert summary["SCIENTIFIC_SEMANTICS"] == "HYBRID_MESH_CAD_PREVIEW"
    assert provenance["scientific_semantics"] == "HYBRID_MESH_CAD_PREVIEW"


def test_not_full_cad(summary):
    assert summary["FULL_CAD_RECOVERY_COMPLETE"] is False
    assert summary["FULL_CAD_ASSEMBLY_COMPLETE"] is False


def test_full_source_mesh_loaded(summary):
    assert summary["FULL_SOURCE_MESH_LOADED"] is True
    assert FULL.is_file()


def test_exact_recovered_parts(summary):
    assert summary["RECOVERED_CAD_PARTS"] == 2
    assert summary["RECOVERED_PART_IDS"] == PARTS
    assert summary["Q1_PARTS"] == summary["Q2_PARTS"] == 1


def test_q3_parts_excluded(summary):
    assert "CADPART_001" not in summary["RECOVERED_PART_IDS"]
    assert "CADPART_006" not in summary["RECOVERED_PART_IDS"]


@pytest.mark.parametrize("part_id", PARTS)
def test_source_triangle_ids_valid(part_id):
    ids = np.load(GRAPH / part_id / "source_triangle_ids.npy")
    assert len(ids) == len(np.unique(ids))
    assert int(ids.min()) >= 0 and int(ids.max()) < 385828


def test_source_triangle_sets_disjoint():
    a = np.load(GRAPH / "CADPART_000/source_triangle_ids.npy")
    b = np.load(GRAPH / "CADPART_004/source_triangle_ids.npy")
    assert len(np.intersect1d(a, b)) == 0


def test_residual_mesh_created(summary):
    path = HYBRID / "REAL_03_residual_mesh.obj"
    assert summary["RESIDUAL_MESH_CREATED"] is True
    assert path.is_file() and path.stat().st_size > 1_000_000


def test_residual_triangle_count(summary):
    residual = trimesh.load(HYBRID / "REAL_03_residual_mesh.obj", force="mesh", process=False)
    assert len(residual.faces) == summary["RESIDUAL_SOURCE_TRIANGLE_COUNT"] == 355020


def test_source_triangle_accounting(summary):
    assert summary["FULL_SOURCE_TRIANGLE_COUNT"] == 385828
    assert summary["RECOVERED_SOURCE_TRIANGLE_COUNT"] == 18776 + 12032
    assert summary["RESIDUAL_SOURCE_TRIANGLE_COUNT"] + summary["RECOVERED_SOURCE_TRIANGLE_COUNT"] == summary["FULL_SOURCE_TRIANGLE_COUNT"]
    assert summary["SOURCE_TRIANGLE_ACCOUNTING_PASS"] is True


def test_exact_triangle_removal_policy(provenance):
    assert provenance["triangle_removal_policy"] == "EXACT_SOURCE_TRIANGLE_IDS_ONLY"
    assert provenance["bbox_crop_used"] is False
    assert provenance["distance_threshold_delete_used"] is False
    assert provenance["manual_selection_used"] is False


@pytest.mark.parametrize("part_id", PARTS)
def test_accepted_step_sha_frozen(part_id, provenance):
    assert provenance["accepted_step_sha256"][part_id] == sha256(ACCEPTED / part_id / "best.step")


@pytest.mark.parametrize("part_id", PARTS)
def test_global_cad_inserted(part_id, summary):
    path = HYBRID / f"{part_id}_global_cad.obj"
    assert summary[f"{part_id}_INSERTED"] is True
    assert path.is_file() and path.stat().st_size > 100000


@pytest.mark.parametrize("part_id", PARTS)
def test_fresh_step_tessellation(part_id):
    path = HYBRID / f"{part_id}_fresh_canonical.stl"
    assert path.is_file() and path.stat().st_size > 100000


def test_hybrid_object_complete(summary):
    assert summary["HYBRID_OBJECT_COMPLETE"] is True


def test_coverage_positive_and_partial(summary):
    assert 0 < summary["HYBRID_CAD_AREA_COVERAGE"] < 1
    assert 0 < summary["HYBRID_MESH_AREA_COVERAGE"] < 1


def test_coverage_sums_to_one(summary):
    assert abs(summary["HYBRID_CAD_AREA_COVERAGE"] + summary["HYBRID_MESH_AREA_COVERAGE"] - 1.0) < 1e-15


def test_coverage_matches_frozen_result(summary):
    frozen = load(OURS3 / "cad_partial_assembly_gate0/artifacts/assembly_metrics.json")
    assert abs(summary["HYBRID_CAD_AREA_COVERAGE"] - frozen["PARTIAL_AREA_COVERAGE"]) < 1e-12


def test_remaining_geometry_is_mesh(summary, provenance):
    assert summary["REMAINING_GEOMETRY_TYPE"] == "MESH"
    assert provenance["remaining_geometry_type"] == "MESH"


def test_no_boolean_union(provenance):
    assert provenance["boolean_union_used"] is False


def test_glb_created(summary):
    path = Path(summary["HYBRID_GLB_PATH"])
    assert summary["HYBRID_GLB_CREATED"] is True
    assert path.is_file() and path.stat().st_size > 1_000_000


def test_glb_three_independent_nodes(summary):
    scene = trimesh.load(summary["HYBRID_GLB_PATH"], force="scene", process=False)
    expected = ["CADPART_000_Q1", "CADPART_004_Q2", "Residual_HighMesh"]
    assert sorted(scene.geometry.keys()) == expected
    assert sorted(scene.graph.nodes_geometry) == expected
    assert len(scene.geometry) == 3


def test_glb_not_merged(provenance):
    assert provenance["glb_nodes_independent"] is True


@pytest.mark.parametrize("name", [
    "REAL_03_whole_machine_hybrid.png",
    "REAL_03_whole_machine_hybrid_contact_sheet.png",
    "whole_machine_before_after.png",
    "whole_machine_cad_highlight.png",
    "whole_machine_cad_wireframe.png",
])
def test_visualization_generated(name):
    path = ART / name
    assert path.is_file() and path.stat().st_size > 100000
    with Image.open(path) as image:
        assert image.width >= 1500 and image.height >= 1000


def test_main_preview_path(summary):
    assert Path(summary["MAIN_PREVIEW_PATH"]) == ART / "REAL_03_whole_machine_hybrid.png"


def test_contact_sheet_path(summary):
    assert Path(summary["CONTACT_SHEET_PATH"]) == ART / "REAL_03_whole_machine_hybrid_contact_sheet.png"


def test_whole_machine_visual_complete(summary):
    assert summary["WHOLE_MACHINE_VISUAL_COMPLETE"] is True


def test_no_p3_runs(summary, provenance):
    assert summary["NEW_P3_RUNS"] == provenance["new_p3_runs"] == 0


def test_no_physx_runs(summary, provenance):
    assert summary["NEW_PHYSX_RUNS"] == provenance["new_physx_runs"] == 0


def test_no_mac_runs(summary, provenance):
    assert summary["NEW_MAC_RUNS"] == provenance["new_mac_runs"] == 0


def test_no_llm_calls(summary, provenance):
    assert summary["NEW_LLM_CALLS"] == provenance["new_llm_calls"] == 0


def test_no_geometry_fitting_runs(summary, provenance):
    assert summary["NEW_GEOMETRY_FITTING_RUNS"] == provenance["new_geometry_fitting_runs"] == 0


def test_blender_not_installed_or_claimed(summary):
    assert summary["BLENDER_SCENE_CREATED"] is False
    assert not list(ROOT.rglob("*.blend"))


def test_report_semantics():
    text = (ART / "whole_machine_hybrid_report.md").read_text(encoding="utf-8")
    assert "HYBRID_MESH_CAD_PREVIEW" in text
    assert "FULL_CAD_RECOVERY_COMPLETE=false" in text
    assert "FULL_CAD_ASSEMBLY_COMPLETE=false" in text


def test_no_blockers(summary):
    assert summary["BLOCKERS"] == []
