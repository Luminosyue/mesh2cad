"""Deterministic STEP tessellation and B-Rep edge extraction (OCP)."""

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

CURVE_TYPE_NAMES = {
    0: "Line",
    1: "Circle",
    2: "Ellipse",
    3: "Hyperbola",
    4: "Parabola",
    5: "Bezier",
    6: "BSpline",
    7: "Offset",
    8: "Other",
}


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
        "mesh_tolerance": lin,
        "angular_deflection_deg": ANGULAR_DEFLECTION_DEG,
        "angular_deflection_rad": ang,
        "is_relative": TESSELLATION_IS_RELATIVE,
        "parallel": TESSELLATION_PARALLEL,
        "bbox_diagonal": float(diag),
    }


def tessellate_shape(shape, params: dict | None = None):
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
    """Merge coincident vertices so face adjacency is well-defined."""
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


def _curve_type_name(adaptor) -> str:
    try:
        kind = int(adaptor.GetType())
    except Exception:
        return "Other"
    return CURVE_TYPE_NAMES.get(kind, "Other")


def _sample_adaptor_polyline(adaptor, n: int) -> tuple[np.ndarray, float]:
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa

    t0 = adaptor.FirstParameter()
    t1 = adaptor.LastParameter()
    try:
        length = float(GCPnts_AbscissaPoint.Length_s(adaptor, t0, t1))
    except Exception:
        length = 0.0
    n = max(int(n), 2)
    pts: list[list[float]] = []
    try:
        ua = GCPnts_UniformAbscissa(adaptor, n)
        if ua.IsDone() and ua.NbPoints() >= 2:
            for i in range(1, ua.NbPoints() + 1):
                p = adaptor.Value(ua.Parameter(i))
                pts.append([p.X(), p.Y(), p.Z()])
    except Exception:
        pts = []
    if len(pts) < 2:
        for t in np.linspace(t0, t1, n):
            p = adaptor.Value(float(t))
            pts.append([p.X(), p.Y(), p.Z()])
    arr = np.asarray(pts, dtype=np.float64)
    if length <= 0 and len(arr) >= 2:
        length = float(np.linalg.norm(np.diff(arr, axis=0), axis=1).sum())
    return arr, length


def _face_normal_at_point(face, xyz: np.ndarray) -> np.ndarray:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.gp import gp_Pnt

    surf = BRep_Tool.Surface_s(face)
    proj = GeomAPI_ProjectPointOnSurf(gp_Pnt(float(xyz[0]), float(xyz[1]), float(xyz[2])), surf)
    if proj.NbPoints() < 1:
        return np.zeros(3, dtype=np.float64)
    u, v = proj.LowerDistanceParameters()
    props = BRepLProp_SLProps(BRepAdaptor_Surface(face), float(u), float(v), 1, 1e-9)
    if not props.IsNormalDefined():
        return np.zeros(3, dtype=np.float64)
    n = props.Normal()
    vec = np.array([n.X(), n.Y(), n.Z()], dtype=np.float64)
    if face.Orientation() == TopAbs_REVERSED:
        vec = -vec
    nrm = float(np.linalg.norm(vec))
    if nrm <= 1e-12:
        return np.zeros(3, dtype=np.float64)
    return vec / nrm


def extract_brep_edges(shape, diag: float) -> dict:
    """Unique topological edges of the solid, sampled as polylines in source space."""
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedDataMapOfShapeListOfShape, TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS

    edge_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)
    ancestors = TopTools_IndexedDataMapOfShapeListOfShape()
    TopExp.MapShapesAndAncestors_s(shape, TopAbs_EDGE, TopAbs_FACE, ancestors)

    spacing = max(diag * 0.005, 1e-9)
    records = []
    v0_all, v1_all, n_all, d_all = [], [], [], []
    skipped_degen = 0
    for i in range(1, edge_map.Size() + 1):
        edge = TopoDS.Edge_s(edge_map.FindKey(i))
        if BRep_Tool.Degenerated_s(edge):
            skipped_degen += 1
            continue
        adaptor = BRepAdaptor_Curve(edge)
        length_est = max(diag * 1e-6, 0.0)
        try:
            from OCP.GCPnts import GCPnts_AbscissaPoint

            length_est = float(
                GCPnts_AbscissaPoint.Length_s(
                    adaptor, adaptor.FirstParameter(), adaptor.LastParameter()
                )
            )
        except Exception:
            length_est = 0.0
        n_poly = max(2, int(np.ceil(length_est / spacing)) + 1) if length_est > 0 else 8
        n_poly = int(np.clip(n_poly, 2, 256))
        poly, length = _sample_adaptor_polyline(adaptor, n_poly)
        if length <= 1e-12 or len(poly) < 2:
            skipped_degen += 1
            continue

        faces = []
        if ancestors.Contains(edge):
            faces = [TopoDS.Face_s(f) for f in ancestors.FindFromKey(edge)]
        mid = poly[len(poly) // 2]
        face_ns = [_face_normal_at_point(f, mid) for f in faces]
        face_ns = [n for n in face_ns if np.linalg.norm(n) > 1e-8]
        if len(face_ns) >= 2:
            n1, n2 = face_ns[0], face_ns[1]
            dihedral = float(np.degrees(np.arccos(np.clip(np.dot(n1, n2), -1.0, 1.0))))
            seg_n = n1 + n2
        elif len(face_ns) == 1:
            dihedral = 0.0
            seg_n = face_ns[0]
        else:
            dihedral = 0.0
            seg_n = np.zeros(3, dtype=np.float64)
        sn = float(np.linalg.norm(seg_n))
        seg_n = seg_n / sn if sn > 1e-12 else np.zeros(3, dtype=np.float64)

        records.append(
            {
                "edge_index": i - 1,
                "curve_type": _curve_type_name(adaptor),
                "length": float(length),
                "n_faces": len(faces),
                "dihedral_deg": dihedral,
                "polyline": poly.astype(np.float32),
            }
        )
        for a, b in zip(poly[:-1], poly[1:]):
            if np.linalg.norm(b - a) <= 1e-12:
                continue
            v0_all.append(a)
            v1_all.append(b)
            n_all.append(seg_n)
            d_all.append(dihedral)

    if not v0_all:
        raise RuntimeError("no usable B-Rep edges")
    return {
        "v0": np.asarray(v0_all, dtype=np.float64),
        "v1": np.asarray(v1_all, dtype=np.float64),
        "segment_normals": np.asarray(n_all, dtype=np.float64),
        "segment_dihedral_deg": np.asarray(d_all, dtype=np.float64),
        "edges": records,
        "num_topo_edges": int(len(records)),
        "num_segments": int(len(v0_all)),
        "skipped_degenerate": int(skipped_degen),
    }


def sharp_segment_mask(dihedral_deg: np.ndarray, sharp_angle_deg: float) -> np.ndarray:
    """Same predicate as mesh sharp edges: θ = arccos(n1·n2) > θ_sharp."""
    return np.asarray(dihedral_deg, dtype=np.float64) > float(sharp_angle_deg)


def tessellate_step(step_path: Path) -> dict:
    shape = load_step_shape(step_path)
    params = tessellate_shape(shape)
    vertices, faces = triangulation_to_arrays(shape)
    vertices, faces, adj, adj_edges = weld_mesh(vertices, faces)
    brep = extract_brep_edges(shape, params["bbox_diagonal"])
    return {
        "params": params,
        "vertices": vertices,
        "faces": faces,
        "face_adjacency": adj,
        "face_adjacency_edges": adj_edges,
        "brep": brep,
    }
