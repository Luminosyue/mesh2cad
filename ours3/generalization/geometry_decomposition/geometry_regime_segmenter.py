from __future__ import annotations

from typing import Any

import numpy as np
import trimesh


def normal_clusters(mesh: trimesh.Trimesh) -> list[dict[str, Any]]:
    normals = np.asarray(mesh.face_normals, dtype=float)
    areas = np.asarray(mesh.area_faces, dtype=float)
    total = max(float(areas.sum()), 1e-12)
    clusters: list[dict[str, Any]] = []
    for normal, area in zip(normals, areas):
        unit = normal / max(float(np.linalg.norm(normal)), 1e-12)
        for cluster in clusters:
            if abs(float(np.dot(cluster["normal"], unit))) > 0.965:
                cluster["area"] += float(area)
                cluster["count"] += 1
                break
        else:
            clusters.append({"normal": unit, "area": float(area), "count": 1})
    clusters.sort(key=lambda row: row["area"], reverse=True)
    return [
        {"normal": row["normal"].tolist(), "area_ratio": row["area"] / total, "triangle_count": row["count"]}
        for row in clusters
    ]


def detect_regime(mesh: trimesh.Trimesh) -> dict[str, Any]:
    extents = np.sort(np.asarray(mesh.extents, dtype=float))[::-1]
    long_to_mid = float(extents[0] / max(extents[1], 1e-12))
    long_to_short = float(extents[0] / max(extents[2], 1e-12))
    mid_to_short = float(extents[1] / max(extents[2], 1e-12))
    clusters = normal_clusters(mesh)
    max_plane = clusters[0]["area_ratio"] if clusters else 0.0
    dominant_plane_count = sum(row["area_ratio"] >= 0.10 for row in clusters)
    linear = bool(long_to_mid >= 3.0 and long_to_short >= 6.0)
    cylinder = bool(linear and 0.55 <= extents[2] / max(extents[1], 1e-12) <= 1.05)
    thin_plate = bool(max_plane >= 0.28 and long_to_short >= 8.0 and mid_to_short >= 3.0)
    box_prism = bool(dominant_plane_count >= 4 and max_plane >= 0.12 and long_to_short < 8.0)
    if cylinder:
        regime = "CYLINDRICAL_ROD"
        confidence = 0.78
    elif linear:
        regime = "PROFILE_EXTRUSION" if mid_to_short > 1.35 else "LINEAR_ROD"
        confidence = 0.72
    elif thin_plate:
        regime = "THIN_PLATE"
        confidence = 0.72
    elif max_plane >= 0.32:
        regime = "PLANAR_PATCH"
        confidence = 0.68
    elif box_prism:
        regime = "BOX_PRISM"
        confidence = 0.62
    else:
        normals = np.asarray(mesh.face_normals, dtype=float)
        mean = normals.mean(axis=0)
        normal_dispersion = float(np.mean(1.0 - np.clip(normals @ (mean / max(np.linalg.norm(mean), 1e-12)), -1, 1)))
        regime = "GENERAL_FREEFORM" if normal_dispersion > 0.55 else "LOFTABLE_FREEFORM"
        confidence = 0.50
    return {
        "geometry_regime": regime,
        "geometry_confidence": confidence,
        "dominant_plane_count": int(dominant_plane_count),
        "max_single_plane_coverage": float(max_plane),
        "principal_axis_length_ratio": long_to_mid,
        "span_to_thickness_ratio": long_to_short,
        "cross_section_variation": float(abs(extents[1] - extents[2]) / max(extents[1], 1e-12)),
        "thin_plate_evidence": thin_plate,
        "linear_structure_evidence": linear,
        "cylinder_evidence": cylinder,
        "profile_extrusion_evidence": regime == "PROFILE_EXTRUSION",
        "box_prism_evidence": box_prism,
        "planar_patch_clusters": clusters[:8],
    }

