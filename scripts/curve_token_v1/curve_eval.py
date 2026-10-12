"""Pure-numpy evaluation of the stored parametric curve blocks.

This module deliberately has **no OCC dependency**. It exists to prove that the
parameters written to `curves.json` are self-sufficient: a downstream Curve
Encoder must be able to reconstruct the curve from JSON alone. `validate_curve_dataset`
cross-checks this evaluator against the original OCC curve.
"""

from __future__ import annotations

import numpy as np


class UnsupportedCurve(Exception):
    """Raised when the stored block cannot be evaluated without OCC."""


def _v(x) -> np.ndarray:
    return np.asarray(x, dtype=np.float64)


# --------------------------------------------------------------- analytic ----
def eval_line(params: dict, u: np.ndarray) -> np.ndarray:
    o, d = _v(params["origin"]), _v(params["direction"])
    return o[None, :] + u[:, None] * d[None, :]


def eval_circle(params: dict, u: np.ndarray) -> np.ndarray:
    c = _v(params["center"])
    x = _v(params["x_axis"])
    y = _v(params["y_axis"])
    r = float(params["radius"])
    return c[None, :] + r * (np.cos(u)[:, None] * x[None, :] + np.sin(u)[:, None] * y[None, :])


def eval_ellipse(params: dict, u: np.ndarray) -> np.ndarray:
    c = _v(params["center"])
    maj = _v(params["major_axis"])
    mnr = _v(params["minor_axis"])
    ra = float(params["major_radius"])
    rb = float(params["minor_radius"])
    return (
        c[None, :]
        + ra * np.cos(u)[:, None] * maj[None, :]
        + rb * np.sin(u)[:, None] * mnr[None, :]
    )


# ---------------------------------------------------------------- b-spline ---
def expand_knots(knots: np.ndarray, mults: np.ndarray) -> np.ndarray:
    return np.repeat(_v(knots), np.asarray(mults, dtype=np.int64))


def _find_span(t: np.ndarray, u: float, degree: int, n_ctrl: int) -> int:
    """Index k with t[k] <= u < t[k+1], clamped to the valid de Boor range."""
    hi = n_ctrl - 1
    if u >= t[hi + 1]:
        return hi
    k = int(np.searchsorted(t, u, side="right") - 1)
    return int(np.clip(k, degree, hi))


def eval_bspline(params: dict, u: np.ndarray) -> np.ndarray:
    """de Boor evaluation of a (possibly rational) clamped/general B-spline.

    Periodic curves are rejected: their stored knot vector needs OCC's wrapping
    convention to be reproduced faithfully, so validation falls back to the OCC
    rebuild path for those.
    """
    if bool(params.get("is_periodic", False)):
        raise UnsupportedCurve("periodic B-spline")

    degree = int(params["degree"])
    ctrl = _v(params["control_points"])
    knots = _v(params["knots"])
    mults = np.asarray(params["multiplicities"], dtype=np.int64)
    t = expand_knots(knots, mults)
    n_ctrl = ctrl.shape[0]

    if t.size != n_ctrl + degree + 1:
        raise UnsupportedCurve(
            f"knot vector length {t.size} != n_ctrl+degree+1 = {n_ctrl + degree + 1}"
        )

    rational = bool(params.get("is_rational", False))
    if rational:
        w = _v(params["weights"]).reshape(-1, 1)
        pts = np.concatenate([ctrl * w, w], axis=1)
    else:
        pts = ctrl

    out = np.zeros((u.size, pts.shape[1]), dtype=np.float64)
    for i, uu in enumerate(np.asarray(u, dtype=np.float64)):
        uu = float(np.clip(uu, t[degree], t[n_ctrl]))
        k = _find_span(t, uu, degree, n_ctrl)
        d = pts[k - degree : k + 1].copy()
        for r in range(1, degree + 1):
            for j in range(degree, r - 1, -1):
                lo = t[j + k - degree]
                hi = t[j + 1 + k - r]
                denom = hi - lo
                a = 0.0 if denom <= 0 else (uu - lo) / denom
                d[j] = (1.0 - a) * d[j - 1] + a * d[j]
        out[i] = d[degree]

    if rational:
        w = out[:, 3:4]
        w = np.where(np.abs(w) < 1e-300, 1e-300, w)
        return out[:, :3] / w
    return out


# ------------------------------------------------------------- dispatcher ----
_EVAL = {
    "LINE": eval_line,
    "CIRCLE": eval_circle,
    "ELLIPSE": eval_ellipse,
    "BSPLINE": eval_bspline,
}


def evaluate(curve_type: str, params: dict, u) -> np.ndarray:
    """Evaluate a stored parameter block at parameters `u`. Returns [len(u), 3]."""
    fn = _EVAL.get(curve_type)
    if fn is None:
        raise UnsupportedCurve(f"no numpy evaluator for {curve_type}")
    if not params:
        raise UnsupportedCurve(f"empty parameter block for {curve_type}")
    return fn(params, np.atleast_1d(np.asarray(u, dtype=np.float64)))


def numpy_evaluable(curve_type: str, params: dict) -> bool:
    try:
        evaluate(curve_type, params, [0.0])
    except Exception:  # noqa: BLE001
        return False
    return True
