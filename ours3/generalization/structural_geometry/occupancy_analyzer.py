from __future__ import annotations

from typing import Any

import numpy as np
import trimesh


def _surface_points(mesh: trimesh.Trimesh, count: int = 7000) -> np.ndarray:
    points = np.asarray(mesh.vertices, dtype=float)
    if len(mesh.faces):
        try:
            sampled, _ = trimesh.sample.sample_surface(mesh, min(count, max(800, len(mesh.faces) * 2)), seed=101)
            points = np.concatenate([points, sampled], axis=0)
        except Exception:
            pass
    return points


def _grid_indices(points: np.ndarray, low: np.ndarray, high: np.ndarray, grid: int) -> np.ndarray:
    scale = np.maximum(high - low, 1e-12)
    coords = ((points - low) / scale * grid).astype(int)
    return np.clip(coords, 0, grid - 1)


def occupancy_mask(mesh: trimesh.Trimesh, low: np.ndarray, high: np.ndarray, grid: int = 24) -> np.ndarray:
    """Scale-normalized occupancy; watertight candidates include interior voxels."""
    mask = np.zeros((grid, grid, grid), dtype=bool)
    surface = _surface_points(mesh)
    if len(surface):
        ids = _grid_indices(surface, low, high, grid)
        mask[ids[:, 0], ids[:, 1], ids[:, 2]] = True
    # trimesh.contains without Embree is O(rays * faces) and can take hours
    # on large watertight meshes. Keep interior fill only for small solids.
    if mesh.is_watertight and len(mesh.vertices) and len(mesh.faces) <= 80000:
        axes = (np.arange(grid, dtype=float) + 0.5) / grid
        x, y, z = np.meshgrid(axes, axes, axes, indexing="ij")
        centers = np.column_stack((
            low[0] + x.ravel() * (high[0] - low[0]),
            low[1] + y.ravel() * (high[1] - low[1]),
            low[2] + z.ravel() * (high[2] - low[2]),
        ))
        try:
            inside = mesh.contains(centers)
            mask |= inside.reshape(mask.shape)
        except Exception:
            pass
    return mask


def section_masks(mesh: trimesh.Trimesh, low: np.ndarray, high: np.ndarray, grid: int = 48) -> list[np.ndarray]:
    points = _surface_points(mesh)
    if len(points) == 0:
        return [np.zeros((grid, grid), dtype=bool) for _ in range(3)]
    result = []
    for axis in range(3):
        others = [index for index in range(3) if index != axis]
        coords = _grid_indices(points, low, high, grid)
        mask = np.zeros((grid, grid), dtype=bool)
        mask[coords[:, others[0]], coords[:, others[1]]] = True
        result.append(mask)
    return result


def occupancy_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh, grid: int = 24) -> dict[str, Any]:
    low = np.minimum(np.asarray(source.bounds[0]), np.asarray(candidate.bounds[0]))
    high = np.maximum(np.asarray(source.bounds[1]), np.asarray(candidate.bounds[1]))
    source_mask = occupancy_mask(source, low, high, grid)
    candidate_mask = occupancy_mask(candidate, low, high, grid)
    intersection = source_mask & candidate_mask
    union = source_mask | candidate_mask
    source_count = max(int(source_mask.sum()), 1)
    candidate_count = max(int(candidate_mask.sum()), 1)
    union_count = max(int(union.sum()), 1)
    false_positive = int((candidate_mask & ~source_mask).sum())
    false_negative = int((source_mask & ~candidate_mask).sum())
    source_void = ~source_mask
    void_preserved = float((source_void & ~candidate_mask).sum() / max(int(source_void.sum()), 1))
    source_sections = section_masks(source, low, high)
    candidate_sections = section_masks(candidate, low, high)
    section_ious = []
    section_fp = []
    for left, right in zip(source_sections, candidate_sections):
        section_ious.append(float((left & right).sum() / max(int((left | right).sum()), 1)))
        section_fp.append(float((right & ~left).sum() / max(int(right.sum()), 1)))
    return {
        "source_occupancy_ratio": float(source_mask.mean()),
        "cad_occupancy_ratio": float(candidate_mask.mean()),
        "occupancy_iou": float(intersection.sum() / union_count),
        "occupancy_precision": float(intersection.sum() / candidate_count),
        "occupancy_recall": float(intersection.sum() / source_count),
        "false_positive_occupancy_ratio": float(false_positive / candidate_count),
        "false_negative_occupancy_ratio": float(false_negative / source_count),
        "void_preservation_ratio": void_preserved,
        "section_occupancy_iou_mean": float(np.mean(section_ious)),
        "section_occupancy_iou_p10": float(np.percentile(section_ious, 10)),
        "section_false_positive_mean": float(np.mean(section_fp)),
        "source_mask": source_mask,
        "candidate_mask": candidate_mask,
    }

