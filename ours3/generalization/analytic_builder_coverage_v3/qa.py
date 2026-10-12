from __future__ import annotations

import math
from typing import Any

import numpy as np
import trimesh
from scipy.spatial import cKDTree

from generalization.structural_geometry.negative_space_analyzer import negative_space_evidence
from generalization.structural_geometry.occupancy_analyzer import occupancy_metrics


THRESHOLDS = {
    "chamfer_max": 0.35,
    "hausdorff_max": 0.75,
    "false_positive_occupancy_max": 0.25,
    "coverage_min": 0.35,
    "normal_error_max": 0.90,
}


def bbox_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, float]:
    source_extent = np.ptp(np.asarray(source.vertices, dtype=float), axis=0)
    candidate_extent = np.ptp(np.asarray(candidate.vertices, dtype=float), axis=0)
    source_volume = float(source.volume) if source.is_volume else 0.0
    candidate_volume = float(candidate.volume) if candidate.is_volume else 0.0
    return {
        "mesh_bbox_x": float(source_extent[0]),
        "mesh_bbox_y": float(source_extent[1]),
        "mesh_bbox_z": float(source_extent[2]),
        "cad_bbox_x": float(candidate_extent[0]),
        "cad_bbox_y": float(candidate_extent[1]),
        "cad_bbox_z": float(candidate_extent[2]),
        "bbox_volume_ratio": float(np.prod(candidate_extent) / max(np.prod(source_extent), 1e-12)),
        "mesh_volume": source_volume,
        "cad_volume": candidate_volume,
        "volume_ratio": float(candidate_volume / source_volume) if source_volume > 1e-12 else math.nan,
    }


def normal_error(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> float:
    if len(source.vertices) == 0 or len(candidate.vertices) == 0:
        return math.inf
    tree = cKDTree(np.asarray(candidate.vertices, dtype=float))
    indices = tree.query(np.asarray(source.vertices, dtype=float), k=1)[1]
    candidate_normals = np.asarray(candidate.vertex_normals, dtype=float)
    source_normals = np.asarray(source.vertex_normals, dtype=float)
    dots = np.abs(np.sum(source_normals * candidate_normals[np.asarray(indices)], axis=1))
    return float(1.0 - np.mean(np.clip(dots, 0.0, 1.0)))


def distance_metrics(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, float]:
    source_points = np.asarray(source.vertices, dtype=float)
    candidate_points = np.asarray(candidate.vertices, dtype=float)
    if len(source_points) == 0 or len(candidate_points) == 0:
        return {"chamfer": math.inf, "hausdorff": math.inf, "coverage": 0.0}
    source_tree = cKDTree(source_points)
    candidate_tree = cKDTree(candidate_points)
    source_to_candidate = candidate_tree.query(source_points)[0]
    candidate_to_source = source_tree.query(candidate_points)[0]
    diag = max(float(np.linalg.norm(np.ptp(source_points, axis=0))), 1e-12)
    threshold = max(diag * 0.12, 0.02)
    return {
        "chamfer": float((source_to_candidate.mean() + candidate_to_source.mean()) * 0.5 / diag),
        "hausdorff": float(max(source_to_candidate.max(), candidate_to_source.max()) / diag),
        "coverage": float(np.mean(source_to_candidate <= threshold)),
    }


def evaluate_candidate(source: trimesh.Trimesh, candidate: trimesh.Trimesh, occ_valid: bool) -> dict[str, Any]:
    metrics = {}
    metrics.update(distance_metrics(source, candidate))
    metrics.update(bbox_metrics(source, candidate))
    metrics["normal_error"] = normal_error(source, candidate)
    occupancy = occupancy_metrics(source, candidate)
    occupancy.update(negative_space_evidence(occupancy))
    metrics.update({
        "occupancy_iou": occupancy["occupancy_iou"],
        "false_positive_occupancy": occupancy["false_positive_occupancy_ratio"],
        "false_negative_occupancy": occupancy["false_negative_occupancy_ratio"],
        "void_preservation_ratio": occupancy["void_preservation_ratio"],
        "section_occupancy_iou_mean": occupancy["section_occupancy_iou_mean"],
        "negative_space_hard_reject": occupancy["negative_space_hard_reject"],
    })
    metrics["occ_valid"] = bool(occ_valid)
    metrics["qa_pass"] = bool(
        occ_valid
        and metrics["chamfer"] <= THRESHOLDS["chamfer_max"]
        and metrics["hausdorff"] <= THRESHOLDS["hausdorff_max"]
        and metrics["false_positive_occupancy"] <= THRESHOLDS["false_positive_occupancy_max"]
        and metrics["coverage"] >= THRESHOLDS["coverage_min"]
        and metrics["normal_error"] <= THRESHOLDS["normal_error_max"]
        and not metrics["negative_space_hard_reject"]
    )
    return metrics


def reject_reason(metrics: dict[str, Any], builder_error: str | None = None) -> tuple[str, str]:
    if builder_error:
        if "NO_SUPPORTED_BUILDER" in builder_error:
            return "NO_SUPPORTED_BUILDER", builder_error
        if "OCC_INVALID" in builder_error:
            return "OCC_INVALID", builder_error
        if "PROFILE" in builder_error or "REVOLUTION" in builder_error or "TAPER" in builder_error:
            return "PARAMETER_FIT_FAILURE", builder_error
        return "BUILDER_EXCEPTION", builder_error
    if not metrics.get("occ_valid", False):
        return "OCC_INVALID", "OCC validity failed"
    if metrics.get("negative_space_hard_reject"):
        return "FP_OCCUPANCY_FAIL", "negative-space hard reject"
    if metrics.get("false_positive_occupancy", 1.0) > THRESHOLDS["false_positive_occupancy_max"]:
        return "FP_OCCUPANCY_FAIL", "false-positive occupancy above threshold"
    if metrics.get("coverage", 0.0) < THRESHOLDS["coverage_min"]:
        return "COVERAGE_FAIL", "source coverage below threshold"
    if metrics.get("chamfer", math.inf) > THRESHOLDS["chamfer_max"]:
        return "CHAMFER_FAIL", "Chamfer above threshold"
    if metrics.get("hausdorff", math.inf) > THRESHOLDS["hausdorff_max"]:
        return "HAUSDORFF_FAIL", "Hausdorff above threshold"
    if metrics.get("normal_error", math.inf) > THRESHOLDS["normal_error_max"]:
        return "NORMAL_FAIL", "normal consistency above threshold"
    return "UNKNOWN", "candidate rejected without a specific metric failure"
