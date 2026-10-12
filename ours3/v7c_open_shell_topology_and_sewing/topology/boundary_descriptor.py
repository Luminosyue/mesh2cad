"""Geometry-only descriptors for genuine BRep face boundaries."""

from __future__ import annotations

import numpy as np


def unit(vector):
    vector = np.asarray(vector, float)
    norm = float(np.linalg.norm(vector))
    return (vector / norm).tolist() if norm > 1e-15 else [0.0, 0.0, 0.0]


def describe_points(points):
    points = np.asarray(points, float)
    if points.ndim != 2 or points.shape[1] != 3 or len(points) < 2:
        raise ValueError("INVALID_BOUNDARY_POINTS")
    segments = np.diff(points, axis=0)
    return {
        "length": float(np.linalg.norm(segments, axis=1).sum()),
        "centroid": points.mean(axis=0).tolist(),
        "bbox": {"min": points.min(axis=0).tolist(), "max": points.max(axis=0).tolist()},
        "endpoints": [points[0].tolist(), points[-1].tolist()],
        "tangent_start": unit(segments[0]),
        "tangent_end": unit(segments[-1]),
    }


def classify_uv_boundary(uv_points, tolerance=1e-7):
    uv = np.asarray(uv_points, float)
    span = np.ptp(uv, axis=0)
    if span[0] <= tolerance and span[1] > tolerance:
        return "ROOT_BOUNDARY" if uv[:, 0].mean() < 0.5 else "TIP_BOUNDARY"
    if span[1] <= tolerance and span[0] > tolerance:
        return "SIDE_BOUNDARY"
    return "UNKNOWN_DESIGN_BOUNDARY"

