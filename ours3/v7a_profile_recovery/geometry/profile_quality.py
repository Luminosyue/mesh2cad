"""Profile orientation, resampling, station alignment and periodic fitting."""

import numpy as np
from scipy.interpolate import splprep, splev
from scipy.spatial import cKDTree


def signed_area(points):
    points = np.asarray(points, dtype=float)
    return 0.5 * float(np.sum(points[:, 0] * np.roll(points[:, 1], -1) -
                              points[:, 1] * np.roll(points[:, 0], -1)))


def perimeter(points):
    points = np.asarray(points, dtype=float)
    return float(np.linalg.norm(np.diff(np.vstack([points, points[0]]), axis=0), axis=1).sum())


def resample_closed(points, count=64):
    points = np.asarray(points, dtype=float)
    ring = np.vstack([points, points[0]])
    lengths = np.linalg.norm(np.diff(ring, axis=0), axis=1)
    cumulative = np.r_[0.0, np.cumsum(lengths)]
    if cumulative[-1] <= 1e-12:
        raise ValueError("DEGENERATE_PROFILE")
    samples = []
    for target in np.linspace(0.0, cumulative[-1], int(count), endpoint=False):
        idx = min(np.searchsorted(cumulative, target, side="right") - 1, len(lengths) - 1)
        alpha = (target - cumulative[idx]) / max(lengths[idx], 1e-12)
        samples.append(ring[idx] * (1.0 - alpha) + ring[idx + 1] * alpha)
    return np.asarray(samples)


def orient_loop(points, outer=True):
    points = np.asarray(points, dtype=float)
    want_positive = bool(outer)
    if (signed_area(points) > 0) != want_positive:
        points = points[::-1].copy()
    return points


def stable_first_profile(points):
    points = np.asarray(points, dtype=float)
    # Deterministic leading extreme: largest U, then largest V.
    idx = int(np.lexsort((points[:, 1], points[:, 0]))[-1])
    return np.roll(points, -idx, axis=0), idx


def cyclic_align(reference, points):
    reference = np.asarray(reference, dtype=float)
    points = np.asarray(points, dtype=float)
    ref = reference - reference.mean(axis=0)
    cur = points - points.mean(axis=0)
    scale_ref = max(np.linalg.norm(ref, axis=1).mean(), 1e-12)
    scale_cur = max(np.linalg.norm(cur, axis=1).mean(), 1e-12)
    errors = [np.mean(np.sum((ref / scale_ref - np.roll(cur / scale_cur, -k, axis=0)) ** 2, axis=1))
              for k in range(len(points))]
    shift = int(np.argmin(errors))
    return np.roll(points, -shift, axis=0), shift, float(errors[shift])


def periodic_bspline_fit(raw_points, resampled_points, dense_count=1024, tolerance_ratio=0.01):
    raw = np.asarray(raw_points, dtype=float)
    sampled = np.asarray(resampled_points, dtype=float)
    try:
        tck, _ = splprep([sampled[:, 0], sampled[:, 1]], s=0.0, per=True,
                         k=min(3, len(sampled) - 1))
        dense = np.asarray(splev(np.linspace(0.0, 1.0, dense_count, endpoint=False), tck)).T
        errors = cKDTree(dense).query(raw)[0]
        diagonal = float(np.linalg.norm(np.ptp(raw, axis=0)))
        p95 = float(np.percentile(errors, 95)) if len(errors) else float("inf")
        mean = float(np.mean(errors)) if len(errors) else float("inf")
        valid = bool(np.isfinite(p95) and p95 <= max(tolerance_ratio * diagonal, 1e-9))
        return {"type": "PERIODIC_BSPLINE", "valid": valid, "mean_error": mean,
                "fit_error_p95": p95, "dense_points_2d": dense.tolist(),
                "tolerance": max(tolerance_ratio * diagonal, 1e-9)}
    except Exception as exc:
        return {"type": "PERIODIC_BSPLINE", "valid": False, "mean_error": float("inf"),
                "fit_error_p95": float("inf"), "error": str(exc), "dense_points_2d": []}
