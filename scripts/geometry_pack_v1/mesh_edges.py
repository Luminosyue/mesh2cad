"""Mesh sharp-edge detection via dihedral angle θ = arccos(n1 · n2)."""

from __future__ import annotations

import numpy as np

from .surface import face_normals


def dihedral_angles_deg(
    vertices: np.ndarray,
    faces: np.ndarray,
    adjacency: np.ndarray,
) -> np.ndarray:
    """θ in degrees for each adjacent face pair. 0 = coplanar, 90 = cube edge."""
    fn = face_normals(vertices, faces)
    n1 = fn[adjacency[:, 0]]
    n2 = fn[adjacency[:, 1]]
    dots = np.sum(n1 * n2, axis=1)
    dots = np.clip(dots, -1.0, 1.0)
    return np.degrees(np.arccos(dots))


def detect_sharp_edges(
    vertices: np.ndarray,
    faces: np.ndarray,
    adjacency: np.ndarray,
    adjacency_edges: np.ndarray,
    sharp_angle_deg: float,
) -> dict:
    """Return unique mesh edges whose adjacent-face dihedral exceeds the threshold."""
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    adjacency = np.asarray(adjacency, dtype=np.int64)
    adjacency_edges = np.asarray(adjacency_edges, dtype=np.int64)
    if len(adjacency) == 0:
        raise ValueError("mesh has no face adjacency; cannot detect sharp edges")

    angles = dihedral_angles_deg(vertices, faces, adjacency)
    keep = angles > float(sharp_angle_deg)
    pairs = adjacency_edges[keep]
    dihedral = angles[keep]
    if len(pairs) == 0:
        return {
            "v0": np.zeros((0, 3), dtype=np.float64),
            "v1": np.zeros((0, 3), dtype=np.float64),
            "vertex_indices": np.zeros((0, 2), dtype=np.int64),
            "dihedral_deg": np.zeros((0,), dtype=np.float64),
            "face_pairs": np.zeros((0, 2), dtype=np.int64),
            "num_segments": 0,
        }

    ordered = np.sort(pairs, axis=1)
    _, uniq = np.unique(ordered, axis=0, return_index=True)
    uniq = np.sort(uniq)
    idx = ordered[uniq]
    v0 = vertices[idx[:, 0]]
    v1 = vertices[idx[:, 1]]
    return {
        "v0": v0,
        "v1": v1,
        "vertex_indices": idx,
        "dihedral_deg": dihedral[uniq],
        "face_pairs": adjacency[keep][uniq],
        "num_segments": int(len(idx)),
    }


def segment_face_pair_normals(
    vertices: np.ndarray,
    faces: np.ndarray,
    face_pairs: np.ndarray,
) -> np.ndarray:
    """Normal of a sharp segment = renormalised mean of the two adjacent face normals."""
    fn = face_normals(vertices, faces)
    if len(face_pairs) == 0:
        return np.zeros((0, 3), dtype=np.float64)
    summed = fn[face_pairs[:, 0]] + fn[face_pairs[:, 1]]
    n = np.linalg.norm(summed, axis=1, keepdims=True)
    return np.divide(summed, n, out=np.zeros_like(summed), where=n > 1e-12)
