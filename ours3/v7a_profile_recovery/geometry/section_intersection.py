"""Low-level triangle/plane intersection with explicit cleanup counters."""

from dataclasses import dataclass
import numpy as np


@dataclass
class IntersectionResult:
    segments: np.ndarray
    raw_segment_count: int
    degenerate_segments_removed: int
    duplicate_segments_removed: int
    coplanar_triangles_removed: int


def _unique_points(points, tolerance):
    unique = []
    for point in points:
        if not any(np.linalg.norm(point - old) <= tolerance for old in unique):
            unique.append(point)
    return unique


def triangle_plane_segments(mesh, plane_origin, plane_normal, absolute_tolerance):
    origin = np.asarray(plane_origin, dtype=float)
    normal = np.asarray(plane_normal, dtype=float)
    normal /= np.linalg.norm(normal)
    eps = max(float(absolute_tolerance), 1e-12)
    raw = []
    degenerate = 0
    coplanar = 0

    triangles = np.asarray(mesh.triangles, dtype=float)
    all_signed = (triangles - origin) @ normal
    coplanar_mask = np.all(np.abs(all_signed) <= eps, axis=1)
    coplanar = int(coplanar_mask.sum())
    same_positive = np.all(all_signed > eps, axis=1)
    same_negative = np.all(all_signed < -eps, axis=1)
    candidates = ~(coplanar_mask | same_positive | same_negative)
    for triangle, signed in zip(triangles[candidates], all_signed[candidates]):
        if np.all(np.abs(signed) <= eps):
            continue
        if np.all(signed > eps) or np.all(signed < -eps):
            continue
        hits = []
        for i, j in ((0, 1), (1, 2), (2, 0)):
            a, b = triangle[i], triangle[j]
            da, db = signed[i], signed[j]
            if abs(da) <= eps:
                hits.append(a.copy())
            if da * db < -(eps * eps):
                hits.append(a + (b - a) * (da / (da - db)))
        hits = _unique_points(hits, eps)
        if len(hits) < 2:
            degenerate += 1
            continue
        if len(hits) > 2:
            pairs = [(np.linalg.norm(hits[i] - hits[j]), i, j)
                     for i in range(len(hits)) for j in range(i + 1, len(hits))]
            _, i, j = max(pairs)
            hits = [hits[i], hits[j]]
        if np.linalg.norm(hits[0] - hits[1]) <= eps:
            degenerate += 1
            continue
        raw.append(np.asarray(hits, dtype=float))

    raw_count = len(raw)
    if not raw:
        return IntersectionResult(np.empty((0, 2, 3)), 0, degenerate, 0, coplanar)

    # Remove orientation-independent duplicates at a much tighter scale than
    # graph snapping. This only removes the same geometric triangle edge.
    quant = max(eps * 0.25, 1e-12)
    seen = set()
    clean = []
    duplicate = 0
    for segment in raw:
        keys = [tuple(np.round(point / quant).astype(np.int64)) for point in segment]
        key = tuple(sorted(keys))
        if key in seen:
            duplicate += 1
            continue
        seen.add(key)
        clean.append(segment)
    return IntersectionResult(np.asarray(clean), raw_count, degenerate, duplicate, coplanar)
