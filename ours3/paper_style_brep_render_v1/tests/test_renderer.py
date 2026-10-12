import json
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/paper_style_brep_render_v1")


def meta(case): return json.loads((ROOT/case/"render_metadata.json").read_text())
def topo(case): return json.loads((ROOT/case/"metrics/brep_topology.json").read_text())


def test_mesh_panel_source_obj_only():
    assert all(meta(c)["MESH_PANEL_SOURCE"] == "SOURCE_OBJ" for c in ("case05","real03"))


def test_mesh_panel_has_triangle_edges():
    assert all(meta(c)["MESH_PANEL_HAS_TRIANGLE_EDGES"] for c in ("case05","real03"))


def test_mesh_panel_no_vertex_scatter():
    assert all(not meta(c)["MESH_PANEL_USES_VERTEX_SCATTER"] for c in ("case05","real03"))


def test_split_panel_has_multiple_regions():
    assert meta("case05")["SPLIT_REGION_COUNT"] == 10 and meta("real03")["SPLIT_REGION_COUNT"] == 26


def test_split_source_p3():
    assert all(meta(c)["SPLIT_VISUALIZATION_TYPE"] == "P3_PARTS" for c in ("case05","real03"))


def test_split_no_triangle_wireframe():
    assert all(not meta(c)["SPLIT_PANEL_HAS_TRIANGLE_WIREFRAME"] for c in ("case05","real03"))


def test_step_fresh_reload():
    assert all(meta(c)["STEP_RELOAD_SUCCESS"] for c in ("case05","real03"))


def test_brep_panel_step_only():
    assert all(meta(c)["BREP_PANEL_SOURCE"] == "STEP_ONLY" for c in ("case05","real03"))


def test_brep_faces_tessellated():
    assert all(meta(c)["BREP_TESSELLATION_TRIANGLE_COUNT"] > 0 for c in ("case05","real03"))


def test_true_brep_edges_extracted():
    assert all(meta(c)["BREP_EDGE_COUNT"] > 0 and meta(c)["EDGE_RENDER_MODE"] == "TRUE_BREP_TOPOLOGY" for c in ("case05","real03"))


def test_no_triangle_edges_in_brep_panel():
    assert all(not meta(c)["TRIANGLE_EDGES_IN_BREP_PANEL"] for c in ("case05","real03"))


def test_brep_vertices_extracted():
    assert all(meta(c)["BREP_VERTEX_COUNT"] > 0 for c in ("case05","real03"))


def test_duplicate_edges_removed():
    assert all("IndexedMapOfShape" in topo(c)["DUPLICATE_EDGE_HANDLING"] for c in ("case05","real03"))


def test_rendered_edges_accounted_for():
    for c in ("case05","real03"):
        t=topo(c); assert t["RENDERED_BREP_EDGE_COUNT"] + t["UNRENDERED_DEGENERATE_EDGE_COUNT"] == t["BREP_EDGE_COUNT"]


def test_curved_edges_smooth():
    assert all(topo(c)["CURVED_EDGE_MIN_SAMPLE_COUNT"] >= 32 for c in ("case05","real03"))


def test_same_camera():
    for c in ("case05","real03"):
        m=meta(c); assert m["WORLD_SCALE_SHARED"] and len(m["CAMERA_DIRECTION"]) == 3


def test_same_world_scale():
    assert all(meta(c)["CAMERA_PARALLEL_SCALE"] > 0 for c in ("case05","real03"))


def test_orthographic_camera():
    assert all(meta(c)["CAMERA_PROJECTION"] == "ORTHOGRAPHIC" for c in ("case05","real03"))


def test_white_background():
    for c in ("case05","real03"):
        assert meta(c)["BACKGROUND"] == "#FFFFFF"
        im=np.asarray(Image.open(ROOT/c/"brep_model.png").convert("RGB")); assert np.all(im[0,0] >= 250)


def test_panel_resolution():
    for c in ("case05","real03"):
        assert Image.open(ROOT/c/"mesh_model.png").size[0] >= 1000


def test_brep_wireframe_output():
    assert all((ROOT/c/"brep_wireframe.png").stat().st_size > 10000 for c in ("case05","real03"))


def test_part_colored_output():
    assert all((ROOT/c/"brep_model_part_colored.png").stat().st_size > 10000 for c in ("case05","real03"))


def test_comparison_figure():
    for c in ("case05","real03"):
        image=Image.open(ROOT/c/"comparison_figure.png"); assert image.width >= 2400 and image.height >= 900


def test_four_panel_figure():
    assert all((ROOT/c/"comparison_figure_4panel.png").stat().st_size > 10000 for c in ("case05","real03"))


def test_no_source_mesh_in_brep():
    assert all(not meta(c)["BREP_RENDER_USES_SOURCE_MESH"] for c in ("case05","real03"))


def test_faceted_brep_audit():
    assert all("FACETED_MESH_WRAPPED_AS_BREP" in topo(c) for c in ("case05","real03"))


def test_real03_holes_visible():
    m=meta("real03"); assert m["RECOVERED_HOLE_COUNT"] == 10 and m["REAL03_HOLE_VISIBILITY_QA"] and m["REAL03_HOLE_ONE_TO_ONE_MATCH_COUNT"] == 10 and m["REAL03_HOLE_NEGATIVE_SPACE_PASS_COUNT"] == 10


def test_real03_source_auto_resolved():
    assert meta("real03")["SOURCE_OBJ_PROVENANCE_PATH"].endswith("fusion_pipeline/cases/REAL_03/source.json")


def test_no_pipeline_reruns():
    for c in ("case05","real03"):
        m=meta(c); assert m["NEW_P3_RUNS"] == m["NEW_PHYSX_RUNS"] == m["NEW_MAC_RUNS"] == m["NEW_LLM_CALLS"] == 0


def test_step_geometry_unmodified():
    assert all(not meta(c)["CAD_GEOMETRY_MODIFIED"] for c in ("case05","real03"))
