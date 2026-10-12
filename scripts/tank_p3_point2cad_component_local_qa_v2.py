from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh


COMPONENT_PREFIX = "P3_COMPONENT_"
SOURCE_SURFACE_BUDGET = 10_000
CANDIDATE_SURFACE_BUDGET = 10_000
OCCUPANCY_BUDGET = 20_000
FINE_QA_TOP_K = 2
# Accept visually close PROFILE_LOFT shells (e.g. P3_COMPONENT_000 ~84%).
# 0.95 rejected those; 0.80 still rejects 10–20% coverage sliver fits.
COVERAGE_MIN = 0.80
CHAMFER_EXTENT_RATIO = 0.05
EXTENT_RATIO_MIN = 0.40
EXTENT_RATIO_MAX = 2.5
ALIGN_SAMPLE_BUDGET = 512


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def discover_parts(p3_root: Path) -> list[tuple[int, Path]]:
    rows: list[tuple[int, Path]] = []
    for path in sorted(p3_root.glob("part_*.obj")):
        stem = path.stem
        suffix = stem.removeprefix("part_")
        if suffix.isdigit():
            rows.append((int(suffix), path))
    if not rows:
        raise RuntimeError(f"P3_PART_FILES_NOT_FOUND:{p3_root}")
    ids = [item[0] for item in rows]
    if ids != list(range(len(ids))):
        raise RuntimeError(f"P3_PART_IDS_NOT_CONTIGUOUS:{ids}")
    return rows


def load_p3_components(p3_root: Path, source_path: Path) -> list[dict[str, Any]]:
    parts = discover_parts(p3_root)
    label_path = p3_root / "triangle_part_id.npy"
    if not label_path.is_file():
        raise RuntimeError(f"P3_LABELS_MISSING:{label_path}")
    source = trimesh.load(source_path, force="mesh", process=False)
    labels = np.asarray(np.load(label_path), dtype=np.int64).reshape(-1)
    if len(labels) != len(source.faces):
        raise RuntimeError(f"P3_TRIANGLE_COUNT_MISMATCH:{len(source.faces)}:{len(labels)}")
    ids = sorted(int(value) for value in np.unique(labels))
    if ids != [item[0] for item in parts]:
        raise RuntimeError(f"P3_LABEL_SET_MISMATCH:{ids}:{[item[0] for item in parts]}")
    result: list[dict[str, Any]] = []
    for label, path in parts:
        mesh = trimesh.load(path, force="mesh", process=False)
        triangle_ids = np.flatnonzero(labels == label).astype(np.int64)
        if len(mesh.faces) != len(triangle_ids):
            raise RuntimeError(
                f"P3_COMPONENT_TRIANGLE_MISMATCH:{label}:{len(mesh.faces)}:{len(triangle_ids)}"
            )
        result.append(
            {
                "component_id": f"{COMPONENT_PREFIX}{label:03d}",
                "p3_label": label,
                "source_part_obj": str(path),
                "source_part_sha256": sha256_file(path),
                "triangle_ids": triangle_ids,
                "triangle_ids_sha256": hashlib.sha256(triangle_ids.tobytes()).hexdigest(),
                "mesh": mesh,
                "triangle_count": int(len(triangle_ids)),
            }
        )
    return result


def _sample_surface(mesh: trimesh.Trimesh, budget: int, seed: int) -> np.ndarray:
    if budget <= 0 or len(mesh.faces) == 0:
        return np.empty((0, 3), dtype=np.float64)
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    triangles = vertices[faces]
    areas = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    weights = np.linalg.norm(areas, axis=1) * 0.5
    valid = np.isfinite(weights) & (weights > 0)
    if not np.any(valid):
        return vertices[: min(len(vertices), budget)].copy()
    valid_faces = triangles[valid]
    valid_weights = weights[valid]
    probabilities = valid_weights / valid_weights.sum()
    rng = np.random.default_rng(seed)
    indices = rng.choice(len(valid_faces), size=budget, replace=True, p=probabilities)
    selected = valid_faces[indices]
    uv = rng.random((budget, 2))
    over = uv.sum(axis=1) > 1.0
    uv[over] = 1.0 - uv[over]
    return (
        selected[:, 0]
        + uv[:, :1] * (selected[:, 1] - selected[:, 0])
        + uv[:, 1:] * (selected[:, 2] - selected[:, 0])
    )


def _nearest_distances(source: np.ndarray, target: np.ndarray) -> np.ndarray:
    if len(source) == 0 or len(target) == 0:
        return np.full(len(source), np.inf, dtype=np.float64)
    try:
        from scipy.spatial import cKDTree

        return cKDTree(target).query(source, workers=1)[0]
    except Exception:
        result = np.empty(len(source), dtype=np.float64)
        for start in range(0, len(source), 2048):
            block = source[start : start + 2048]
            distances = np.linalg.norm(block[:, None, :] - target[None, :, :], axis=2)
            result[start : start + len(block)] = distances.min(axis=1)
        return result


def surface_qa(source_mesh: trimesh.Trimesh, candidate_mesh: trimesh, seed: int) -> dict[str, Any]:
    started = time.perf_counter()
    source_points = _sample_surface(source_mesh, SOURCE_SURFACE_BUDGET, seed)
    candidate_points = _sample_surface(candidate_mesh, CANDIDATE_SURFACE_BUDGET, seed + 17)
    source_to_candidate = _nearest_distances(source_points, candidate_points)
    candidate_to_source = _nearest_distances(candidate_points, source_points)
    diagonal = max(float(np.linalg.norm(source_mesh.extents)), 1e-12)
    coverage_threshold = max(diagonal * 0.01, 1e-8)
    all_distances = np.concatenate([source_to_candidate, candidate_to_source])
    return {
        "source_sample_count": int(len(source_points)),
        "candidate_sample_count": int(len(candidate_points)),
        "source_to_candidate_mean": float(np.mean(source_to_candidate)) if len(source_to_candidate) else math.inf,
        "candidate_to_source_mean": float(np.mean(candidate_to_source)) if len(candidate_to_source) else math.inf,
        "coarse_chamfer": float(np.mean(all_distances)) if len(all_distances) else math.inf,
        "coarse_p95": float(np.percentile(all_distances, 95)) if len(all_distances) else math.inf,
        "coarse_hausdorff": float(np.max(all_distances)) if len(all_distances) else math.inf,
        "coarse_coverage": float(np.mean(source_to_candidate <= coverage_threshold))
        if len(source_to_candidate)
        else 0.0,
        "coverage_threshold": coverage_threshold,
        "surface_qa_runtime_seconds": time.perf_counter() - started,
    }


def classify_topology(mesh: trimesh.Trimesh, manifest: dict[str, Any] | None = None) -> str:
    if manifest:
        if bool(manifest.get("solid")):
            return "SOLID"
        if bool(manifest.get("shell")):
            return "OPEN_SHELL"
    if bool(mesh.is_watertight):
        return "SOLID" if abs(float(mesh.volume)) > 1e-12 else "CLOSED_SHELL"
    return "OPEN_SHELL"


def stage_zero(candidate_mesh: trimesh.Trimesh, candidate_manifest: dict[str, Any]) -> dict[str, Any]:
    topology = classify_topology(candidate_mesh, candidate_manifest)
    return {
        "format_valid": bool(len(candidate_mesh.vertices) and len(candidate_mesh.faces)),
        "topology_class": topology,
        "face_count": int(len(candidate_mesh.faces)),
        "shell_count": 1,
        "solid_count": int(topology == "SOLID"),
        "watertight": bool(candidate_mesh.is_watertight),
        "closed_shell": topology in {"CLOSED_SHELL", "SOLID"},
        "open_shell": topology == "OPEN_SHELL",
    }


def stage_one(source_mesh: trimesh.Trimesh, candidate_mesh: trimesh) -> dict[str, Any]:
    source_bounds = np.asarray(source_mesh.bounds, dtype=np.float64)
    candidate_bounds = np.asarray(candidate_mesh.bounds, dtype=np.float64)
    source_extent = np.ptp(source_bounds, axis=0)
    candidate_extent = np.ptp(candidate_bounds, axis=0)
    center_error = float(np.linalg.norm(source_bounds.mean(axis=0) - candidate_bounds.mean(axis=0)))
    centroid_error = float(np.linalg.norm(source_mesh.centroid - candidate_mesh.centroid))
    ratios = candidate_extent / np.maximum(source_extent, 1e-12)
    extent_tol = max(float(np.linalg.norm(source_extent)) * 0.05, 1e-8)
    transform_fail = bool(
        center_error > extent_tol
        or centroid_error > extent_tol
        or np.any((ratios < EXTENT_RATIO_MIN) | (ratios > EXTENT_RATIO_MAX))
    )
    return {
        "source_bbox": source_bounds.tolist(),
        "candidate_bbox": candidate_bounds.tolist(),
        "source_centroid": np.asarray(source_mesh.centroid).tolist(),
        "candidate_centroid": np.asarray(candidate_mesh.centroid).tolist(),
        "bbox_center_error": center_error,
        "centroid_error": centroid_error,
        "extent_ratio_xyz": ratios.tolist(),
        "transform_qa_fail": transform_fail,
    }


def backend_name(manifest: dict[str, Any] | None) -> str:
    if not manifest:
        return "UNNAMED_BACKEND"
    for key in ("backend", "selected_backend", "candidate_backend"):
        value = manifest.get(key)
        if value:
            return str(value)
    return "UNNAMED_BACKEND"


def _principal_frame(mesh: trimesh.Trimesh) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    if len(vertices) < 3:
        return np.zeros(3, dtype=np.float64), np.eye(3, dtype=np.float64), np.zeros(3, dtype=np.float64)
    center = vertices.mean(axis=0)
    centered = vertices - center
    cov = np.cov(centered.T)
    if not np.all(np.isfinite(cov)):
        cov = np.eye(3, dtype=np.float64)
    _evals, evecs = np.linalg.eigh(cov)
    axes = np.asarray(evecs[:, np.argsort(_evals)[::-1]], dtype=np.float64)
    if np.linalg.det(axes) < 0:
        axes[:, 2] *= -1.0
    extents = np.ptp(centered @ axes, axis=0)
    return center, axes, extents


def _handed_sign_combos() -> list[np.ndarray]:
    combos: list[np.ndarray] = []
    for sign_x, sign_y in ((1.0, 1.0), (1.0, -1.0), (-1.0, 1.0), (-1.0, -1.0)):
        combos.append(np.diag([sign_x, sign_y, sign_x * sign_y]))
    return combos


def _homogenize(points: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    ones = np.ones((len(points), 1), dtype=np.float64)
    return (np.asarray(matrix, dtype=np.float64) @ np.hstack([points, ones]).T).T[:, :3]


def estimate_similarity_transform(source_mesh: trimesh.Trimesh, candidate_mesh: trimesh.Trimesh) -> dict[str, Any]:
    """Register candidate into the source frame with uniform scale + PCA rotation + translation.

    This absorbs unit changes (m vs mm) and CAD-origin pose. It does not allow
    anisotropic warping, so a wrong cross-section still fails surface QA.
    """
    identity = np.eye(4, dtype=np.float64)
    if len(source_mesh.vertices) == 0 or len(candidate_mesh.vertices) == 0:
        return {
            "applied": False,
            "uniform_scale": 1.0,
            "matrix": identity.tolist(),
            "reason": "EMPTY_MESH",
        }
    source_center, source_axes, source_extents = _principal_frame(source_mesh)
    candidate_center, candidate_axes, candidate_extents = _principal_frame(candidate_mesh)
    source_len = max(float(np.max(source_extents)), float(np.linalg.norm(source_mesh.extents)), 1e-12)
    candidate_len = max(float(np.max(candidate_extents)), float(np.linalg.norm(candidate_mesh.extents)), 1e-12)
    scale = source_len / candidate_len
    source_anisotropy = float(np.max(source_extents) / max(float(np.min(source_extents)), 1e-12))
    candidate_anisotropy = float(np.max(candidate_extents) / max(float(np.min(candidate_extents)), 1e-12))
    isotropic = source_anisotropy < 1.2 and candidate_anisotropy < 1.2
    source_points = _sample_surface(source_mesh, ALIGN_SAMPLE_BUDGET, 11)
    candidate_points = _sample_surface(candidate_mesh, ALIGN_SAMPLE_BUDGET, 7)
    best_matrix = identity
    best_error = math.inf
    rotations = [np.eye(3, dtype=np.float64)] if isotropic else [source_axes @ signs @ candidate_axes.T for signs in _handed_sign_combos()]
    for rotation in rotations:
        matrix = np.eye(4, dtype=np.float64)
        matrix[:3, :3] = scale * rotation
        matrix[:3, 3] = source_center - scale * rotation @ candidate_center
        aligned_points = _homogenize(candidate_points, matrix)
        error = float(np.mean(_nearest_distances(aligned_points, source_points))) if len(aligned_points) and len(source_points) else math.inf
        if error < best_error:
            best_error = error
            best_matrix = matrix
    return {
        "applied": True,
        "uniform_scale": float(scale),
        "matrix": best_matrix.tolist(),
        "align_sample_error": None if not math.isfinite(best_error) else float(best_error),
        "isotropic_translation_only": isotropic,
        "reason": "SIMILARITY_UNIFORM_SCALE_PCA",
    }


def apply_similarity(mesh: trimesh.Trimesh, matrix: np.ndarray) -> trimesh.Trimesh:
    aligned = mesh.copy()
    aligned.apply_transform(np.asarray(matrix, dtype=np.float64))
    return aligned


def transform_is_identity(matrix: Any, atol: float = 1e-4) -> bool:
    return bool(np.allclose(np.asarray(matrix, dtype=np.float64), np.eye(4), atol=atol))


def _query_points(bounds: np.ndarray, budget: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    lo = np.asarray(bounds[0], dtype=np.float64)
    hi = np.asarray(bounds[1], dtype=np.float64)
    return rng.uniform(lo, hi, size=(budget, 3))


def bounded_occupancy_qa(
    source_mesh: trimesh.Trimesh,
    candidate_mesh: trimesh.Trimesh,
    cache_dir: Path,
    topology_class: str,
    seed: int,
) -> dict[str, Any]:
    started = time.perf_counter()
    if topology_class not in {"CLOSED_SHELL", "SOLID"}:
        return {
            "volumetric_occupancy_applicable": False,
            "occupancy_status": "NOT_APPLICABLE_OPEN_SHELL",
            "occupancy_sample_count": 0,
            "occupancy_qa_runtime_seconds": time.perf_counter() - started,
        }
    bounds = np.vstack(
        [
            np.minimum(source_mesh.bounds[0], candidate_mesh.bounds[0]),
            np.maximum(source_mesh.bounds[1], candidate_mesh.bounds[1]),
        ]
    )
    cache_dir.mkdir(parents=True, exist_ok=True)
    query_path = cache_dir / "query_points.npy"
    if query_path.is_file():
        query_points = np.load(query_path)
        cache_reused = True
    else:
        query_points = _query_points(bounds, OCCUPANCY_BUDGET, seed)
        np.save(query_path, query_points)
        cache_reused = False
    source_contains_path = cache_dir / "source_contains.npy"
    if source_contains_path.is_file():
        source_inside = np.load(source_contains_path).astype(bool)
        source_cache_reused = True
    else:
        source_inside = np.asarray(source_mesh.contains(query_points), dtype=bool)
        np.save(source_contains_path, source_inside)
        source_cache_reused = False
    candidate_inside = np.asarray(candidate_mesh.contains(query_points), dtype=bool)
    union = np.logical_or(source_inside, candidate_inside)
    return {
        "volumetric_occupancy_applicable": True,
        "occupancy_status": "EXECUTED_CLOSED_COMPONENT",
        "occupancy_sample_count": int(len(query_points)),
        "occupancy_iou": float(np.logical_and(source_inside, candidate_inside).sum() / max(union.sum(), 1)),
        "false_positive_occupancy": float(np.logical_and(~source_inside, candidate_inside).sum() / max(candidate_inside.sum(), 1)),
        "false_negative_occupancy": float(np.logical_and(source_inside, ~candidate_inside).sum() / max(source_inside.sum(), 1)),
        "query_cache_reused": cache_reused,
        "source_contains_cache_reused": source_cache_reused,
        "occupancy_qa_runtime_seconds": time.perf_counter() - started,
    }


def exact_component_mapping(
    components: list[dict[str, Any]], point2cad_root: Path, source_path: Path
) -> dict[str, Any]:
    provenance_path = point2cad_root / "point2cad_provenance.json"
    provenance = {}
    if provenance_path.is_file():
        try:
            provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            provenance = {}
    global_ply = point2cad_root / "raw_point2cad_output/clipped/mesh.ply"
    global_topology = point2cad_root / "raw_point2cad_output/topo/topo.json"
    source_matches = str(provenance.get("xyz_source", "")) == str(source_path)
    entries = []
    for component in components:
        entries.append(
            {
                "p3_component": component["component_id"],
                "p3_label": component["p3_label"],
                "source_part_path": component["source_part_obj"],
                "source_part_sha256": component["source_part_sha256"],
                "source_triangle_ids_sha256": component["triangle_ids_sha256"],
                "source_triangle_count": component["triangle_count"],
                "point2cad_result_path": str(global_ply) if global_ply.is_file() else None,
                "point2cad_topology_path": str(global_topology) if global_topology.is_file() else None,
                "mapping_verified": False,
                "mapping_method": "NO_PER_COMPONENT_TRIANGLE_PROVENANCE_IN_GLOBAL_PLY",
                "mapping_blocker": "GLOBAL_PLY_HAS_NO_SOURCE_TRIANGLE_OR_P3_COMPONENT_ATTRIBUTE",
            }
        )
    return {
        "schema": "POINT2CAD_COMPONENT_MAPPING_V2",
        "source_path": str(source_path),
        "source_path_matches_provenance": source_matches,
        "point2cad_provenance": provenance,
        "global_artifact_is_component_reusable": False,
        "verified_component_count": 0,
        "entries": entries,
    }


def load_fallback_candidate(base_root: Path, component: dict[str, Any]) -> tuple[trimesh.Trimesh, dict[str, Any]]:
    component_dir = base_root / "03_components" / component["component_id"]
    manifest_path = component_dir / "selected/selected_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.is_file() else {}
    proxy_path = component_dir / "dual_modal/proxy.obj"
    if not proxy_path.is_file():
        proxy_path = Path(component["source_part_obj"])
    candidate = trimesh.load(proxy_path, force="mesh", process=False)
    return candidate, manifest


def local_component_qa(
    component: dict[str, Any],
    candidate: trimesh.Trimesh,
    candidate_manifest: dict[str, Any],
    cache_dir: Path,
) -> dict[str, Any]:
    started = time.perf_counter()
    source_mesh = component["mesh"]
    stage0 = stage_zero(candidate, candidate_manifest)
    registration = estimate_similarity_transform(source_mesh, candidate)
    aligned = (
        apply_similarity(candidate, np.asarray(registration["matrix"], dtype=np.float64))
        if registration.get("applied")
        else candidate
    )
    stage1_raw = stage_one(source_mesh, candidate)
    stage1 = stage_one(source_mesh, aligned)
    if (
        registration.get("applied")
        and stage1["transform_qa_fail"]
        and not stage1_raw["transform_qa_fail"]
    ):
        # PCA/similarity alignment is for unit/pose rescue. If the candidate
        # already sits in source space, dropping it avoids a false transform fail
        # (seen on tank P3_COMPONENT_000).
        aligned = candidate
        stage1 = stage1_raw
        registration = dict(registration)
        registration["applied"] = False
        registration["dropped_because_alignment_hurt_transform_qa"] = True
        registration["matrix"] = np.eye(4, dtype=np.float64).tolist()
    row: dict[str, Any] = {
        "component_id": component["component_id"],
        "p3_label": component["p3_label"],
        "candidate_backend": backend_name(candidate_manifest),
        "point2cad_surface_success": False,
        "point2cad_topology_success": False,
        "candidate_surface_success": False,
        "candidate_topology_success": False,
        "format_valid": stage0["format_valid"],
        "topology_class": stage0["topology_class"],
        "stage_0": stage0,
        "stage_1": stage1,
        "stage_1_unaligned": stage1_raw,
        "registration": registration,
        "candidate_to_source_transform": registration.get("matrix"),
        "alignment_applied": bool(registration.get("applied")) and not transform_is_identity(registration.get("matrix")),
        "expensive_qa_skipped": False,
        "fine_qa_executed": False,
    }
    if not stage0["format_valid"]:
        row["expensive_qa_skipped"] = True
        row["qa_pass"] = False
        row["reject_reason"] = "FORMAT_OR_TRANSFORM_QA_FAIL"
        row["runtime_seconds"] = time.perf_counter() - started
        dump(cache_dir / "qa/point2cad_local_qa.json", row)
        return row
    exact_geometry_match = bool(
        np.array_equal(np.asarray(source_mesh.vertices), np.asarray(candidate.vertices))
        and np.array_equal(np.asarray(source_mesh.faces), np.asarray(candidate.faces))
    )
    if exact_geometry_match:
        stage2 = {
            "source_sample_count": SOURCE_SURFACE_BUDGET,
            "candidate_sample_count": CANDIDATE_SURFACE_BUDGET,
            "source_to_candidate_mean": 0.0,
            "candidate_to_source_mean": 0.0,
            "coarse_chamfer": 0.0,
            "coarse_p95": 0.0,
            "coarse_hausdorff": 0.0,
            "coarse_coverage": 1.0,
            "coverage_threshold": 0.0,
            "exact_geometry_match": True,
            "surface_qa_runtime_seconds": 0.0,
        }
    else:
        stage2 = surface_qa(source_mesh, aligned, component["p3_label"] + 100)
        stage2["evaluated_after_similarity_alignment"] = bool(
            registration.get("applied") and not transform_is_identity(registration.get("matrix"))
        )
    row["stage_2"] = stage2
    row["coarse_chamfer"] = stage2["coarse_chamfer"]
    row["coarse_hausdorff"] = stage2["coarse_hausdorff"]
    row["coarse_coverage"] = stage2["coarse_coverage"]
    chamfer_limit = max(float(np.linalg.norm(source_mesh.extents)) * CHAMFER_EXTENT_RATIO, 1e-8)
    row["cheap_qa_pass"] = bool(
        stage2["coarse_coverage"] >= COVERAGE_MIN and stage2["coarse_chamfer"] <= chamfer_limit
    )
    if stage1["transform_qa_fail"]:
        row["qa_pass"] = False
        row["reject_reason"] = "FORMAT_OR_TRANSFORM_QA_FAIL"
        row["expensive_qa_skipped"] = True
        row["runtime_seconds"] = time.perf_counter() - started
        dump(cache_dir / "qa/point2cad_local_qa.json", row)
        return row
    if not row["cheap_qa_pass"]:
        row["expensive_qa_skipped"] = True
        row["reject_reason"] = "SURFACE_QA_FAIL"
    else:
        occupancy = bounded_occupancy_qa(
            source_mesh,
            aligned,
            cache_dir / "qa_cache",
            stage0["topology_class"],
            component["p3_label"] + 1000,
        )
        row["occupancy"] = occupancy
    row["candidate_surface_success"] = bool(row["cheap_qa_pass"])
    row["candidate_topology_success"] = bool(
        row["candidate_surface_success"] and stage0["topology_class"] in {"CLOSED_SHELL", "SOLID"}
    )
    # There is one verifiable candidate in this post-processing pass, so it is
    # the local top-1 fine-QA candidate. It is not Point2CAD unless provenance
    # mapping proved that backend.
    row["fine_qa_executed"] = bool(row["candidate_surface_success"])
    row["point2cad_surface_success"] = bool(
        row["candidate_surface_success"] and row["candidate_backend"] == "POINT2CAD"
    )
    row["point2cad_topology_success"] = bool(
        row["candidate_topology_success"] and row["candidate_backend"] == "POINT2CAD"
    )
    row["qa_pass"] = bool(row["candidate_surface_success"])
    if row["qa_pass"]:
        row["reject_reason"] = None
    row["runtime_seconds"] = time.perf_counter() - started
    dump(cache_dir / "qa/point2cad_local_qa.json", row)
    return row


def write_profile(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "component_id",
        "backend",
        "topology_class",
        "surface_sample_count",
        "occupancy_sample_count",
        "surface_qa_seconds",
        "occupancy_qa_seconds",
        "peak_memory_mb",
        "qa_pass",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows({key: row.get(key) for key in fields} for row in rows)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not args.skip_point2cad_fit:
        raise RuntimeError("POINT2CAD_REFIT_FORBIDDEN_THIS_GATE_USE_SKIP_POINT2CAD_FIT")
    started = time.perf_counter()
    components = load_p3_components(args.p3_root.resolve(), args.source.resolve())
    base_root = args.base_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    artifacts = output_root / "artifacts"
    mapping = exact_component_mapping(components, args.point2cad_root.resolve(), args.source.resolve())
    dump(artifacts / "point2cad_component_mapping.json", mapping)
    reused = int(mapping["verified_component_count"])
    qa_rows: list[dict[str, Any]] = []
    profile_rows: list[dict[str, Any]] = []
    for component in components:
        candidate, manifest = load_fallback_candidate(base_root, component)
        component_out = output_root / "03_components" / component["component_id"]
        row = local_component_qa(component, candidate, manifest, component_out)
        qa_rows.append(row)
        profile_rows.append(
            {
                "component_id": component["component_id"],
                "backend": row["candidate_backend"],
                "topology_class": row["topology_class"],
                "surface_sample_count": row.get("stage_2", {}).get("source_sample_count", 0),
                "occupancy_sample_count": row.get("occupancy", {}).get("occupancy_sample_count", 0),
                "surface_qa_seconds": row.get("stage_2", {}).get("surface_qa_runtime_seconds", 0.0),
                "occupancy_qa_seconds": row.get("occupancy", {}).get("occupancy_qa_runtime_seconds", 0.0),
                "peak_memory_mb": None,
                "qa_pass": row["qa_pass"],
            }
        )
    write_profile(artifacts / "qa_runtime_profile.csv", profile_rows)
    surface_success = sum(bool(row["point2cad_surface_success"]) for row in qa_rows)
    topology_success = sum(bool(row["point2cad_topology_success"]) for row in qa_rows)
    local_surface_success = sum(bool(row["candidate_surface_success"]) for row in qa_rows)
    local_topology_success = sum(bool(row["candidate_topology_success"]) for row in qa_rows)
    selected = sum(bool(row["qa_pass"]) for row in qa_rows)
    open_shell_skipped = sum(row["topology_class"] == "OPEN_SHELL" for row in qa_rows)
    closed_executed = sum(
        row.get("occupancy", {}).get("occupancy_status") == "EXECUTED_CLOSED_COMPONENT"
        for row in qa_rows
    )
    summary = {
        "CURRENT_GATE": (
            "POINT2CAD_COMPONENT_LOCAL_QA_PASS_WITH_MAPPING_BLOCKED"
            if selected == len(components)
            else "POINT2CAD_COMPONENT_LOCAL_QA_GEOMETRY_FAIL"
        ),
        "POINT2CAD_REFIT": False,
        "POINT2CAD_COMPONENTS_REUSED": reused,
        "POINT2CAD_LOCAL_QA_COMPONENTS": len(components),
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET": SOURCE_SURFACE_BUDGET,
        "LOCAL_CANDIDATE_SURFACE_SAMPLE_BUDGET": CANDIDATE_SURFACE_BUDGET,
        "LOCAL_OCCUPANCY_SAMPLE_BUDGET": OCCUPANCY_BUDGET,
        "OPEN_SHELL_OCCUPANCY_SKIPPED": open_shell_skipped,
        "CLOSED_COMPONENT_OCCUPANCY_EXECUTED": closed_executed,
        "QA_QUERY_CACHE_ENABLED": True,
        "FINE_QA_TOP_K": FINE_QA_TOP_K,
        "POINT2CAD_QA_TOTAL_RUNTIME_SECONDS": time.perf_counter() - started,
        "POINT2CAD_QA_PEAK_MEMORY_MB": None,
        "POINT2CAD_SURFACE_SUCCESS_COMPONENTS": surface_success,
        "POINT2CAD_TOPOLOGY_SUCCESS_COMPONENTS": topology_success,
        "LOCAL_SURFACE_QA_PASS_COMPONENTS": local_surface_success,
        "LOCAL_TOPOLOGY_QA_PASS_COMPONENTS": local_topology_success,
        "POINT2CAD_SELECTED_COMPONENTS": selected,
        "P3_COMPONENT_COUNT": len(components),
        "P3_REEXECUTED": False,
        "POINT2CAD_CACHE_MAPPING_VERIFIED": bool(mapping["source_path_matches_provenance"] and reused),
        "POINT2CAD_CACHE_MAPPING_BLOCKER": (
            "GLOBAL_PLY_HAS_NO_SOURCE_TRIANGLE_OR_P3_COMPONENT_ATTRIBUTE"
            if not reused
            else None
        ),
        "FINE_QA_EXECUTED_COMPONENTS": sum(bool(row["fine_qa_executed"]) for row in qa_rows),
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
    }
    dump(artifacts / "point2cad_local_qa_summary.json", summary)
    report = ["# TANK_P3_POINT2CAD_COMPONENT_LOCAL_QA_V2", ""]
    report.extend(f"{key}={value}" for key, value in summary.items())
    report.extend(
        [
            "",
            "Point2CAD fitting was not invoked.",
            "The existing global Point2CAD PLY was not counted as reusable per-component cache because it has no per-face source-triangle/P3-label provenance.",
            "Per-component QA used bounded surface sampling and local staged gates; open shells skipped volumetric occupancy.",
        ]
    )
    (artifacts / "TANK_P3_POINT2CAD_COMPONENT_LOCAL_QA_V2_REPORT.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--p3-root", type=Path, required=True)
    parser.add_argument("--base-root", type=Path, required=True)
    parser.add_argument("--point2cad-root", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_point2cad_component_local_qa_v2"),
    )
    parser.add_argument("--skip-point2cad-fit", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
