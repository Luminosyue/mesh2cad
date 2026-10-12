"""Exact G0 and diagnostic G1 measurements."""

from __future__ import annotations

import numpy as np
from OCP.gp import gp_Pnt, gp_Vec


def sample_side(surface, side, count=513):
    u0, u1, v0, v1 = surface.Bounds()
    v = v0 if side == "V_MIN" else v1
    points, normals = [], []
    for u in np.linspace(u0, u1, count):
        point, d1u, d1v = gp_Pnt(), gp_Vec(), gp_Vec()
        surface.D1(float(u), v, point, d1u, d1v)
        normal = np.cross([d1u.X(), d1u.Y(), d1u.Z()], [d1v.X(), d1v.Y(), d1v.Z()])
        normal /= max(float(np.linalg.norm(normal)), 1e-15)
        points.append([point.X(), point.Y(), point.Z()])
        normals.append(normal)
    return np.asarray(points), np.asarray(normals)


def errors(a, b):
    values = np.linalg.norm(np.asarray(a) - np.asarray(b), axis=1)
    return {"mean": float(values.mean()), "p95": float(np.quantile(values, 0.95)), "max": float(values.max())}


def compare(surface_a, side_a, surface_b, side_b):
    a, na = sample_side(surface_a, side_a)
    b, nb = sample_side(surface_b, side_b)
    direct = errors(a, b)
    reverse = errors(a, b[::-1])
    if reverse["mean"] < direct["mean"]:
        b, nb, ab = b[::-1], nb[::-1], reverse
    else:
        ab = direct
    angles = np.degrees(np.arccos(np.clip(np.abs(np.sum(na * nb, axis=1)), -1.0, 1.0)))
    return a, b, {
        "A_B_BOUNDARY_MEAN": ab["mean"],
        "A_B_BOUNDARY_P95": ab["p95"],
        "A_B_BOUNDARY_MAX": ab["max"],
        "BOUNDARY_NORMAL_ANGLE_MEAN": float(angles.mean()),
        "BOUNDARY_NORMAL_ANGLE_P95": float(np.quantile(angles, 0.95)),
    }
