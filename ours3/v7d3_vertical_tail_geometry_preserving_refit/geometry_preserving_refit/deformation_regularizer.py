from __future__ import annotations


def budget(metrics, bbox_diagonal, max_ratio):
    ratio = metrics["MAX_CONTROL_POINT_DISPLACEMENT"] / max(float(bbox_diagonal), 1e-15)
    return {
        "MAX_CONTROL_POINT_DISPLACEMENT_RATIO": float(ratio),
        "MAX_ALLOWED_RATIO": float(max_ratio),
        "CONTROL_NET_DEFORMATION_BUDGET_EXCEEDED": bool(ratio > max_ratio),
    }
