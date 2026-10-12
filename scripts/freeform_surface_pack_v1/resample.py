"""Online resampling API (train-time). Face GT fixed; points re-sampled by seed."""

from __future__ import annotations

from pathlib import Path

import numpy as np

from .constants import N_BOUNDARY_POINTS, N_PATCH_POINTS
from .sample import polylines_to_segments, sample_boundary_from_segments, sample_patch_from_face_mesh


def load_face_mesh(sample_dir: Path) -> dict:
    data = np.load(sample_dir / "face_mesh.npz", allow_pickle=False)
    out = {
        "vertices": np.asarray(data["vertices"], dtype=np.float64),
        "triangles": np.asarray(data["triangles"], dtype=np.int64),
    }
    if "vertex_uv" in data.files:
        out["vertex_uv"] = np.asarray(data["vertex_uv"], dtype=np.float64)
    else:
        out["vertex_uv"] = None
    return out


def resample_patch(
    sample_dir: Path,
    *,
    n_points: int = N_PATCH_POINTS,
    seed: int,
) -> np.ndarray:
    """Return (n_points, 6) xyz+triangle_normal. Prefer UV from stored mesh UVs."""
    mesh = load_face_mesh(sample_dir)
    samp = sample_patch_from_face_mesh(
        mesh["vertices"],
        mesh["triangles"],
        n_points,
        seed,
        vertex_uv=mesh["vertex_uv"],
    )
    return np.concatenate([samp["points"], samp["normals"]], axis=1).astype(np.float32)


def resample_boundary(
    sample_dir: Path,
    *,
    n_points: int = N_BOUNDARY_POINTS,
    seed: int,
) -> np.ndarray:
    data = np.load(sample_dir / "boundary_segments.npz", allow_pickle=False)
    v0 = np.asarray(data["v0"], dtype=np.float64)
    v1 = np.asarray(data["v1"], dtype=np.float64)
    nrm = np.asarray(data["normals"], dtype=np.float64)
    pts, normals, _, _ = sample_boundary_from_segments(v0, v1, nrm, n_points, seed)
    return np.concatenate([pts, normals], axis=1).astype(np.float32)
