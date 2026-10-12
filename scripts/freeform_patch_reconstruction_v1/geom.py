"""Geometry helpers: rebuild OCC BSpline, dense UV sampling, Chamfer/Hausdorff."""

from __future__ import annotations

from pathlib import Path

import numpy as np


def load_raw_bspline(npz_path: Path):
    """Rebuild Geom_BSplineSurface from surface_raw.npz."""
    from OCP.Geom import Geom_BSplineSurface
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal, TColStd_Array2OfReal
    from OCP.gp import gp_Pnt

    raw = np.load(npz_path)
    poles = np.asarray(raw["poles"], dtype=np.float64)
    weights = np.asarray(raw["weights"], dtype=np.float64)
    nu, nv = poles.shape[:2]
    arr = TColgp_Array2OfPnt(1, nu, 1, nv)
    ww = TColStd_Array2OfReal(1, nu, 1, nv)
    for i in range(nu):
        for j in range(nv):
            arr.SetValue(i + 1, j + 1, gp_Pnt(*map(float, poles[i, j])))
            ww.SetValue(i + 1, j + 1, float(weights[i, j]))
    uk, um = raw["u_knots"], raw["u_multiplicities"]
    vk, vm = raw["v_knots"], raw["v_multiplicities"]
    U = TColStd_Array1OfReal(1, len(uk))
    MU = TColStd_Array1OfInteger(1, len(um))
    V = TColStd_Array1OfReal(1, len(vk))
    MV = TColStd_Array1OfInteger(1, len(vm))
    for i, x in enumerate(uk):
        U.SetValue(i + 1, float(x))
    for i, x in enumerate(um):
        MU.SetValue(i + 1, int(x))
    for i, x in enumerate(vk):
        V.SetValue(i + 1, float(x))
    for i, x in enumerate(vm):
        MV.SetValue(i + 1, int(x))
    deg_u = int(np.asarray(raw["degree_u"]).reshape(-1)[0])
    deg_v = int(np.asarray(raw["degree_v"]).reshape(-1)[0])
    u_per = bool(np.asarray(raw["u_periodic"]).reshape(-1)[0]) if "u_periodic" in raw.files else False
    v_per = bool(np.asarray(raw["v_periodic"]).reshape(-1)[0]) if "v_periodic" in raw.files else False
    surf = Geom_BSplineSurface(arr, ww, U, V, MU, MV, deg_u, deg_v, u_per, v_per)
    bounds = np.asarray(raw["uv_bounds"], dtype=np.float64)
    return surf, bounds, raw


def build_bspline_from_poles(
    poles: np.ndarray,
    *,
    degree_u: int,
    degree_v: int,
    uv_bounds: np.ndarray | None = None,
):
    """Cubic/clamped open BSpline from a regular control grid (unit knot domain mapped to uv_bounds)."""
    from OCP.Geom import Geom_BSplineSurface
    from OCP.TColgp import TColgp_Array2OfPnt
    from OCP.TColStd import TColStd_Array1OfInteger, TColStd_Array1OfReal, TColStd_Array2OfReal
    from OCP.gp import gp_Pnt

    from freeform_surface_pack_v1.canonical import clamped_uniform_knots

    poles = np.asarray(poles, dtype=np.float64)
    nu, nv = poles.shape[:2]
    arr = TColgp_Array2OfPnt(1, nu, 1, nv)
    ww = TColStd_Array2OfReal(1, nu, 1, nv)
    for i in range(nu):
        for j in range(nv):
            arr.SetValue(i + 1, j + 1, gp_Pnt(*map(float, poles[i, j])))
            ww.SetValue(i + 1, j + 1, 1.0)
    uk, um = clamped_uniform_knots(nu, degree_u)
    vk, vm = clamped_uniform_knots(nv, degree_v)
    U = TColStd_Array1OfReal(1, len(uk))
    MU = TColStd_Array1OfInteger(1, len(um))
    V = TColStd_Array1OfReal(1, len(vk))
    MV = TColStd_Array1OfInteger(1, len(vm))
    for i, x in enumerate(uk):
        U.SetValue(i + 1, float(x))
    for i, x in enumerate(um):
        MU.SetValue(i + 1, int(x))
    for i, x in enumerate(vk):
        V.SetValue(i + 1, float(x))
    for i, x in enumerate(vm):
        MV.SetValue(i + 1, int(x))
    return Geom_BSplineSurface(arr, ww, U, V, MU, MV, int(degree_u), int(degree_v), False, False)


def sample_surface_uv_grid(
    surf,
    uv_bounds: np.ndarray,
    nu: int,
    nv: int,
    *,
    with_normals: bool = False,
) -> dict:
    """Evaluate surface on a uniform UV grid over uv_bounds."""
    from OCP.GeomLProp import GeomLProp_SLProps

    umin, umax, vmin, vmax = [float(x) for x in uv_bounds]
    us = np.linspace(umin, umax, nu)
    vs = np.linspace(vmin, vmax, nv)
    pts = np.zeros((nu, nv, 3), dtype=np.float64)
    nrms = np.zeros((nu, nv, 3), dtype=np.float64) if with_normals else None
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            p = surf.Value(float(u), float(v))
            pts[i, j] = (p.X(), p.Y(), p.Z())
            if with_normals:
                props = GeomLProp_SLProps(surf, float(u), float(v), 1, 1e-9)
                if props.IsNormalDefined():
                    n = props.Normal()
                    vec = np.array([n.X(), n.Y(), n.Z()], dtype=np.float64)
                    nn = float(np.linalg.norm(vec))
                    nrms[i, j] = vec / nn if nn > 1e-12 else 0.0
    out = {"points": pts, "us": us, "vs": vs}
    if with_normals:
        out["normals"] = nrms
    return out


def flatten_grid(pts: np.ndarray) -> np.ndarray:
    return np.asarray(pts, dtype=np.float64).reshape(-1, 3)


def chamfer_l1(a: np.ndarray, b: np.ndarray) -> float:
    from scipy.spatial import cKDTree

    a = np.asarray(a, dtype=np.float64).reshape(-1, 3)
    b = np.asarray(b, dtype=np.float64).reshape(-1, 3)
    da, _ = cKDTree(b).query(a, k=1)
    db, _ = cKDTree(a).query(b, k=1)
    return float(0.5 * (da.mean() + db.mean()))


def hausdorff95(a: np.ndarray, b: np.ndarray) -> float:
    from scipy.spatial import cKDTree

    a = np.asarray(a, dtype=np.float64).reshape(-1, 3)
    b = np.asarray(b, dtype=np.float64).reshape(-1, 3)
    da, _ = cKDTree(b).query(a, k=1)
    db, _ = cKDTree(a).query(b, k=1)
    return float(max(np.percentile(da, 95), np.percentile(db, 95)))


def normal_consistency(a_pts, a_n, b_pts, b_n) -> float:
    """Mean |dot| of nearest-neighbor normals."""
    from scipy.spatial import cKDTree

    a_pts = np.asarray(a_pts, dtype=np.float64).reshape(-1, 3)
    b_pts = np.asarray(b_pts, dtype=np.float64).reshape(-1, 3)
    a_n = np.asarray(a_n, dtype=np.float64).reshape(-1, 3)
    b_n = np.asarray(b_n, dtype=np.float64).reshape(-1, 3)
    _, idx = cKDTree(b_pts).query(a_pts, k=1)
    dots = np.abs(np.sum(a_n * b_n[idx], axis=1))
    return float(np.nanmean(dots))
