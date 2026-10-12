"""OCC helpers for V4 geometry QA, surface, edge, curve."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from ..config import BBOX_DIAG_EPS, VOLUME_EPS


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


def shape_bbox(shape) -> tuple[np.ndarray, np.ndarray]:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return (
        np.array([xmin, ymin, zmin], dtype=np.float64),
        np.array([xmax, ymax, zmax], dtype=np.float64),
    )


def shape_volume_area(shape) -> tuple[float, float]:
    from OCP.BRepGProp import BRepGProp
    from OCP.GProp import GProp_GProps

    mass = GProp_GProps()
    surf = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, mass)
    BRepGProp.SurfaceProperties_s(shape, surf)
    return float(mass.Mass()), float(surf.Mass())


def tessellate(shape) -> tuple[np.ndarray, np.ndarray]:
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE, TopAbs_REVERSED
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    mn, mx = shape_bbox(shape)
    diag = float(np.linalg.norm(mx - mn))
    lin = max(0.002 * diag, 1e-4)
    mesh = BRepMesh_IncrementalMesh(shape, lin, False, float(np.radians(20.0)), True)
    mesh.Perform()
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


def sample_surface_4096(vertices: np.ndarray, faces: np.ndarray, n_points: int, seed: int) -> np.ndarray:
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    tri = vertices[faces]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = 0.5 * np.linalg.norm(cr, axis=1)
    usable = areas > 0
    if not np.any(usable):
        raise RuntimeError("zero-area mesh")
    probs = np.zeros_like(areas)
    probs[usable] = areas[usable] / areas[usable].sum()
    rng = np.random.default_rng(int(seed))
    idx = rng.choice(len(faces), size=n_points, replace=True, p=probs)
    chosen = tri[idx]
    u = rng.random(n_points)
    v = rng.random(n_points)
    mask = u + v > 1.0
    u = u.copy()
    v = v.copy()
    u[mask] = 1.0 - u[mask]
    v[mask] = 1.0 - v[mask]
    w = 1.0 - u - v
    pts = w[:, None] * chosen[:, 0] + u[:, None] * chosen[:, 1] + v[:, None] * chosen[:, 2]
    nrm = cr[idx]
    nn = np.linalg.norm(nrm, axis=1, keepdims=True)
    nrm = np.divide(nrm, nn, out=np.zeros_like(nrm), where=nn > 1e-12)
    out = np.concatenate([pts, nrm], axis=1).astype(np.float32)
    return out


def write_stl(vertices: np.ndarray, faces: np.ndarray, path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        import trimesh

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=False)
        mesh.export(str(path))
    except Exception:
        # Minimal ASCII STL fallback
        with path.open("w", encoding="utf-8") as f:
            f.write("solid v4\n")
            for a, b, c in faces:
                p0, p1, p2 = vertices[a], vertices[b], vertices[c]
                n = np.cross(p1 - p0, p2 - p0)
                nn = float(np.linalg.norm(n))
                if nn > 1e-12:
                    n = n / nn
                f.write(f"  facet normal {n[0]} {n[1]} {n[2]}\n    outer loop\n")
                for p in (p0, p1, p2):
                    f.write(f"      vertex {p[0]} {p[1]} {p[2]}\n")
                f.write("    endloop\n  endfacet\n")
            f.write("endsolid v4\n")


def geometry_metrics(shape) -> dict:
    mn, mx = shape_bbox(shape)
    diag = float(np.linalg.norm(mx - mn))
    vol, area = shape_volume_area(shape)
    bbox_valid = bool(np.isfinite(diag) and diag > BBOX_DIAG_EPS)
    nonzero_volume = bool(np.isfinite(vol) and abs(vol) > VOLUME_EPS)
    return {
        "bbox_min": mn.tolist(),
        "bbox_max": mx.tolist(),
        "bbox_extent": (mx - mn).tolist(),
        "bbox_diag": diag,
        "bbox_valid": bbox_valid,
        "volume": vol,
        "surface_area": area,
        "nonzero_volume": nonzero_volume,
        "geometry_metrics_ok": bbox_valid and nonzero_volume and np.isfinite(area) and area > 0,
    }


def extract_oracle_edges_and_curves(shape, n_sample: int = 32) -> dict:
    from OCP.BRep import BRep_Tool
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa
    from OCP.TopAbs import TopAbs_EDGE
    from OCP.TopExp import TopExp
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopoDS import TopoDS

    TYPE_MAP = {
        0: "LINE",
        1: "CIRCLE",
        2: "ELLIPSE",
        3: "OTHER",
        4: "OTHER",
        5: "BSPLINE",
        6: "BSPLINE",
        7: "OTHER",
        8: "OTHER",
    }

    edge_map = TopTools_IndexedMapOfShape()
    TopExp.MapShapes_s(shape, TopAbs_EDGE, edge_map)
    curves = []
    edge_pts = []
    skipped = []
    for i in range(1, edge_map.Size() + 1):
        edge = TopoDS.Edge_s(edge_map.FindKey(i))
        if BRep_Tool.Degenerated_s(edge):
            skipped.append({"edge_id": i - 1, "reason": "degenerate"})
            continue
        adaptor = BRepAdaptor_Curve(edge)
        u0 = float(adaptor.FirstParameter())
        u1 = float(adaptor.LastParameter())
        try:
            length = float(GCPnts_AbscissaPoint.Length_s(adaptor, u0, u1))
        except Exception as exc:  # noqa: BLE001
            skipped.append({"edge_id": i - 1, "reason": f"length_fail:{exc}"})
            continue
        if not np.isfinite(length) or length <= 1e-12:
            skipped.append({"edge_id": i - 1, "reason": "zero_length", "length": length})
            continue
        kind = int(adaptor.GetType())
        ctype = TYPE_MAP.get(kind, "OTHER")
        # Do not silently merge partial circles into CIRCLE.
        if ctype == "CIRCLE":
            period = 2.0 * np.pi
            span = abs(u1 - u0)
            is_full = bool(adaptor.IsClosed()) and abs(span - period) <= 1e-4
            if not is_full:
                ctype = "ARC"
        xyz = np.zeros((n_sample, 3), dtype=np.float64)
        tan = np.zeros((n_sample, 3), dtype=np.float64)
        s = np.linspace(0.0, 1.0, n_sample, dtype=np.float64).reshape(n_sample, 1)
        ok = True
        try:
            ua = GCPnts_UniformAbscissa(adaptor, n_sample)
            if ua.IsDone() and ua.NbPoints() >= 2:
                n_got = min(n_sample, ua.NbPoints())
                us = [ua.Parameter(j) for j in range(1, n_got + 1)]
                if n_got < n_sample:
                    us = list(np.linspace(u0, u1, n_sample))
            else:
                us = list(np.linspace(u0, u1, n_sample))
        except Exception:
            us = list(np.linspace(u0, u1, n_sample))
        from OCP.gp import gp_Pnt, gp_Vec

        for j, u in enumerate(us[:n_sample]):
            p, v = gp_Pnt(), gp_Vec()
            try:
                adaptor.D1(float(u), p, v)
                xyz[j] = (p.X(), p.Y(), p.Z())
                tv = np.array([v.X(), v.Y(), v.Z()], dtype=np.float64)
                nrm = float(np.linalg.norm(tv))
                tan[j] = (tv / nrm) if nrm > 1e-12 else np.zeros(3, dtype=np.float64)
            except Exception:
                ok = False
                break
        if not ok or not np.isfinite(xyz).all():
            skipped.append({"edge_id": i - 1, "reason": "sample_fail"})
            continue
        bb_min = xyz.min(0)
        bb_max = xyz.max(0)
        poly = float(np.linalg.norm(np.diff(xyz, axis=0), axis=1).sum())
        curves.append(
            {
                "curve_id": len(curves),
                "curve_type": ctype,
                "source_edge_ids": [i - 1],
                "xyz": xyz.tolist(),
                "tangent": tan.tolist(),
                "s": s.tolist(),
                "polyline_length": poly,
                "bbox": {"min": bb_min.tolist(), "max": bb_max.tolist()},
                "length": length,
            }
        )
        edge_pts.append(xyz.astype(np.float32))
    counts = {}
    for c in curves:
        counts[c["curve_type"]] = counts.get(c["curve_type"], 0) + 1
    return {
        "curves": curves,
        "edge_polylines": edge_pts,
        "num_raw_edges": int(edge_map.Size()),
        "num_curves": len(curves),
        "skipped": skipped,
        "type_counts": counts,
        "edge_source": "oracle_brep_edge",
    }
