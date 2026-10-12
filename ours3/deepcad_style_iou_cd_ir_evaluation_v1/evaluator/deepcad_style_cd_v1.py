"""Deterministic compatibility implementation of DeepCAD evaluate_ae_cd.py."""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree


GLOBAL_SEED = 20260915
SAMPLE_N = 2000


def case_seed(case_id: str, global_seed: int = GLOBAL_SEED) -> int:
    digest = hashlib.sha256(f"{global_seed}:{case_id}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big", signed=False) % (2**32)


def sample_mesh_surface(vertices, faces, n_points: int = SAMPLE_N, seed: int = 0):
    """Uniform-by-area triangle sampling with an explicit NumPy RNG."""
    vertices = np.asarray(vertices, dtype=np.float64)
    faces = np.asarray(faces, dtype=np.int64)
    tri = vertices[faces]
    cross = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    areas = 0.5 * np.linalg.norm(cross, axis=1)
    if len(areas) == 0 or not np.isfinite(areas).all() or areas.sum() <= 0:
        raise ValueError("surface has no positive-area triangles")
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(tri), size=n_points, p=areas / areas.sum())
    chosen = tri[idx]
    uv = rng.random((n_points, 2))
    over = uv.sum(axis=1) > 1.0
    uv[over] = 1.0 - uv[over]
    return chosen[:, 0] + uv[:, :1] * (chosen[:, 1] - chosen[:, 0]) + uv[:, 1:] * (chosen[:, 2] - chosen[:, 0])


def chamfer_squared_symmetric(gt_points, pred_points) -> float:
    gt = np.asarray(gt_points, dtype=np.float64)
    pred = np.asarray(pred_points, dtype=np.float64)
    if gt.ndim != 2 or pred.ndim != 2 or gt.shape[1] != 3 or pred.shape[1] != 3:
        raise ValueError("point clouds must have shape (N, 3)")
    if len(gt) == 0 or len(pred) == 0:
        raise ValueError("empty point cloud")
    d_gt = cKDTree(pred).query(gt, k=1)[0]
    d_pred = cKDTree(gt).query(pred, k=1)[0]
    return float(np.mean(np.square(d_gt)) + np.mean(np.square(d_pred)))


def deterministic_cd(gt_mesh, pred_mesh, case_id: str, n_points: int = SAMPLE_N) -> float:
    seed = case_seed(case_id)
    gt = sample_mesh_surface(gt_mesh.vertices, gt_mesh.faces, n_points, seed)
    pred = sample_mesh_surface(pred_mesh.vertices, pred_mesh.faces, n_points, seed + 1)
    return chamfer_squared_symmetric(gt, pred)
