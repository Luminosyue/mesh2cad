"""Tracked Point2CAD-compatible normalization with invertible transform."""
from __future__ import annotations

import numpy as np

EPS = 1e-8


def pca_numpy(X: np.ndarray):
    S, U = np.linalg.eig(X.T @ X)
    return S, U


def rotation_matrix_a_to_b(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    cos = float(np.dot(A, B))
    sin = float(np.linalg.norm(np.cross(B, A)))
    u = A
    v = B - np.dot(A, B) * A
    v = v / (np.linalg.norm(v) + EPS)
    w = np.cross(B, A)
    w = w / (np.linalg.norm(w) + EPS)
    F = np.stack([u, v, w], 1)
    G = np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]], dtype=np.float64)
    try:
        R = F @ G @ np.linalg.inv(F)
    except np.linalg.LinAlgError:
        R = np.eye(3)
    # handle reflection / degenerate
    if np.linalg.det(R) < 0:
        R[:, 2] *= -1
    return R.astype(np.float64)


def normalize_points_tracked(points: np.ndarray, anisotropic: bool = False):
    """Match point2cad.utils.normalize_points but return invertible metadata."""
    points = np.asarray(points, dtype=np.float64)
    centroid = np.mean(points, axis=0, keepdims=True)
    centered = points - centroid
    S, U = pca_numpy(centered)
    smallest_ev = U[:, np.argmin(S)].real
    smallest_ev = smallest_ev / (np.linalg.norm(smallest_ev) + EPS)
    R = rotation_matrix_a_to_b(smallest_ev, np.array([1.0, 0.0, 0.0]))
    rotated = (R @ centered.T).T
    std = np.max(rotated, 0) - np.min(rotated, 0)
    if anisotropic:
        scale_vec = std + EPS
        normed = rotated / scale_vec.reshape((1, 3))
        meta = {
            "centroid": centroid.reshape(3).tolist(),
            "R": R.tolist(),
            "scale": scale_vec.tolist(),
            "anisotropic": True,
            "mode": "pca_axis_to_x",
        }
    else:
        scale = float(np.max(std) + EPS)
        normed = rotated / scale
        meta = {
            "centroid": centroid.reshape(3).tolist(),
            "R": R.tolist(),
            "scale": scale,
            "anisotropic": False,
            "mode": "pca_axis_to_x",
        }
    return normed.astype(np.float32), meta


def inverse_normalize_points(points: np.ndarray, meta: dict) -> np.ndarray:
    points = np.asarray(points, dtype=np.float64)
    R = np.asarray(meta["R"], dtype=np.float64)
    centroid = np.asarray(meta["centroid"], dtype=np.float64).reshape(1, 3)
    if meta.get("anisotropic"):
        scale = np.asarray(meta["scale"], dtype=np.float64).reshape(1, 3)
        rotated = points * scale
    else:
        rotated = points * float(meta["scale"])
    centered = (R.T @ rotated.T).T
    return (centered + centroid).astype(np.float64)


def bbox_stats(points: np.ndarray) -> dict:
    points = np.asarray(points, dtype=np.float64)
    if len(points) == 0:
        return {"min": [0, 0, 0], "max": [0, 0, 0], "centroid": [0, 0, 0], "diagonal": 0.0}
    mn = points.min(0)
    mx = points.max(0)
    return {
        "min": mn.tolist(),
        "max": mx.tolist(),
        "centroid": points.mean(0).tolist(),
        "diagonal": float(np.linalg.norm(mx - mn)),
    }
