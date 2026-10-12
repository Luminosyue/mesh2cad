from __future__ import annotations

import numpy as np
import trimesh


def detect_skeletal_structure(mesh: trimesh.Trimesh, occupancy: dict, topology: dict) -> dict:
    points = np.asarray(mesh.vertices, dtype=float)
    if len(points) < 3:
        return {"structural_class": "UNKNOWN", "structural_branching": False, "sparse_open": False, "skeleton_to_volume_ratio": 0.0}
    _, values, _ = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)
    ratios = np.sort(np.maximum(values, 1e-12))[::-1]
    aspect = float(ratios[0] / max(ratios[1], 1e-12))
    components = mesh.split(only_watertight=False)
    component_weights = sorted((float(item.area) for item in components), reverse=True)
    dominant_fraction = float(component_weights[0] / max(sum(component_weights), 1e-12)) if component_weights else 1.0
    sparse = bool(
        occupancy["source_occupancy_ratio"] < 0.18
        or topology["boundary_edge_count"] > max(8, len(mesh.faces) * 0.2)
        or len(components) > 1
    )
    branching = bool(
        sparse
        and (
            len(components) > 2
            or topology["skeleton_branch_count"] > max(8, len(mesh.faces) * 0.002)
            or (ratios[1] / max(ratios[2], 1e-12) > 2.0 and aspect < 4.0)
        )
    )
    if len(components) > 1 and dominant_fraction >= 0.55 and aspect > 1.5:
        structural_class = "BODY_WITH_APPENDAGES"
    elif branching and aspect > 2.0:
        structural_class = "ROD_NETWORK"
    elif branching:
        structural_class = "SPARSE_FRAME"
    elif sparse and occupancy["source_occupancy_ratio"] < 0.08:
        structural_class = "OPEN_FRAME"
    elif occupancy["source_occupancy_ratio"] < 0.22:
        structural_class = "SURFACE_LIKE"
    elif mesh.is_watertight:
        structural_class = "SOLID_LIKE"
    else:
        structural_class = "SURFACE_LIKE"
    return {
        "structural_class": structural_class,
        "structural_branching": branching,
        "sparse_open": sparse,
        "skeleton_to_volume_ratio": float(min(1.0, 1.0 / max(occupancy["source_occupancy_ratio"], 1e-6))),
        "principal_axis_ratio": aspect,
    }
