"""Canonical fixed-size cubic BSpline grid (8x8 poles) for reconstruction targets."""

from __future__ import annotations

import numpy as np

from .constants import CANONICAL_DEGREE, CANONICAL_NU, CANONICAL_NV


def clamped_uniform_knots(n_poles: int, degree: int) -> tuple[np.ndarray, np.ndarray]:
    """Return (unique_knots, multiplicities) for a clamped open BSpline."""
    if n_poles <= degree:
        raise ValueError("n_poles must exceed degree")
    n_internal = n_poles - degree - 1
    # unique knots: 0, internals, 1
    if n_internal > 0:
        internals = np.linspace(0.0, 1.0, n_internal + 2)[1:-1]
        knots = np.concatenate([[0.0], internals, [1.0]])
        mult = np.array([degree + 1] + [1] * n_internal + [degree + 1], dtype=np.int32)
    else:
        knots = np.array([0.0, 1.0], dtype=np.float64)
        mult = np.array([degree + 1, degree + 1], dtype=np.int32)
    return knots.astype(np.float64), mult


def build_canonical_uv_grid(
    face,
    uv_bounds: np.ndarray,
    nu: int = CANONICAL_NU,
    nv: int = CANONICAL_NV,
) -> dict:
    """Sample S(u,v) on a uniform UV grid of the *underlying* surface domain.

    This is a fixed-size geometric proxy, NOT a least-squares re-fit of the
    trimmed face. Raw NURBS remains the source of truth in surface_raw.npz.
    """
    from .occ_extract import eval_surface_point_normal

    umin, umax, vmin, vmax = [float(x) for x in uv_bounds]
    us = np.linspace(umin, umax, nu)
    vs = np.linspace(vmin, vmax, nv)
    poles = np.zeros((nu, nv, 3), dtype=np.float64)
    normals = np.zeros((nu, nv, 3), dtype=np.float64)
    for i, u in enumerate(us):
        for j, v in enumerate(vs):
            xyz, nrm = eval_surface_point_normal(face, u, v)
            poles[i, j] = xyz
            normals[i, j] = nrm
    u_knots, u_mult = clamped_uniform_knots(nu, CANONICAL_DEGREE)
    v_knots, v_mult = clamped_uniform_knots(nv, CANONICAL_DEGREE)
    weights = np.ones((nu, nv), dtype=np.float64)
    return {
        "degree_u": CANONICAL_DEGREE,
        "degree_v": CANONICAL_DEGREE,
        "poles": poles,
        "weights": weights,
        "u_knots": u_knots,
        "v_knots": v_knots,
        "u_multiplicities": u_mult,
        "v_multiplicities": v_mult,
        "u_periodic": False,
        "v_periodic": False,
        "uv_bounds": np.array([umin, umax, vmin, vmax], dtype=np.float64),
        "grid_u": us.astype(np.float64),
        "grid_v": vs.astype(np.float64),
        "normals": normals,
        "representation": "uv_grid_cubic_clamped_not_lsq_refit",
        "num_poles_u": nu,
        "num_poles_v": nv,
    }
