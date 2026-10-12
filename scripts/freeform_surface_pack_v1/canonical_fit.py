"""True least-squares cubic BSpline fit with fixed 4×4 (or NxN) control grid.

Canonical convention (frozen for Exp1):
  degree_u = degree_v = 3
  n_poles_u = n_poles_v = N  (default 4)
  open clamped uniform knots on [0,1]
  poles solved by linear least squares against dense UV samples of the
  *original* Fusion360 BSpline — NOT UV samples used as poles.
"""

from __future__ import annotations

import numpy as np

from freeform_surface_pack_v1.canonical import clamped_uniform_knots


def full_knot_vector(unique_knots: np.ndarray, multiplicities: np.ndarray) -> np.ndarray:
    out = []
    for k, m in zip(unique_knots, multiplicities):
        out.extend([float(k)] * int(m))
    return np.asarray(out, dtype=np.float64)


def basis_vector(u: float, degree: int, knots: np.ndarray) -> np.ndarray:
    """All non-zero Cox–de Boor basis values N_0..N_{n-1} at parameter u."""
    n = len(knots) - degree - 1
    # Evaluate at the right endpoint: put mass on the last basis.
    u_max = float(knots[-degree - 1])
    u_min = float(knots[degree])
    if u >= u_max - 1e-15:
        out = np.zeros(n, dtype=np.float64)
        out[-1] = 1.0
        return out
    u = float(np.clip(u, u_min, u_max - 1e-15))
    span = int(np.searchsorted(knots, u, side="right") - 1)
    span = int(np.clip(span, degree, n - 1))

    ndu = np.zeros((degree + 1, degree + 1), dtype=np.float64)
    left = np.zeros(degree + 1, dtype=np.float64)
    right = np.zeros(degree + 1, dtype=np.float64)
    ndu[0, 0] = 1.0
    for j in range(1, degree + 1):
        left[j] = u - knots[span + 1 - j]
        right[j] = knots[span + j] - u
        saved = 0.0
        for r in range(j):
            denom = right[r + 1] + left[j - r]
            temp = ndu[r, j - 1] / denom if abs(denom) > 1e-18 else 0.0
            ndu[r, j] = saved + right[r + 1] * temp
            saved = left[j - r] * temp
        ndu[j, j] = saved

    out = np.zeros(n, dtype=np.float64)
    for i in range(degree + 1):
        out[span - degree + i] = ndu[i, degree]
    return out


def tensor_basis_row(u: float, v: float, degree: int, ku: np.ndarray, kv: np.ndarray) -> np.ndarray:
    """Row of the design matrix for one (u,v): length nu*nv, column-major over (i,j)."""
    bu = basis_vector(u, degree, ku)
    bv = basis_vector(v, degree, kv)
    # flatten poles as [i, j] with j fastest: P[i,j] -> index i*nv + j
    return np.outer(bu, bv).reshape(-1)


def fit_cubic_grid_lsq(
    sample_uv: np.ndarray,
    sample_xyz: np.ndarray,
    *,
    n_u: int = 4,
    n_v: int = 4,
    degree: int = 3,
    ridge: float = 1e-10,
) -> dict:
    """Fit open-clamped cubic BSpline poles by linear least squares.

    sample_uv: (M, 2) in the *canonical* parameter domain [0,1]^2
    sample_xyz: (M, 3) corresponding surface points
    """
    sample_uv = np.asarray(sample_uv, dtype=np.float64)
    sample_xyz = np.asarray(sample_xyz, dtype=np.float64)
    if sample_uv.shape[0] != sample_xyz.shape[0]:
        raise ValueError("uv/xyz length mismatch")
    if n_u <= degree or n_v <= degree:
        raise ValueError("n_poles must exceed degree")

    uk, um = clamped_uniform_knots(n_u, degree)
    vk, vm = clamped_uniform_knots(n_v, degree)
    ku = full_knot_vector(uk, um)
    kv = full_knot_vector(vk, vm)

    m = sample_uv.shape[0]
    n_poles = n_u * n_v
    A = np.zeros((m, n_poles), dtype=np.float64)
    for k in range(m):
        A[k] = tensor_basis_row(float(sample_uv[k, 0]), float(sample_uv[k, 1]), degree, ku, kv)

    # Solve independently per XYZ channel: (A^T A + ridge I) p = A^T x
    ata = A.T @ A
    ata.flat[:: n_poles + 1] += ridge
    poles = np.zeros((n_u, n_v, 3), dtype=np.float64)
    residual = {}
    for c in range(3):
        rhs = A.T @ sample_xyz[:, c]
        try:
            sol = np.linalg.solve(ata, rhs)
        except np.linalg.LinAlgError:
            sol, *_ = np.linalg.lstsq(A, sample_xyz[:, c], rcond=None)
        poles[:, :, c] = sol.reshape(n_u, n_v)
        pred = A @ sol
        residual[f"rmse_ch{c}"] = float(np.sqrt(np.mean((pred - sample_xyz[:, c]) ** 2)))

    pred_xyz = (A @ poles.reshape(n_poles, 3))
    point_rmse = float(np.sqrt(np.mean(np.sum((pred_xyz - sample_xyz) ** 2, axis=1))))
    return {
        "poles": poles,
        "weights": np.ones((n_u, n_v), dtype=np.float64),
        "degree_u": degree,
        "degree_v": degree,
        "u_knots": uk,
        "v_knots": vk,
        "u_multiplicities": um,
        "v_multiplicities": vm,
        "u_periodic": False,
        "v_periodic": False,
        "uv_domain": np.array([0.0, 1.0, 0.0, 1.0], dtype=np.float64),
        "num_poles_u": n_u,
        "num_poles_v": n_v,
        "point_rmse": point_rmse,
        "channel_rmse": residual,
        "representation": "lsq_cubic_clamped_open",
        "n_fit_samples": int(m),
    }


def map_uv_to_unit(uv: np.ndarray, uv_bounds: np.ndarray) -> np.ndarray:
    """Map original surface UV bounds → [0,1]^2."""
    umin, umax, vmin, vmax = [float(x) for x in uv_bounds]
    out = np.empty_like(uv, dtype=np.float64)
    out[:, 0] = (uv[:, 0] - umin) / max(umax - umin, 1e-18)
    out[:, 1] = (uv[:, 1] - vmin) / max(vmax - vmin, 1e-18)
    return np.clip(out, 0.0, 1.0)


def evaluate_fitted_grid(
    poles: np.ndarray,
    *,
    degree: int = 3,
    nu_eval: int = 32,
    nv_eval: int = 32,
) -> np.ndarray:
    """Evaluate fitted cubic BSpline on a dense [0,1]^2 UV grid → (nu*nv, 3)."""
    n_u, n_v = poles.shape[:2]
    uk, um = clamped_uniform_knots(n_u, degree)
    vk, vm = clamped_uniform_knots(n_v, degree)
    ku = full_knot_vector(uk, um)
    kv = full_knot_vector(vk, vm)
    us = np.linspace(0.0, 1.0, nu_eval)
    vs = np.linspace(0.0, 1.0, nv_eval)
    pts = np.zeros((nu_eval * nv_eval, 3), dtype=np.float64)
    flat = poles.reshape(n_u * n_v, 3)
    k = 0
    for u in us:
        for v in vs:
            b = tensor_basis_row(float(u), float(v), degree, ku, kv)
            pts[k] = b @ flat
            k += 1
    return pts
