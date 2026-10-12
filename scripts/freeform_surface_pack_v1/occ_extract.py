"""OCC helpers: STEP load, tessellation with face ids, BSpline / boundary extract."""

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
    0: "LINE",
    1: "CIRCLE",
    2: "ELLIPSE",
    3: "HYPERBOLA",
    4: "PARABOLA",
    5: "BEZIER",
    6: "BSPLINE",
    7: "OFFSET",
    8: "OTHER",
}

SURFACE_TYPE_NAMES = {
    0: "PLANE",
    1: "CYLINDER",
    2: "CONE",
    3: "SPHERE",
    4: "TORUS",
    5: "BEZIER",
    6: "BSPLINE",
    7: "REVOLUTION",
    8: "EXTRUSION",
    9: "OFFSET",
    10: "OTHER",
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
        raise RuntimeError(f"empty STEP: {step_path}")
    return shape


def shape_aabb_diagonal(shape) -> float:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    d = np.array([xmax - xmin, ymax - ymin, zmax - zmin], dtype=np.float64)
    return float(max(np.linalg.norm(d), 1e-12))


def tessellate_shape(shape) -> dict:
    from OCP.BRepMesh import BRepMesh_IncrementalMesh

    diag = shape_aabb_diagonal(shape)
    lin = max(LINEAR_DEFLECTION_RELATIVE * diag, LINEAR_DEFLECTION_MIN)
    ang = float(np.radians(ANGULAR_DEFLECTION_DEG))
    params = {
        "linear_deflection_relative": LINEAR_DEFLECTION_RELATIVE,
        "linear_deflection": lin,
        "mesh_tolerance": lin,
        "angular_deflection_deg": ANGULAR_DEFLECTION_DEG,
        "angular_deflection_rad": ang,
        "is_relative": TESSELLATION_IS_RELATIVE,
        "parallel": TESSELLATION_PARALLEL,
        "bbox_diagonal": diag,
    }
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


def iter_faces(shape):
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    exp = TopExp_Explorer(shape, TopAbs_FACE)
    face_id = 0
    while exp.More():
        yield face_id, TopoDS.Face_s(exp.Current())
        face_id += 1
        exp.Next()


def surface_type_name(face) -> str:
    from OCP.BRepAdaptor import BRepAdaptor_Surface

    t = int(BRepAdaptor_Surface(face).GetType())
    return SURFACE_TYPE_NAMES.get(t, "OTHER")


def face_area(face) -> float:
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    props = GProp_GProps()
    BRepGProp.SurfaceProperties_s(face, props)
    return float(props.Mass())


def extract_face_triangulation(face) -> dict | None:
    """Return vertices/triangles/uv for one face triangulation (already meshed)."""
    from OCP.BRep import BRep_Tool
    from OCP.TopAbs import TopAbs_REVERSED
    from OCP.TopLoc import TopLoc_Location

    loc = TopLoc_Location()
    poly = BRep_Tool.Triangulation_s(face, loc)
    if poly is None or poly.NbTriangles() <= 0:
        return None
    trsf = loc.Transformation()
    n_nodes = poly.NbNodes()
    verts = np.zeros((n_nodes, 3), dtype=np.float64)
    uvs = np.zeros((n_nodes, 2), dtype=np.float64)
    has_uv = bool(poly.HasUVNodes())
    for i in range(1, n_nodes + 1):
        p = poly.Node(i).Transformed(trsf)
        verts[i - 1] = (p.X(), p.Y(), p.Z())
        if has_uv:
            uv = poly.UVNode(i)
            uvs[i - 1] = (uv.X(), uv.Y())
    n_tri = poly.NbTriangles()
    tris = np.zeros((n_tri, 3), dtype=np.int64)
    reversed_face = face.Orientation() == TopAbs_REVERSED
    for i in range(1, n_tri + 1):
        a, b, c = poly.Triangle(i).Get()
        if reversed_face:
            a, b, c = a, c, b
        tris[i - 1] = (a - 1, b - 1, c - 1)
    return {
        "vertices": verts,
        "triangles": tris,
        "vertex_uv": uvs if has_uv else None,
        "has_uv": has_uv,
        "n_triangles": int(n_tri),
    }


def extract_bspline_raw(face) -> dict:
    """Extract Geom_BSplineSurface parameters in world frame (via adaptor)."""
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.GeomAbs import GeomAbs_SurfaceType

    ad = BRepAdaptor_Surface(face)
    if ad.GetType() != GeomAbs_SurfaceType.GeomAbs_BSplineSurface:
        raise ValueError("face is not BSpline")
    surf = ad.BSpline()
    if surf is None:
        raise RuntimeError("adaptor.BSpline() returned None")

    nu, nv = int(surf.NbUPoles()), int(surf.NbVPoles())
    poles = np.zeros((nu, nv, 3), dtype=np.float64)
    weights = np.zeros((nu, nv), dtype=np.float64)
    for i in range(1, nu + 1):
        for j in range(1, nv + 1):
            p = surf.Pole(i, j)
            poles[i - 1, j - 1] = (p.X(), p.Y(), p.Z())
            weights[i - 1, j - 1] = float(surf.Weight(i, j))

    nku, nkv = int(surf.NbUKnots()), int(surf.NbVKnots())
    u_knots = np.array([float(surf.UKnot(i)) for i in range(1, nku + 1)], dtype=np.float64)
    v_knots = np.array([float(surf.VKnot(i)) for i in range(1, nkv + 1)], dtype=np.float64)
    u_mult = np.array([int(surf.UMultiplicity(i)) for i in range(1, nku + 1)], dtype=np.int32)
    v_mult = np.array([int(surf.VMultiplicity(i)) for i in range(1, nkv + 1)], dtype=np.int32)
    umin, umax, vmin, vmax = surf.Bounds()
    return {
        "degree_u": int(surf.UDegree()),
        "degree_v": int(surf.VDegree()),
        "poles": poles,
        "weights": weights,
        "u_knots": u_knots,
        "v_knots": v_knots,
        "u_multiplicities": u_mult,
        "v_multiplicities": v_mult,
        "u_periodic": bool(surf.IsUPeriodic()),
        "v_periodic": bool(surf.IsVPeriodic()),
        "u_rational": bool(surf.IsURational()),
        "v_rational": bool(surf.IsVRational()),
        "uv_bounds": np.array([umin, umax, vmin, vmax], dtype=np.float64),
        "num_poles_u": nu,
        "num_poles_v": nv,
        "num_knots_u": nku,
        "num_knots_v": nkv,
        "has_weights": bool(surf.IsURational() or surf.IsVRational()),
    }


def eval_surface_point_normal(face, u: float, v: float) -> tuple[np.ndarray, np.ndarray]:
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepLProp import BRepLProp_SLProps
    from OCP.TopAbs import TopAbs_REVERSED

    props = BRepLProp_SLProps(BRepAdaptor_Surface(face), float(u), float(v), 1, 1e-9)
    if not props.IsNormalDefined():
        p = BRepAdaptor_Surface(face).Value(float(u), float(v))
        return np.array([p.X(), p.Y(), p.Z()], dtype=np.float64), np.zeros(3)
    p = props.Value()
    n = props.Normal()
    xyz = np.array([p.X(), p.Y(), p.Z()], dtype=np.float64)
    nrm = np.array([n.X(), n.Y(), n.Z()], dtype=np.float64)
    if face.Orientation() == TopAbs_REVERSED:
        nrm = -nrm
    nn = float(np.linalg.norm(nrm))
    if nn > 1e-12:
        nrm /= nn
    return xyz, nrm


def project_xyz_to_uv(face, xyz: np.ndarray) -> np.ndarray:
    from OCP.BRep import BRep_Tool
    from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
    from OCP.gp import gp_Pnt

    surf = BRep_Tool.Surface_s(face)
    out = np.zeros((len(xyz), 2), dtype=np.float64)
    for i, p in enumerate(xyz):
        proj = GeomAPI_ProjectPointOnSurf(
            gp_Pnt(float(p[0]), float(p[1]), float(p[2])), surf
        )
        if proj.NbPoints() < 1:
            out[i] = np.nan
            continue
        u, v = proj.LowerDistanceParameters()
        out[i] = (u, v)
    return out


def _curve_type_name(adaptor) -> str:
    try:
        return CURVE_TYPE_NAMES.get(int(adaptor.GetType()), "OTHER")
    except Exception:
        return "OTHER"


def _sample_curve_3d(adaptor, n: int) -> tuple[np.ndarray, float]:
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa

    t0, t1 = adaptor.FirstParameter(), adaptor.LastParameter()
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


def extract_trim_loops(face) -> dict:
    """Outer + inner wires with edge metadata and dense polylines."""
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.BRepTools import BRepTools
    from OCP.TopAbs import TopAbs_EDGE, TopAbs_WIRE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    outer = BRepTools.OuterWire_s(face)
    wires = []
    wexp = TopExp_Explorer(face, TopAbs_WIRE)
    while wexp.More():
        wires.append(TopoDS.Wire_s(wexp.Current()))
        wexp.Next()

    def pack_wire(wire, role: str) -> dict:
        edges = []
        eexp = TopExp_Explorer(wire, TopAbs_EDGE)
        eid = 0
        while eexp.More():
            edge = TopoDS.Edge_s(eexp.Current())
            from OCP.BRep import BRep_Tool

            if BRep_Tool.Degenerated_s(edge):
                eexp.Next()
                continue
            ad = BRepAdaptor_Curve(edge)
            poly, length = _sample_curve_3d(ad, n=max(8, int(32)))
            from OCP.TopAbs import TopAbs_REVERSED

            edges.append(
                {
                    "edge_id": eid,
                    "curve_type": _curve_type_name(ad),
                    "orientation": (
                        "REVERSED" if edge.Orientation() == TopAbs_REVERSED else "FORWARD"
                    ),
                    "length": float(length),
                    "polyline": poly.astype(np.float32),
                }
            )
            eid += 1
            eexp.Next()
        return {"role": role, "edges": edges}

    outer_rec = None
    inners = []
    for w in wires:
        is_outer = (not outer.IsNull()) and w.IsSame(outer)
        rec = pack_wire(w, "outer" if is_outer else "inner")
        if is_outer:
            outer_rec = rec
        else:
            inners.append(rec)
    if outer_rec is None and wires:
        # fallback: first wire as outer
        outer_rec = pack_wire(wires[0], "outer")
        inners = [pack_wire(w, "inner") for w in wires[1:]]
    if outer_rec is None:
        outer_rec = {"role": "outer", "edges": []}
    return {
        "outer": {"edges": [{k: v for k, v in e.items() if k != "polyline"} for e in outer_rec["edges"]]},
        "inners": [
            {"edges": [{k: v for k, v in e.items() if k != "polyline"} for e in inn["edges"]]}
            for inn in inners
        ],
        "_polylines_outer": [e["polyline"] for e in outer_rec["edges"]],
        "_polylines_inners": [[e["polyline"] for e in inn["edges"]] for inn in inners],
        "_edge_meta_full": outer_rec["edges"] + [e for inn in inners for e in inn["edges"]],
    }
