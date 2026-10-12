import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.gp import gp_Vec


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "case09_aircraft_end2end_cad_v1"


def prism(m, vertices, axis, count):
    axis_index = {"X": 0, "Y": 1, "Z": 2}[axis]
    plane_axes = [i for i in range(3) if i != axis_index]
    profile = m.reduce_convex_polygon(np.asarray(vertices)[:, plane_axes], count)
    values = np.asarray(vertices)[:, axis_index]
    low, high = float(values.min()), float(values.max())
    points = []
    for uv in profile:
        xyz = np.zeros(3); xyz[axis_index] = low; xyz[plane_axes] = uv; points.append(xyz)
    face = BRepBuilderAPI_MakeFace(m.polygon_wire(points), True).Face()
    vector = np.zeros(3); vector[axis_index] = high - low
    shape = BRepPrimAPI_MakePrism(face, gp_Vec(*map(float, vector)), True).Shape()
    assert BRepCheck_Analyzer(shape).IsValid()
    return shape


def main():
    spec = importlib.util.spec_from_file_location("v1", V1 / "scripts/end2end_pipeline.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    source = trimesh.load(m.SOURCE, force="mesh", process=False)
    labels = np.load(m.P3 / "triangle_part_id.npy")
    boundary, sharp = m.source_feature_points(source, labels)
    diag = float(np.linalg.norm(source.extents))
    shapes = []
    fuselage_mesh, _ = m.source_part_mesh(source, labels, [8])
    fuselage, _ = m.measured_profile_loft(fuselage_mesh, "Y", 14, 10, "FUSELAGE")
    shapes.append(fuselage)
    for part in m.PART_SPECS[1:5]:
        mesh, _ = m.source_part_mesh(source, labels, part["segments"])
        shape, _ = m.measured_profile_loft(mesh, "X", 7, 12, part["part_id"])
        shapes.append(shape)
    for profile_vertices in (8, 10, 12, 16, 20, 24, 32):
        trial = list(shapes)
        for part in m.PART_SPECS[5:]:
            local = []
            for segment in part["segments"]:
                mesh = trimesh.load(m.P3 / f"part_{segment:03d}.obj", force="mesh", process=False)
                local.append(prism(m, mesh.vertices, part["axis"], profile_vertices))
            trial.append(m.compound(local))
        assembly = m.compound(trial)
        vertices, faces, _ = m.tessellate(assembly)
        mesh = trimesh.Trimesh(vertices, faces, process=False)
        metrics = m.geometry_metrics(source, mesh, diag, samples=30000)
        _, records = m.true_edges(assembly, diag)
        row = {
            "extrusion_profile_vertices": profile_vertices,
            "faces": m.topology_count(assembly, m.TopAbs_FACE),
            "edges": m.topology_count(assembly, m.TopAbs_EDGE),
            "sharp_edge_recall": m.recall(sharp, records, diag),
            "feature_boundary_recall": m.recall(boundary, records, diag),
            "strip_edge_count": m.strip_audit(records, diag)["STRIP_EDGE_COUNT"],
            **metrics,
        }
        print(json.dumps(row), flush=True)


if __name__ == "__main__":
    main()
