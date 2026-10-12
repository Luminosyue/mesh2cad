"""Measured-profile CAD wire helpers. Sampling points define a smooth curve, not design edges."""

import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire
from OCP.GeomAPI import GeomAPI_Interpolate
from OCP.TColgp import TColgp_HArray1OfPnt
from OCP.gp import gp_Pnt


def frame(direction):
    d = np.asarray(direction, float)
    d /= np.linalg.norm(d)
    ref = np.array([0., 0., 1.]) if abs(d[2]) < .9 else np.array([0., 1., 0.])
    e1 = np.cross(d, ref)
    e1 /= np.linalg.norm(e1)
    return d, e1, np.cross(d, e1)


def profile_points(spec, profile):
    _, e1, e2 = frame(profile.get("plane_normal", spec["axis"]["direction"]))
    center = np.asarray(profile.get("plane_origin"), float)
    if center.shape != (3,):
        d = np.asarray(spec["axis"]["direction"], float)
        d /= np.linalg.norm(d)
        center = np.asarray(spec["axis"]["origin"], float) + d * ((float(profile["t"]) - .5) * float(spec["span"]))
    uv = np.asarray(profile.get("points_2d") or profile["outer_loop"]["resampled_points_2d"], float)
    return center + uv[:, 0, None] * e1 + uv[:, 1, None] * e2


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
    if not edge.IsDone():
        raise RuntimeError("SMOOTH_PROFILE_EDGE_FAILED")
    wire = BRepBuilderAPI_MakeWire(edge.Edge())
    if not wire.IsDone():
        raise RuntimeError("SMOOTH_PROFILE_WIRE_FAILED")
    return wire.Wire()
