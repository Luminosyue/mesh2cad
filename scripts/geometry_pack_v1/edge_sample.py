"""Length-proportional sampling of polyline / segment sets into a fixed-size cloud."""

from __future__ import annotations

import numpy as np

from separate_edge_tokens_v1.edge_sampling import (  # noqa: E402
    allocate_points_by_length,
    sample_points_on_segments,
)


def _fit_to_size(
    points: np.ndarray,
    normals: np.ndarray,
    seg_idx: np.ndarray,
    num_points: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    n = points.shape[0]
    if n == num_points:
        return points, normals, seg_idx
    if n > num_points:
        keep = rng.choice(n, size=num_points, replace=False)
        keep.sort()
        return points[keep], normals[keep], seg_idx[keep]
    if n == 0:
        # Zero-sharp / empty branch: pad with zeros (edge_valid=false upstream).
        z = np.zeros((num_points, points.shape[1] if points.ndim == 2 else 3), dtype=np.float64)
        zn = np.zeros((num_points, 3), dtype=np.float64)
        zs = np.full((num_points,), -1, dtype=np.int32)
        return z, zn, zs
    extra = rng.choice(n, size=num_points - n, replace=True)
    return (
        np.concatenate([points, points[extra]], axis=0),
        np.concatenate([normals, normals[extra]], axis=0),
        np.concatenate([seg_idx, seg_idx[extra]], axis=0),
    )


def sample_edge_cloud(
    v0: np.ndarray,
    v1: np.ndarray,
    normals_per_segment: np.ndarray,
    num_points: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    """Return (points, normals, segment_index, stats) in the same coordinate frame as v0/v1."""
    v0 = np.asarray(v0, dtype=np.float64).reshape(-1, 3)
    v1 = np.asarray(v1, dtype=np.float64).reshape(-1, 3)
    normals_per_segment = np.asarray(normals_per_segment, dtype=np.float64).reshape(-1, 3)
    rng = np.random.default_rng(int(seed))
    if v0.shape[0] == 0:
        points = np.zeros((0, 3), dtype=np.float64)
        normals = np.zeros((0, 3), dtype=np.float64)
        seg_idx = np.zeros((0,), dtype=np.int32)
        points, normals, seg_idx = _fit_to_size(points, normals, seg_idx, num_points, rng)
        stats = {
            "num_segments": 0,
            "total_length": 0.0,
            "num_points": int(points.shape[0]),
            "points_per_segment_min": 0,
            "points_per_segment_max": 0,
            "degenerate_normal_count": int(num_points),
            "empty_padded": True,
        }
        return points, normals, seg_idx.astype(np.int32), stats

    lengths = np.linalg.norm(v1 - v0, axis=1)
    counts = allocate_points_by_length(lengths, num_points)
    points, seg_idx = sample_points_on_segments(v0, v1, counts)
    normals = normals_per_segment[seg_idx]
    nrm = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, nrm, out=np.zeros_like(normals), where=nrm > 1e-12)

    points, normals, seg_idx = _fit_to_size(points, normals, seg_idx, num_points, rng)
    stats = {
        "num_segments": int(v0.shape[0]),
        "total_length": float(lengths.sum()),
        "num_points": int(points.shape[0]),
        "points_per_segment_min": int(counts.min()),
        "points_per_segment_max": int(counts.max()),
        "degenerate_normal_count": int((np.linalg.norm(normals, axis=1) <= 1e-8).sum()),
        "empty_padded": False,
    }
    return points, normals, seg_idx.astype(np.int32), stats
