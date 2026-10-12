from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "generalization/run_building_generalization_v1.py"


def test_no_case09_artifact_dependency() -> None:
    paths = [ROOT / "generalization/run_building_generalization_v1.py"]
    paths.extend((ROOT / "generalization/common").glob("*.py"))
    text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
    assert "case09_full_pipeline_" not in text
    assert "case09_front_and_dorsal_" not in text
    assert "case09_part_input_stability_" not in text
    assert "remote_gate10" not in text


def test_no_aircraft_role_routing() -> None:
    source = (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")
    for token in ("FUSELAGE", "MAIN_WING", "TAILPLANE", "VERTICAL_TAIL", "PROPELLER", "DORSAL"):
        assert not any(
            token in line and ("if " in line or "elif " in line or "match " in line or "case " in line)
            for line in source.splitlines()
        )


def test_no_building_part_id_hardcode() -> None:
    source = (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")
    assert "part_4=roof" not in source
    assert "part_7=window" not in source


def test_generic_backend_router() -> None:
    source = (ROOT / "generalization/common/geometry_backend_router.py").read_text(encoding="utf-8")
    assert '"PLANAR": "PROFILE_EXTRUSION"' in source
    assert '"FREEFORM": "SEMANTIC_FREEFORM_SKINS"' in source


def test_planar_part_can_select_analytic() -> None:
    spec = importlib.util.spec_from_file_location("selector", ROOT / "generalization/common/candidate_selector.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    winner, _ = module.select_candidate([
        {"candidate_id": "a", "backend": "CURRENT_ANALYTIC", "safety_pass": True, "hard_reject": False,
         "metrics": {"chamfer": 0.01, "analytic_surface_ratio": 1.0, "nativeness_score": 1.0, "face_count": 6}},
        {"candidate_id": "v", "backend": "V6_GEOMETRY", "safety_pass": True, "hard_reject": False,
         "metrics": {"chamfer": 0.0104, "analytic_surface_ratio": 0.2, "nativeness_score": 0.2, "face_count": 50}},
    ])
    assert winner and winner["backend"] == "CURRENT_ANALYTIC"


def test_freeform_part_can_select_v6() -> None:
    spec = importlib.util.spec_from_file_location("selector", ROOT / "generalization/common/candidate_selector.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    winner, _ = module.select_candidate([
        {"candidate_id": "a", "backend": "CURRENT_ANALYTIC", "safety_pass": False, "hard_reject": True,
         "metrics": {"chamfer": 0.01}},
        {"candidate_id": "v", "backend": "V6_GEOMETRY", "safety_pass": True, "hard_reject": False,
         "metrics": {"chamfer": 0.03, "analytic_surface_ratio": 0.2, "nativeness_score": 0.2, "face_count": 50}},
    ])
    assert winner and winner["backend"] == "V6_GEOMETRY"


def test_semantics_cannot_override_geometry_eligibility() -> None:
    assert "geometry.get(\"analytic_eligible\")" in (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")


def test_unknown_semantic_role_supported() -> None:
    text = (ROOT / "generalization/common/semantic_role_adapter.py").read_text(encoding="utf-8")
    assert 'role = "UNKNOWN"' in text


def test_no_hidden_mesh_step_fallback() -> None:
    text = (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")
    assert "mesh_wrapped_step_count" in text
    assert "NO_SELECTED_PARTS" in text


def test_omitted_part_not_fake_component() -> None:
    text = (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")
    assert '"omitted_parts"' in text
    assert 'if selected_entries:' in text


def test_final_step_reload() -> None:
    text = (ROOT / "generalization/common/assembly_runner.py").read_text(encoding="utf-8")
    assert "reload_xcaf" in text
    assert "validate_reloaded_components" in text


def test_renderer_true_edges_separated() -> None:
    text = (ROOT / "generalization/run_building_generalization_v1.py").read_text(encoding="utf-8")
    assert "building_final_true_edges.png" in text
    assert "building_tessellation_debug.png" in text


def test_explicit_input_required() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert 'parser.add_argument("--input_obj", type=Path, required=True)' in text


def test_input_basename_matches_requested() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "expected_basename" in text
    assert "TARGET_BASENAME_MATCH" in text


def test_input_sha_propagates_to_p3() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert '"SOURCE_OBJ_SHA256": source_sha' in text
    assert "run_p3(source_path" in text


def test_input_sha_propagates_to_physx() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "run_physx(" in text
    assert "PHYSX_SOURCE_OBJ_SHA256" in text or "physx_source_obj_sha256" in text


def test_input_sha_propagates_to_part_graph() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "part_graph_source_obj_sha256" in text
    assert "source_provenance_audit.csv" in text


def test_input_sha_propagates_to_candidates() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "CURRENT_BACKEND" in text
    assert "V6_BACKEND" in text
    assert "SOURCE_OBJ_SHA256" in text


def test_input_sha_propagates_to_assembly() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "assembly_source_sha256" in text
    assert "building_assembly_manifest.json" in text


def test_wrong_case_artifact_not_reused() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "wrong_case_reconstruction_artifact_reuse_count" in text
    assert "WRONG_CASE_PATH" in text


def test_auto_discovery_disabled() -> None:
    text = RUNNER.read_text(encoding="utf-8")
    assert "AUTO_DISCOVERY_DISABLED" in text
    assert "AUTO_DISCOVERY_DISABLED=true" in text
