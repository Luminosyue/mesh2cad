"""Area-weighted patch sampling and arc-length boundary sampling."""

from __future__ import annotations

import numpy as np

from separate_edge_tokens_v1.edge_sampling import (
    allocate_points_by_length,
    sample_points_on_segments,
)


def triangle_areas(vertices: np.ndarray, triangles: np.ndarray) -> np.ndarray:
    tri = vertices[triangles]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    return 0.5 * np.linalg.norm(cr, axis=1)


def sample_barycentric(n: int, rng: np.random.Generator):
    u = rng.random(n)
    v = rng.random(n)
    mask = u + v > 1.0
    u = u.copy()
    v = v.copy()
    u[mask] = 1.0 - u[mask]
    v[mask] = 1.0 - v[mask]
    w = 1.0 - u - v
    return w, u, v


def sample_patch_from_face_mesh(
    vertices: np.ndarray,
    triangles: np.ndarray,
    n_points: int,
    seed: int,
    vertex_uv: np.ndarray | None = None,
) -> dict:
    """Uniform area sampling on one face triangulation. Never uses mesh vertices as the cloud."""
    vertices = np.asarray(vertices, dtype=np.float64)
    triangles = np.asarray(triangles, dtype=np.int64)
    if len(triangles) == 0:
        raise ValueError("empty face triangulation")
    areas = triangle_areas(vertices, triangles)
    usable = areas > 0
    if not np.any(usable):
        raise ValueError("zero-area triangulation")
    probs = np.zeros_like(areas)
    probs[usable] = areas[usable] / areas[usable].sum()
    rng = np.random.default_rng(int(seed))
    tri_idx = rng.choice(len(triangles), size=n_points, replace=True, p=probs)
    tri = vertices[triangles[tri_idx]]
    w, u, v = sample_barycentric(n_points, rng)
    points = w[:, None] * tri[:, 0] + u[:, None] * tri[:, 1] + v[:, None] * tri[:, 2]
    # geometric triangle normals as fallback
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm = np.linalg.norm(cr, axis=1, keepdims=True)
    normals = np.divide(cr, nrm, out=np.zeros_like(cr), where=nrm > 1e-18)
    uv = None
    if vertex_uv is not None:
        uvt = np.asarray(vertex_uv, dtype=np.float64)[triangles[tri_idx]]
        uv = w[:, None] * uvt[:, 0] + u[:, None] * uvt[:, 1] + v[:, None] * uvt[:, 2]
    return {
        "points": points.astype(np.float64),
        "normals": normals.astype(np.float64),
        "uv": None if uv is None else uv.astype(np.float64),
        "triangle_index": tri_idx.astype(np.int32),
    }


def sample_boundary_from_segments(
    segments_v0: np.ndarray,
    segments_v1: np.ndarray,
    segment_normals: np.ndarray,
    n_points: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, dict]:
    v0 = np.asarray(segments_v0, dtype=np.float64)
    v1 = np.asarray(segments_v1, dtype=np.float64)
    if len(v0) == 0:
        raise ValueError("no boundary segments")
    lengths = np.linalg.norm(v1 - v0, axis=1)
    counts = allocate_points_by_length(lengths, n_points)
    pts, seg_idx = sample_points_on_segments(v0, v1, counts)
    normals = np.asarray(segment_normals, dtype=np.float64)[seg_idx]
    nrm = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, nrm, out=np.zeros_like(normals), where=nrm > 1e-12)
    rng = np.random.default_rng(int(seed))
    n = pts.shape[0]
    if n > n_points:
        keep = rng.choice(n, size=n_points, replace=False)
        keep.sort()
        pts, normals, seg_idx = pts[keep], normals[keep], seg_idx[keep]
    elif n < n_points:
        if n == 0:
            raise ValueError("empty boundary cloud")
        extra = rng.choice(n, size=n_points - n, replace=True)
        pts = np.concatenate([pts, pts[extra]], axis=0)
        normals = np.concatenate([normals, normals[extra]], axis=0)
        seg_idx = np.concatenate([seg_idx, seg_idx[extra]], axis=0)
    stats = {
        "num_segments": int(len(v0)),
        "total_length": float(lengths.sum()),
        "num_points": int(pts.shape[0]),
    }
    return pts, normals, seg_idx.astype(np.int32), stats


def polylines_to_segments(polylines: list[np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    v0, v1 = [], []
    for poly in polylines:
        poly = np.asarray(poly, dtype=np.float64)
        if len(poly) < 2:
            continue
        for a, b in zip(poly[:-1], poly[1:]):
            if np.linalg.norm(b - a) <= 1e-12:
                continue
            v0.append(a)
            v1.append(b)
    if not v0:
        return np.zeros((0, 3)), np.zeros((0, 3))
    return np.asarray(v0), np.asarray(v1)
