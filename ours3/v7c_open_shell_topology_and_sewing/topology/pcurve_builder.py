"""Build and measure pcurves for a shared 3D edge on two support faces."""

from __future__ import annotations

import numpy as np

from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Curve2d
from OCP.ShapeFix import ShapeFix_Edge


def ensure_pcurve(edge, face, precision):
    fixer = ShapeFix_Edge()
    created = bool(fixer.FixAddPCurve(edge, face, False, float(precision)))
    try:
        adaptor = BRepAdaptor_Curve2d(edge, face)
        adaptor.Value(0.5 * (adaptor.FirstParameter() + adaptor.LastParameter()))
        exists = True
    except Exception:
        exists = False
    return created, exists


def pcurve_3d_error(edge, face, samples=257):
    curve3d, curve2d = BRepAdaptor_Curve(edge), BRepAdaptor_Curve2d(edge, face)
    surface = BRep_Tool.Surface_s(face)
    parameters = np.linspace(curve3d.FirstParameter(), curve3d.LastParameter(), samples)
    errors = []
    for parameter in parameters:
        point = curve3d.Value(float(parameter))
        uv = curve2d.Value(float(parameter))
        lifted = surface.Value(uv.X(), uv.Y())
        errors.append(point.Distance(lifted))
    errors = np.asarray(errors)
    return {"mean": float(errors.mean()), "p95": float(np.quantile(errors, .95)), "max": float(errors.max())}

