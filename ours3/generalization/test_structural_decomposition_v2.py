from __future__ import annotations

from pathlib import Path

import trimesh

from generalization.structural_geometry.occupancy_analyzer import occupancy_metrics
from generalization.structural_geometry.negative_space_analyzer import negative_space_evidence
from generalization.structural_geometry.primitive_explainability import builder_capability_audit
from generalization.structural_geometry.repetition_detector_v2 import detect_repetition_v2
from generalization.structural_geometry.recursive_decomposer import structural_decomposition_decision
from generalization.structural_geometry.structural_complexity import analyze
from generalization.structural_geometry.structural_router import route
from generalization.structural_geometry.topology_complexity import topology_complexity


def box(extents, center=(0.0, 0.0, 0.0)):
    mesh = trimesh.creation.box(extents=extents)
    mesh.apply_translation(center)
    return mesh


def test_simple_box_kept_single():
    result = analyze(box((2.0, 1.0, 0.5)))
    assert result["structural_class"] == "SOLID_LIKE"
    assert not structural_decomposition_decision(result)["recursive_decomposition_required"]


def test_simple_cylinder_kept_single():
    result = analyze(trimesh.creation.cylinder(radius=0.25, height=3.0, sections=24))
    assert result["structural_class"] == "SOLID_LIKE"


def test_frame_not_reconstructed_as_filled_block():
    frame = trimesh.util.concatenate([
        box((4.0, 0.15, 0.15), (-1.5, 0, 0)),
        box((4.0, 0.15, 0.15), (1.5, 0, 0)),
        box((0.15, 3.0, 0.15), (0, 0, 0)),
    ])
    result = analyze(frame)
    assert result["sparse_open"]
    assert structural_decomposition_decision(result)["recursive_decomposition_required"]


def test_plate_with_hole_preserves_negative_space():
    plate = trimesh.util.concatenate([
        box((3.0, 0.4, 0.2), (0, -1.3, 0)),
        box((3.0, 0.4, 0.2), (0, 1.3, 0)),
        box((0.4, 2.2, 0.2), (-1.3, 0, 0)),
        box((0.4, 2.2, 0.2), (1.3, 0, 0)),
    ])
    candidate = box((3.0, 3.0, 0.2))
    metrics = occupancy_metrics(plate, candidate)
    metrics.update(negative_space_evidence(metrics))
    assert metrics["negative_space_hard_reject"]
    assert metrics["false_positive_occupancy_ratio"] > 0.0


def test_plate_plus_rod_is_split():
    mesh = trimesh.util.concatenate([
        box((3.0, 2.0, 0.2)),
        box((0.2, 0.2, 3.0), (0, 0, 1.5)),
    ])
    result = analyze(mesh)
    assert result["structural_class"] in {"BODY_WITH_APPENDAGES", "ROD_NETWORK", "SPARSE_FRAME"}


def test_body_plus_appendage_is_split():
    mesh = trimesh.util.concatenate([
        box((2.5, 2.0, 1.5)),
        box((0.25, 0.25, 3.0), (1.5, 0, 1.5)),
    ])
    result = analyze(mesh)
    assert result["structural_class"] == "BODY_WITH_APPENDAGES"


def test_branching_linear_structure_not_single_extrusion():
    mesh = trimesh.util.concatenate([
        box((4.0, 0.15, 0.15)),
        box((0.15, 2.0, 0.15), (1.0, 0, 0)),
        box((0.15, 2.0, 0.15), (-1.0, 0, 0)),
    ])
    decision = structural_decomposition_decision(analyze(mesh))
    assert decision["recursive_decomposition_required"]


def test_repetition_detected_from_geometry():
    parts = [box((0.2, 0.2, 1.0), (index * 0.7, 0, 0)) for index in range(5)]
    result = detect_repetition_v2(parts)
    assert result["repetition_detected"]
    assert result["repetition_group_count"] == 1


def test_non_repetition_not_grouped():
    parts = [box((0.2 + index * 0.2, 0.2, 1.0), (index * 0.7, 0, 0)) for index in range(4)]
    assert not detect_repetition_v2(parts)["repetition_detected"]


def test_coherent_freeform_remains_v6_eligible():
    analysis = analyze(trimesh.creation.icosphere(subdivisions=2, radius=1.0))
    routed = route(analysis, {"single_construction_explainable": False})
    assert routed["route"] == "V6_GEOMETRY"


def test_builder_capability_gap_blocks_invalid_build():
    analysis = {
        "major_hole_count": 2,
        "structural_class": "SURFACE_LIKE",
        "structural_branching": False,
    }
    audit = builder_capability_audit("CURRENT_ANALYTIC", analysis)
    assert audit["builder_capability_insufficient"]


def test_mixed_part_not_sent_to_v6():
    analysis = {
        "structural_class": "BODY_WITH_APPENDAGES",
        "significant_component_count": 2,
        "structural_branching": True,
        "major_hole_count": 0,
        "negative_space_hard_reject": False,
    }
    routed = route(analysis, {"single_construction_explainable": False})
    assert routed["route"] != "V6_GEOMETRY"


def test_topology_boundary_edges_are_real_boundaries():
    result = topology_complexity(trimesh.creation.box())
    assert result["boundary_edge_count"] == 0


def test_triangle_coverage_contract():
    meshes = [box((1, 1, 1)), box((0.5, 0.5, 0.5), (2, 0, 0))]
    combined = trimesh.util.concatenate(meshes)
    assert len(combined.faces) == sum(len(mesh.faces) for mesh in meshes)


def test_no_case_specific_routing():
    package = Path(__file__).parents[1] / "structural_geometry"
    source = "\n".join(path.read_text(encoding="utf-8") for path in package.glob("*.py"))
    for token in ("5iHumo", "Building", "CADPART_000", "CADPART_008", "wall", "roof", "wing", "fuselage"):
        assert token not in source
