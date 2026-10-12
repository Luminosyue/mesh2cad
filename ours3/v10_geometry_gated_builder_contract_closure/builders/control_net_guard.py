"""Control-net audit before MakeFace. Invalid nets are rejected, never clamped."""
from __future__ import annotations

from typing import Any

import numpy as np


def audit_control_net(poles: np.ndarray, part_bbox: dict[str, Any], support_bbox: dict[str, Any], cfg: dict[str, Any]) -> dict[str, Any]:
    poles = np.asarray(poles, float).reshape(-1, 3) if poles.ndim == 2 else np.asarray(poles, float)
    flat = poles.reshape(-1, 3)
    part_lo = np.asarray(part_bbox["bbox_min"], float)
    part_hi = np.asarray(part_bbox["bbox_max"], float)
    part_diag = max(float(part_bbox.get("bbox_diag") or np.linalg.norm(part_hi - part_lo)), 1e-12)
    support_lo = np.asarray(support_bbox.get("bbox_min") or part_lo, float)
    support_hi = np.asarray(support_bbox.get("bbox_max") or part_hi, float)
    lo = flat.min(0)
    hi = flat.max(0)
    diag = float(np.linalg.norm(hi - lo))
    dx = np.maximum(support_lo - flat, 0.0) + np.maximum(flat - support_hi, 0.0)
    dist = np.linalg.norm(dx, axis=1)
    grid = poles if poles.ndim == 3 else None
    steps = []
    folds = 0
    if grid is not None:
        for i in range(grid.shape[0]):
            d = np.diff(grid[i], axis=0)
            steps.extend(np.linalg.norm(d, axis=1).tolist())
            mean_dir = d.mean(axis=0) if len(d) else np.zeros(3)
            for a, b in zip(d[:-1], d[1:]):
                # Count foldover (parameter reversal along the row), not ordinary curvature.
                if np.dot(a, mean_dir) < 0 and np.dot(b, mean_dir) < 0:
                    folds += 1
        for j in range(grid.shape[1]):
            d = np.diff(grid[:, j], axis=0)
            steps.extend(np.linalg.norm(d, axis=1).tolist())
    steps = np.asarray(steps, float) if steps else np.asarray([0.0])
    cnet = cfg["control_net"]
    outlier_count = int(np.sum(dist > cnet["outlier_to_support_reject"] * part_diag))
    reasons = []
    if diag / part_diag >= cnet["diag_to_part_reject"]:
        reasons.append("CONTROL_POINT_BBOX_DIAG_RATIO")
    if float(dist.max() if len(dist) else 0) >= cnet["outlier_to_support_reject"] * part_diag:
        reasons.append("MAX_CONTROL_POINT_DISTANCE_TO_SUPPORT")
    if float(steps.max()) >= cnet["step_max_to_part_reject"] * part_diag:
        reasons.append("CONTROL_NET_EDGE_LENGTH_MAX")
    if folds > cnet["max_fold_count"]:
        reasons.append("CONTROL_NET_FOLD")
    if outlier_count > cnet["max_outlier_count"]:
        reasons.append("CONTROL_NET_OUTLIER")
    return {
        "CONTROL_NET_GUARD_PASS": not reasons,
        "BSPLINE_CONTROL_NET_REJECTED": bool(reasons),
        "reasons": reasons,
        "CONTROL_POINT_COUNT": int(len(flat)),
        "CONTROL_POINT_BBOX_DIAG_RATIO_TO_PART": diag / part_diag,
        "MAX_CONTROL_POINT_DISTANCE_TO_SUPPORT": float(dist.max() if len(dist) else 0.0),
        "CONTROL_NET_EDGE_LENGTH_P95": float(np.percentile(steps, 95)),
        "CONTROL_NET_EDGE_LENGTH_MAX": float(steps.max()),
        "CONTROL_NET_FOLD_COUNT": int(folds),
        "CONTROL_NET_OUTLIER_COUNT": outlier_count,
        "CONTROL_NET_OUTLIER": outlier_count > 0,
    }
