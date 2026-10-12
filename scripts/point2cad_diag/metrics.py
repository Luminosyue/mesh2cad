"""Geometry / segmentation / topology metrics for diagnosis."""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np


def chamfer_symmetric(a: np.ndarray, b: np.ndarray, max_points: int = 8000, seed: int = 0) -> Dict:
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if len(a) == 0 or len(b) == 0:
        return {"chamfer_sym": None, "a_to_b": None, "b_to_a": None, "hausdorff": None}
    if len(a) > max_points:
        a = a[rng.choice(len(a), max_points, replace=False)]
    if len(b) > max_points:
        b = b[rng.choice(len(b), max_points, replace=False)]
    # chunked cdist to limit memory
    def mean_min(src, dst):
        mins = []
        for i in range(0, len(src), 1000):
            chunk = src[i : i + 1000]
            d2 = ((chunk[:, None, :] - dst[None, :, :]) ** 2).sum(-1)
            mins.append(np.sqrt(d2.min(1)))
        return np.concatenate(mins)

    a2b = mean_min(a, b)
    b2a = mean_min(b, a)
    return {
        "chamfer_sym": float(a2b.mean() + b2a.mean()),
        "a_to_b": float(a2b.mean()),
        "b_to_a": float(b2a.mean()),
        "hausdorff": float(max(a2b.max(), b2a.max())),
        "coverage_at_0.02": float((a2b < 0.02).mean()),
        "coverage_at_0.05": float((a2b < 0.05).mean()),
        "coverage_at_0.10": float((a2b < 0.10).mean()),
    }


def bbox_iou(a: np.ndarray, b: np.ndarray) -> float:
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    if len(a) == 0 or len(b) == 0:
        return 0.0
    amin, amax = a.min(0), a.max(0)
    bmin, bmax = b.min(0), b.max(0)
    inter_min = np.maximum(amin, bmin)
    inter_max = np.minimum(amax, bmax)
    inter = np.maximum(0.0, inter_max - inter_min)
    inter_vol = float(np.prod(inter))
    vol_a = float(np.prod(np.maximum(0.0, amax - amin)))
    vol_b = float(np.prod(np.maximum(0.0, bmax - bmin)))
    union = vol_a + vol_b - inter_vol + 1e-12
    return inter_vol / union


def segmentation_stats(labels: np.ndarray, gt_face_count: Optional[int] = None) -> Dict:
    labels = np.asarray(labels, dtype=np.int32)
    if len(labels) == 0:
        return {"predicted_cluster_count": 0}
    uniq, counts = np.unique(labels, return_counts=True)
    counts_sorted = np.sort(counts)[::-1]
    total = int(counts.sum())
    out = {
        "predicted_cluster_count": int(len(uniq)),
        "cluster_sizes": counts.tolist(),
        "cluster_size_min": int(counts.min()),
        "cluster_size_median": float(np.median(counts)),
        "cluster_size_max": int(counts.max()),
        "clusters_lt_20": int((counts < 20).sum()),
        "clusters_lt_50": int((counts < 50).sum()),
        "clusters_lt_100": int((counts < 100).sum()),
        "clusters_lt_200": int((counts < 200).sum()),
        "max_cluster_fraction": float(counts.max() / total),
        "cluster_size_rank": [
            {"rank": i + 1, "label": int(uniq[np.argsort(-counts)[i]]), "points": int(counts_sorted[i])}
            for i in range(len(counts_sorted))
        ],
    }
    if gt_face_count is not None and gt_face_count > 0:
        ratio = out["predicted_cluster_count"] / float(gt_face_count)
        out["gt_step_face_count"] = int(gt_face_count)
        out["cluster_count_over_face_count_ratio"] = float(ratio)
        out["severe_under_segmentation"] = bool(out["predicted_cluster_count"] < 0.5 * gt_face_count)
    else:
        out["severe_under_segmentation"] = None
    out["dominant_cluster_warning"] = bool(out["max_cluster_fraction"] > 0.25)
    return out


def mesh_quality_stats(mesh) -> Dict:
    import trimesh

    if mesh is None:
        return {"empty": True}
    if isinstance(mesh, trimesh.Scene):
        geoms = list(mesh.geometry.values())
        mesh = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.faces)
    try:
        comps = mesh.split(only_watertight=False)
        ncomp = len(comps)
    except Exception:
        ncomp = 1 if len(F) else 0
    # duplicate vertex ratio
    if len(V):
        rounded = np.round(V, 6)
        uniq = np.unique(rounded, axis=0)
        dup_ratio = 1.0 - len(uniq) / len(V)
    else:
        dup_ratio = 0.0
    return {
        "vertex_count": int(len(V)),
        "triangle_count": int(len(F)),
        "connected_component_count": int(ncomp),
        "watertight": bool(getattr(mesh, "is_watertight", False)),
        "is_watertight": bool(getattr(mesh, "is_watertight", False)),
        "is_winding_consistent": bool(getattr(mesh, "is_winding_consistent", False)) if hasattr(mesh, "is_winding_consistent") else None,
        "duplicate_point_ratio": float(dup_ratio),
        "bbox": {
            "min": V.min(0).tolist() if len(V) else [0, 0, 0],
            "max": V.max(0).tolist() if len(V) else [0, 0, 0],
            "diagonal": float(np.linalg.norm(V.max(0) - V.min(0))) if len(V) else 0.0,
        },
    }


def normal_stats(normals: Optional[np.ndarray]) -> Dict:
    if normals is None or len(normals) == 0:
        return {"normal_count": 0, "invalid_normal_count": 0, "flipped_normal_ratio": None}
    n = np.asarray(normals, dtype=np.float64)
    nn = np.linalg.norm(n, axis=1)
    invalid = int((~np.isfinite(nn) | (nn < 1e-8)).sum())
    # flipped ratio undefined without reference; report None
    return {
        "normal_count": int(len(n)),
        "invalid_normal_count": invalid,
        "flipped_normal_ratio": None,
        "mean_norm": float(nn[np.isfinite(nn)].mean()) if np.isfinite(nn).any() else None,
    }
