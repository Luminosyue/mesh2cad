"""Extract true OCC boundary edges; never derives CAD edges from mesh samples."""

from __future__ import annotations

import numpy as np

from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d, BRepAdaptor_Surface
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GeomAbs import GeomAbs_BSplineCurve, GeomAbs_BSplineSurface, GeomAbs_Line
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_WIRE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

from .boundary_descriptor import classify_uv_boundary, describe_points


def _curve_type(kind):
    return "BSPLINE" if kind == GeomAbs_BSplineCurve else "LINE" if kind == GeomAbs_Line else str(kind)


def _surface_type(kind):
    return "BSPLINE" if kind == GeomAbs_BSplineSurface else str(kind)


def _sample(adaptor, count=257):
    parameters = np.linspace(adaptor.FirstParameter(), adaptor.LastParameter(), count)
    values = [adaptor.Value(float(parameter)) for parameter in parameters]
    dimension = 2 if hasattr(values[0], "X") and not hasattr(values[0], "Z") else 3
    if dimension == 2:
        return np.asarray([[point.X(), point.Y()] for point in values])
    return np.asarray([[point.X(), point.Y(), point.Z()] for point in values])


def extract_boundaries(shape, part_id, samples=257):
    records, faces = [], []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        faces.append(TopoDS.Face_s(explorer.Current()))
        explorer.Next()
    for face_index, face in enumerate(faces):
        face_id = f"{part_id}_FACE_{face_index:02d}"
        wire_count = 0
        wire_explorer = TopExp_Explorer(face, TopAbs_WIRE)
        while wire_explorer.More():
            wire_count += 1
            wire_explorer.Next()
        edge_records = []
        edge_explorer = TopExp_Explorer(face, TopAbs_EDGE)
        while edge_explorer.More():
            edge = TopoDS.Edge_s(edge_explorer.Current())
            curve = BRepAdaptor_Curve(edge)
            points = _sample(curve, samples)
            pcurve_exists, pcurve_type, uv_points = False, None, None
            try:
                curve2d = BRepAdaptor_Curve2d(edge, face)
                uv_points = _sample(curve2d, samples)
                pcurve_exists = bool(np.isfinite(uv_points).all())
                pcurve_type = _curve_type(curve2d.GetType())
            except Exception:
                pass
            boundary_id = f"{face_id}_BND_{len(edge_records):02d}"
            descriptor = describe_points(points)
            edge_records.append({
                "boundary_id": boundary_id,
                "face_id": face_id,
                "face_index": face_index,
                "edge_index": len(edge_records),
                "curve_type": _curve_type(curve.GetType()),
                "surface_type": _surface_type(BRepAdaptor_Surface(face).GetType()),
                "orientation": int(edge.Orientation()),
                "source": "BREP_FACE_BOUNDARY",
                "boundary_class": "DESIGN_BOUNDARY",
                "semantic_type": classify_uv_boundary(uv_points) if uv_points is not None else "UNKNOWN_DESIGN_BOUNDARY",
                "edge_has_pcurve": pcurve_exists,
                "pcurve_type": pcurve_type,
                "points": points.tolist(),
                "uv_points": uv_points.tolist() if uv_points is not None else None,
                **descriptor,
            })
            edge_explorer.Next()
        records.append({
            "part_id": part_id,
            "face_id": face_id,
            "surface_type": _surface_type(BRepAdaptor_Surface(face).GetType()),
            "edge_count": len(edge_records),
            "wire_count": wire_count,
            "free_edge_count": len(edge_records),
            "face_orientation": int(face.Orientation()),
            "occ_face_valid": bool(BRepCheck_Analyzer(face).IsValid()),
            "boundaries": edge_records,
        })
    return faces, records

