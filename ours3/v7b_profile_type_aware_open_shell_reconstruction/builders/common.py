"""Frozen V7A smooth closed profile helpers reused by the closed branch."""

import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.TColgp import TColgp_HArray1OfPnt
from OCP.gp import gp_Pnt


def frame(direction):
    direction = np.asarray(direction, float)
    direction /= np.linalg.norm(direction)
    reference = np.array([0.0, 0.0, 1.0]) if abs(direction[2]) < 0.9 else np.array([0.0, 1.0, 0.0])
    first = np.cross(direction, reference)
    first /= np.linalg.norm(first)
    return direction, first, np.cross(direction, first)


def profile_points(spec, profile):
    _, first, second = frame(profile.get("plane_normal", spec["axis"]["direction"]))
    center = np.asarray(profile["plane_origin"], float)
    uv = np.asarray(profile.get("points_2d") or profile["outer_loop"]["resampled_points_2d"], float)
    return center + uv[:, 0, None] * first + uv[:, 1, None] * second


def smooth_closed_wire(points, tolerance=1e-6):
    points = np.asarray(points, float)
    array = TColgp_HArray1OfPnt(1, len(points))
    for index, xyz in enumerate(points, 1):
        array.SetValue(index, gp_Pnt(*map(float, xyz)))
    interpolation = GeomAPI_Interpolate(array, True, float(tolerance))
    interpolation.Perform()
    if not interpolation.IsDone():
        raise RuntimeError("SMOOTH_PERIODIC_PROFILE_FAILED")
    edge = BRepBuilderAPI_MakeEdge(interpolation.Curve())
    wire = BRepBuilderAPI_MakeWire(edge.Edge())
    if not edge.IsDone() or not wire.IsDone():
        raise RuntimeError("SMOOTH_PROFILE_WIRE_FAILED")
    return wire.Wire()
