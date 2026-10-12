from __future__ import annotations

from typing import Any

import numpy as np

from .connected_component_splitter import Component


def detect_repetition(components: list[Component]) -> list[dict[str, Any]]:
    significant = [item for item in components if not item.tiny]
    if len(significant) < 4:
        return []
    dims = []
    centers = []
    for comp in significant:
        bounds = np.asarray(comp.bbox, dtype=float)
        dims.append(np.sort(bounds[1] - bounds[0]))
        centers.append(np.asarray(comp.centroid, dtype=float))
    dims = np.asarray(dims)
    centers = np.asarray(centers)
    mean_dim = dims.mean(axis=0)
    dim_variation = float(np.max(np.linalg.norm(dims - mean_dim, axis=1) / max(np.linalg.norm(mean_dim), 1e-12)))
    _, values, axes = np.linalg.svd(centers - centers.mean(axis=0), full_matrices=False)
    linearity = float(values[0] / max(values[1], 1e-12)) if len(values) > 1 else 0.0
    if dim_variation > 0.22 or linearity < 2.0:
        return []
    order = np.argsort((centers - centers.mean(axis=0)) @ axes[0])
    sorted_centers = centers[order]
    spacing = np.linalg.norm(np.diff(sorted_centers, axis=0), axis=1)
    spacing_variation = float(np.std(spacing) / max(np.mean(spacing), 1e-12)) if len(spacing) else 0.0
    if spacing_variation > 0.35:
        return []
    members = [significant[int(index)].component_id for index in order]
    return [{
        "group_id": "REP_" + "_".join(str(item) for item in members[:3]),
        "prototype_component_id": members[0],
        "member_component_ids": members,
        "member_count": len(members),
        "axis": axes[0].tolist(),
        "spacing_vector": (axes[0] * float(np.mean(spacing))).tolist() if len(spacing) else [0.0, 0.0, 0.0],
        "shape_similarity": 1.0 - dim_variation,
        "regularity_score": 1.0 - spacing_variation,
    }]

