from __future__ import annotations

from OCP.Geom import Geom_BSplineCurve
from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal
from OCP.TColgp import TColgp_Array1OfPnt
from OCP.gp import gp_Pnt


def curve_from_three_poles(points):
    poles = TColgp_Array1OfPnt(1, len(points))
    for index, point in enumerate(points, 1): poles.SetValue(index, gp_Pnt(*map(float, point)))
    knots = TColStd_Array1OfReal(1, 2); knots.SetValue(1, 0.0); knots.SetValue(2, 1.0)
    mults = TColStd_Array1OfInteger(1, 2); mults.SetValue(1, 3); mults.SetValue(2, 3)
    return Geom_BSplineCurve(poles, knots, mults, 2, False)


def make_compatible(surface_a, surface_b, master_curve):
    a, b, curve = surface_a.Copy(), surface_b.Copy(), master_curve.Copy()
    # Segmented source surfaces retain their original U domains.  Knot-affine
    # normalization changes parameter values only, never the V7B geometry.
    for surface in (a, b):
        low, high = surface.UKnot(1), surface.UKnot(surface.NbUKnots())
        values = [(surface.UKnot(i) - low) / (high - low) for i in range(1, surface.NbUKnots() + 1)]
        for index, value in enumerate(values, 1):
            surface.SetUKnot(index, float(value))
    low, high = curve.Knot(1), curve.Knot(curve.NbKnots())
    values = [(curve.Knot(i) - low) / (high - low) for i in range(1, curve.NbKnots() + 1)]
    for index, value in enumerate(values, 1):
        curve.SetKnot(index, float(value))
    degree = max(a.UDegree(), b.UDegree(), curve.Degree())
    a.IncreaseDegree(degree, a.VDegree()); b.IncreaseDegree(degree, b.VDegree()); curve.IncreaseDegree(degree)
    def multiplicities(entity, count, knot, mult):
        return {round(knot(i), 12): int(mult(i)) for i in range(1, count() + 1)}
    ma = multiplicities(a, a.NbUKnots, a.UKnot, a.UMultiplicity)
    mb = multiplicities(b, b.NbUKnots, b.UKnot, b.UMultiplicity)
    mc = multiplicities(curve, curve.NbKnots, curve.Knot, curve.Multiplicity)
    values = sorted(set(ma) | set(mb) | set(mc))
    for value in values[1:-1]:
        target = max(ma.get(value, 0), mb.get(value, 0), mc.get(value, 0))
        a.InsertUKnot(value, target, 1e-10, False); b.InsertUKnot(value, target, 1e-10, False); curve.InsertKnot(value, target, 1e-10, False)
    if a.NbUPoles() != b.NbUPoles() or a.NbUPoles() != curve.NbPoles():
        raise RuntimeError("COMMON_U_REPRESENTATION_FAILED")
    master_poles = [[curve.Pole(i).X(), curve.Pole(i).Y(), curve.Pole(i).Z()] for i in range(1, curve.NbPoles() + 1)]
    return a, b, curve, master_poles
