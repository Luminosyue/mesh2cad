from __future__ import annotations

from typing import Any

import numpy as np


def _as_parts(value: Any) -> list[Any]:
    if value is None:
        return []
    if hasattr(value, "split") and hasattr(value, "vertices"):
        try:
            return list(value.split(only_watertight=False))
        except Exception:
            return [value]
    if isinstance(value, (list, tuple)):
        return list(value)
    return [value]


def _descriptor(part: Any) -> dict[str, Any]:
    vertices = np.asarray(part.vertices, dtype=float)
    if len(vertices) == 0:
        return {"centroid": np.zeros(3), "signature": np.zeros(3)}
    extents = np.ptp(vertices, axis=0)
    return {
        "centroid": vertices.mean(axis=0),
        "signature": np.sort(np.maximum(extents, 1e-12)),
    }


def _similar(left: dict[str, Any], right: dict[str, Any], tolerance: float) -> bool:
    scale = max(float(np.linalg.norm(left["signature"])), float(np.linalg.norm(right["signature"])), 1e-12)
    return float(np.linalg.norm(left["signature"] - right["signature"]) / scale) <= tolerance


def _regular_spacing(centroids: np.ndarray) -> tuple[bool, float]:
    if len(centroids) < 3:
        return False, 0.0
    centered = centroids - centroids.mean(axis=0)
    _, _, vectors = np.linalg.svd(centered, full_matrices=False)
    axis = vectors[0]
    positions = np.sort(centered @ axis)
    gaps = np.diff(positions)
    if len(gaps) == 0 or float(np.mean(np.abs(gaps))) <= 1e-9:
        return False, 0.0
    regularity = float(np.std(gaps) / max(abs(float(np.mean(gaps))), 1e-12))
    return regularity <= 0.2, max(0.0, 1.0 - regularity)


def detect_repetition_v2(parts: Any, min_members: int = 3, tolerance: float = 0.12) -> dict:
    """Detect repeated geometry using shape similarity and regular placement."""
    members = _as_parts(parts)
    if len(members) < min_members:
        return {
            "repetition_detected": False,
            "repetition_group_count": 0,
            "repetition_member_count": 0,
            "confidence": 0.0,
            "groups": [],
        }
    descriptors = [_descriptor(part) for part in members]
    groups: list[list[int]] = []
    unused = set(range(len(members)))
    while unused:
        seed = min(unused)
        group = [seed]
        unused.remove(seed)
        for index in list(unused):
            if _similar(descriptors[seed], descriptors[index], tolerance):
                group.append(index)
                unused.remove(index)
        if len(group) >= min_members:
            regular, _ = _regular_spacing(
                np.vstack([descriptors[index]["centroid"] for index in group])
            )
            if regular:
                groups.append(group)
    member_count = sum(len(group) for group in groups)
    return {
        "repetition_detected": bool(groups),
        "repetition_group_count": len(groups),
        "repetition_member_count": member_count,
        "confidence": float(member_count / max(len(members), 1)) if groups else 0.0,
        "groups": [
            {
                "member_indices": group,
                "prototype_index": group[0],
                "member_count": len(group),
            }
            for group in groups
        ],
    }
