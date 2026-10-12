from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


def _unit(vector: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(vector))
    return vector / max(norm, 1e-12)


def _radial_residual(points: np.ndarray, axis: np.ndarray, origin: np.ndarray) -> float:
    centered = points - origin
    axial = centered @ axis
    radial = centered - np.outer(axial, axis)
    radius = np.linalg.norm(radial, axis=1)
    if len(radius) < 8:
        return float(np.std(radius) / max(np.mean(radius), 1e-12))
    bins = np.linspace(float(axial.min()), float(axial.max()), 13)
    residuals = []
    for low, high in zip(bins[:-1], bins[1:]):
        values = radius[(axial >= low) & (axial <= high)]
        if len(values) >= 4:
            residuals.append(float(np.std(values) / max(np.mean(values), 1e-12)))
    return float(np.mean(residuals)) if residuals else float(np.std(radius) / max(np.mean(radius), 1e-12))


def canonical_frame(mesh: trimesh.Trimesh) -> dict[str, Any]:
    points = np.asarray(mesh.vertices, dtype=float)
    if len(points) < 3:
        raise ValueError("LOCAL_FRAME_TOO_FEW_VERTICES")
    origin = points.mean(axis=0)
    _, singular_values, vh = np.linalg.svd(points - origin, full_matrices=False)
    pca_axes = np.asarray(vh, dtype=float)
    ratios = singular_values / max(float(singular_values[0]), 1e-12)
    planarity = float(ratios[-1])
    if planarity < 0.15:
        axis_z = _unit(pca_axes[-1])
        method = "PCA_THIN_AXIS_WITH_NORMAL_PRIOR"
        confidence = float(max(0.0, 1.0 - planarity / 0.15))
    else:
        scores = [_radial_residual(points, _unit(axis), origin) for axis in pca_axes]
        best = int(np.argmin(scores))
        axis_z = _unit(pca_axes[best])
        method = "PCA_RADIAL_RESIDUAL_AXIS"
        confidence = float(max(0.0, 1.0 - min(scores[best], 1.0)))
    normal_hint = np.asarray(mesh.face_normals, dtype=float).mean(axis=0) if len(mesh.faces) else axis_z
    if float(np.dot(axis_z, normal_hint)) < 0:
        axis_z *= -1.0
    remaining = [axis for axis in pca_axes if abs(float(np.dot(axis, axis_z))) < 0.95]
    axis_x = _unit(remaining[0] if remaining else np.array([1.0, 0.0, 0.0]))
    axis_x = _unit(axis_x - axis_z * float(np.dot(axis_x, axis_z)))
    axis_y = _unit(np.cross(axis_z, axis_x))
    axis_x = _unit(np.cross(axis_y, axis_z))
    axes = np.column_stack((axis_x, axis_y, axis_z))
    world_to_local = np.eye(4)
    world_to_local[:3, :3] = axes.T
    world_to_local[:3, 3] = -axes.T @ origin
    local_to_world = np.linalg.inv(world_to_local)
    return {
        "origin": origin.tolist(),
        "axis_x": axis_x.tolist(),
        "axis_y": axis_y.tolist(),
        "axis_z": axis_z.tolist(),
        "axes": axes.tolist(),
        "world_to_local": world_to_local.tolist(),
        "local_to_world": local_to_world.tolist(),
        "method": method,
        "confidence": confidence,
        "planarity": planarity,
        "singular_value_ratios": ratios.tolist(),
        "radial_residual": _radial_residual(points, axis_z, origin),
    }


def transform_mesh(mesh: trimesh.Trimesh, matrix: np.ndarray) -> trimesh.Trimesh:
    vertices = np.column_stack((np.asarray(mesh.vertices, dtype=float), np.ones(len(mesh.vertices))))
    transformed = (matrix @ vertices.T).T[:, :3]
    return trimesh.Trimesh(vertices=transformed, faces=np.asarray(mesh.faces), process=False)


def localize_mesh(mesh: trimesh.Trimesh, frame: dict[str, Any]) -> trimesh.Trimesh:
    return transform_mesh(mesh, np.asarray(frame["world_to_local"], dtype=float))


def save_frame(frame: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(frame, indent=2, sort_keys=True) + "\n", encoding="utf-8")
