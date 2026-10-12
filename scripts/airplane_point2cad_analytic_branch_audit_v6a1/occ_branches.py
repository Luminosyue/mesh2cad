"""OCC surface-surface intersection branch extraction."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
import routeb_point2cad_brep_closure_v4 as v4


def surface_geom(model: dict):
    g = v4._geom_from_model(model)
    if g is not None:
        return g
    if model.get("mesh") is not None:
        return v4.bspline_surface_from_mesh(model["mesh"])
    return None


def curve_type_name(crv) -> str:
    try:
        from OCP.Geom import Geom_Line, Geom_Circle, Geom_Ellipse, Geom_BSplineCurve, Geom_BezierCurve

        if hasattr(Geom_Line, "get_type_desc"):
            pass
        # downcast via type name
        t = crv.DynamicType().Name()
        if "Line" in t:
            return "Line"
        if "Circle" in t:
            return "Circle"
        if "Ellipse" in t:
            return "Ellipse"
        if "BSpline" in t:
            return "BSpline"
        if "Bezier" in t:
            return "Bezier"
        return t.replace("Geom_", "")
    except Exception:
        return "unknown"


def sample_curve(crv, n: int = 400) -> tuple[np.ndarray, np.ndarray, float, bool]:
    from OCP.GeomAdaptor import GeomAdaptor_Curve
    from OCP.GCPnts import GCPnts_UniformAbscissa
    from OCP.GCPnts import GCPnts_AbscissaPoint

    ad = GeomAdaptor_Curve(crv)
    t0 = ad.FirstParameter()
    t1 = ad.LastParameter()
    try:
        length = float(GCPnts_AbscissaPoint.Length(ad, t0, t1))
    except Exception:
        length = 0.0
    pts = []
    ts = []
    try:
        ua = GCPnts_UniformAbscissa(ad, max(n, 20))
        if ua.IsDone() and ua.NbPoints() >= 2:
            for i in range(1, ua.NbPoints() + 1):
                t = ua.Parameter(i)
                p = ad.Value(t)
                pts.append([p.X(), p.Y(), p.Z()])
                ts.append(t)
    except Exception:
        ts_lin = np.linspace(t0, t1, max(n, 20))
        for t in ts_lin:
            p = ad.Value(float(t))
            pts.append([p.X(), p.Y(), p.Z()])
            ts.append(float(t))
    arr = np.asarray(pts, float)
    closed = len(arr) > 8 and float(np.linalg.norm(arr[0] - arr[-1])) < max(1e-4, 0.01 * length)
    return arr, np.asarray(ts, float), length, closed


def extract_occ_branches(sa: dict, sb: dict, pair: tuple[int, int], diag: float) -> list[dict]:
    from OCP.GeomAPI import GeomAPI_IntSS

    ga = surface_geom(sa)
    gb = surface_geom(sb)
    if ga is None or gb is None:
        return []
    try:
        inter = GeomAPI_IntSS(ga, gb, 1e-6)
        if not inter.IsDone():
            return []
    except Exception:
        return []
    branches = []
    for k in range(1, inter.NbLines() + 1):
        try:
            crv = inter.Line(k)
            pts, ts, length, closed = sample_curve(crv, n=400)
            if len(pts) < 2:
                continue
            branches.append(
                {
                    "branch_id": f"OCC_BRANCH_{len(branches):03d}",
                    "surface_pair": list(pair),
                    "curve_type": curve_type_name(crv),
                    "length": length if length > 0 else float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()),
                    "bbox": [pts.min(0).tolist(), pts.max(0).tolist()],
                    "start": pts[0].tolist(),
                    "end": pts[-1].tolist(),
                    "closed": closed,
                    "parameter_range": [float(ts[0]), float(ts[-1])],
                    "points": pts,
                    "parameters": ts,
                    "occ_curve": crv,
                }
            )
        except Exception:
            continue
    return branches


def project_point_to_branch(crv, p: np.ndarray) -> tuple[float, float]:
    from OCP.GeomAPI import GeomAPI_ProjectPointOnCurve
    from OCP.gp import gp_Pnt

    proj = GeomAPI_ProjectPointOnCurve(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), crv)
    if proj.NbPoints() < 1:
        return float("nan"), float("inf")
    return float(proj.LowerDistanceParameter()), float(proj.LowerDistance())
