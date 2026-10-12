"""Construct and validate shared OCC edge candidates."""

from __future__ import annotations

import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge
from OCP.GeomAPI import GeomAPI_Interpolate, GeomAPI_ProjectPointOnSurf
from OCP.TColgp import TColgp_HArray1OfPnt
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt


def sample_surface_distance(points, surface):
    values = []
    for point in np.asarray(points, float):
        projection = GeomAPI_ProjectPointOnSurf(gp_Pnt(*map(float, point)), surface)
        values.append(float(projection.LowerDistance()) if projection.NbPoints() else float("inf"))
    values = np.asarray(values)
    return {"mean": float(values.mean()), "p95": float(np.quantile(values, .95)), "max": float(values.max())}


def surface_intersections(face_a, face_b):
    operation = BRepAlgoAPI_Section(face_a, face_b, False)
    operation.ComputePCurveOn1(True)
    operation.ComputePCurveOn2(True)
    operation.Approximation(True)
    operation.Build()
    edges = []
    if operation.IsDone():
        explorer = TopExp_Explorer(operation.Shape(), TopAbs_EDGE)
        while explorer.More():
            edges.append(TopoDS.Edge_s(explorer.Current()))
            explorer.Next()
    return operation.IsDone(), edges


def reconciled_edge(points_a, points_b, reverse_b, tolerance):
    a, b = np.asarray(points_a, float), np.asarray(points_b, float)
    if reverse_b:
        b = b[::-1]
    if len(a) != len(b):
        raise ValueError("RECONCILIATION_SAMPLE_MISMATCH")
    points = 0.5 * (a + b)
    array = TColgp_HArray1OfPnt(1, len(points))
    for index, point in enumerate(points, 1):
        array.SetValue(index, gp_Pnt(*map(float, point)))
    interpolator = GeomAPI_Interpolate(array, False, float(tolerance))
    interpolator.Perform()
    if not interpolator.IsDone():
        raise RuntimeError("SHARED_EDGE_INTERPOLATION_FAILED")
    edge = BRepBuilderAPI_MakeEdge(interpolator.Curve()).Edge()
    return edge, points


def validate_candidate_on_surfaces(points, face_a, face_b, threshold):
    surface_a, surface_b = BRep_Tool.Surface_s(face_a), BRep_Tool.Surface_s(face_b)
    a = sample_surface_distance(points, surface_a)
    b = sample_surface_distance(points, surface_b)
    return a, b, bool(a["p95"] <= threshold and b["p95"] <= threshold)

