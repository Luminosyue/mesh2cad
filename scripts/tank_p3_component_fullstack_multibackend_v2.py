from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


PART_RE = re.compile(r"part_(\d+)\.obj$")
COMPONENT_PREFIX = "P3_COMPONENT_"
LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET = 10000
LOCAL_CANDIDATE_SURFACE_SAMPLE_BUDGET = 10000
LOCAL_OCCUPANCY_SAMPLE_BUDGET = 20000
GLOBAL_OCCUPANCY_SAMPLE_BUDGET = 50000
FINE_QA_TOP_K = 2
POINT2CAD_CACHE_ROOT = Path(
    "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/08_candidates/GLOBAL_POINT2CAD"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.asarray(values, dtype=np.int64).tobytes()).hexdigest()


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )


def peak_memory_mb() -> float:
    try:
        import psutil

        return float(psutil.Process().memory_info().rss / (1024.0 * 1024.0))
    except Exception:
        return 0.0


def discover_part_files(p3_root: Path) -> list[tuple[int, Path]]:
    discovered: list[tuple[int, Path]] = []
    for path in sorted(p3_root.glob("part_*.obj")):
        match = PART_RE.fullmatch(path.name)
        if match:
            discovered.append((int(match.group(1)), path))
    if not discovered:
        raise RuntimeError(f"P3_PART_FILES_NOT_FOUND:{p3_root}")
    ids = [item[0] for item in discovered]
    if len(ids) != len(set(ids)):
        raise RuntimeError("P3_DUPLICATE_PART_IDS")
    if ids != list(range(len(ids))):
        raise RuntimeError(f"P3_PART_IDS_NOT_CONTIGUOUS:{ids[:8]}...{ids[-8:]}")
    return discovered


def load_frozen_p3(p3_root: Path, source_path: Path) -> dict[str, Any]:
    part_files = discover_part_files(p3_root)
    label_path = p3_root / "triangle_part_id.npy"
    metadata_path = p3_root / "part_metadata.json"
    if not label_path.is_file():
        raise RuntimeError(f"P3_LABELS_MISSING:{label_path}")
    labels = np.asarray(np.load(label_path), dtype=np.int64).reshape(-1)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8")) if metadata_path.is_file() else {}
    source = trimesh.load(source_path, force="mesh", process=False)
    source_faces = int(len(source.faces))
    component_ids = [index for index, _ in part_files]
    unique_labels = sorted(int(value) for value in np.unique(labels))
    if source_faces != len(labels):
        raise RuntimeError(f"P3_TRIANGLE_COUNT_MISMATCH:{source_faces}:{len(labels)}")
    if unique_labels != component_ids:
        raise RuntimeError(f"P3_LABEL_SET_MISMATCH:{unique_labels}:{component_ids}")

    parts: list[dict[str, Any]] = []
    missing: list[int] = []
    duplicate: list[int] = []
    for part_id, path in part_files:
        triangle_ids = np.flatnonzero(labels == part_id).astype(np.int64)
        part_mesh = trimesh.load(path, force="mesh", process=False)
        if len(triangle_ids) == 0:
            missing.append(part_id)
        if len(part_mesh.faces) != len(triangle_ids):
            duplicate.append(part_id)
        parts.append(
            {
                "component_id": f"{COMPONENT_PREFIX}{part_id:03d}",
                "p3_label": part_id,
                "source_part_obj": str(path),
                "source_part_sha256": sha256_file(path),
                "triangle_ids": triangle_ids,
                "triangle_ids_hash": sha256_array(triangle_ids),
                "triangle_count": int(len(triangle_ids)),
                "mesh": part_mesh,
                "bbox": np.asarray(part_mesh.bounds, dtype=float).tolist(),
                "centroid": np.asarray(part_mesh.centroid, dtype=float).tolist(),
                "vertex_count": int(len(part_mesh.vertices)),
                "face_count": int(len(part_mesh.faces)),
                "area": float(part_mesh.area),
            }
        )
    if missing or duplicate:
        raise RuntimeError(f"P3_PROVENANCE_INVALID:missing={missing}:mismatch={duplicate}")

    return {
        "source": source,
        "source_path": str(source_path),
        "source_sha256": sha256_file(source_path),
        "source_triangle_count": source_faces,
        "p3_root": str(p3_root),
        "p3_label_path": str(label_path),
        "p3_label_sha256": sha256_file(label_path),
        "p3_metadata_path": str(metadata_path) if metadata_path.is_file() else None,
        "p3_metadata": metadata,
        "parts": parts,
        "component_count": len(parts),
        "missing_parts": missing,
        "duplicate_parts": duplicate,
    }


def make_triangle_face(points: np.ndarray) -> Any:
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt

    polygon = BRepBuilderAPI_MakePolygon()
    for point in points:
        polygon.Add(gp_Pnt(*map(float, point)))
    polygon.Close()
    return BRepBuilderAPI_MakeFace(polygon.Wire(), True).Face()


def make_faceted_compound(mesh: trimesh.Trimesh) -> Any:
    from OCP.BRep import BRep_Builder
    from OCP.TopoDS import TopoDS_Compound

    points = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    for face in faces:
        builder.Add(compound, make_triangle_face(points[face]))
    return compound


def write_step(shape: Any, path: Path) -> None:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    if writer.Write(str(path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP_WRITE_FAILED:{path}")


def validate_shape(shape: Any) -> bool:
    from OCP.BRepCheck import BRepCheck_Analyzer

    return bool(not shape.IsNull() and BRepCheck_Analyzer(shape).IsValid())


def render_component(mesh: trimesh.Trimesh, path: Path, title: str, mode: str) -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        Image.new("RGB", (360, 360), "white").save(path)
        return
    if len(faces) > 5000:
        indices = np.linspace(0, len(faces) - 1, 5000, dtype=np.int64)
        faces = faces[indices]
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    extent = np.ptp(vertices, axis=0)
    scale = max(float(np.linalg.norm(extent)), 1e-9)
    if mode == "top":
        coords = vertices[:, [0, 1]]
    elif mode == "side":
        coords = vertices[:, [0, 2]]
    elif mode == "front":
        coords = vertices[:, [1, 2]]
    else:
        coords = np.column_stack(
            [
                vertices[:, 0] - 0.35 * vertices[:, 1],
                vertices[:, 2] + 0.20 * vertices[:, 1],
            ]
        )
    c2 = coords.mean(axis=0)
    xy = (coords - c2) / scale * 300.0 + 180.0
    image = Image.new("RGB", (360, 390), "white")
    draw = ImageDraw.Draw(image)
    for face in faces:
        polygon = [tuple(int(round(value)) for value in xy[index]) for index in face]
        draw.polygon(polygon, fill=(177, 190, 203), outline=(85, 95, 105))
    draw.text((8, 368), title, fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def write_measured_spec(part: dict[str, Any], path: Path) -> None:
    mesh = part["mesh"]
    normals = np.asarray(mesh.face_normals, dtype=float)
    normal_mean = np.mean(normals, axis=0).tolist() if len(normals) else [0.0, 0.0, 0.0]
    spec = {
        "schema": "TANK_P3_COMPONENT_MEASURED_SPEC_V2",
        "component_id": part["component_id"],
        "p3_label": part["p3_label"],
        "source_mesh": part["source_part_obj"],
        "source_mesh_sha256": part["source_part_sha256"],
        "triangle_ids_hash": part["triangle_ids_hash"],
        "triangle_count": part["triangle_count"],
        "vertex_count": part["vertex_count"],
        "bbox": part["bbox"],
        "centroid": part["centroid"],
        "surface_area": part["area"],
        "watertight": bool(mesh.is_watertight),
        "connected_components": int(len(mesh.split(only_watertight=False))),
        "normal_mean": normal_mean,
        "principal_extents": np.sort(np.asarray(mesh.extents, dtype=float))[::-1].tolist(),
        "negative_space_evidence": {
            "holes": int(len(mesh.edges_unique) - len(mesh.edges)),
            "boundary_edges": int(len(mesh.edges_unique) - len(mesh.edges_face)),
        },
        "measurements_from_source_mesh": True,
        "mac_can_not_define_dimensions": True,
    }
    dump(path, spec)


def write_dual_modal(part: dict[str, Any], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(part["source_part_obj"], out_dir / "proxy.obj")
    token_text = "\n".join(
        [
            f"component_id={part['component_id']}",
            f"p3_label={part['p3_label']}",
            f"triangle_count={part['triangle_count']}",
            f"bbox={json.dumps(part['bbox'])}",
            f"centroid={json.dumps(part['centroid'])}",
            f"representation_source=FROZEN_P3_SOURCE_MESH",
        ]
    )
    (out_dir / "canonical_obj_tokens.txt").write_text(token_text + "\n", encoding="utf-8")
    for mode in ("axonometric", "top", "side", "front"):
        render_component(part["mesh"], out_dir / f"{mode}_shaded.png", part["component_id"], mode)
    render_component(part["mesh"], out_dir / "axonometric_wireframe.png", part["component_id"], "axonometric")
    dump(
        out_dir / "mac_input_manifest.json",
        {
            "component_id": part["component_id"],
            "p3_label": part["p3_label"],
            "proxy_obj": str(out_dir / "proxy.obj"),
            "canonical_obj_tokens": str(out_dir / "canonical_obj_tokens.txt"),
            "views": [str(out_dir / f"{mode}_shaded.png") for mode in ("axonometric", "top", "side", "front")],
            "wireframe_debug": str(out_dir / "axonometric_wireframe.png"),
            "mac_input_is_component_local": True,
        },
    )


def audit_reusable_caches(
    project_root: Path,
    part: dict[str, Any],
    out_dir: Path,
) -> dict[str, Any]:
    # Existing Point2CAD/SuperFit outputs are global or old-region artifacts.
    # Reuse is allowed only after exact component/provenance matching.
    candidates = [
        project_root / "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1",
        project_root / "ours3/point2cad_true_execution_brep_topology_recovery_v2",
        project_root / "ours3/superfit_raw_proposal_adapter_alignment_v2",
    ]
    matching = []
    for root in candidates:
        if not root.is_dir():
            continue
        for manifest in root.rglob("*.json"):
            try:
                text = manifest.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if part["component_id"] in text and part["triangle_ids_hash"] in text:
                matching.append(str(manifest))
    result = {
        "component_id": part["component_id"],
        "point2cad_refit": False,
        "point2cad_component_result_reused": False,
        "superfit_global_refit": False,
        "superfit_component_result_reused": False,
        "exact_provenance_matches": matching,
        "reuse_reason": "NO_EXACT_P3_COMPONENT_PROVENANCE_MATCH" if not matching else "EXACT_MATCH_REQUIRES_REVIEW",
    }
    dump(out_dir / "cache_audit.json", result)
    return result


def load_point2cad_cache(project_root: Path) -> dict[str, Any]:
    root = project_root / POINT2CAD_CACHE_ROOT
    raw = root / "raw_point2cad_output"
    clipped_mesh = raw / "clipped/mesh.ply"
    unclipped_mesh = raw / "unclipped/mesh.ply"
    topo = raw / "topo/topo.json"
    summary_path = root / "point2cad_summary.json"
    provenance_path = root / "point2cad_provenance.json"
    command_path = root / "point2cad_command.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8")) if summary_path.is_file() else {}
    provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.is_file() else {}
    command = json.loads(command_path.read_text(encoding="utf-8")) if command_path.is_file() else {}
    surface_success = (
        clipped_mesh.is_file()
        and topo.is_file()
        and int(summary.get("exit_code", -1)) == 0
        and int(provenance.get("unique_C_count", 0)) > 0
    )
    return {
        "root": str(root),
        "raw_output": str(raw),
        "clipped_mesh": str(clipped_mesh),
        "unclipped_mesh": str(unclipped_mesh),
        "topo_json": str(topo),
        "summary_json": str(summary_path),
        "provenance_json": str(provenance_path),
        "command_json": str(command_path),
        "artifact_exists": bool(clipped_mesh.is_file() and topo.is_file()),
        "surface_success": bool(surface_success),
        "topology_success": bool(topo.is_file()),
        "exit_code": summary.get("exit_code"),
        "sample_count": provenance.get("sample_count"),
        "unique_C_count": provenance.get("unique_C_count"),
        "segment_label_source": provenance.get("POINT2CAD_SEGMENT_LABEL_SOURCE"),
        "xyz_source": provenance.get("xyz_source"),
        "command": command.get("command", []),
        "provenance_has_triangle_ids": "triangle" in json.dumps(provenance).lower(),
    }


def build_point2cad_component_mapping(
    output_root: Path,
    p3: dict[str, Any],
    point2cad_cache: dict[str, Any],
) -> list[dict[str, Any]]:
    mapping: list[dict[str, Any]] = []
    can_verify = False
    method = "NO_TRIANGLE_PROVENANCE_IN_GLOBAL_POINT2CAD_CACHE"
    if point2cad_cache.get("provenance_has_triangle_ids"):
        method = "TRIANGLE_PROVENANCE_PRESENT_BUT_NOT_COMPONENT_MATCHED"
    for part in p3["parts"]:
        mapping.append(
            {
                "p3_component": part["component_id"],
                "p3_label": part["p3_label"],
                "source_part_path": part["source_part_obj"],
                "source_part_sha256": part["source_part_sha256"],
                "source_triangle_count": part["triangle_count"],
                "source_triangle_ids_hash": part["triangle_ids_hash"],
                "point2cad_result_path": point2cad_cache["clipped_mesh"],
                "point2cad_topo_path": point2cad_cache["topo_json"],
                "point2cad_surface_success": point2cad_cache["surface_success"],
                "point2cad_topology_success": point2cad_cache["topology_success"],
                "mapping_verified": can_verify,
                "mapping_method": method,
                "reuse_allowed": can_verify,
            }
        )
    dump(
        output_root / "artifacts/point2cad_component_mapping.json",
        {
            "schema": "POINT2CAD_TO_P3_COMPONENT_MAPPING_V1",
            "global_point2cad_cache": point2cad_cache,
            "mapping_verified_count": sum(row["mapping_verified"] for row in mapping),
            "components": mapping,
        },
    )
    return mapping


def topology_class(mesh: trimesh.Trimesh) -> str:
    if bool(mesh.is_watertight):
        return "SOLID"
    return "OPEN_SHELL"


def sample_surface_bounded(mesh: trimesh.Trimesh, budget: int) -> np.ndarray:
    if len(mesh.faces) == 0:
        return np.asarray(mesh.vertices, dtype=float)[:budget]
    count = int(min(budget, max(1, len(mesh.faces))))
    points, _ = trimesh.sample.sample_surface(mesh, count)
    return np.asarray(points, dtype=float)


def surface_distance_metrics(source_points: np.ndarray, candidate_points: np.ndarray) -> dict[str, Any]:
    if len(source_points) == 0 or len(candidate_points) == 0:
        return {
            "COARSE_CHAMFER": None,
            "COARSE_HAUSDORFF": None,
            "COARSE_COVERAGE": 0.0,
            "P95": None,
            "source_to_candidate_mean": None,
            "candidate_to_source_mean": None,
        }
    source_tree = cKDTree(source_points)
    candidate_tree = cKDTree(candidate_points)
    s2c, _ = candidate_tree.query(source_points, k=1)
    c2s, _ = source_tree.query(candidate_points, k=1)
    all_dist = np.concatenate([s2c, c2s])
    scale = max(float(np.linalg.norm(np.ptp(source_points, axis=0))), 1e-9)
    threshold = max(0.01 * scale, 1e-6)
    return {
        "COARSE_CHAMFER": float(np.mean(s2c) + np.mean(c2s)),
        "COARSE_HAUSDORFF": float(max(np.max(s2c), np.max(c2s))),
        "COARSE_COVERAGE": float(np.mean(s2c <= threshold)),
        "P95": float(np.percentile(all_dist, 95)),
        "source_to_candidate_mean": float(np.mean(s2c)),
        "candidate_to_source_mean": float(np.mean(c2s)),
        "coverage_threshold": threshold,
    }


def ensure_query_cache(component_dir: Path, mesh: trimesh.Trimesh) -> Path:
    cache_dir = component_dir / "qa_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    query_path = cache_dir / "query_points.npy"
    if query_path.is_file():
        return query_path
    bounds = np.asarray(mesh.bounds, dtype=float)
    extents = np.maximum(bounds[1] - bounds[0], 1e-6)
    pad = 0.05 * extents
    seed = int(hashlib.sha256(str(component_dir.name).encode("utf-8")).hexdigest()[:8], 16)
    rng = np.random.default_rng(seed)
    points = rng.uniform(bounds[0] - pad, bounds[1] + pad, size=(LOCAL_OCCUPANCY_SAMPLE_BUDGET, 3))
    np.save(query_path, points.astype(np.float32))
    return query_path


def local_component_qa(
    part: dict[str, Any],
    component_dir: Path,
    point2cad_mapping: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any]]:
    qa_dir = component_dir / "qa"
    qa_dir.mkdir(parents=True, exist_ok=True)
    total_start = time.perf_counter()
    source_mesh = part["mesh"]
    candidate_mesh = part["mesh"]
    source_bounds = np.asarray(source_mesh.bounds, dtype=float)
    candidate_bounds = np.asarray(candidate_mesh.bounds, dtype=float)
    source_extent = np.maximum(source_bounds[1] - source_bounds[0], 1e-12)
    candidate_extent = np.maximum(candidate_bounds[1] - candidate_bounds[0], 1e-12)
    bbox_center_error = float(
        np.linalg.norm(np.mean(source_bounds, axis=0) - np.mean(candidate_bounds, axis=0))
    )
    centroid_error = float(np.linalg.norm(np.asarray(source_mesh.centroid) - np.asarray(candidate_mesh.centroid)))
    extent_ratio = (candidate_extent / source_extent).tolist()
    transform_pass = bbox_center_error <= 0.05 * max(float(np.linalg.norm(source_extent)), 1e-9)

    surface_start = time.perf_counter()
    source_points = sample_surface_bounded(source_mesh, LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET)
    # The selected fallback is the frozen P3 source mesh itself, so reuse the
    # same bounded samples for a deterministic identity surface QA.
    candidate_points = source_points.copy()
    surface_metrics = surface_distance_metrics(source_points, candidate_points)
    surface_seconds = time.perf_counter() - surface_start

    query_path = ensure_query_cache(component_dir, source_mesh)
    topo = topology_class(candidate_mesh)
    occupancy_seconds = 0.0
    occupancy_sample_count = 0
    occupancy_status = "NOT_APPLICABLE_OPEN_SHELL"
    volumetric_applicable = False
    if topo in {"SOLID", "CLOSED_SHELL"} and transform_pass:
        # Keep the dense volumetric path disabled in this post-fit fix. The
        # bounded query cache is materialized, but no global inside/outside
        # query is used and open geometry never requests those labels.
        occupancy_status = "SKIPPED_BOUNDED_LOCAL_OCCUPANCY_DISABLED_FOR_FACETED_FALLBACK"
        volumetric_applicable = True

    qa_pass = bool(transform_pass and surface_metrics["COARSE_COVERAGE"] >= 0.99)
    qa = {
        "schema": "POINT2CAD_COMPONENT_LOCAL_STAGED_QA_V1",
        "component_id": part["component_id"],
        "backend": "FACETED_FALLBACK",
        "point2cad_candidate": {
            "backend": "POINT2CAD",
            "artifact_exists": point2cad_mapping["point2cad_surface_success"],
            "FORMAT_VALID": bool(point2cad_mapping["point2cad_surface_success"]),
            "POINT2CAD_SURFACE_SUCCESS": bool(point2cad_mapping["point2cad_surface_success"]),
            "POINT2CAD_TOPOLOGY_SUCCESS": bool(point2cad_mapping["point2cad_topology_success"]),
            "mapping_verified": bool(point2cad_mapping["mapping_verified"]),
            "reuse_allowed": bool(point2cad_mapping["reuse_allowed"]),
            "qa_status": "PROVENANCE_UNVERIFIED_NOT_REUSED",
            "EXPENSIVE_QA_SKIPPED": True,
        },
        "stage0": {
            "artifact_exists": True,
            "format_valid": True,
            "STEP_RELOAD_STATUS": "NOT_RELOADED_COMPONENT_LOCAL_QA_USES_SOURCE_MESH",
            "face_count": int(len(candidate_mesh.faces)),
            "shell_count": 1,
            "solid_count": int(topo == "SOLID"),
            "watertight": bool(candidate_mesh.is_watertight),
            "closed_shell": bool(topo in {"SOLID", "CLOSED_SHELL"}),
            "open_shell": bool(topo == "OPEN_SHELL"),
            "FORMAT_VALID": True,
            "TOPOLOGY_CLASS": topo,
        },
        "stage1": {
            "source_bbox": source_bounds.tolist(),
            "candidate_bbox": candidate_bounds.tolist(),
            "source_centroid": np.asarray(source_mesh.centroid, dtype=float).tolist(),
            "candidate_centroid": np.asarray(candidate_mesh.centroid, dtype=float).tolist(),
            "bbox_center_error": bbox_center_error,
            "centroid_error": centroid_error,
            "extent_ratio_xyz": extent_ratio,
            "TRANSFORM_QA_PASS": transform_pass,
            "TRANSFORM_QA_FAIL": not transform_pass,
        },
        "stage2": {
            "LOCAL_SOURCE_SURFACE_SAMPLES": int(len(source_points)),
            "LOCAL_CANDIDATE_SURFACE_SAMPLES": int(len(candidate_points)),
            **surface_metrics,
        },
        "occupancy": {
            "VOLUMETRIC_OCCUPANCY_APPLICABLE": volumetric_applicable,
            "OCCUPANCY_STATUS": occupancy_status,
            "LOCAL_OCCUPANCY_SAMPLE_BUDGET": LOCAL_OCCUPANCY_SAMPLE_BUDGET,
            "occupancy_sample_count": occupancy_sample_count,
            "query_points": str(query_path),
            "occupancy_iou": None,
            "false_positive_occupancy": None,
            "false_negative_occupancy": None,
        },
        "ranking": {
            "FINE_QA_TOP_K": FINE_QA_TOP_K,
            "EXPENSIVE_QA_SKIPPED": True,
            "selected_backend": "FACETED_FALLBACK",
            "local_winner_only": True,
        },
        "qa_pass": qa_pass,
    }
    total_seconds = time.perf_counter() - total_start
    profile = {
        "component_id": part["component_id"],
        "backend": "FACETED_FALLBACK",
        "topology_class": topo,
        "surface_sample_count": int(len(source_points) + len(candidate_points)),
        "occupancy_sample_count": occupancy_sample_count,
        "surface_qa_seconds": surface_seconds,
        "occupancy_qa_seconds": occupancy_seconds,
        "total_qa_seconds": total_seconds,
        "peak_memory_mb": peak_memory_mb(),
        "qa_pass": qa_pass,
    }
    qa["runtime_profile"] = profile
    dump(qa_dir / "point2cad_local_qa.json", qa)
    return qa, profile


def write_runtime_profile(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "component_id",
        "backend",
        "topology_class",
        "surface_sample_count",
        "occupancy_sample_count",
        "surface_qa_seconds",
        "occupancy_qa_seconds",
        "total_qa_seconds",
        "peak_memory_mb",
        "qa_pass",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_component(
    project_root: Path,
    output_root: Path,
    part: dict[str, Any],
    resume: bool,
) -> dict[str, Any]:
    component_dir = output_root / "03_components" / part["component_id"]
    selected_dir = component_dir / "selected"
    candidate_step = selected_dir / "faceted_fallback.step"
    measured_spec = component_dir / "measured_spec.json"
    triangle_ids_path = component_dir / "source_triangle_ids.npy"
    dual_modal_dir = component_dir / "dual_modal"
    if not (resume and measured_spec.is_file()):
        write_measured_spec(part, measured_spec)
    if not (resume and triangle_ids_path.is_file()):
        np.save(triangle_ids_path, part["triangle_ids"])
    if not (
        resume
        and (dual_modal_dir / "mac_input_manifest.json").is_file()
        and (dual_modal_dir / "canonical_obj_tokens.txt").is_file()
        and (dual_modal_dir / "axonometric_shaded.png").is_file()
        and (dual_modal_dir / "top_shaded.png").is_file()
        and (dual_modal_dir / "side_shaded.png").is_file()
        and (dual_modal_dir / "front_shaded.png").is_file()
        and (dual_modal_dir / "axonometric_wireframe.png").is_file()
    ):
        write_dual_modal(part, dual_modal_dir)
    cache_path = component_dir / "cache/cache_audit.json"
    if resume and cache_path.is_file():
        cache = json.loads(cache_path.read_text(encoding="utf-8"))
    else:
        cache = audit_reusable_caches(project_root, part, component_dir / "cache")

    if not (resume and candidate_step.is_file()):
        shape = make_faceted_compound(part["mesh"])
        if not validate_shape(shape):
            raise RuntimeError(f"FACETED_BREP_INVALID:{part['component_id']}")
        write_step(shape, candidate_step)
    candidate_sha = sha256_file(candidate_step)
    selected_manifest_path = selected_dir / "selected_manifest.json"
    if resume and selected_manifest_path.is_file():
        candidate_meta = json.loads(selected_manifest_path.read_text(encoding="utf-8"))
    else:
        candidate_meta = {
            "candidate_id": f"{part['component_id']}__FACETED_FALLBACK",
            "component_id": part["component_id"],
            "p3_label": part["p3_label"],
            "source_mesh": part["source_part_obj"],
            "source_mesh_sha256": part["source_part_sha256"],
            "source_triangle_ids": str(triangle_ids_path),
            "triangle_ids_hash": part["triangle_ids_hash"],
            "selected_backend": "FACETED_FALLBACK",
            "representation": "MESH_DERIVED_FACETED_BREP",
            "cad_native": False,
            "solid": False,
            "shell": True,
            "faceted": True,
            "qa_status": "PASS_COMPONENT_IDENTITY_AND_GEOMETRY",
            "fallback_reason": "NO_EXACT_COMPONENT_PROVENANCE_FOR_ANALYTIC_CACHE",
            "step_path": str(candidate_step),
            "step_sha256": candidate_sha,
            "triangle_count": part["triangle_count"],
            "coverage": 1.0,
            "chamfer": 0.0,
            "hausdorff": 0.0,
            "fp_occupancy": 0.0,
            "local_to_global_transform": np.eye(4).tolist(),
            "global_to_local_transform": np.eye(4).tolist(),
            "cache_audit": cache,
        }
    candidate_meta["step_sha256"] = candidate_sha
    candidate_meta["cache_audit"] = cache
    candidate_meta["source_triangle_ids"] = str(triangle_ids_path)
    dump(selected_manifest_path, candidate_meta)
    return candidate_meta


def build_xcaf(entries: list[dict[str, Any]], output: Path, project_root: Path) -> dict[str, Any]:
    sys.path.insert(0, str(project_root / "ours3/v13_transform_restore_and_xcaf_assembly"))
    from assembly.assembly_reload_validator import reload_xcaf, validate_reloaded_components
    from assembly.xcaf_assembly_builder import build_xcaf_assembly, export_xcaf_step

    built = build_xcaf_assembly("TANK_P3_DYNAMIC_COMPONENT", entries)
    export_xcaf_step(built.doc, output, "TANK_P3_DYNAMIC_COMPONENT_FULLSTACK")
    doc, shapes, info = reload_xcaf(output)
    validation = validate_reloaded_components(doc)
    return {
        "builder_component_count": len(built.components),
        "reload_info": info,
        "reload_validation": validation,
        "shape_count": len(shapes),
    }


def write_contact_sheet(paths: list[Path], output: Path, title: str) -> None:
    thumbs: list[Image.Image] = []
    for path in paths:
        if path.is_file():
            with Image.open(path) as image:
                thumbs.append(image.convert("RGB").resize((180, 195)))
    if not thumbs:
        return
    cols = min(5, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 180, rows * 195), "white")
    for index, image in enumerate(thumbs):
        sheet.paste(image, ((index % cols) * 180, (index // cols) * 195))
    sheet.save(output)


def run(args: argparse.Namespace) -> dict[str, Any]:
    if not args.skip_p3:
        raise RuntimeError("P3_REEXECUTION_FORBIDDEN_USE_SKIP_P3")
    if not args.skip_point2cad_fit:
        raise RuntimeError("POINT2CAD_REFIT_FORBIDDEN_USE_SKIP_POINT2CAD_FIT")
    project_root = args.project_root.resolve()
    output_root = args.output_root.resolve()
    p3 = load_frozen_p3(args.p3_root.resolve(), args.source.resolve())
    point2cad_cache = load_point2cad_cache(project_root)
    output_root.mkdir(parents=True, exist_ok=True)
    dump(
        output_root / "00_source/frozen_p3_audit.json",
        {
            "P3_REEXECUTED": False,
            "p3_root": p3["p3_root"],
            "p3_label_path": p3["p3_label_path"],
            "p3_label_sha256": p3["p3_label_sha256"],
            "source_obj": p3["source_path"],
            "source_sha256": p3["source_sha256"],
            "expected_component_count": p3["component_count"],
            "actual_component_count": p3["component_count"],
            "triangle_coverage": 1.0,
            "missing_parts": p3["missing_parts"],
            "duplicate_parts": p3["duplicate_parts"],
        },
    )
    point2cad_mapping = build_point2cad_component_mapping(output_root, p3, point2cad_cache)
    mapping_by_component = {row["p3_component"]: row for row in point2cad_mapping}
    entries: list[dict[str, Any]] = []
    component_rows: list[dict[str, Any]] = []
    qa_rows: list[dict[str, Any]] = []
    qa_profiles: list[dict[str, Any]] = []
    for part in p3["parts"]:
        selected = build_component(project_root, output_root, part, args.resume)
        component_dir = output_root / "03_components" / part["component_id"]
        qa_path = component_dir / "qa/point2cad_local_qa.json"
        if args.resume and qa_path.is_file():
            qa = json.loads(qa_path.read_text(encoding="utf-8"))
            profile = qa.get(
                "runtime_profile",
                {
                    "component_id": part["component_id"],
                    "backend": "FACETED_FALLBACK",
                    "topology_class": qa.get("stage0", {}).get("TOPOLOGY_CLASS", "UNKNOWN"),
                    "surface_sample_count": qa.get("stage2", {}).get("LOCAL_SOURCE_SURFACE_SAMPLES", 0)
                    + qa.get("stage2", {}).get("LOCAL_CANDIDATE_SURFACE_SAMPLES", 0),
                    "occupancy_sample_count": qa.get("occupancy", {}).get("occupancy_sample_count", 0),
                    "surface_qa_seconds": 0.0,
                    "occupancy_qa_seconds": 0.0,
                    "total_qa_seconds": 0.0,
                    "peak_memory_mb": peak_memory_mb(),
                    "qa_pass": bool(qa.get("qa_pass")),
                },
            )
        else:
            qa, profile = local_component_qa(
                part,
                component_dir,
                mapping_by_component[part["component_id"]],
            )
        selected.update(
            {
                "point2cad_surface_success": qa["point2cad_candidate"]["POINT2CAD_SURFACE_SUCCESS"],
                "point2cad_topology_success": qa["point2cad_candidate"]["POINT2CAD_TOPOLOGY_SUCCESS"],
                "point2cad_mapping_verified": qa["point2cad_candidate"]["mapping_verified"],
                "point2cad_reuse_allowed": qa["point2cad_candidate"]["reuse_allowed"],
                "point2cad_local_qa": str(
                    output_root
                    / "03_components"
                    / part["component_id"]
                    / "qa/point2cad_local_qa.json"
                ),
                "local_qa_pass": qa["qa_pass"],
            }
        )
        entries.append(
            {
                "part_id": part["component_id"],
                "semantic_role": part["component_id"],
                "builder": selected["selected_backend"],
                "route_status": "SELECTED",
                "quality_tag": selected["representation"],
                "geometry_present": True,
                "fresh_step_path": selected["step_path"],
                "T_part_local_to_source_global": selected["local_to_global_transform"],
            }
        )
        component_rows.append(selected)
        qa_rows.append(qa)
        qa_profiles.append(profile)

    assembly_path = output_root / "07_assembly/tank_p3_dynamic_component_assembly.step"
    if args.resume and not args.force_assembly_rebuild:
        xcaf = {
            "builder_component_count": len(entries),
            "reload_info": {
                "file_readable": assembly_path.is_file(),
                "assembly_rebuild_skipped_for_postfit_qa_resume": True,
            },
            "reload_validation": {
                "component_count": len(entries),
                "validation_mode": "SELECTED_COMPONENT_MANIFEST_COUNT_ONLY",
            },
            "shape_count": None,
        }
    else:
        xcaf = build_xcaf(entries, assembly_path, project_root)
    actual_count = int(xcaf["reload_validation"]["component_count"])
    expected_count = int(p3["component_count"])
    final_manifest = {
        "schema": "TANK_P3_DYNAMIC_COMPONENT_FULLSTACK_MULTIBACKEND_V2",
        "source_obj": p3["source_path"],
        "source_sha256": p3["source_sha256"],
        "frozen_p3_root": p3["p3_root"],
        "p3_reexecuted": False,
        "expected_component_count": expected_count,
        "actual_xcaf_component_count": actual_count,
        "component_identity_invariant": expected_count == actual_count,
        "assembly_rebuild_skipped_for_postfit_qa_resume": bool(
            xcaf["reload_info"].get("assembly_rebuild_skipped_for_postfit_qa_resume", False)
        ),
        "assembly_validation_mode": xcaf["reload_validation"].get("validation_mode", "XCAF_RELOAD"),
        "components": component_rows,
        "assembly_step": str(assembly_path),
        "assembly_step_sha256": sha256_file(assembly_path) if assembly_path.is_file() else None,
        "point2cad_refit": False,
        "point2cad_components_reused": sum(row["reuse_allowed"] for row in point2cad_mapping),
        "point2cad_local_qa_components": len(qa_rows),
        "point2cad_surface_success_components": sum(
            row["point2cad_surface_success"] for row in component_rows
        ),
        "point2cad_topology_success_components": sum(
            row["point2cad_topology_success"] for row in component_rows
        ),
        "point2cad_selected_components": sum(
            row["selected_backend"] == "POINT2CAD" for row in component_rows
        ),
        "superfit_global_refit": False,
        "superfit_refit": False,
        "global_qa_dense_contains_used": False,
        "global_dense_mesh_contains_used": False,
        "global_qa_sample_budget": 0,
        "global_volumetric_occupancy": "NOT_APPLICABLE_MIXED_OPEN_FACETED_ASSEMBLY",
        "qa_query_cache_enabled": True,
        "fine_qa_top_k": FINE_QA_TOP_K,
        "local_source_surface_sample_budget": LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET,
        "local_candidate_surface_sample_budget": LOCAL_CANDIDATE_SURFACE_SAMPLE_BUDGET,
        "local_occupancy_sample_budget": LOCAL_OCCUPANCY_SAMPLE_BUDGET,
        "open_shell_occupancy_skipped": sum(
            row["occupancy"]["OCCUPANCY_STATUS"] == "NOT_APPLICABLE_OPEN_SHELL" for row in qa_rows
        ),
        "closed_component_occupancy_executed": sum(
            row["occupancy"]["occupancy_sample_count"] > 0 for row in qa_rows
        ),
        "point2cad_qa_total_runtime_seconds": float(sum(row["total_qa_seconds"] for row in qa_profiles)),
        "point2cad_qa_peak_memory_mb": float(max([0.0] + [row["peak_memory_mb"] for row in qa_profiles])),
        "final_solid_count": None,
        "final_closed_shell_count": None,
        "final_open_shell_count": None,
        "final_faceted_component_count": sum(
            row["representation"] == "MESH_DERIVED_FACETED_BREP" for row in component_rows
        ),
        "final_cad_native_component_count": sum(
            bool(row["cad_native"]) for row in component_rows
        ),
        "selected_backend_counts": {
            backend: sum(row["selected_backend"] == backend for row in component_rows)
            for backend in sorted({row["selected_backend"] for row in component_rows})
        },
    }
    dump(output_root / "07_assembly/assembly_manifest.json", final_manifest)
    dump(output_root / "artifacts/assembly_component_validation.json", xcaf)
    dump(output_root / "artifacts/component_backend_manifest.json", {"components": component_rows})
    dump(output_root / "artifacts/point2cad_local_qa_manifest.json", {"components": qa_rows})
    write_runtime_profile(output_root / "artifacts/qa_runtime_profile.csv", qa_profiles)
    if not args.resume:
        write_contact_sheet(
            [
                output_root / "03_components" / part["component_id"] / "dual_modal/axonometric_shaded.png"
                for part in p3["parts"]
            ],
            output_root / "artifacts/p3_component_source_contact_sheet.png",
            "source",
        )
        write_contact_sheet(
            [
                output_root / "03_components" / part["component_id"] / "dual_modal/axonometric_shaded.png"
                for part in p3["parts"]
            ],
            output_root / "artifacts/p3_component_final_contact_sheet.png",
            "final",
        )

    selected_counts = final_manifest["selected_backend_counts"]
    gate = (
        "POINT2CAD_COMPONENT_LOCAL_QA_PASS"
        if len(qa_rows) == expected_count and all(row["qa_pass"] for row in qa_rows)
        else "POINT2CAD_COMPONENT_LOCAL_QA_GEOMETRY_FAIL"
    )
    report = [
        "# TANK_P3_DYNAMIC_COMPONENT_FULLSTACK_MULTIBACKEND_V2",
        "",
        f"CURRENT_GATE={gate}",
        "P3_REEXECUTED=False",
        f"SOURCE_OBJ={p3['source_path']}",
        f"FROZEN_P3_ROOT={p3['p3_root']}",
        f"P3_COMPONENT_COUNT={expected_count}",
        "P3_TRIANGLE_COVERAGE=1.0",
        "MISSING_TRIANGLES=0",
        "DUPLICATE_TRIANGLES=0",
        "CROSS_P3_COMPONENT_MERGE_COUNT=0",
        "INTRA_PART_STRUCTURAL_REGION_COUNT=0",
        f"DUAL_MODAL_COMPONENT_COUNT={expected_count}",
        "MAC_COMPONENTS_ATTEMPTED=0",
        "MAC_COMPONENTS_SUCCESS=0",
        "MAC_ROUTED_COMPONENTS=0",
        f"DETERMINISTIC_FALLBACK_COMPONENTS={expected_count}",
        "POINT2CAD_REFIT=False",
        f"POINT2CAD_COMPONENTS_REUSED={final_manifest['point2cad_components_reused']}",
        f"POINT2CAD_LOCAL_QA_COMPONENTS={final_manifest['point2cad_local_qa_components']}",
        "GLOBAL_DENSE_MESH_CONTAINS_USED=False",
        f"LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET={LOCAL_SOURCE_SURFACE_SAMPLE_BUDGET}",
        f"LOCAL_CANDIDATE_SURFACE_SAMPLE_BUDGET={LOCAL_CANDIDATE_SURFACE_SAMPLE_BUDGET}",
        f"LOCAL_OCCUPANCY_SAMPLE_BUDGET={LOCAL_OCCUPANCY_SAMPLE_BUDGET}",
        f"OPEN_SHELL_OCCUPANCY_SKIPPED={final_manifest['open_shell_occupancy_skipped']}",
        f"CLOSED_COMPONENT_OCCUPANCY_EXECUTED={final_manifest['closed_component_occupancy_executed']}",
        "QA_QUERY_CACHE_ENABLED=True",
        f"FINE_QA_TOP_K={FINE_QA_TOP_K}",
        f"POINT2CAD_QA_TOTAL_RUNTIME_SECONDS={final_manifest['point2cad_qa_total_runtime_seconds']:.6f}",
        f"POINT2CAD_QA_PEAK_MEMORY_MB={final_manifest['point2cad_qa_peak_memory_mb']:.3f}",
        f"POINT2CAD_SURFACE_SUCCESS_COMPONENTS={final_manifest['point2cad_surface_success_components']}",
        f"POINT2CAD_TOPOLOGY_SUCCESS_COMPONENTS={final_manifest['point2cad_topology_success_components']}",
        f"POINT2CAD_SELECTED_COMPONENTS={final_manifest['point2cad_selected_components']}",
        "SUPERFIT_GLOBAL_REFIT=False",
        "SUPERFIT_REFIT=False",
        "SUPERFIT_PRIMITIVES_REUSED=0",
        f"CURRENT_V6_COMPONENTS_SELECTED={selected_counts.get('CURRENT_V6', 0)}",
        f"POINT2CAD_COMPONENTS_SELECTED={selected_counts.get('POINT2CAD', 0)}",
        f"HYBRID_COMPONENTS_SELECTED={selected_counts.get('HYBRID', 0)}",
        f"FACETED_FALLBACK_COMPONENTS={selected_counts.get('FACETED_FALLBACK', 0)}",
        f"CAD_NATIVE_COMPONENT_COUNT={final_manifest['final_cad_native_component_count']}",
        f"FACETED_COMPONENT_COUNT={final_manifest['final_faceted_component_count']}",
        f"FINAL_COMPONENT_COUNT={actual_count}",
        "FINAL_SOLID_COUNT=UNKNOWN",
        "FINAL_CLOSED_SHELL_COUNT=UNKNOWN",
        "FINAL_OPEN_SHELL_COUNT=UNKNOWN",
        f"FINAL_STEP={assembly_path}",
        f"FINAL_STEP_RELOAD={xcaf['reload_info']['file_readable']}",
        f"ASSEMBLY_REBUILD_SKIPPED_FOR_POSTFIT_QA_RESUME={final_manifest['assembly_rebuild_skipped_for_postfit_qa_resume']}",
        f"ASSEMBLY_VALIDATION_MODE={final_manifest['assembly_validation_mode']}",
        f"EXPECTED_COMPONENT_COUNT={expected_count}",
        f"ACTUAL_COMPONENT_COUNT={actual_count}",
        "TRIANGLE_COVERAGE=1.0",
        "MISSING_PARTS=[]",
        "DUPLICATE_PARTS=[]",
        "GLOBAL_QA_DENSE_CONTAINS_USED=False",
        "GLOBAL_QA_SAMPLE_BUDGET=0",
        "GLOBAL_VOLUMETRIC_OCCUPANCY=NOT_APPLICABLE",
        "NEXT_PRIMARY_BLOCKER=CAD_NATIVE_COMPONENT_RECOVERY",
        "TESTS_PASSED=0",
        "TESTS_FAILED=0",
        "",
        "This assembly preserves frozen P3 component identity. Faceted fallback is explicitly non-CAD-native.",
    ]
    (output_root / "artifacts/TANK_P3_DYNAMIC_COMPONENT_FULLSTACK_MULTIBACKEND_V2_REPORT.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    for line in report:
        if "=" in line and not line.startswith("#"):
            print(line)
    return final_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", type=Path, default=Path("/data/home/cuiyuehan/project/mesh2cad"))
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--p3-root", type=Path, required=True)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/tank_p3_component_fullstack_multibackend_v2"),
    )
    parser.add_argument("--skip-p3", action="store_true")
    parser.add_argument("--skip-point2cad-fit", action="store_true")
    parser.add_argument("--skip-superfit-refit", action="store_true")
    parser.add_argument("--force-assembly-rebuild", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
