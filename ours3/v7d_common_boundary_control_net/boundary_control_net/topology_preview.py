"""Build one real OCC edge shared by two faces and carry two pcurves."""

from __future__ import annotations

import numpy as np
from OCP.BRep import BRep_Builder, BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepTools import BRepTools_ReShape
from OCP.ShapeAnalysis import ShapeAnalysis_Edge
from OCP.ShapeFix import ShapeFix_Edge
from OCP.ShapeFix import ShapeFix_Face
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.TopLoc import TopLoc_Location


def _points(edge, count=257):
    curve = BRepAdaptor_Curve(edge)
    return np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in np.linspace(curve.FirstParameter(), curve.LastParameter(), count)])


def _side_edge(face, surface, side):
    u0, u1, v0, v1 = surface.Bounds()
    v = v0 if side == "V_MIN" else v1
    target = np.asarray([[surface.Value(float(u), v).X(), surface.Value(float(u), v).Y(), surface.Value(float(u), v).Z()] for u in np.linspace(u0, u1, 129)])
    candidates = []
    explorer = TopExp_Explorer(face, TopAbs_EDGE)
    while explorer.More():
        edge = TopoDS.Edge_s(explorer.Current())
        points = _points(edge, 129)
        direct = float(np.linalg.norm(points - target, axis=1).mean())
        reverse = float(np.linalg.norm(points[::-1] - target, axis=1).mean())
        candidates.append((min(direct, reverse), edge))
        explorer.Next()
    return min(candidates, key=lambda row: row[0])[1]


def _pcurve_error(edge, face, count=257):
    curve3d, curve2d, surface = BRepAdaptor_Curve(edge), BRepAdaptor_Curve2d(edge, face), BRep_Tool.Surface_s(face)
    low = max(curve3d.FirstParameter(), curve2d.FirstParameter())
    high = min(curve3d.LastParameter(), curve2d.LastParameter())
    values = []
    for parameter in np.linspace(low, high, count):
        point = curve3d.Value(float(parameter))
        uv = curve2d.Value(float(parameter))
        values.append(point.Distance(surface.Value(uv.X(), uv.Y())))
    values = np.asarray(values)
    return {"mean": float(values.mean()), "p95": float(np.quantile(values, 0.95)), "max": float(values.max())}


def build(surface_a, face_a, surface_b, face_b, side_a, side_b, precision):
    u0, u1, v0, v1 = surface_a.Bounds()
    curve = surface_a.VIso(v0 if side_a == "V_MIN" else v1)
    edge = BRepBuilderAPI_MakeEdge(curve).Edge()
    old_a, old_b = _side_edge(face_a, surface_a, side_a), _side_edge(face_b, surface_b, side_b)
    # Copy the natural exact pcurves from each native boundary edge onto the
    # one shared 3D edge before replacing topology.
    adaptor_a, adaptor_b = BRepAdaptor_Curve2d(old_a, face_a), BRepAdaptor_Curve2d(old_b, face_b)
    pcurve_a, pcurve_b = adaptor_a.Curve(), adaptor_b.Curve()
    first_a, last_a = adaptor_a.FirstParameter(), adaptor_a.LastParameter()
    first_b, last_b = adaptor_b.FirstParameter(), adaptor_b.LastParameter()
    builder = BRep_Builder()
    builder.UpdateEdge(edge, pcurve_a, surface_a, TopLoc_Location(), float(precision))
    builder.UpdateEdge(edge, pcurve_b, surface_b, TopLoc_Location(), float(precision))
    builder.Range(edge, surface_a, TopLoc_Location(), first_a, last_a)
    builder.Range(edge, surface_b, TopLoc_Location(), first_b, last_b)
    reshape_a, reshape_b = BRepTools_ReShape(), BRepTools_ReShape()
    reshape_a.Replace(old_a, edge.Oriented(old_a.Orientation()))
    reshape_b.Replace(old_b, edge.Oriented(old_b.Orientation()))
    trimmed_a, trimmed_b = TopoDS.Face_s(reshape_a.Apply(face_a)), TopoDS.Face_s(reshape_b.Apply(face_b))
    for name, candidate in (("a", trimmed_a), ("b", trimmed_b)):
        fixer_face = ShapeFix_Face(candidate)
        fixer_face.SetPrecision(float(precision))
        fixer_face.SetMaxTolerance(float(precision))
        fixer_face.Perform()
        if name == "a": trimmed_a = fixer_face.Face()
        else: trimmed_b = fixer_face.Face()
    has_a = ShapeAnalysis_Edge().HasPCurve(edge, trimmed_a)
    has_b = ShapeAnalysis_Edge().HasPCurve(edge, trimmed_b)
    try:
        error_a = _pcurve_error(edge, trimmed_a)
        error_b = _pcurve_error(edge, trimmed_b)
    except Exception:
        error_a = error_b = {"mean": float("inf"), "p95": float("inf"), "max": float("inf")}
    return {
        "edge": edge,
        "trimmed_face_a": trimmed_a,
        "trimmed_face_b": trimmed_b,
        "EDGE_OCC_VALID": bool(BRepCheck_Analyzer(edge).IsValid()),
        "TRIMMED_FACE_A_VALID": bool(BRepCheck_Analyzer(trimmed_a).IsValid()),
        "TRIMMED_FACE_B_VALID": bool(BRepCheck_Analyzer(trimmed_b).IsValid()),
        "PCURVE_A_SUCCESS": bool(has_a),
        "PCURVE_B_SUCCESS": bool(has_b),
        "PCURVE_A_ERROR": error_a,
        "PCURVE_B_ERROR": error_b,
    }
