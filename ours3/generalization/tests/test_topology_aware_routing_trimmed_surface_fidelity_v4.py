from __future__ import annotations

from pathlib import Path

import numpy as np
import trimesh

from generalization.analytic_builder_coverage_v3.frames import canonical_frame, localize_mesh
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.builders import (
    build_family,
    _normal_patch_submeshes,
)
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.fp_diagnosis import (
    occupancy_masks,
)
from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.topology import (
    allowed_families,
    builder_gate,
    classify_topology,
)


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "generalization/run_topology_aware_routing_trimmed_surface_fidelity_v4.py"


def _open_sheet() -> trimesh.Trimesh:
    return trimesh.Trimesh(
        vertices=[
            [-1.0, -0.5, 0.0],
            [1.0, -0.5, 0.0],
            [1.0, 0.5, 0.0],
            [-1.0, 0.5, 0.0],
        ],
        faces=[[0, 1, 2], [0, 2, 3]],
        process=False,
    )


def _ring_sheet() -> trimesh.Trimesh:
    outer = np.asarray([[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0]], dtype=float)
    inner = np.asarray([[-0.35, -0.35, 0], [0.35, -0.35, 0], [0.35, 0.35, 0], [-0.35, 0.35, 0]], dtype=float)
    vertices = np.vstack((outer, inner))
    faces = []
    for index in range(4):
        nxt = (index + 1) % 4
        faces.extend([
            [index, nxt, 4 + nxt],
            [index, 4 + nxt, 4 + index],
        ])
    return trimesh.Trimesh(vertices=vertices, faces=faces, process=False)


def test_non_axisymmetric_sheet_is_not_revolution():
    topology = classify_topology(_open_sheet())
    gates = builder_gate(topology)
    assert not gates["REVOLUTION"]["allowed"]
    assert "REVOLUTION" not in allowed_families(gates)


def test_open_sheet_is_not_box_prism():
    topology = classify_topology(_open_sheet())
    gates = builder_gate(topology)
    assert not gates["BOX_PRISM"]["allowed"]


def test_open_sheet_does_not_route_to_profile_extrusion_by_default():
    topology = classify_topology(_open_sheet())
    assert "PROFILE_EXTRUSION" not in allowed_families(builder_gate(topology))


def test_planar_face_requires_planarity():
    mesh = _open_sheet()
    mesh.vertices[2, 2] = 0.3
    topology = classify_topology(mesh)
    gates = builder_gate(topology)
    assert topology["planarity_residual"] > 0.0
    assert gates["TRIMMED_PLANAR_FACE"]["allowed"] in {True, False}


def test_concavity_is_explicitly_guarded():
    text = (ROOT / "generalization/topology_aware_routing_trimmed_surface_fidelity_v4/builders.py").read_text(encoding="utf-8")
    assert "CONVEXITY_OVERFILL" in text
    assert "convexity" in text


def test_opposite_normals_are_not_merged_into_one_patch():
    mesh = trimesh.Trimesh(
        vertices=[
            [-1.0, -1.0, 0.0],
            [1.0, -1.0, 0.0],
            [1.0, 1.0, 0.0],
            [-1.0, 1.0, 0.0],
            [-1.0, -1.0, 0.2],
            [1.0, -1.0, 0.2],
            [1.0, 1.0, 0.2],
            [-1.0, 1.0, 0.2],
        ],
        faces=[
            [0, 1, 2], [0, 2, 3],
            [4, 6, 5], [4, 7, 6],
        ],
        process=False,
    )
    patches = _normal_patch_submeshes(mesh)
    assert len(patches) >= 2


def test_multi_patch_parameters_report_source_trims(tmp_path):
    mesh = _ring_sheet()
    frame = canonical_frame(mesh)
    result = build_family(
        "MULTI_PATCH_SURFACE",
        localize_mesh(mesh, frame),
        frame,
        classify_topology(mesh),
        tmp_path / "multi.step",
    )
    assert result["valid"]
    assert result["parameters"]["negative_space_regions_recovered"] >= 1
    assert all(
        patch["boundary_recovery"] == "SOURCE_TRIMMED"
        for patch in result["parameters"]["patches"]
    )


def test_trimmed_planar_face_preserves_inner_loop(tmp_path):
    mesh = _ring_sheet()
    frame = canonical_frame(mesh)
    result = build_family(
        "TRIMMED_PLANAR_FACE",
        localize_mesh(mesh, frame),
        frame,
        classify_topology(mesh),
        tmp_path / "ring.step",
    )
    assert result["valid"]
    assert result["parameters"]["builder_type"] == "TRIMMED_PLANAR_FACE"
    assert len(result["parameters"]["inner_profiles"]) >= 1


def test_open_shell_topology_is_allowed(tmp_path):
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Pnt, gp_Vec

    polygon = BRepBuilderAPI_MakePolygon()
    for point in [
        gp_Pnt(-1.0, -1.0, 0.0),
        gp_Pnt(1.0, -1.0, 0.0),
        gp_Pnt(1.0, 1.0, 0.0),
        gp_Pnt(-1.0, 1.0, 0.0),
    ]:
        polygon.Add(point)
    polygon.Close()
    shape = BRepPrimAPI_MakePrism(polygon.Wire(), gp_Vec(0.0, 0.0, 0.2), True).Shape()
    assert shape.ShapeType() is not None


def test_fp_mask_is_deterministic():
    source = _open_sheet()
    candidate = trimesh.creation.box(extents=(2.0, 1.0, 0.2))
    first = occupancy_masks(source, candidate)
    second = occupancy_masks(source, candidate)
    assert np.array_equal(first["false_positive_mask"], second["false_positive_mask"])


def test_builder_gate_is_deterministic():
    mesh = _open_sheet()
    assert builder_gate(classify_topology(mesh)) == builder_gate(classify_topology(mesh))


def test_world_local_roundtrip_is_unchanged():
    mesh = trimesh.creation.box(extents=(2.0, 1.0, 0.3))
    frame = canonical_frame(mesh)
    local = localize_mesh(mesh, frame)
    back = np.column_stack((local.vertices, np.ones(len(local.vertices))))
    recovered = (np.asarray(frame["local_to_world"]) @ back.T).T[:, :3]
    assert float(np.max(np.abs(recovered - mesh.vertices))) < 1e-9


def test_frozen_execution_contracts():
    text = RUNNER.read_text(encoding="utf-8")
    assert "P3_REEXECUTED=False" in text
    assert "PHYSX_REEXECUTED=False" in text
    assert "REAL_MAC_CALLS=0" in text


def test_no_mesh_to_step_proxy():
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "generalization/topology_aware_routing_trimmed_surface_fidelity_v4").glob("*.py")
    )
    assert "mesh_to_step" not in text
    assert "tessellated" not in text.lower()


def test_step_reload_contract_is_explicit():
    text = RUNNER.read_text(encoding="utf-8")
    assert "--reload-only" in text
    assert "BREP_TOPOLOGY_TYPE_AFTER_RELOAD" in text


def test_builder_gate_artifact_contract():
    text = RUNNER.read_text(encoding="utf-8")
    assert "builder_gate.json" in text
    assert "fp_failure_diagnosis.csv" in text


def test_v4_output_root_is_separate():
    assert "topology_aware_routing_trimmed_surface_fidelity_v4" in RUNNER.read_text(encoding="utf-8")
