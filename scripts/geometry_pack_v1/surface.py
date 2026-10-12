"""Area-weighted uniform surface sampling. Mesh vertices are never used as the cloud."""

from __future__ import annotations

import numpy as np


def triangle_areas(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    return 0.5 * np.linalg.norm(cr, axis=1)


def face_normals(vertices: np.ndarray, faces: np.ndarray) -> np.ndarray:
    tri = vertices[faces]
    cr = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n = np.linalg.norm(cr, axis=1, keepdims=True)
    return np.divide(cr, n, out=np.zeros_like(cr), where=n > 1e-18)


def sample_barycentric(n: int, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Uniform samples inside a triangle via folded unit square."""
    u = rng.random(n)
    v = rng.random(n)
    mask = u + v > 1.0
    u = u.copy()
    v = v.copy()
    u[mask] = 1.0 - u[mask]
    v[mask] = 1.0 - v[mask]
    w = 1.0 - u - v
    return w, u, v


def sample_surface_uniform(
    vertices: np.ndarray,
    faces: np.ndarray,
    n_points: int,
    seed: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (points, normals, face_index).

    Triangle i is chosen with p_i = A_i / sum_j A_j.
    The point is uniform in that triangle. Normal is the geometric face normal.
    """
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    if n_points <= 0:
        raise ValueError("n_points must be positive")
    if len(faces) == 0:
        raise ValueError("mesh has no faces")

    areas = triangle_areas(vertices, faces)
    total = float(areas.sum())
    if total <= 0:
        raise ValueError("mesh has zero area")
    usable = areas > 0
    if not np.any(usable):
        raise ValueError("all triangles have zero area")

    probs = np.zeros_like(areas)
    probs[usable] = areas[usable] / areas[usable].sum()
    rng = np.random.default_rng(int(seed))
    face_idx = rng.choice(len(faces), size=n_points, replace=True, p=probs)

    tri = vertices[faces[face_idx]]
    w, u, v = sample_barycentric(n_points, rng)
    points = w[:, None] * tri[:, 0] + u[:, None] * tri[:, 1] + v[:, None] * tri[:, 2]

    normals = face_normals(vertices, faces)[face_idx]
    nrm = np.linalg.norm(normals, axis=1, keepdims=True)
    normals = np.divide(normals, nrm, out=np.zeros_like(normals), where=nrm > 1e-12)
    return points.astype(np.float64), normals.astype(np.float64), face_idx.astype(np.int32)
