"""Fit smooth CAD-native master curves from paired endpoint evidence."""

from __future__ import annotations

import numpy as np
from OCP.GeomAPI import GeomAPI_Interpolate, GeomAPI_ProjectPointOnCurve
from OCP.TColgp import TColgp_HArray1OfPnt
from OCP.gp import gp_Pnt


def fit(points, tolerance):
    points = np.asarray(points, float)
    array = TColgp_HArray1OfPnt(1, len(points))
    for index, point in enumerate(points, 1):
        array.SetValue(index, gp_Pnt(*map(float, point)))
    fitter = GeomAPI_Interpolate(array, False, float(tolerance))
    fitter.Perform()
    if not fitter.IsDone():
        raise RuntimeError("MASTER_BOUNDARY_FIT_FAILED")
    curve = fitter.Curve()
    distances = np.asarray([GeomAPI_ProjectPointOnCurve(gp_Pnt(*map(float, point)), curve).LowerDistance() for point in points])
    length_points = np.asarray([[curve.Value(float(t)).X(), curve.Value(float(t)).Y(), curve.Value(float(t)).Z()] for t in np.linspace(curve.FirstParameter(), curve.LastParameter(), 513)])
    return curve, {
        "CURVE_DEGREE": int(curve.Degree()),
        "CONTROL_POINT_COUNT": int(curve.NbPoles()),
        "KNOT_COUNT": int(curve.NbKnots()),
        "FIT_MEAN_ERROR": float(distances.mean()),
        "FIT_P95_ERROR": float(np.quantile(distances, 0.95)),
        "FIT_MAX_ERROR": float(distances.max()),
        "CURVE_LENGTH": float(np.linalg.norm(np.diff(length_points, axis=0), axis=1).sum()),
    }

