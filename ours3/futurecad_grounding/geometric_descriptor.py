from __future__ import annotations

import math
from typing import Any

import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.GeomAbs import (
    GeomAbs_BezierCurve, GeomAbs_BezierSurface, GeomAbs_BSplineCurve,
    GeomAbs_BSplineSurface, GeomAbs_Circle, GeomAbs_Cone, GeomAbs_Cylinder,
    GeomAbs_Ellipse, GeomAbs_Hyperbola, GeomAbs_Line, GeomAbs_OffsetCurve,
    GeomAbs_OffsetSurface, GeomAbs_OtherCurve, GeomAbs_OtherSurface,
    GeomAbs_Parabola, GeomAbs_Plane, GeomAbs_Sphere,
    GeomAbs_SurfaceOfExtrusion, GeomAbs_SurfaceOfRevolution, GeomAbs_Torus,
)
from OCP.gp import gp_Pnt, gp_Vec

SURFACE_NAMES = {
    GeomAbs_Plane: 'PLANE', GeomAbs_Cylinder: 'CYLINDER', GeomAbs_Cone: 'CONE',
    GeomAbs_Sphere: 'SPHERE', GeomAbs_Torus: 'TORUS',
    GeomAbs_BezierSurface: 'BEZIER', GeomAbs_BSplineSurface: 'BSPLINE',
    GeomAbs_SurfaceOfRevolution: 'REVOLUTION',
    GeomAbs_SurfaceOfExtrusion: 'EXTRUSION', GeomAbs_OffsetSurface: 'OFFSET',
    GeomAbs_OtherSurface: 'OTHER',
}
CURVE_NAMES = {
    GeomAbs_Line: 'LINE', GeomAbs_Circle: 'CIRCLE', GeomAbs_Ellipse: 'ELLIPSE',
    GeomAbs_Hyperbola: 'HYPERBOLA', GeomAbs_Parabola: 'PARABOLA',
    GeomAbs_BezierCurve: 'BEZIER', GeomAbs_BSplineCurve: 'BSPLINE',
    GeomAbs_OffsetCurve: 'OFFSET', GeomAbs_OtherCurve: 'OTHER',
}


def unit(value) -> np.ndarray:
    result = np.asarray(value, float)
    return result / max(float(np.linalg.norm(result)), 1e-12)


def point_array(point) -> np.ndarray:
    return np.asarray([point.X(), point.Y(), point.Z()], float)


def shape_bbox(shape) -> list[list[float]]:
    box = Bnd_Box(); BRepBndLib.Add_s(shape, box)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return [[float(xmin), float(ymin), float(zmin)], [float(xmax), float(ymax), float(zmax)]]


def surface_name(face) -> str:
    try:
        return SURFACE_NAMES.get(BRepAdaptor_Surface(face).GetType(), 'OTHER')
    except Exception:
        return 'OTHER'


def curve_name(edge) -> str:
    try:
        return CURVE_NAMES.get(BRepAdaptor_Curve(edge).GetType(), 'OTHER')
    except Exception:
        return 'OTHER'


def representative_surface_frame(face) -> tuple[list[float], list[float], list[list[float]]]:
    adaptor = BRepAdaptor_Surface(face)
    u0, u1 = adaptor.FirstUParameter(), adaptor.LastUParameter()
    v0, v1 = adaptor.FirstVParameter(), adaptor.LastVParameter()
    u = 0.5 * (u0 + u1) if math.isfinite(u0 + u1) else 0.0
    v = 0.5 * (v0 + v1) if math.isfinite(v0 + v1) else 0.0
    point, du, dv = gp_Pnt(), gp_Vec(), gp_Vec()
    try:
        adaptor.D1(u, v, point, du, dv)
        a, b = unit([du.X(), du.Y(), du.Z()]), unit([dv.X(), dv.Y(), dv.Z()])
        normal = unit(np.cross(a, b))
        return point_array(point).tolist(), normal.tolist(), [a.tolist(), b.tolist()]
    except Exception:
        return [0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]


def representative_curve_frame(edge) -> tuple[list[float], list[float], bool]:
    adaptor = BRepAdaptor_Curve(edge)
    first, last = adaptor.FirstParameter(), adaptor.LastParameter()
    middle = 0.5 * (first + last)
    point, tangent = gp_Pnt(), gp_Vec()
    adaptor.D1(middle, point, tangent)
    p0, p1 = adaptor.Value(first), adaptor.Value(last)
    closed = float(point_array(p0).dot(point_array(p0))) >= 0 and np.linalg.norm(point_array(p0) - point_array(p1)) <= 1e-7
    return point_array(point).tolist(), unit([tangent.X(), tangent.Y(), tangent.Z()]).tolist(), bool(closed)


def angle_degrees(a, b) -> float:
    return float(np.degrees(np.arccos(np.clip(abs(float(unit(a) @ unit(b))), -1.0, 1.0))))


def relative_labels(local_point, local_bounds) -> list[str]:
    point = np.asarray(local_point, float)
    low, high = np.asarray(local_bounds[0], float), np.asarray(local_bounds[1], float)
    center = (low + high) * 0.5
    span = np.maximum(high - low, 1e-9)
    delta = (point - center) / span
    labels = []
    if delta[2] >= 0.20: labels += ['TOP', 'UPPER']
    elif delta[2] <= -0.20: labels += ['BOTTOM', 'LOWER']
    if delta[1] >= 0.20: labels.append('RIGHT')
    elif delta[1] <= -0.20: labels.append('LEFT')
    if delta[0] >= 0.20: labels.append('FRONT')
    elif delta[0] <= -0.20: labels += ['BACK', 'REAR']
    if not labels: labels.append('CENTER')
    return labels


def orientation_labels(tangent, frame) -> list[str]:
    tangent = unit(tangent)
    scores = {
        'LONGITUDINAL': abs(float(tangent @ frame.longitudinal)),
        'TRANSVERSE': abs(float(tangent @ frame.transverse)),
        'VERTICAL': abs(float(tangent @ frame.up)),
    }
    labels = [max(scores, key=scores.get)]
    if scores['VERTICAL'] <= 0.25:
        labels.append('HORIZONTAL')
    return labels
