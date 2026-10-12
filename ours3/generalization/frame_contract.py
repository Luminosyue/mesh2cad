from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np


CONVENTION = "COLUMN_VECTOR"


def as_matrix(value) -> np.ndarray:
    matrix = np.asarray(value, dtype=float)
    if matrix.shape != (4, 4):
        raise ValueError(f"EXPECTED_4X4_MATRIX:{matrix.shape}")
    return matrix


def inverse_pair(matrix) -> tuple[np.ndarray, np.ndarray]:
    forward = as_matrix(matrix)
    return forward, np.linalg.inv(forward)


def compose(*matrices) -> np.ndarray:
    result = np.eye(4, dtype=float)
    for matrix in matrices:
        result = result @ as_matrix(matrix)
    return result


def apply_transform(points: np.ndarray, matrix) -> np.ndarray:
    values = np.asarray(points, dtype=float)
    transform = as_matrix(matrix)
    homogeneous = np.column_stack([values, np.ones(len(values), dtype=float)])
    return (homogeneous @ transform.T)[:, :3]


def inverse_error(forward, backward) -> float:
    left = as_matrix(forward) @ as_matrix(backward)
    right = as_matrix(backward) @ as_matrix(forward)
    return float(max(np.max(np.abs(left - np.eye(4))), np.max(np.abs(right - np.eye(4)))))


def matrix_hash(matrix) -> str:
    values = np.asarray(matrix, dtype=np.float64)
    return hashlib.sha256(np.ascontiguousarray(values).tobytes()).hexdigest()


def axis_angle_error(left, right) -> float:
    a = as_matrix(left)[:3, :3]
    b = as_matrix(right)[:3, :3]
    relative = a.T @ b
    cosine = float(np.clip((np.trace(relative) - 1.0) * 0.5, -1.0, 1.0))
    return float(np.arccos(cosine))


def bbox(points: np.ndarray) -> np.ndarray:
    values = np.asarray(points, dtype=float)
    return np.vstack([values.min(axis=0), values.max(axis=0)])


def bbox_error(left: np.ndarray, right: np.ndarray) -> float:
    a = bbox(left)
    b = bbox(right)
    diag = max(float(np.linalg.norm(a[1] - a[0])), float(np.linalg.norm(b[1] - b[0])), 1e-12)
    return float(np.linalg.norm(a - b) / diag)


def centroid_error(left: np.ndarray, right: np.ndarray) -> float:
    diag = max(float(np.linalg.norm(bbox(left)[1] - bbox(left)[0])), 1e-12)
    return float(np.linalg.norm(np.mean(left, axis=0) - np.mean(right, axis=0)) / diag)
