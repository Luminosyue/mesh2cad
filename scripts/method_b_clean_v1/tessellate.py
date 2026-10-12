"""OCC tessellation with Method-B frozen deflection knobs."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .constants import (
    ANGULAR_DEFLECTION_DEG,
    LINEAR_DEFLECTION_MIN,
    LINEAR_DEFLECTION_RELATIVE,
    TESSELLATION_IS_RELATIVE,
    TESSELLATION_PARALLEL,
)


def load_step_shape(step_path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {step_path}")
    if not reader.TransferRoots():
        raise RuntimeError(f"STEP transfer failed: {step_path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"empty STEP shape: {step_path}")
    return shape


def shape_aabb_diagonal(shape) -> float:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    d = np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=np.float64)
    return float(np.linalg.norm(d))


def tessellation_params(diag: float) -> dict:
    lin = max(float(LINEAR_DEFLECTION_RELATIVE) * float(diag), float(LINEAR_DEFLECTION_MIN))
    ang = float(np.radians(ANGULAR_DEFLECTION_DEG))
    return {
        "linear_deflection_relative": LINEAR_DEFLECTION_RELATIVE,
        "linear_deflection": lin,
        "linear_deflection_min": LINEAR_DEFLECTION_MIN,
        "angular_deflection_deg": ANGULAR_DEFLECTION_DEG,
        "angular_deflection_rad": ang,
        "is_relative": TESSELLATION_IS_RELATIVE,
        "parallel": TESSELLATION_PARALLEL,
        "bbox_diagonal": float(diag),
    }


def tessellate_shape(shape, params: dict | None = None) -> dict:
    from OCP.BRepMesh import BRepMesh_IncrementalMesh

    diag = shape_aabb_diagonal(shape)
    params = params or tessellation_params(diag)
    mesh = BRepMesh_IncrementalMesh(
        shape,
        float(params["linear_deflection"]),
        bool(params["is_relative"]),
        float(params["angular_deflection_rad"]),
        bool(params["parallel"]),
    )
    mesh.Perform()
    if not mesh.IsDone():
        raise RuntimeError("BRepMesh_IncrementalMesh failed")
    return params


def triangulation_to_arrays(shape) -> tuple[np.ndarray, np.ndarray]:
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    verts: list[np.ndarray] = []
    faces: list[np.ndarray] = []
    offset = 0
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        loc = TopLoc_Location()
        poly = BRep_Tool.Triangulation_s(face, loc)
        if poly is None:
            exp.Next()
            continue
        trsf = loc.Transformation()
        n_nodes = poly.NbNodes()
        vs = np.zeros((n_nodes, 3), dtype=np.float64)
        for i in range(1, n_nodes + 1):
            p = poly.Node(i).Transformed(trsf)
            vs[i - 1] = (p.X(), p.Y(), p.Z())
        n_tri = poly.NbTriangles()
        fs = np.zeros((n_tri, 3), dtype=np.int64)
        reversed_face = face.Orientation() == TopAbs_REVERSED
        for i in range(1, n_tri + 1):
            a, b, c = poly.Triangle(i).Get()
            if reversed_face:
                a, b, c = a, c, b
            fs[i - 1] = (a - 1 + offset, b - 1 + offset, c - 1 + offset)
        verts.append(vs)
        faces.append(fs)
        offset += n_nodes
        exp.Next()
    if not verts:
        raise RuntimeError("tessellation produced no triangles")
    return np.concatenate(verts, axis=0), np.concatenate(faces, axis=0)


def weld_mesh(vertices: np.ndarray, faces: np.ndarray, digits: int = 9):
    import trimesh

    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
    mesh.merge_vertices(digits_vertex=digits)
    mesh.update_faces(mesh.unique_faces())
    mesh.remove_unreferenced_vertices()
    if len(mesh.faces) == 0:
        raise RuntimeError("empty mesh after weld")
    return (
        np.asarray(mesh.vertices, dtype=np.float64),
        np.asarray(mesh.faces, dtype=np.int64),
        np.asarray(mesh.face_adjacency, dtype=np.int64),
        np.asarray(mesh.face_adjacency_edges, dtype=np.int64),
    )


def tessellate_step(step_path: Path) -> dict:
    shape = load_step_shape(step_path)
    params = tessellate_shape(shape)
    vertices, faces = triangulation_to_arrays(shape)
    vertices, faces, adj, adj_edges = weld_mesh(vertices, faces)
    return {
        "shape": shape,
        "params": params,
        "vertices": vertices,
        "faces": faces,
        "face_adjacency": adj,
        "face_adjacency_edges": adj_edges,
    }
