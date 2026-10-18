#!/usr/bin/env python3
"""Load Dora SES salient-edge priors and turn them into CADFit plane seeds.

Expected NPZ (preferred): salient_edges_source_space.npz with
  edge_xyz0 (N,3), edge_xyz1 (N,3), optionally dihedral_deg / edge_length.
Coordinates must be in the same space as the CADFit input STL *before*
CADFit's internal normalize (X-Part / source mesh space).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np


def resolve_dora_prior(
    dora_dir: str | Path | None,
    part_id: str,
    threshold: int = 25,
    prefer_thresholds: tuple[int, ...] = (25, 35, 15, 45),
) -> Path | None:
    """Return best available salient_edges_source_space.npz for a part."""
    if not dora_dir:
        return None
    root = Path(dora_dir)
    if not root.is_dir():
        return None
    ordered = [int(threshold)]
    ordered.extend(int(t) for t in prefer_thresholds if int(t) != int(threshold))
    for th in ordered:
        p = root / f"threshold_{th}" / part_id / "salient_edges_source_space.npz"
        if p.is_file() and p.stat().st_size > 0:
            return p
        # fallback: Dora-norm indices only (less useful without mesh verts)
        p2 = root / f"threshold_{th}" / part_id / "salient_edges.npz"
        if p2.is_file() and p2.stat().st_size > 0:
            # only accept if it has xyz fields
            try:
                with np.load(p2) as z:
                    if "edge_xyz0" in z.files and "edge_xyz1" in z.files:
                        return p2
            except Exception:
                pass
    return None


def load_edge_segments(npz_path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    """Load edge endpoints as float64 arrays (N,3), (N,3)."""
    path = Path(npz_path)
    with np.load(path) as z:
        if "edge_xyz0" not in z.files or "edge_xyz1" not in z.files:
            raise ValueError(f"{path} missing edge_xyz0/edge_xyz1")
        p0 = np.asarray(z["edge_xyz0"], dtype=np.float64)
        p1 = np.asarray(z["edge_xyz1"], dtype=np.float64)
    if p0.ndim != 2 or p0.shape[1] != 3 or p0.shape != p1.shape:
        raise ValueError(f"bad edge arrays in {path}: {p0.shape} {p1.shape}")
    # drop degenerate
    lens = np.linalg.norm(p1 - p0, axis=1)
    keep = np.isfinite(lens) & (lens > 1e-9)
    return p0[keep], p1[keep]


def normalize_points(
    points: np.ndarray,
    center: np.ndarray,
    scale: float,
) -> np.ndarray:
    return (points - center.reshape(1, 3)) * float(scale)


def _xdir_from_normal(normal: np.ndarray) -> np.ndarray:
    n = normal / (np.linalg.norm(normal) + 1e-12)
    if abs(n[2]) < 0.9:
        u = np.cross(n, np.array([0.0, 0.0, 1.0]))
    else:
        u = np.cross(n, np.array([1.0, 0.0, 0.0]))
    u = u / (np.linalg.norm(u) + 1e-12)
    return u


def fit_planes_from_edges(
    p0: np.ndarray,
    p1: np.ndarray,
    *,
    min_edges: int = 6,
    residual_tol: float = 0.02,
    max_planes: int = 48,
    ransac_iters: int = 80,
    rng: np.random.Generator | None = None,
) -> list[dict[str, Any]]:
    """RANSAC-fit planes to Dora edge polylines in already-normalized space."""
    if len(p0) < min_edges:
        return []
    rng = rng or np.random.default_rng(0)
    pts = np.concatenate([p0, p1], axis=0)
    # also keep unique midpoints for scoring
    mids = 0.5 * (p0 + p1)
    dirs = p1 - p0
    dirs = dirs / (np.linalg.norm(dirs, axis=1, keepdims=True) + 1e-12)

    remaining = np.arange(len(mids))
    planes: list[dict[str, Any]] = []

    while len(remaining) >= min_edges and len(planes) < max_planes:
        best_inliers = None
        best_normal = None
        best_origin = None
        best_count = 0

        for _ in range(ransac_iters):
            if len(remaining) < 3:
                break
            # sample 3 midpoints (or 2 edges → 4 points, take first 3)
            idx = rng.choice(remaining, size=min(3, len(remaining)), replace=False)
            sample = mids[idx]
            if len(sample) < 3:
                continue
            c = sample.mean(axis=0)
            centered = sample - c
            try:
                _, _, vt = np.linalg.svd(centered, full_matrices=False)
            except np.linalg.LinAlgError:
                continue
            normal = vt[-1]
            nn = np.linalg.norm(normal)
            if nn < 1e-9:
                continue
            normal = normal / nn
            # prefer normals not parallel to all sampled edge dirs
            resid = np.abs((mids[remaining] - c) @ normal)
            inliers = remaining[resid <= residual_tol]
            if len(inliers) > best_count:
                best_count = len(inliers)
                best_inliers = inliers
                best_normal = normal
                best_origin = c

        if best_inliers is None or best_count < min_edges:
            break

        # refine with all inlier endpoints
        cloud = np.concatenate([p0[best_inliers], p1[best_inliers]], axis=0)
        origin = cloud.mean(axis=0)
        centered = cloud - origin
        try:
            _, _, vt = np.linalg.svd(centered, full_matrices=False)
            normal = vt[-1]
            normal = normal / (np.linalg.norm(normal) + 1e-12)
        except np.linalg.LinAlgError:
            normal = best_normal
            origin = best_origin

        # snap near-axis normals for CAD friendliness
        abs_n = np.abs(normal)
        if abs_n.max() > 0.95:
            axis = int(np.argmax(abs_n))
            snapped = np.zeros(3)
            snapped[axis] = 1.0 if normal[axis] >= 0 else -1.0
            normal = snapped

        xdir = _xdir_from_normal(normal)
        planes.append(
            {
                "origin": [round(float(x), 7) for x in origin.tolist()],
                "normal": [round(float(x), 7) for x in normal.tolist()],
                "xdir": [round(float(x), 7) for x in xdir.tolist()],
                "points": cloud[: min(64, len(cloud))].tolist(),
                "face_indices": [],
                "num_faces": int(best_count),
                "num_points": int(len(cloud)),
                "max_residual": float(
                    np.max(np.abs((cloud - origin) @ normal)) if len(cloud) else 0.0
                ),
                "source": "DORA_SALIENT_EDGE",
            }
        )
        remaining = np.setdiff1d(remaining, best_inliers, assume_unique=False)

    return planes


def planes_from_npz(
    npz_path: str | Path,
    *,
    center: np.ndarray | None = None,
    scale: float | None = None,
    min_edges: int = 6,
    residual_tol: float = 0.02,
    max_planes: int = 48,
) -> list[dict[str, Any]]:
    """Load NPZ, optionally normalize into CADFit box, fit planes."""
    p0, p1 = load_edge_segments(npz_path)
    if center is not None and scale is not None and float(scale) != 0.0:
        p0 = normalize_points(p0, np.asarray(center, dtype=np.float64), float(scale))
        p1 = normalize_points(p1, np.asarray(center, dtype=np.float64), float(scale))
    return fit_planes_from_edges(
        p0,
        p1,
        min_edges=min_edges,
        residual_tol=residual_tol,
        max_planes=max_planes,
    )
