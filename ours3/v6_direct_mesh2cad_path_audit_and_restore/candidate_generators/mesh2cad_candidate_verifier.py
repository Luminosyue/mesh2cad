from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import cKDTree


def _sample(vertices: np.ndarray, faces: np.ndarray, count: int = 12000) -> np.ndarray:
    if len(faces) == 0:
        return vertices[:count]
    tri = vertices[faces]
    area = np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1) * 0.5
    if not np.isfinite(area).all() or area.sum() <= 1e-15:
        return vertices[:count]
    rng = np.random.default_rng(20260814)
    indexes = rng.choice(len(faces), size=count, p=area / area.sum())
    u = rng.random(count)
    v = rng.random(count)
    flip = u + v > 1.0
    u[flip] = 1.0 - u[flip]
    v[flip] = 1.0 - v[flip]
    selected = tri[indexes]
    return selected[:, 0] + u[:, None] * (selected[:, 1] - selected[:, 0]) + v[:, None] * (selected[:, 2] - selected[:, 0])


def _raster(vertices: np.ndarray, faces: np.ndarray, axes: tuple[int, int], bounds: np.ndarray, size: int = 320) -> np.ndarray:
    from PIL import Image, ImageDraw

    low = bounds[0, list(axes)]
    span = np.maximum(bounds[1, list(axes)] - low, 1e-12)
    projected = np.clip((vertices[:, list(axes)] - low) / span, 0.0, 1.0)
    pixels = np.column_stack((projected[:, 0] * (size - 1), (1.0 - projected[:, 1]) * (size - 1)))
    image = Image.new("1", (size, size), 0)
    draw = ImageDraw.Draw(image)
    for face in faces:
        draw.polygon([tuple(pixels[int(i)]) for i in face], fill=1)
    return np.asarray(image, dtype=bool)


def geometry_metrics(source_vertices: np.ndarray, source_faces: np.ndarray, cad_vertices: np.ndarray, cad_faces: np.ndarray) -> dict[str, Any]:
    source_samples = _sample(source_vertices, source_faces)
    cad_samples = _sample(cad_vertices, cad_faces)
    if not len(source_samples) or not len(cad_samples):
        return {"chamfer": float("inf"), "hausdorff": float("inf"), "silhouette_iou": 0.0, "silhouette_iou_min": 0.0}
    forward = cKDTree(cad_samples).query(source_samples, workers=-1)[0]
    backward = cKDTree(source_samples).query(cad_samples, workers=-1)[0]
    bounds = np.asarray([source_vertices.min(0), source_vertices.max(0)])
    views = []
    for axes in ((0, 1), (0, 2), (1, 2)):
        a = _raster(source_vertices, source_faces, axes, bounds)
        b = _raster(cad_vertices, cad_faces, axes, bounds)
        union = np.logical_or(a, b).sum()
        views.append(float(np.logical_and(a, b).sum() / max(union, 1)))
    return {
        "chamfer": float((forward.mean() + backward.mean()) * 0.5),
        "hausdorff": float(max(forward.max(), backward.max())),
        "silhouette_iou": float(np.mean(views)),
        "silhouette_iou_min": float(np.min(views)),
        "silhouette_views": views,
        "section_profile_error": _section_profile_error(source_samples, cad_samples),
    }


def _section_profile_error(source: np.ndarray, candidate: np.ndarray) -> float:
    if not len(source) or not len(candidate):
        return float("inf")
    axis = int(np.argmax(np.ptp(source, axis=0)))
    errors = []
    for quantile in (0.08, 0.20, 0.35, 0.50, 0.65, 0.80, 0.92):
        station = float(np.quantile(source[:, axis], quantile))
        band = max(float(np.ptp(source[:, axis])) * 0.025, 1e-6)
        source_section = source[np.abs(source[:, axis] - station) <= band]
        candidate_section = candidate[np.abs(candidate[:, axis] - station) <= band]
        if len(source_section) < 8 or len(candidate_section) < 8:
            continue
        plane = [index for index in range(3) if index != axis]
        scale = max(float(np.linalg.norm(np.ptp(source_section[:, plane], axis=0))), 1e-9)
        forward = cKDTree(candidate_section[:, plane]).query(source_section[:, plane], workers=-1)[0]
        backward = cKDTree(source_section[:, plane]).query(candidate_section[:, plane], workers=-1)[0]
        errors.append(float((forward.mean() + backward.mean()) * 0.5 / scale))
    return float(np.mean(errors)) if errors else float("inf")


def verify_candidate(
    *,
    shape: Any,
    step_path: Path,
    source_vertices: np.ndarray,
    source_faces: np.ndarray,
    triangulate,
    shape_counts,
    read_step,
    write_step,
    validation: dict[str, Any],
    execution: dict[str, Any],
) -> dict[str, Any]:
    from OCP.BRepCheck import BRepCheck_Analyzer

    write_step(shape, step_path)
    reloaded = read_step(step_path)
    valid = bool(reloaded is not None and BRepCheck_Analyzer(reloaded).IsValid())
    cad_vertices, cad_faces = triangulate(reloaded)
    metrics = geometry_metrics(source_vertices, source_faces, cad_vertices, cad_faces)
    face_count, edge_count, analytic_count = shape_counts(reloaded)
    source_diag = float(np.linalg.norm(np.ptp(source_vertices, axis=0)))
    cad_diag = float(np.linalg.norm(np.ptp(cad_vertices, axis=0))) if len(cad_vertices) else float("inf")
    bbox_ratio = cad_diag / max(source_diag, 1e-12)
    consumed = execution.get("consumed") or []
    parameter_complete = bool(validation.get("PLAN_REFERENCE_VALID") and all(item.get("SOURCE_REF") for item in consumed))
    hard_safety = bool(valid and parameter_complete and np.isfinite(bbox_ratio) and 0.2 <= bbox_ratio <= 5.0)
    return {
        **metrics,
        "occ_valid": valid,
        "fresh_step_reload_valid": valid,
        "bbox_diagonal_ratio": bbox_ratio,
        "parameter_provenance_complete": parameter_complete,
        "hard_safety_pass": hard_safety,
        "face_count": face_count,
        "true_edge_count": edge_count,
        "analytic_face_count": analytic_count,
        "analytic_ratio": analytic_count / max(face_count, 1),
        "step_path": str(step_path),
        "step_sha256": hashlib.sha256(step_path.read_bytes()).hexdigest(),
        "raw_parameter_consumed": False,
        "direct_occ_bypass": False,
        "historical_step_reused": False,
        "builder_runtime_source_mesh_read": False,
    }


def ranking_key(candidate: dict[str, Any]) -> tuple[Any, ...]:
    metrics = candidate.get("metrics") or {}
    return (
        0 if metrics.get("hard_safety_pass") else 1,
        -float(metrics.get("silhouette_iou") or 0.0),
        float(metrics.get("chamfer") or float("inf")),
        float(metrics.get("hausdorff") or float("inf")),
        -float(metrics.get("analytic_ratio") or 0.0),
        int(metrics.get("face_count") or 10**9),
        int(metrics.get("true_edge_count") or 10**9),
    )
