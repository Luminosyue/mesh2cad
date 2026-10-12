from __future__ import annotations

import math
from typing import Any

import numpy as np
import trimesh


def _pca(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    points = np.asarray(mesh.vertices, dtype=float)
    origin = points.mean(axis=0)
    _, singular, axes = np.linalg.svd(points - origin, full_matrices=False)
    return origin, singular, np.asarray(axes, dtype=float)


def _boundary_stats(mesh: trimesh.Trimesh) -> dict[str, Any]:
    edges = np.asarray(mesh.edges_unique, dtype=np.int64)
    inverse = np.asarray(mesh.edges_unique_inverse, dtype=np.int64)
    if not len(edges):
        return {
            "boundary_edge_count": 0,
            "boundary_vertex_count": 0,
            "closed_loop_count": 0,
            "open_chain_count": 0,
            "self_intersection_count": 0,
            "boundary_edges": [],
        }
    counts = np.bincount(inverse, minlength=len(edges))
    boundary = edges[counts == 1]
    if not len(boundary):
        return {
            "boundary_edge_count": 0,
            "boundary_vertex_count": 0,
            "closed_loop_count": 0,
            "open_chain_count": 0,
            "self_intersection_count": 0,
            "boundary_edges": [],
        }
    adjacency: dict[int, list[int]] = {}
    for index, (a, b) in enumerate(boundary):
        adjacency.setdefault(int(a), []).append(index)
        adjacency.setdefault(int(b), []).append(index)
    degrees = [len(value) for value in adjacency.values()]
    unused = set(range(len(boundary)))
    closed = 0
    chains = 0
    while unused:
        edge_index = min(unused)
        a, b = map(int, boundary[edge_index])
        unused.remove(edge_index)
        start, current = a, b
        previous = a
        steps = 1
        while current != start:
            choices = [
                item for item in adjacency.get(current, [])
                if item in unused
            ]
            if not choices:
                break
            next_edge = min(choices)
            unused.remove(next_edge)
            x, y = map(int, boundary[next_edge])
            next_vertex = y if x == current else x
            previous, current = current, next_vertex
            steps += 1
            if steps > len(boundary) + 2:
                break
        if current == start and steps >= 3:
            closed += 1
        else:
            chains += 1
    return {
        "boundary_edge_count": int(len(boundary)),
        "boundary_vertex_count": int(len(adjacency)),
        "closed_loop_count": int(closed),
        "open_chain_count": int(chains),
        "boundary_degree_min": int(min(degrees)),
        "boundary_degree_max": int(max(degrees)),
        "self_intersection_count": 0,
        "boundary_edges": boundary.tolist(),
    }


def _normal_cluster_count(mesh: trimesh.Trimesh) -> tuple[int, list[dict[str, Any]]]:
    normals = np.asarray(mesh.face_normals, dtype=float)
    if len(normals) == 0:
        return 0, []
    quantized = np.round(normals, 1)
    unique, counts = np.unique(quantized, axis=0, return_counts=True)
    order = np.argsort(counts)[::-1]
    clusters = [
        {
            "normal": unique[index].tolist(),
            "triangle_count": int(counts[index]),
            "fraction": float(counts[index] / len(normals)),
        }
        for index in order[:12]
    ]
    dominant = [item for item in clusters if item["fraction"] >= 0.015]
    return len(dominant), clusters


def _thickness_estimate(mesh: trimesh.Trimesh, singular: np.ndarray) -> dict[str, Any]:
    ratios = singular / max(float(singular[0]), 1e-12)
    if len(singular) < 3:
        return {
            "thickness": 0.0,
            "thickness_ratio": 1.0,
            "method": "INSUFFICIENT_PCA",
        }
    thickness = float(singular[-1] / max(float(singular[0]), 1e-12))
    return {
        "thickness": thickness,
        "thickness_ratio": thickness,
        "in_plane_ratio": float(singular[1] / max(float(singular[0]), 1e-12)),
        "method": "PCA_THIN_AXIS_ROBUST_PERCENTILE_PROXY",
        "singular_value_ratios": ratios.tolist(),
    }


def _planarity_residual(mesh: trimesh.Trimesh, origin: np.ndarray, axes: np.ndarray) -> float:
    points = np.asarray(mesh.vertices, dtype=float)
    distances = np.abs((points - origin) @ axes[-1])
    scale = max(float(np.linalg.norm(np.ptp(points, axis=0))), 1e-12)
    return float(np.percentile(distances, 95) / scale)


def _orthogonal_evidence(clusters: list[dict[str, Any]]) -> float:
    normals = [
        np.asarray(item["normal"], dtype=float)
        for item in clusters
        if item["fraction"] >= 0.03
    ]
    if len(normals) < 3:
        return 0.0
    scores = []
    for index, first in enumerate(normals):
        for second in normals[index + 1:]:
            scores.append(abs(float(np.dot(first, second))))
    if not scores:
        return 0.0
    return float(np.mean([value < 0.12 for value in scores]))


def _revolution_evidence(mesh: trimesh.Trimesh, origin: np.ndarray, axes: np.ndarray) -> dict[str, float]:
    points = np.asarray(mesh.vertices, dtype=float)
    best = math.inf
    best_index = 0
    for index, axis in enumerate(axes):
        centered = points - origin
        axial = centered @ axis
        radial = centered - np.outer(axial, axis)
        radius = np.linalg.norm(radial, axis=1)
        if len(radius) < 10:
            continue
        bins = np.linspace(float(axial.min()), float(axial.max()), 13)
        residuals = []
        for low, high in zip(bins[:-1], bins[1:]):
            values = radius[(axial >= low) & (axial <= high)]
            if len(values) >= 8:
                residuals.append(float(np.std(values) / max(np.mean(values), 1e-12)))
        score = float(np.mean(residuals)) if residuals else math.inf
        if score < best:
            best, best_index = score, index
    radial_residual = float(best if math.isfinite(best) else 1.0)
    return {
        "revolution_radial_residual": radial_residual,
        "revolution_symmetry_score": float(max(0.0, 1.0 - radial_residual)),
        "revolution_axis_index": int(best_index),
        "revolution_allowed": bool(radial_residual <= 0.12),
    }


def classify_topology(mesh: trimesh.Trimesh) -> dict[str, Any]:
    origin, singular, axes = _pca(mesh)
    boundary = _boundary_stats(mesh)
    cluster_count, clusters = _normal_cluster_count(mesh)
    thickness = _thickness_estimate(mesh, singular)
    planarity = _planarity_residual(mesh, origin, axes)
    area = float(mesh.area)
    extents = np.ptp(np.asarray(mesh.vertices, dtype=float), axis=0)
    bbox_volume = float(np.prod(np.maximum(extents, 1e-12)))
    volume = float(mesh.volume) if mesh.is_volume else 0.0
    revolution = _revolution_evidence(mesh, origin, axes)
    orthogonal = _orthogonal_evidence(clusters)
    open_surface = bool(
        not mesh.is_watertight
        and boundary["boundary_edge_count"] > 0
    )
    thin_sheet = bool(
        open_surface
        and thickness["thickness_ratio"] <= 0.16
        and (extents.max() / max(np.sort(extents)[-2], 1e-12)) >= 1.8
    )
    multi_patch = bool(
        open_surface
        and (cluster_count >= 5 or planarity > 0.08 or orthogonal >= 0.45)
    )
    if mesh.is_watertight and volume > bbox_volume * 1e-4 and not open_surface:
        topology_class = "VOLUMETRIC_SOLID"
    elif multi_patch:
        topology_class = "MULTI_PATCH_SURFACE"
    elif thin_sheet:
        topology_class = "THIN_SHEET"
    elif open_surface:
        topology_class = "OPEN_SURFACE"
    else:
        topology_class = "UNKNOWN"
    return {
        "topology_class": topology_class,
        "watertight": bool(mesh.is_watertight),
        "volume": volume,
        "surface_area": area,
        "bbox_volume": bbox_volume,
        "surface_area_to_bbox_volume": float(area / max(bbox_volume, 1e-12)),
        "bbox_extent": extents.tolist(),
        "planarity_residual": planarity,
        "normal_cluster_count": cluster_count,
        "normal_clusters": clusters,
        "orthogonal_structure_score": orthogonal,
        "boundary": boundary,
        "thickness": thickness,
        **revolution,
        "dominant_axis": int(np.argmax(singular)),
        "pca_axes": axes.tolist(),
        "pca_singular_values": singular.tolist(),
    }


def builder_gate(topology: dict[str, Any]) -> dict[str, Any]:
    topology_class = topology["topology_class"]
    revolution_allowed = bool(
        topology["revolution_allowed"]
        and topology_class not in {"THIN_SHEET", "MULTI_PATCH_SURFACE", "OPEN_SURFACE"}
    )
    box_allowed = bool(
        topology_class == "VOLUMETRIC_SOLID"
        and topology["orthogonal_structure_score"] >= 0.55
        and topology["normal_cluster_count"] <= 8
    )
    planar_allowed = bool(topology["planarity_residual"] <= 0.035)
    extrusion_allowed = bool(
        topology_class == "VOLUMETRIC_SOLID"
        and topology["normal_cluster_count"] <= 4
    )
    gates = {
        "topology_class": topology_class,
        "TRIMMED_PLANAR_FACE": {
            "allowed": planar_allowed,
            "reason": "planarity_residual_gate" if planar_allowed else "planarity_residual_above_threshold",
        },
        "RULED_SURFACE": {
            "allowed": topology_class in {"THIN_SHEET", "OPEN_SURFACE", "MULTI_PATCH_SURFACE"},
            "reason": "open_surface_family" if topology_class != "VOLUMETRIC_SOLID" else "solid_surface_route_not_preferred",
        },
        "LOFT_SURFACE": {
            "allowed": topology_class in {"THIN_SHEET", "OPEN_SURFACE", "MULTI_PATCH_SURFACE"},
            "reason": "non_solid_surface_family" if topology_class != "VOLUMETRIC_SOLID" else "solid_surface_route_not_preferred",
        },
        "MULTI_PATCH_SURFACE": {
            "allowed": topology_class == "MULTI_PATCH_SURFACE",
            "reason": "normal_cluster_and_boundary_evidence",
        },
        "REVOLUTION": {
            "allowed": revolution_allowed,
            "reason": "radial_symmetry_pass" if revolution_allowed else "radial_symmetry_insufficient_or_non_axisymmetric",
        },
        "BOX_PRISM": {
            "allowed": box_allowed,
            "reason": "volumetric_orthogonal_pass" if box_allowed else "non_volumetric_or_non_orthogonal",
        },
        "PROFILE_EXTRUSION": {
            "allowed": extrusion_allowed,
            "reason": "thin_sheet_or_solid_simple_profile" if extrusion_allowed else "topology_or_profile_gate_failed",
        },
    }
    return gates


def allowed_families(gates: dict[str, Any]) -> list[str]:
    order = [
        "TRIMMED_PLANAR_FACE",
        "MULTI_PATCH_SURFACE",
        "RULED_SURFACE",
        "LOFT_SURFACE",
        "PROFILE_EXTRUSION",
        "REVOLUTION",
        "BOX_PRISM",
    ]
    return [family for family in order if gates.get(family, {}).get("allowed")]
