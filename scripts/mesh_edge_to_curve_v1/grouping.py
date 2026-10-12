"""Oracle grouping (6.1A): mesh sharp segments → per-B-Rep-curve 32-point polylines.

What is oracle here (and must be replaced in 6.1B):
  * which curve a mesh segment belongs to  (uses GT curve geometry)
  * the order of points along the curve     (projection onto the GT polyline)

What stays purely mesh-derived (this is what we want to measure):
  * point positions, point spacing, and tangents estimated by finite differences
"""

from __future__ import annotations

import numpy as np
from scipy.spatial import cKDTree

from .config import KNN_CANDIDATES, MIN_MESH_POINTS, N_POINTS


def _point_seg_dist(pts: np.ndarray, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Distance from each point in ``pts`` [M,3] to segments a→b [S,3]. → [M,S]."""
    ab = b - a
    denom = (ab * ab).sum(-1)
    denom = np.where(denom < 1e-18, 1.0, denom)
    ap = pts[:, None, :] - a[None, :, :]
    t = np.clip((ap * ab[None, :, :]).sum(-1) / denom[None, :], 0.0, 1.0)
    proj = a[None, :, :] + t[:, :, None] * ab[None, :, :]
    return np.linalg.norm(pts[:, None, :] - proj, axis=-1)


def _project_arclen(pts: np.ndarray, poly: np.ndarray) -> np.ndarray:
    """Arc-length position of each point projected onto polyline ``poly`` [P,3]."""
    a, b = poly[:-1], poly[1:]
    seg = np.linalg.norm(b - a, axis=-1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    ab = b - a
    denom = np.where((ab * ab).sum(-1) < 1e-18, 1.0, (ab * ab).sum(-1))
    ap = pts[:, None, :] - a[None, :, :]
    t = np.clip((ap * ab[None, :, :]).sum(-1) / denom[None, :], 0.0, 1.0)
    proj = a[None, :, :] + t[:, :, None] * ab[None, :, :]
    d = np.linalg.norm(pts[:, None, :] - proj, axis=-1)
    j = d.argmin(axis=1)
    rows = np.arange(len(pts))
    return cum[j] + t[rows, j] * seg[j]


def assign_segments(
    seg_v0: np.ndarray,
    seg_v1: np.ndarray,
    gt_polys: list[np.ndarray],
    tol: float,
) -> np.ndarray:
    """Oracle assignment of each mesh segment to a GT curve (-1 = unassigned)."""
    n_seg = len(seg_v0)
    out = np.full((n_seg,), -1, dtype=np.int64)
    if n_seg == 0 or not gt_polys:
        return out

    flat = np.concatenate(gt_polys, axis=0)
    owner = np.concatenate(
        [np.full((len(p),), i, dtype=np.int64) for i, p in enumerate(gt_polys)]
    )
    tree = cKDTree(flat)
    k = min(KNN_CANDIDATES, len(flat))
    mids = 0.5 * (seg_v0 + seg_v1)

    _, idx = tree.query(mids, k=k)
    idx = np.atleast_2d(idx)
    for i in range(n_seg):
        cands = np.unique(owner[idx[i]])
        best, best_d = -1, np.inf
        for c in cands:
            poly = gt_polys[c]
            d = _point_seg_dist(
                np.stack([seg_v0[i], seg_v1[i], mids[i]]), poly[:-1], poly[1:]
            ).min(axis=1)
            # require the whole segment to lie on the curve, not just its middle
            dmax = float(d.max())
            if dmax < best_d:
                best_d, best = dmax, int(c)
        if best_d <= tol:
            out[i] = best
    return out


def resample_polyline(poly: np.ndarray, n: int = N_POINTS) -> np.ndarray:
    """Uniform arc-length resampling of an ordered polyline → [n,3]."""
    seg = np.linalg.norm(np.diff(poly, axis=0), axis=1)
    cum = np.concatenate([[0.0], np.cumsum(seg)])
    total = float(cum[-1])
    if total < 1e-12:
        return np.repeat(poly[:1], n, axis=0)
    targets = np.linspace(0.0, total, n)
    out = np.empty((n, 3), dtype=np.float64)
    for d in range(3):
        out[:, d] = np.interp(targets, cum, poly[:, d])
    return out


def tangents_from_points(pts: np.ndarray) -> np.ndarray:
    """Unit tangents by central differences (forward/backward at the ends)."""
    t = np.gradient(pts, axis=0)
    n = np.linalg.norm(t, axis=1, keepdims=True)
    n = np.where(n < 1e-12, 1.0, n)
    return t / n


def build_curve_polyline(
    seg_v0: np.ndarray,
    seg_v1: np.ndarray,
    gt_poly: np.ndarray,
    is_closed: bool,
) -> np.ndarray | None:
    """Ordered mesh polyline for one curve, ordered by projection onto ``gt_poly``.

    Returns ``None`` when the group carries too little geometry to resample.
    """
    if len(seg_v0) == 0:
        return None
    pts = np.concatenate([seg_v0, seg_v1], axis=0)
    # de-duplicate shared segment endpoints
    _, keep = np.unique(np.round(pts, 7), axis=0, return_index=True)
    pts = pts[np.sort(keep)]
    if len(pts) < MIN_MESH_POINTS:
        return None

    s = _project_arclen(pts, gt_poly)
    order = np.argsort(s)
    pts = pts[order]
    if is_closed and len(pts) >= 3:
        # close the loop so the resampled polyline covers the full circumference
        pts = np.concatenate([pts, pts[:1]], axis=0)
    if float(np.linalg.norm(np.diff(pts, axis=0), axis=1).sum()) < 1e-9:
        return None
    return pts
