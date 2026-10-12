from __future__ import annotations

from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from .io_utils import bbox_diag, load_mesh


def geometry_qa(src: trimesh.Trimesh, cad: trimesh.Trimesh, qa_source: str = "HYBRID") -> dict[str, Any]:
    a = np.asarray(src.sample(5000), dtype=float)
    b = np.asarray(cad.sample(min(5000, max(100, len(cad.vertices)))), dtype=float)
    d_ab = cKDTree(b).query(a)[0]
    d_ba = cKDTree(a).query(b)[0]
    diag = max(bbox_diag(src.vertices), 1e-12)
    bmin = np.minimum(a.min(0), b.min(0))
    bmax = np.maximum(a.max(0), b.max(0))
    ext = np.maximum(bmax - bmin, 1e-9)
    res = 28

    def vox(p):
        q = np.clip(np.floor((p - bmin) / ext * (res - 1)).astype(int), 0, res - 1)
        return set(map(tuple, q.tolist()))

    vs, vc = vox(a), vox(b)
    iou = len(vs & vc) / max(1, len(vs | vc))
    fp = len(vc - vs) / max(1, len(vc))
    return {
        "IoU": float(iou),
        "Chamfer": float(0.5 * (d_ab.mean() + d_ba.mean()) / diag),
        "Hausdorff": float(max(d_ab.max(), d_ba.max()) / diag),
        "Coverage": float(np.mean(d_ab <= 0.03 * diag)),
        "FP_OCCUPANCY": float(fp),
        "GEOMETRY_QA_FAIL": False,
        "QA_SOURCE": qa_source,
    }


def region_masked_qa(src: trimesh.Trimesh, cad: trimesh.Trimesh, region_mesh: trimesh.Trimesh) -> dict[str, Any]:
    rng = np.random.default_rng(11)
    pts = region_mesh.sample(min(3000, max(200, len(region_mesh.faces) * 3)))
    tree_s = cKDTree(np.asarray(src.vertices, dtype=float))
    tree_c = cKDTree(np.asarray(cad.vertices, dtype=float))
    d_s, _ = tree_s.query(pts)
    d_c, _ = tree_c.query(pts)
    diag = max(bbox_diag(src.vertices), 1e-12)
    return {
        "IoU": float(np.mean(d_c <= 0.04 * diag)),
        "Coverage": float(np.mean(d_c <= 0.03 * diag)),
        "FP_OCCUPANCY": float(np.mean(d_c < d_s) * 0.5),
        "Chamfer": float((d_c.mean()) / diag),
        "Hausdorff": float(d_c.max() / diag),
        "QA_SOURCE": "REGION_MASKED",
    }


def geometry_score(qa: dict[str, Any]) -> float:
    iou = float(qa.get("IoU") or 0.0)
    fp = float(qa.get("FP_OCCUPANCY") or 0.0)
    cov = float(qa.get("Coverage") or 0.0)
    return float(iou * (1.0 - fp) * max(cov, 0.05))


def cadfit_qa_fail(qa: dict[str, Any]) -> bool:
    iou = float(qa.get("IoU") or 0.0)
    return iou < 0.42


def selection_score(qa: dict[str, Any], validity: float, compactness: float, analyticity: float, weights: dict[str, float]) -> float:
    g = geometry_score(qa)
    return (
        weights["geometry"] * g
        + weights["validity"] * validity
        + weights["compactness"] * compactness
        + weights["analyticity"] * analyticity
    )
