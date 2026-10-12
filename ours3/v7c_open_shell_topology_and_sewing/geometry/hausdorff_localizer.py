"""Localize raw symmetric mesh/BRep tessellation Hausdorff outliers."""

from __future__ import annotations

import numpy as np
import trimesh
from scipy.spatial import cKDTree


def localize(source_path, brep_mesh_path, boundaries, sample_count=30000, seed=20260813):
    source = trimesh.load(source_path, force="mesh", process=False)
    brep = trimesh.load(brep_mesh_path, force="mesh", process=False)
    diagonal = float(np.linalg.norm(source.extents))
    source_points = trimesh.sample.sample_surface(source, sample_count, seed=seed)[0]
    brep_points = trimesh.sample.sample_surface(brep, sample_count, seed=seed + 1)[0]
    source_dist, source_index = cKDTree(brep_points).query(source_points)
    brep_dist, brep_index = cKDTree(source_points).query(brep_points)
    if source_dist.max() >= brep_dist.max():
        raw = float(source_dist.max())
        source_point = source_points[int(source_dist.argmax())]
        brep_point = brep_points[int(source_index[source_dist.argmax()])]
        direction = "SOURCE_TO_BREP"
    else:
        raw = float(brep_dist.max())
        brep_point = brep_points[int(brep_dist.argmax())]
        source_point = source_points[int(brep_index[brep_dist.argmax()])]
        direction = "BREP_TO_SOURCE"
    nearest = None
    for boundary in boundaries:
        points = np.asarray(boundary["points"], float)
        distance = float(cKDTree(points).query(brep_point)[0])
        if nearest is None or distance < nearest[0]:
            nearest = (distance, boundary)
    boundary = nearest[1]
    boundary_distance = nearest[0]
    region = boundary["semantic_type"] if boundary_distance <= diagonal * .05 else "INTERIOR"
    return {
        "HAUSDORFF_WORST_POINT_SOURCE": source_point.tolist(),
        "HAUSDORFF_WORST_POINT_BREP": brep_point.tolist(),
        "HAUSDORFF_WORST_DISTANCE_RAW": raw,
        "HAUSDORFF_WORST_DISTANCE": raw / max(diagonal, 1e-15),
        "HAUSDORFF_DIRECTION": direction,
        "HAUSDORFF_WORST_FACE_ID": boundary["face_id"],
        "HAUSDORFF_WORST_BOUNDARY_ID": boundary["boundary_id"],
        "HAUSDORFF_DISTANCE_TO_BOUNDARY_RAW": boundary_distance,
        "HAUSDORFF_WORST_REGION": region.replace("_BOUNDARY", ""),
        "SOURCE_DIAGONAL": diagonal,
    }

