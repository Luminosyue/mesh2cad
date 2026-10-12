from __future__ import annotations

import math
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw

from generalization.structural_geometry.occupancy_analyzer import (
    _grid_indices,
    _surface_points,
    occupancy_mask,
)


def _mask_points(mask: np.ndarray, low: np.ndarray, high: np.ndarray) -> np.ndarray:
    grid = mask.shape[0]
    ids = np.argwhere(mask)
    if not len(ids):
        return np.empty((0, 3), dtype=float)
    centers = (ids.astype(float) + 0.5) / grid
    return low + centers * (high - low)


def occupancy_masks(
    source: trimesh.Trimesh,
    candidate: trimesh.Trimesh,
    grid: int = 32,
) -> dict[str, Any]:
    low = np.minimum(np.asarray(source.bounds[0]), np.asarray(candidate.bounds[0]))
    high = np.maximum(np.asarray(source.bounds[1]), np.asarray(candidate.bounds[1]))
    source_mask = occupancy_mask(source, low, high, grid)
    candidate_mask = occupancy_mask(candidate, low, high, grid)
    false_positive = candidate_mask & ~source_mask
    false_negative = source_mask & ~candidate_mask
    return {
        "low": low,
        "high": high,
        "source_mask": source_mask,
        "candidate_mask": candidate_mask,
        "false_positive_mask": false_positive,
        "false_negative_mask": false_negative,
        "false_positive_voxel_count": int(false_positive.sum()),
        "false_negative_voxel_count": int(false_negative.sum()),
        "candidate_voxel_count": int(max(candidate_mask.sum(), 1)),
        "fp_ratio": float(false_positive.sum() / max(candidate_mask.sum(), 1)),
    }


def _project(points: np.ndarray, center: np.ndarray, direction: np.ndarray) -> np.ndarray:
    direction = direction / max(float(np.linalg.norm(direction)), 1e-12)
    right = np.cross(direction, np.asarray([0.0, 0.0, 1.0]))
    if np.linalg.norm(right) < 1e-8:
        right = np.cross(direction, np.asarray([0.0, 1.0, 0.0]))
    right = right / max(float(np.linalg.norm(right)), 1e-12)
    up = np.cross(right, direction)
    return np.column_stack(((points - center) @ right, (points - center) @ up))


def render_overlay(
    source: trimesh.Trimesh,
    candidate: trimesh.Trimesh,
    path: Path,
    title: str,
    mode: str = "FP",
) -> None:
    size = (760, 560)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    masks = occupancy_masks(source, candidate)
    points = np.concatenate(
        [
            _mask_points(masks["source_mask"], masks["low"], masks["high"]),
            _mask_points(masks["candidate_mask"], masks["low"], masks["high"]),
        ],
        axis=0,
    )
    if len(points) == 0:
        draw.text((20, 20), title, fill=(20, 30, 40))
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path)
        return
    center = (masks["low"] + masks["high"]) * 0.5
    projected = _project(points, center, np.asarray([1.2, -1.35, 0.85]))
    scale = max(float(np.max(np.abs(projected))), 1e-9)

    def draw_points(mask: np.ndarray, color: tuple[int, int, int]) -> None:
        for point in _mask_points(mask, masks["low"], masks["high"]):
            xy = _project(point[None], center, np.asarray([1.2, -1.35, 0.85]))[0]
            x = int(round(380 + xy[0] * 320 / scale))
            y = int(round(300 - xy[1] * 320 / scale))
            draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=color)

    if mode == "FP":
        draw_points(masks["source_mask"], (185, 205, 225))
        draw_points(masks["false_positive_mask"], (220, 55, 45))
    elif mode == "FN":
        draw_points(masks["candidate_mask"], (185, 205, 225))
        draw_points(masks["false_negative_mask"], (240, 180, 40))
    else:
        draw_points(masks["source_mask"], (125, 170, 220))
        draw_points(masks["candidate_mask"], (220, 130, 100))
        draw_points(masks["false_positive_mask"], (220, 55, 45))
    draw.rectangle((0, 0, size[0], 42), fill="white")
    draw.text((16, 14), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def _convexity_overfill(source: trimesh.Trimesh) -> float:
    points = np.asarray(source.vertices, dtype=float)
    if len(points) < 4:
        return 0.0
    _, _, axes = np.linalg.svd(points - points.mean(axis=0), full_matrices=False)
    uv = np.column_stack(((points - points.mean(axis=0)) @ axes[0], (points - points.mean(axis=0)) @ axes[1]))
    try:
        from scipy.spatial import ConvexHull

        hull_area = float(ConvexHull(uv).volume)
        faces = np.asarray(source.faces, dtype=np.int64)
        tri = uv[faces]
        mesh_area = float(
            np.sum(
                0.5
                * np.abs(
                    (tri[:, 1, 0] - tri[:, 0, 0]) * (tri[:, 2, 1] - tri[:, 0, 1])
                    - (tri[:, 1, 1] - tri[:, 0, 1]) * (tri[:, 2, 0] - tri[:, 0, 0])
                )
            )
        )
    except Exception:
        return 0.0
    return float(max(0.0, hull_area / max(mesh_area, 1e-12) - 1.0))


def classify_fp_cause(
    source: trimesh.Trimesh,
    candidate: trimesh.Trimesh,
    builder_family: str,
    metrics: dict[str, Any],
    topology: dict[str, Any],
) -> dict[str, Any]:
    source_extent = np.ptp(np.asarray(source.vertices, dtype=float), axis=0)
    candidate_extent = np.ptp(np.asarray(candidate.vertices, dtype=float), axis=0)
    extent_ratio = candidate_extent / np.maximum(source_extent, 1e-12)
    causes: list[str] = []
    if np.any(extent_ratio > 1.12):
        causes.append("EXTENT_OVERFLOW")
    if not source.is_watertight and candidate.is_watertight:
        causes.append("OPEN_SURFACE_CLOSED")
    if builder_family == "REVOLUTION" and not topology.get("revolution_allowed", False):
        causes.append("WRONG_BUILDER_FAMILY")
    if builder_family == "BOX_PRISM" and topology.get("topology_class") != "VOLUMETRIC_SOLID":
        causes.append("WRONG_BUILDER_FAMILY")
    if topology.get("topology_class") == "MULTI_PATCH_SURFACE":
        causes.append("MULTI_PATCH_COLLAPSED")
    convexity = _convexity_overfill(source)
    if convexity > 0.08:
        causes.append("CONVEX_HULL_OVERFILL")
    if topology.get("boundary", {}).get("closed_loop_count", 0) > 1:
        causes.append("HOLE_FILLED")
    if not causes:
        causes.append("OTHER")
    return {
        "primary_fp_cause": causes[0],
        "secondary_fp_cause": causes[1] if len(causes) > 1 else "OTHER",
        "cause_evidence": causes,
        "source_to_cad_bbox_ratio": (1.0 / np.maximum(extent_ratio, 1e-12)).tolist(),
        "cad_to_source_bbox_ratio": extent_ratio.tolist(),
        "convexity_overfill_ratio": convexity,
        "fp_volume_or_area": float(metrics.get("false_positive_occupancy", 0.0)),
        "fp_region_count": int(
            max(
                1,
                metrics.get("false_positive_region_count", 1),
            )
        ),
    }


def diagnose_candidate(
    source: trimesh.Trimesh,
    candidate: trimesh.Trimesh,
    candidate_id: str,
    part_id: str,
    builder_family: str,
    metrics: dict[str, Any],
    topology: dict[str, Any],
    output_dir: Path,
) -> dict[str, Any]:
    masks = occupancy_masks(source, candidate)
    cause = classify_fp_cause(source, candidate, builder_family, metrics, topology)
    render_overlay(source, candidate, output_dir / "source_geometry.png", f"{part_id} SOURCE", "SOURCE")
    render_overlay(source, candidate, output_dir / "candidate_geometry.png", f"{candidate_id} CANDIDATE", "CANDIDATE")
    render_overlay(source, candidate, output_dir / "false_positive_overlay.png", f"{candidate_id} FALSE POSITIVE", "FP")
    render_overlay(source, candidate, output_dir / "false_negative_overlay.png", f"{candidate_id} FALSE NEGATIVE", "FN")
    render_overlay(source, candidate, output_dir / "source_vs_candidate.png", f"{candidate_id} SOURCE VS CANDIDATE", "BOTH")
    return {
        "PART_ID": part_id,
        "CANDIDATE_ID": candidate_id,
        "BUILDER_FAMILY": builder_family,
        "CHAMFER": metrics.get("chamfer"),
        "HAUSDORFF": metrics.get("hausdorff"),
        "COVERAGE": metrics.get("coverage"),
        "FP_OCCUPANCY": metrics.get("false_positive_occupancy"),
        "PRIMARY_FP_CAUSE": cause["primary_fp_cause"],
        "SECONDARY_FP_CAUSE": cause["secondary_fp_cause"],
        "FP_VOLUME_OR_AREA": cause["fp_volume_or_area"],
        "FP_REGION_COUNT": cause["fp_region_count"],
        "SOURCE_TO_CAD_BBOX_RATIO": cause["source_to_cad_bbox_ratio"],
        "CAD_TO_SOURCE_BBOX_RATIO": cause["cad_to_source_bbox_ratio"],
        "TOPOLOGY_CLASS": topology.get("topology_class"),
        "OCCUPANCY_FP_VOXEL_COUNT": masks["false_positive_voxel_count"],
        "OCCUPANCY_FN_VOXEL_COUNT": masks["false_negative_voxel_count"],
    }
