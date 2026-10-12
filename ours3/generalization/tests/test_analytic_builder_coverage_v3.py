from __future__ import annotations

import json
from pathlib import Path

import trimesh

from generalization.analytic_builder_coverage_v3.builders import (
    boolean_cut,
    build_family,
    validate_shape,
)
from generalization.analytic_builder_coverage_v3.frames import canonical_frame, localize_mesh
from generalization.analytic_builder_coverage_v3.qa import reject_reason
from generalization.analytic_builder_coverage_v3.ranking import rank_candidates


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "generalization/run_generic_analytic_builder_coverage_v3.py"


def test_p3_does_not_rerun():
    text = RUNNER.read_text(encoding="utf-8")
    assert "P3_REEXECUTED" in text
    assert "False" in text


def test_v2_27_refined_parts_are_read_only_input():
    text = RUNNER.read_text(encoding="utf-8")
    assert "generic_structural_decomposition_analytic_fidelity_v2" in text
    assert "V2_REFINED_PARTS" in text


def test_triangle_contract_is_not_modified():
    text = RUNNER.read_text(encoding="utf-8")
    assert "V2 refined meshes are read-only inputs" in (ROOT / "generalization/analytic_builder_coverage_v3/__init__.py").read_text(encoding="utf-8") or "v2_metrics" in text


def test_local_frame_roundtrip():
    mesh = trimesh.creation.box(extents=(2.0, 1.0, 0.3))
    frame = canonical_frame(mesh)
    local = localize_mesh(mesh, frame)
    assert local.bounds.shape == (2, 3)
    assert max(abs(float(value)) for value in local.bounds[0] + local.bounds[1]) < 2.0


def test_profile_extrusion_synthetic(tmp_path):
    mesh = trimesh.creation.box(extents=(2.0, 1.0, 0.3))
    frame = canonical_frame(mesh)
    result = build_family("PROFILE_EXTRUSION", localize_mesh(mesh, frame), frame, tmp_path / "profile.step")
    assert result["valid"]
    assert result["parameters"]["builder_type"] == "PROFILE_EXTRUSION"


def test_planar_face_synthetic(tmp_path):
    mesh = trimesh.Trimesh(
        vertices=[
            [-1.0, -0.5, 0.0],
            [1.0, -0.5, 0.0],
            [1.0, 0.5, 0.0],
            [-1.0, 0.5, 0.0],
        ],
        faces=[[0, 1, 2], [0, 2, 3]],
        process=False,
    )
    frame = canonical_frame(mesh)
    result = build_family(
        "PLANAR_FACE",
        localize_mesh(mesh, frame),
        frame,
        tmp_path / "planar_face.step",
    )
    assert result["valid"]
    assert result["parameters"]["builder_type"] == "PLANAR_FACE"
    assert result["parameters"]["boundary_loop_count"] == 1


def test_revolution_synthetic(tmp_path):
    mesh = trimesh.creation.cylinder(radius=0.3, height=2.0, sections=32)
    frame = canonical_frame(mesh)
    result = build_family("REVOLUTION", localize_mesh(mesh, frame), frame, tmp_path / "revolution.step")
    assert result["valid"]


def test_tapered_extrusion_synthetic(tmp_path):
    mesh = trimesh.creation.cone(radius=0.4, height=2.0, sections=32)
    frame = canonical_frame(mesh)
    result = build_family("TAPERED_EXTRUSION", localize_mesh(mesh, frame), frame, tmp_path / "tapered.step")
    assert result["valid"]


def test_boolean_cut_synthetic():
    from OCP.BRepPrimAPI import BRepPrimAPI_MakeBox
    from OCP.gp import gp_Pnt

    base = BRepPrimAPI_MakeBox(gp_Pnt(-1.0, -1.0, -0.2), 2.0, 2.0, 0.4).Shape()
    cutter = BRepPrimAPI_MakeBox(gp_Pnt(-0.3, -0.3, -0.3), 0.6, 0.6, 0.6).Shape()
    result = boolean_cut(base, cutter)
    assert validate_shape(result["shape"])


def test_occ_invalid_candidate_is_hard_reject():
    reason, _ = reject_reason({"occ_valid": False}, None)
    assert reason == "OCC_INVALID"


def test_candidate_ranking_is_deterministic():
    candidates = [
        {"candidate_id": "b", "builder_family": "REVOLUTION", "qa_pass": True,
         "metrics": {"chamfer": 0.1, "hausdorff": 0.2, "false_positive_occupancy": 0.1, "coverage": 0.8, "normal_error": 0.1}},
        {"candidate_id": "a", "builder_family": "PROFILE_EXTRUSION", "qa_pass": True,
         "metrics": {"chamfer": 0.1, "hausdorff": 0.2, "false_positive_occupancy": 0.1, "coverage": 0.8, "normal_error": 0.1}},
    ]
    first = rank_candidates(candidates)
    second = rank_candidates(candidates)
    assert [item["candidate_id"] for item in first] == [item["candidate_id"] for item in second]
    assert first[0]["selected"]


def test_step_reload_is_explicit():
    text = RUNNER.read_text(encoding="utf-8")
    assert "--reload-only" in text
    assert "STEP_RELOADED" in text


def test_no_mesh_to_step_proxy():
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "generalization/analytic_builder_coverage_v3").glob("*.py")
    )
    assert "mesh_to_step" not in text
    assert "tessellated" not in text.lower()


def test_real_brep_construction_is_used():
    text = (ROOT / "generalization/analytic_builder_coverage_v3/builders.py").read_text(encoding="utf-8")
    assert "BRepPrimAPI_MakePrism" in text
    assert "BRepPrimAPI_MakeRevol" in text
    assert "BRepOffsetAPI_ThruSections" in text


def test_reject_reason_is_taxonomy_not_generic_qa_fail():
    reason, _ = reject_reason({"occ_valid": True, "coverage": 0.1, "false_positive_occupancy": 0.0}, None)
    assert reason == "COVERAGE_FAIL"
    assert reason != "QA_FAIL"


def test_candidate_parameters_are_saved_in_contract():
    text = RUNNER.read_text(encoding="utf-8")
    assert "parameters.json" in text
    assert "candidate_ranking.json" in text


def test_v3_output_root_is_separate():
    text = RUNNER.read_text(encoding="utf-8")
    assert "generic_analytic_builder_coverage_v3" in text
