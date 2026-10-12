"""Track-B private OCC helpers (OCP / cadquery-ocp backend).

Deliberately a separate implementation from `scripts/geometry_pack_v1/occ.py`:
Track A's module is frozen, so Track B carries its own copy of the shared
primitives (STEP loading, bbox, arc-length sampling) rather than importing it.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_step_shape(step_path: Path):
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader

    reader = STEPControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {step_path}")
    if not reader.TransferRoots():
        raise RuntimeError(f"STEP transfer failed: {step_path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"empty STEP shape: {step_path}")
    return shape


def shape_bbox(shape) -> tuple[np.ndarray, np.ndarray]:
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    xmin, ymin, zmin, xmax, ymax, zmax = box.Get()
    return (
        np.array([xmin, ymin, zmin], dtype=np.float64),
        np.array([xmax, ymax, zmax], dtype=np.float64),
    )


def pnt_to_np(p) -> np.ndarray:
    return np.array([p.X(), p.Y(), p.Z()], dtype=np.float64)


def make_adaptor(edge):
    from OCP.BRepAdaptor import BRepAdaptor_Curve

    return BRepAdaptor_Curve(edge)


def curve_length(adaptor, u0: float, u1: float) -> float:
    from OCP.GCPnts import GCPnts_AbscissaPoint

    try:
        return float(GCPnts_AbscissaPoint.Length_s(adaptor, float(u0), float(u1)))
    except Exception:  # noqa: BLE001
        return float("nan")


def eval_point(adaptor, u: float) -> np.ndarray:
    return pnt_to_np(adaptor.Value(float(u)))


def eval_point_tangent(adaptor, u: float) -> tuple[np.ndarray, np.ndarray]:
    """Point + unit tangent via first derivative, with a finite-difference fallback."""
    from OCP.gp import gp_Pnt, gp_Vec

    p, v = gp_Pnt(), gp_Vec()
    try:
        adaptor.D1(float(u), p, v)
        pos = pnt_to_np(p)
        tan = np.array([v.X(), v.Y(), v.Z()], dtype=np.float64)
    except Exception:  # noqa: BLE001
        pos = eval_point(adaptor, u)
        tan = np.zeros(3, dtype=np.float64)

    n = float(np.linalg.norm(tan))
    if n > 1e-12:
        return pos, tan / n

    u0, u1 = float(adaptor.FirstParameter()), float(adaptor.LastParameter())
    h = max((u1 - u0) * 1e-6, 1e-12)
    ua = min(max(float(u) - h, u0), u1)
    ub = min(max(float(u) + h, u0), u1)
    if ub <= ua:
        return pos, np.zeros(3, dtype=np.float64)
    fd = eval_point(adaptor, ub) - eval_point(adaptor, ua)
    n = float(np.linalg.norm(fd))
    return pos, (fd / n if n > 1e-12 else np.zeros(3, dtype=np.float64))


def arclength_params(adaptor, n: int, u0: float, u1: float) -> tuple[np.ndarray, str]:
    """n parameters spaced (approximately) uniformly in arc length.

    Returns (params, mode) where mode records which strategy actually produced
    the values, so per-curve sampling quality is auditable rather than silent.
    """
    from OCP.GCPnts import GCPnts_AbscissaPoint, GCPnts_UniformAbscissa

    n = max(int(n), 2)
    u0, u1 = float(u0), float(u1)

    try:
        ua = GCPnts_UniformAbscissa(adaptor, n, u0, u1)
        if ua.IsDone() and ua.NbPoints() == n:
            return np.array([ua.Parameter(i) for i in range(1, n + 1)], dtype=np.float64), "uniform_abscissa"
    except Exception:  # noqa: BLE001
        pass

    total = curve_length(adaptor, u0, u1)
    if np.isfinite(total) and total > 0:
        params = np.empty(n, dtype=np.float64)
        params[0], params[-1] = u0, u1
        ok = True
        for i in range(1, n - 1):
            try:
                apt = GCPnts_AbscissaPoint(adaptor, total * i / (n - 1), u0)
                if not apt.IsDone():
                    ok = False
                    break
                params[i] = float(apt.Parameter())
            except Exception:  # noqa: BLE001
                ok = False
                break
        if ok and np.all(np.diff(params) >= -1e-12):
            return params, "abscissa_point"

    return np.linspace(u0, u1, n), "parameter_uniform"


# ------------------------------------------------------ OCC curve rebuild ----
def rebuild_occ_curve(curve_type: str, params: dict):
    """Rebuild a fresh OCC curve from a stored parameter block.

    Used by validation: proves the JSON round-trips back into the CAD kernel,
    not merely into our own numpy evaluator.
    """
    from OCP.gp import gp_Ax1, gp_Ax2, gp_Circ, gp_Dir, gp_Elips, gp_Lin, gp_Pnt

    def P(v):
        return gp_Pnt(float(v[0]), float(v[1]), float(v[2]))

    def D(v):
        return gp_Dir(float(v[0]), float(v[1]), float(v[2]))

    if curve_type == "LINE":
        from OCP.Geom import Geom_Line

        return Geom_Line(gp_Lin(P(params["origin"]), D(params["direction"])))

    if curve_type == "CIRCLE":
        from OCP.Geom import Geom_Circle

        ax2 = gp_Ax2(P(params["center"]), D(params["normal"]), D(params["x_axis"]))
        return Geom_Circle(gp_Circ(ax2, float(params["radius"])))

    if curve_type == "ELLIPSE":
        from OCP.Geom import Geom_Ellipse

        ax2 = gp_Ax2(P(params["center"]), D(params["normal"]), D(params["major_axis"]))
        return Geom_Ellipse(
            gp_Elips(ax2, float(params["major_radius"]), float(params["minor_radius"]))
        )

    if curve_type in ("BSPLINE", "BEZIER"):
        from OCP.Geom import Geom_BSplineCurve
        from OCP.TColgp import TColgp_Array1OfPnt
        from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal

        ctrl = np.asarray(params["control_points"], dtype=np.float64)
        knots = np.asarray(params["knots"], dtype=np.float64)
        mults = np.asarray(params["multiplicities"], dtype=np.int64)
        npoles, nknots = ctrl.shape[0], knots.shape[0]

        arr_p = TColgp_Array1OfPnt(1, npoles)
        for i in range(npoles):
            arr_p.SetValue(i + 1, P(ctrl[i]))
        arr_k = TColStd_Array1OfReal(1, nknots)
        for i in range(nknots):
            arr_k.SetValue(i + 1, float(knots[i]))
        arr_m = TColStd_Array1OfInteger(1, nknots)
        for i in range(nknots):
            arr_m.SetValue(i + 1, int(mults[i]))

        degree = int(params["degree"])
        periodic = bool(params.get("is_periodic", False))
        if bool(params.get("is_rational", False)):
            w = np.asarray(params["weights"], dtype=np.float64)
            arr_w = TColStd_Array1OfReal(1, npoles)
            for i in range(npoles):
                arr_w.SetValue(i + 1, float(w[i]))
            return Geom_BSplineCurve(arr_p, arr_w, arr_k, arr_m, degree, periodic)
        return Geom_BSplineCurve(arr_p, arr_k, arr_m, degree, periodic)

    raise ValueError(f"no OCC rebuild for curve_type={curve_type}")
