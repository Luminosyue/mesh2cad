import json
from pathlib import Path

OUT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/batch10_semantic_mesh2cad_tts_v5")
CASE09 = json.loads((OUT / "09_case09_smoke/case09_smoke_summary.json").read_text())
REG = json.loads((OUT / "artifacts/best_result_registry.json").read_text())


def test_p3_preserved():
    manifest = json.loads((OUT / "00_provenance/frozen_10_case_source_manifest.json").read_text())
    assert manifest["cases"]["CASE_09"]["source_is_original_obj_geometry"]


def test_physx_preserved():
    assert Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/01_part_discovery/physx/physx_part_hypotheses.json").is_file()


def test_part_graph_preserved():
    assert Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_aircraft_end2end_cad_v1/02_cad_part_graph/cad_part_graph.json").is_file()


def test_original_obj_geometry_source():
    for row in CASE09["part_results"]:
        spec = json.loads(Path(row["measured_cad_spec"]).read_text())
        assert spec["measurement_source"] == "original_high_poly_part_mesh"
        assert spec["proxy_mesh_used_for_exact_measurement"] is False


def test_semantic_surface_v2():
    for row in CASE09["part_results"]:
        ssg = json.loads(Path(row["semantic_surface_graph"]).read_text())
        assert ssg["schema"] == "SemanticSurfaceAnalyzerV2"
        assert "GLOBAL_LOFT_SURFACE" in ssg["supported_surface_types"]


def test_sampling_topology_not_propagated():
    for row in CASE09["part_results"]:
        ssg = json.loads(Path(row["semantic_surface_graph"]).read_text())
        assert ssg["mesh_triangles_are_fitting_constraints_only"]
        assert ssg["mesh_patch_boundaries_final_topology"] is False
        assert ssg["section_sampling_boundaries_final_topology"] is False


def test_dual_modal_mesh_adapter():
    for row in CASE09["part_results"]:
        adapter = row["dual_modal_adapter"]
        assert Path(adapter["canonical_obj_tokens"]).is_file()
        assert Path(adapter["axonometric_render"]).is_file()
        assert adapter["render_may_not_override_measured_dimensions"]


def test_proxy_mesh_source_mapping():
    for row in CASE09["part_results"]:
        adapter = row["dual_modal_adapter"]
        assert adapter["proxy_to_source_mapping"]
        assert adapter["source_triangle_count"] >= adapter["proxy_triangle_count"]


def test_canonical_obj_tokens():
    sample = Path(CASE09["part_results"][0]["dual_modal_adapter"]["canonical_obj_tokens"]).read_text().splitlines()
    assert any(x.startswith("v ") for x in sample)
    assert any(x.startswith("f ") for x in sample)


def test_part_render():
    for row in CASE09["part_results"]:
        assert Path(row["dual_modal_adapter"]["axonometric_render"]).stat().st_size > 100


def test_exact_measurement_not_proxy():
    for row in CASE09["part_results"]:
        spec = json.loads(Path(row["measured_cad_spec"]).read_text())
        assert spec["triangle_count"] > 0
        assert spec["proxy_mesh_used_for_exact_measurement"] is False


def test_design_intent_hypotheses():
    for row in CASE09["part_results"]:
        assert 2 <= len(row["design_intent_hypotheses"]["hypotheses"]) <= 4


def test_multi_candidate_mac():
    non_wing = [r for r in CASE09["part_results"] if "WING" not in r["label"]]
    assert all(len(r["candidates"]) >= 3 for r in non_wing)


def test_all_candidates_executed():
    for row in CASE09["part_results"]:
        for c in row["candidates"]:
            assert c.get("executed") is True or c.get("invalid_reason")


def test_cad_nativeness_verifier():
    for row in CASE09["part_results"]:
        for c in row["candidates"]:
            if c.get("executed"):
                assert "MESH_LIKE_BREP_SCORE" in c["nativeness"]


def test_geometry_hard_gate():
    for row in CASE09["part_results"]:
        selected = row["SELECTED_BEST"]
        assert selected["geometry"]["GEOM_Q"] in ("Q1", "Q2")


def test_artificial_edge_metric():
    assert CASE09["part_results"][0]["SELECTED_BEST"]["nativeness"]["ARTIFICIAL_EDGE_COUNT"] >= 0


def test_mesh_like_score():
    assert 0 <= CASE09["part_results"][0]["SELECTED_BEST"]["nativeness"]["MESH_LIKE_BREP_SCORE"] <= 1


def test_feature_verifier():
    for row in CASE09["part_results"]:
        assert "feature" in row["SELECTED_BEST"]


def test_representation_complexity():
    for row in CASE09["part_results"]:
        assert row["SELECTED_BEST"]["nativeness"]["REPRESENTATION_COMPLEXITY"] > 0


def test_futurecad_grounding():
    assert Path("/data/home/cuiyuehan/project/mesh2cad/ours3/case09_semantic_surface_face_reduction_v4/05_grounding/grounding_summary.json").is_file()


def test_best_result_registry():
    assert REG["no_regression_policy"]
    assert REG["q3_never_replaces_q1_q2"]


def test_case03_no_regression():
    assert REG["cases"]["CASE_03"]["PROTECTED_NO_REGRESSION"]


def test_case09_wings_frozen():
    assert CASE09["NO_WING_REGRESSION"]
    assert CASE09["WING_HASH_BEFORE"] == CASE09["WING_HASH_AFTER"]


def test_xcaf_assembly():
    assert CASE09["FINAL_COMPONENT_COUNT"] == 8


def test_final_step_reload():
    assert Path(CASE09["FINAL_STEP"]).is_file()
    assert CASE09["FINAL_BREP_VALID"]


def test_batch10_visualization():
    for name in [
        "batch10_v5_source_vs_cad_shaded.png",
        "batch10_v5_true_edges.png",
        "batch10_v5_semantic_surfaces.png",
        "batch10_v5_artificial_edges.png",
    ]:
        assert (OUT / "artifacts" / name).is_file()
