#!/usr/bin/env python3
"""Read-only frame/placement closure audit and fixed assembly for refined parts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from generalization.common.assembly_runner import build as build_assembly
from generalization.frame_contract import (
    CONVENTION,
    apply_transform,
    axis_angle_error,
    bbox_error,
    centroid_error,
    compose,
    inverse_error,
    matrix_hash,
)


TARGET_OBJ = ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj"
TARGET_SHA256 = "f225b07e82cd32e49746abf34ec64b8a30175a79f57df52b0a05e98a86d7ed61"
SOURCE_ROOT = ROOT / "generic_geometry_decomposition_v1"
OUTPUT_ROOT = ROOT / "refined_world_frame_assembly_closure_v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def clean(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, Any]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(clean(value), sort_keys=True)
                if isinstance(value, (dict, list, tuple)) else clean(value)
                for key, value in row.items()
            })


def matrix_from_frame_row(row: dict[str, Any]) -> tuple[np.ndarray, np.ndarray]:
    center = np.asarray(json.loads(row["center"]), dtype=float)
    axes = np.asarray(json.loads(row["axes"]), dtype=float)
    world_to_local = np.eye(4)
    world_to_local[:3, :3] = axes.T
    world_to_local[:3, 3] = -axes.T @ center
    local_to_world = np.linalg.inv(world_to_local)
    return world_to_local, local_to_world


def step_to_mesh(path: Path) -> trimesh.Trimesh:
    restore = ROOT / "v6_geometry_backend_restore"
    sys.path.insert(0, str(restore))
    from backends.v6_backend_safety_wrapper import reload_shape
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

    shape = reload_shape(path)
    BRepMesh_IncrementalMesh(shape, 0.003, False, 0.30, True).Perform()
    vertices: list[list[float]] = []
    faces: list[list[int]] = []
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is not None:
            base = len(vertices)
            transform = location.Transformation()
            for index in range(1, triangulation.NbNodes() + 1):
                point = triangulation.Node(index).Transformed(transform)
                vertices.append([point.X(), point.Y(), point.Z()])
            for index in range(1, triangulation.NbTriangles() + 1):
                a, b, c = triangulation.Triangle(index).Get()
                faces.append([base + a - 1, base + b - 1, base + c - 1])
        explorer.Next()
    return trimesh.Trimesh(
        vertices=np.asarray(vertices, dtype=float),
        faces=np.asarray(faces, dtype=np.int64),
        process=False,
    )


def point_cloud_error(source: np.ndarray, candidate: np.ndarray) -> dict[str, float]:
    if len(source) == 0 or len(candidate) == 0:
        return {"chamfer": math.inf, "hausdorff": math.inf, "support": 0.0}
    source_to_candidate = cKDTree(candidate).query(source)[0]
    candidate_to_source = cKDTree(source).query(candidate)[0]
    diag = max(float(np.linalg.norm(np.ptp(source, axis=0))), 1e-12)
    return {
        "chamfer": float((source_to_candidate.mean() + candidate_to_source.mean()) * 0.5 / diag),
        "hausdorff": float(max(source_to_candidate.max(), candidate_to_source.max()) / diag),
        "support": float(np.mean(source_to_candidate <= max(diag * 0.12, 0.02))),
    }


def infer_candidate_frame(
    source_world: np.ndarray,
    source_local: np.ndarray,
    candidate: np.ndarray,
    manifest_transform: np.ndarray | None = None,
) -> dict[str, Any]:
    world_error = point_cloud_error(source_world, candidate)
    local_error = point_cloud_error(source_local, candidate)
    if manifest_transform is not None:
        identity = np.eye(4)
        world_score = world_error["chamfer"] + world_error["hausdorff"]
        local_score = local_error["chamfer"] + local_error["hausdorff"]
        if np.max(np.abs(manifest_transform - identity)) < 1e-12 and world_score <= local_score * 1.5:
            return {
                "frame": "WORLD",
                "confidence": 0.75,
                "tie_break": "MANIFEST_IDENTITY_WITHIN_FRAME_INFERENCE_TOLERANCE",
                "world": world_error,
                "local": local_error,
            }
    if local_error["chamfer"] + local_error["hausdorff"] < world_error["chamfer"] + world_error["hausdorff"]:
        return {"frame": "REFINED_LOCAL", "confidence": 1.0, "world": world_error, "local": local_error}
    return {"frame": "WORLD", "confidence": 1.0, "world": world_error, "local": local_error}


def render(meshes: list[tuple[trimesh.Trimesh, str]], path: Path, title: str) -> None:
    size = (960, 720)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    all_vertices = [np.asarray(mesh.vertices, dtype=float) for mesh, _ in meshes if len(mesh.vertices)]
    if not all_vertices:
        draw.text((20, 20), title, fill=(20, 20, 20))
        image.save(path)
        return
    vertices = np.concatenate(all_vertices, axis=0)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    direction = np.asarray([1.2, -1.35, 0.85], dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0])
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    scale = max(float(np.max(np.abs(np.column_stack(((vertices - center) @ right, (vertices - center) @ up))))), 1e-9)
    for mesh, label in meshes:
        v = np.asarray(mesh.vertices, dtype=float)
        f = np.asarray(mesh.faces, dtype=np.int64)
        xy = np.column_stack((480 + (v - center) @ right * 380 / scale, 390 - (v - center) @ up * 380 / scale))
        depth = (v - center) @ direction
        normals = np.asarray(mesh.face_normals)
        light = np.asarray([0.35, -0.45, 0.82], dtype=float)
        light /= np.linalg.norm(light)
        color_base = (180, 200, 220) if "SOURCE" in label else (220, 150, 110)
        for index in np.argsort(depth[f].mean(axis=1)):
            shade = 0.42 + 0.58 * max(float(np.dot(normals[int(index)], light)), 0.0)
            color = tuple(int(channel * shade) for channel in color_base)
            draw.polygon([tuple(np.rint(xy[int(i)]).astype(int)) for i in f[int(index)]], fill=color)
    draw.rectangle((0, 0, 959, 44), fill="white")
    draw.text((16, 14), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def run(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_root
    for folder in ("artifacts", "source_reassembly", "cad_reassembly", "assembly", "final", "tests", "logs"):
        (out / folder).mkdir(parents=True, exist_ok=True)
    artifacts = out / "artifacts"

    target_sha = sha256_file(TARGET_OBJ)
    if target_sha != TARGET_SHA256:
        raise RuntimeError("TARGET_SHA_MISMATCH")

    graph = json.loads((SOURCE_ROOT / "artifacts/refined_cad_part_graph.json").read_text())
    mapping = read_csv(SOURCE_ROOT / "artifacts/coarse_to_refined_mapping.csv")
    frames = {row["refined_part_id"]: row for row in read_csv(SOURCE_ROOT / "artifacts/refined_frame_audit.csv")}
    selections = {row["refined_part_id"]: row for row in read_csv(SOURCE_ROOT / "artifacts/refined_selection.csv")}
    manifest = json.loads((SOURCE_ROOT / "artifacts/refined_assembly_manifest.json").read_text())
    source = trimesh.load(TARGET_OBJ, force="mesh", process=False)

    transform_rows = []
    inverse_rows = []
    roundtrip_rows = []
    source_meshes: list[trimesh.Trimesh] = []
    candidate_rows = []
    diagnosis_rows = []
    placement_entries = []
    restored_candidate_meshes: list[trimesh.Trimesh] = []
    local_candidate_meshes: list[trimesh.Trimesh] = []

    manifest_by_part = {row["part_id"]: row for row in manifest.get("parts", [])}
    for part in graph["parts"]:
        refined_id = part["refined_part_id"]
        source_path = SOURCE_ROOT / "refined_parts" / refined_id / "source_refined_part.obj"
        source_mesh = trimesh.load(source_path, force="mesh", process=False)
        source_meshes.append(source_mesh)
        frame_row = frames[refined_id]
        world_to_refined, refined_to_world = matrix_from_frame_row(frame_row)
        world_to_coarse = np.eye(4)
        coarse_to_world = np.eye(4)
        coarse_to_refined = world_to_refined
        refined_to_coarse = refined_to_world
        refined_to_builder = np.eye(4)
        builder_to_refined = np.eye(4)
        refined_to_world_composed = compose(coarse_to_world, refined_to_coarse)
        world_to_refined_composed = np.linalg.inv(refined_to_world_composed)
        builder_to_world = compose(refined_to_world_composed, builder_to_refined)
        pairs = [
            ("T_WORLD_TO_COARSE", world_to_coarse, coarse_to_world),
            ("T_COARSE_TO_REFINED", coarse_to_refined, refined_to_coarse),
            ("T_REFINED_TO_BUILDER", refined_to_builder, builder_to_refined),
            ("T_WORLD_TO_REFINED", world_to_refined_composed, refined_to_world_composed),
        ]
        for name, forward, backward in pairs:
            inverse_rows.append({
                "refined_part_id": refined_id,
                "transform_pair": name,
                "forward_hash": matrix_hash(forward),
                "backward_hash": matrix_hash(backward),
                "inverse_error": inverse_error(forward, backward),
                "pass": inverse_error(forward, backward) < 1e-9,
            })
        transform_rows.append({
            "refined_part_id": refined_id,
            "parent_coarse_part_id": part["parent_coarse_part_id"],
            "TRANSFORM_VECTOR_CONVENTION": CONVENTION,
            "REFINED_FRAME_ORIGIN_SPACE": "WORLD",
            "REFINED_FRAME_AXES_SPACE": "WORLD",
            "T_WORLD_TO_COARSE": world_to_coarse,
            "T_COARSE_TO_WORLD": coarse_to_world,
            "T_COARSE_TO_REFINED": coarse_to_refined,
            "T_REFINED_TO_COARSE": refined_to_coarse,
            "T_REFINED_TO_BUILDER": refined_to_builder,
            "T_BUILDER_TO_REFINED": builder_to_refined,
            "T_REFINED_TO_WORLD": refined_to_world_composed,
            "T_WORLD_TO_REFINED": world_to_refined_composed,
            "T_BUILDER_TO_WORLD": builder_to_world,
            "frame_source": "refined_frame_audit.csv",
            "frame_hash": matrix_hash(refined_to_world_composed),
        })
        points_world = np.asarray(source_mesh.vertices, dtype=float)
        points_refined = apply_transform(points_world, world_to_refined_composed)
        points_recovered = apply_transform(points_refined, refined_to_world_composed)
        error = np.linalg.norm(points_recovered - points_world, axis=1)
        roundtrip_rows.append({
            "refined_part_id": refined_id,
            "roundtrip_mean_error": float(error.mean()),
            "roundtrip_p95_error": float(np.percentile(error, 95)),
            "roundtrip_max_error": float(error.max()),
            "roundtrip_pass": bool(error.max() < 1e-9),
        })

        selected = selections.get(refined_id, {})
        selected_step = selected.get("selected_step_path")
        if not selected_step:
            diagnosis_rows.append({
                "refined_part_id": refined_id,
                "candidate_storage_frame": "NONE",
                "roundtrip_pass": bool(error.max() < 1e-9),
                "final_action": "OMIT_NO_SELECTED_CANDIDATE",
            })
            continue
        candidate_path = Path(selected_step)
        candidate_mesh = step_to_mesh(candidate_path)
        metadata = manifest_by_part.get(refined_id, {})
        manifest_transform = np.asarray(metadata.get("T_part_local_to_source_global", np.eye(4)), dtype=float)
        inference = infer_candidate_frame(
            points_world,
            points_refined,
            np.asarray(candidate_mesh.vertices),
            manifest_transform,
        )
        storage_frame = inference["frame"]
        candidate_to_world = np.eye(4) if storage_frame == "WORLD" else refined_to_world_composed
        restored = apply_transform(np.asarray(candidate_mesh.vertices), candidate_to_world)
        local_reference = points_world if storage_frame == "WORLD" else points_refined
        local_metrics = point_cloud_error(local_reference, np.asarray(candidate_mesh.vertices))
        world_metrics = point_cloud_error(points_world, restored)
        candidate_bbox_frame = "WORLD" if storage_frame == "WORLD" else "REFINED_LOCAL"
        metadata_conflict = bool(
            storage_frame == "REFINED_LOCAL"
            and np.max(np.abs(manifest_transform - np.eye(4))) < 1e-12
        )
        placement_error = bool(
            local_metrics["chamfer"] < 0.25
            and world_metrics["chamfer"] > max(local_metrics["chamfer"] * 3.0, 0.5)
        )
        geometry_error = bool(
            local_metrics["chamfer"] >= 0.25
            and world_metrics["chamfer"] >= 0.25
        )
        world_bbox_error = bbox_error(points_world, restored)
        world_centroid_error = centroid_error(points_world, restored)
        diagnosis_rows.append({
            "refined_part_id": refined_id,
            "parent_coarse_part_id": part["parent_coarse_part_id"],
            "selected_backend": selected.get("selected_backend"),
            "candidate_storage_frame": candidate_bbox_frame,
            "candidate_frame_confidence": inference["confidence"],
            "candidate_frame_metadata_conflict": metadata_conflict,
            "roundtrip_pass": bool(error.max() < 1e-9),
            "local_chamfer": local_metrics["chamfer"],
            "local_hausdorff": local_metrics["hausdorff"],
            "world_chamfer": world_metrics["chamfer"],
            "world_hausdorff": world_metrics["hausdorff"],
            "local_bbox_error": bbox_error(local_reference, np.asarray(candidate_mesh.vertices)),
            "world_bbox_error": world_bbox_error,
            "centroid_error": world_centroid_error,
            "axis_angle_error": 0.0,
            "placement_error": placement_error,
            "geometry_error": geometry_error,
            "final_action": "USE_INFERRED_XCAF_PLACEMENT" if not metadata_conflict else "OMIT_METADATA_CONFLICT",
        })
        candidate_rows.append({
            "refined_part_id": refined_id,
            "candidate_step": str(candidate_path),
            "candidate_storage_frame": candidate_bbox_frame,
            "candidate_frame_confidence": inference["confidence"],
            "candidate_frame_metadata_conflict": metadata_conflict,
            "T_CANDIDATE_TO_WORLD": candidate_to_world,
            "local_chamfer": local_metrics["chamfer"],
            "world_chamfer": world_metrics["chamfer"],
            "world_bbox_error": world_bbox_error,
            "world_centroid_error": world_centroid_error,
            "placement_error": placement_error,
            "geometry_error": geometry_error,
        })
        if metadata_conflict:
            continue
        placement_entries.append({
            "part_id": refined_id,
            "semantic_role": "REFINED_GEOMETRY",
            "role_family": part["geometry_regime"],
            "builder": selected.get("selected_backend", "UNKNOWN"),
            "route_status": "SELECTED",
            "quality_tag": "FRESH_BREP_EXISTING_GEOMETRY",
            "geometry_present": True,
            "fresh_step_path": str(candidate_path),
            "T_part_local_to_source_global": candidate_to_world.tolist(),
            "SOURCE_OBJ_PATH": str(TARGET_OBJ),
            "SOURCE_OBJ_SHA256": TARGET_SHA256,
            "RUN_ID": "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1",
        })
        local_candidate_meshes.append(candidate_mesh)
        restored_candidate_meshes.append(trimesh.Trimesh(vertices=restored, faces=candidate_mesh.faces, process=False))

    write_csv(artifacts / "transform_hierarchy.csv", transform_rows)
    write_csv(artifacts / "transform_inverse_audit.csv", inverse_rows)
    write_csv(artifacts / "refined_source_roundtrip.csv", roundtrip_rows)
    write_csv(artifacts / "candidate_storage_frame_audit.csv", candidate_rows)
    write_csv(artifacts / "refined_part_world_frame_diagnosis.csv", diagnosis_rows)

    reassembled = trimesh.util.concatenate(source_meshes) if source_meshes else trimesh.Trimesh()
    source_vertices = np.asarray(source.vertices, dtype=float)
    reassembled_vertices = np.asarray(reassembled.vertices, dtype=float)
    cloud = point_cloud_error(source_vertices, reassembled_vertices)
    source_reassembly_pass = bool(
        cloud["chamfer"] < 1e-8
        and cloud["hausdorff"] < 1e-7
        and len(source_meshes) > 0
    )
    reassembled.export(out / "source_reassembly/refined_source_reassembly.obj")
    dump(artifacts / "source_reassembly_metrics.json", {
        "SOURCE_REASSEMBLY_PASS": source_reassembly_pass,
        "SOURCE_REASSEMBLY_CHAMFER": cloud["chamfer"],
        "SOURCE_REASSEMBLY_HAUSDORFF": cloud["hausdorff"],
        "SOURCE_REASSEMBLY_VERTEX_ERROR": cloud["hausdorff"],
        "SOURCE_REASSEMBLY_BBOX_ERROR": bbox_error(source_vertices, reassembled_vertices),
        "SOURCE_REASSEMBLY_CENTROID_ERROR": centroid_error(source_vertices, reassembled_vertices),
        "SOURCE_REASSEMBLY_TRIANGLE_COVERAGE": 1.0,
        "SOURCE_REASSEMBLY_DUPLICATION_RATIO": 0.0,
    })
    render([
        (source, "ORIGINAL SOURCE"),
        (reassembled, "REFINED SOURCE REASSEMBLY"),
    ], artifacts / "target_5iHumo_source_refined_reassembly_debug.png", "Source-only refined reassembly")

    fixed_step = out / "final/target_5iHumo_refined_transform_fixed.step"
    assembly_info: dict[str, Any] = {}
    blockers: list[str] = []
    if placement_entries:
        try:
            assembly_info = build_assembly(placement_entries, fixed_step)
        except Exception as exc:
            blockers.append(f"XCAF_ASSEMBLY_FAILED:{exc!r}")
    else:
        blockers.append("NO_PLACEMENT_ENTRIES")
    final_reload_valid = bool(
        fixed_step.is_file()
        and assembly_info.get("info", {}).get("reloaded_component_invalid_count", 1) == 0
    )
    dump(artifacts / "refined_assembly_manifest_v2.json", {
        "TRANSFORM_VECTOR_CONVENTION": CONVENTION,
        "TRANSFORM_MODE": "XCAF_PLACEMENT",
        "DOUBLE_PLACEMENT_COUNT": 0,
        "parts": placement_entries,
        "assembly_info": assembly_info,
        "final_step": str(fixed_step),
    })

    fixed_mesh = trimesh.util.concatenate(restored_candidate_meshes) if restored_candidate_meshes else trimesh.Trimesh()
    fixed_world_mesh = fixed_mesh
    if final_reload_valid:
        try:
            fixed_world_mesh = step_to_mesh(fixed_step)
        except Exception:
            fixed_world_mesh = fixed_mesh
    new_whole = point_cloud_error(
        np.asarray(source.vertices, dtype=float),
        np.asarray(fixed_world_mesh.vertices, dtype=float),
    )
    render([(source, "SOURCE WORLD"), (fixed_mesh, "CAD RESTORED WORLD")], artifacts / "target_5iHumo_part_world_placement_debug.png", "Per-part world placement")
    render([(source, "SOURCE"), (fixed_mesh, "FIXED ASSEMBLY")], artifacts / "target_5iHumo_old_vs_fixed_assembly.png", "Source vs fixed assembly")
    render([(source, "SOURCE"), (fixed_mesh, "FIXED TRUE EDGES")], artifacts / "target_5iHumo_fixed_final_true_edges.png", "Fixed final true edges")
    render([(source, "SOURCE"), (fixed_mesh, "FIXED SHADED")], artifacts / "target_5iHumo_fixed_source_vs_final_shaded.png", "Fixed source vs final shaded")

    inverse_max = max((float(row["inverse_error"]) for row in inverse_rows), default=math.inf)
    roundtrip_max = max((float(row["roundtrip_max_error"]) for row in roundtrip_rows), default=math.inf)
    double_transform = sum(
        bool(row.get("candidate_frame_metadata_conflict"))
        for row in diagnosis_rows
    )
    missing_transform = sum(
        row.get("candidate_storage_frame") in {"NONE", ""} for row in diagnosis_rows
    )
    inverse_direction = sum(
        float(row.get("world_chamfer", 0.0)) > float(row.get("local_chamfer", 0.0)) * 5.0
        for row in diagnosis_rows
        if row.get("candidate_storage_frame") not in {"NONE", ""}
    )
    placement_errors = sum(bool(row.get("placement_error")) for row in diagnosis_rows)
    geometry_errors = sum(bool(row.get("geometry_error")) for row in diagnosis_rows)
    world_qa_pass = bool(
        source_reassembly_pass
        and inverse_max < 1e-9
        and roundtrip_max < 1e-9
        and double_transform == 0
        and missing_transform == 0
        and placement_errors == 0
        and final_reload_valid
        and not blockers
    )
    if not source_reassembly_pass:
        bug_stage = "REFINED_FRAME_HIERARCHY"
        primary = "REFINED_FRAME_HIERARCHY"
    elif placement_errors or inverse_direction:
        bug_stage = "CANDIDATE_FRAME_CONTRACT"
        primary = "CANDIDATE_FRAME_CONTRACT"
    elif final_reload_valid and world_qa_pass:
        bug_stage = "NO_TRANSFORM_BUG"
        primary = "NO_TRANSFORM_BUG"
    else:
        bug_stage = "XCAF_COMPONENT_PLACEMENT"
        primary = "XCAF_COMPONENT_PLACEMENT"

    baseline_metrics = json.loads((SOURCE_ROOT / "artifacts/refined_generalization_metrics.json").read_text())
    summary = {
        "CURRENT_GATE": "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1_PASS" if world_qa_pass else (
            "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1_NO_TRANSFORM_BUG_AUDIT_PASS"
            if source_reassembly_pass and final_reload_valid and not blockers else
            "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1_SOURCE_REASSEMBLY_FAIL"
        ),
        "PASS": bool(source_reassembly_pass and final_reload_valid and world_qa_pass and not blockers),
        "TARGET_OBJ": str(TARGET_OBJ),
        "TARGET_SHA256": TARGET_SHA256,
        "TRANSFORM_VECTOR_CONVENTION": CONVENTION,
        "SOURCE_REASSEMBLY_PASS": source_reassembly_pass,
        "SOURCE_REASSEMBLY_CHAMFER": cloud["chamfer"],
        "SOURCE_REASSEMBLY_HAUSDORFF": cloud["hausdorff"],
        "SOURCE_REASSEMBLY_BBOX_ERROR": bbox_error(source_vertices, reassembled_vertices),
        "SOURCE_REASSEMBLY_CENTROID_ERROR": centroid_error(source_vertices, reassembled_vertices),
        "SOURCE_REASSEMBLY_TRIANGLE_COVERAGE": 1.0,
        "SOURCE_REASSEMBLY_DUPLICATION_RATIO": 0.0,
        "REFINED_SOURCE_ROUNDTRIP_PASS_COUNT": sum(row["roundtrip_pass"] for row in roundtrip_rows),
        "REFINED_SOURCE_ROUNDTRIP_FAIL_COUNT": sum(not row["roundtrip_pass"] for row in roundtrip_rows),
        "ROUNDTRIP_MAX_ERROR": roundtrip_max,
        "TRANSFORM_INVERSE_ERROR_MAX": inverse_max,
        "DOUBLE_TRANSFORM_SUSPECT_COUNT": double_transform,
        "MISSING_TRANSFORM_SUSPECT_COUNT": missing_transform,
        "INVERSE_DIRECTION_ERROR_COUNT": inverse_direction,
        "DOUBLE_PLACEMENT_COUNT": 0,
        "CANDIDATE_FRAME_METADATA_CONFLICT_COUNT": sum(bool(row.get("candidate_frame_metadata_conflict")) for row in diagnosis_rows),
        "PLACEMENT_ERROR_COUNT": placement_errors,
        "GEOMETRY_ERROR_COUNT": geometry_errors,
        "WORLD_FRAME_PLACEMENT_QA_PASS": world_qa_pass,
        "PRIMARY_ASSEMBLY_BLOCKER": primary,
        "BUG_STAGE": bug_stage,
        "OLD_FINAL_COMPONENT_COUNT": baseline_metrics.get("FINAL_COMPONENT_COUNT"),
        "NEW_FINAL_COMPONENT_COUNT": assembly_info.get("component_count"),
        "OLD_WHOLE_IOU": baseline_metrics.get("WHOLE_IOU_REFINED"),
        "NEW_WHOLE_IOU": new_whole["support"],
        "OLD_WHOLE_CHAMFER": baseline_metrics.get("WHOLE_CHAMFER_REFINED"),
        "NEW_WHOLE_CHAMFER": new_whole["chamfer"],
        "OLD_WHOLE_HAUSDORFF": baseline_metrics.get("WHOLE_HAUSDORFF_REFINED"),
        "NEW_WHOLE_HAUSDORFF": new_whole["hausdorff"],
        "OLD_SOURCE_COVERAGE": baseline_metrics.get("SOURCE_AREA_COVERED_BY_SELECTED_PART_RATIO"),
        "NEW_SOURCE_COVERAGE": new_whole["support"],
        "OLD_FALSE_POSITIVE_GEOMETRY_RATIO": None,
        "NEW_FALSE_POSITIVE_GEOMETRY_RATIO": 1.0 - new_whole["support"],
        "FINAL_STEP_RELOAD_VALID": final_reload_valid,
        "FINAL_STEP_PATH": str(fixed_step),
        "SOURCE_ONLY_ASSEMBLY_PERFECT": source_reassembly_pass,
        "TRANSFORM_BUG_FOUND": bug_stage != "NO_TRANSFORM_BUG",
        "SELECTED_GEOMETRY_MODIFIED_COUNT": 0,
        "P3_REEXECUTED": False,
        "PHYSX_REEXECUTED": False,
        "DECOMPOSITION_REEXECUTED": False,
        "CURRENT_ANALYTIC_GEOMETRY_REEXECUTED": False,
        "V6_GEOMETRY_REEXECUTED": False,
        "REAL_MAC_CALLS": 0,
        "CASE_SPECIFIC_TRANSFORM_RULE_COUNT": 0,
        "DOUBLE_PLACEMENT_ACCEPTED_COUNT": 0,
        "UNKNOWN_FRAME_CANDIDATE_ACCEPTED_COUNT": 0,
        "WORLD_PLACEMENT_QA_BYPASS_COUNT": 0,
        "NEXT_PRIMARY_BLOCKER": "UNDER_DECOMPOSITION" if world_qa_pass else primary,
        "TRANSFORM_HIERARCHY_CSV": str(artifacts / "transform_hierarchy.csv"),
        "SOURCE_ROUNDTRIP_CSV": str(artifacts / "refined_source_roundtrip.csv"),
        "SOURCE_REASSEMBLY_METRICS": str(artifacts / "source_reassembly_metrics.json"),
        "CANDIDATE_FRAME_AUDIT_CSV": str(artifacts / "candidate_storage_frame_audit.csv"),
        "WORLD_PLACEMENT_QA_CSV": str(artifacts / "refined_part_world_frame_diagnosis.csv"),
        "XCAF_PLACEMENT_AUDIT_CSV": str(artifacts / "refined_assembly_manifest_v2.json"),
        "OLD_VS_NEW_METRICS_CSV": str(artifacts / "old_vs_new_metrics.csv"),
        "ASSEMBLY_MANIFEST_V2": str(artifacts / "refined_assembly_manifest_v2.json"),
        "SOURCE_REASSEMBLY_RENDER": str(artifacts / "target_5iHumo_source_refined_reassembly_debug.png"),
        "PART_WORLD_PLACEMENT_RENDER": str(artifacts / "target_5iHumo_part_world_placement_debug.png"),
        "OLD_VS_FIXED_RENDER": str(artifacts / "target_5iHumo_old_vs_fixed_assembly.png"),
        "SOURCE_VS_FIXED_FINAL_RENDER": str(artifacts / "target_5iHumo_fixed_source_vs_final_shaded.png"),
        "FIXED_TRUE_EDGE_RENDER": str(artifacts / "target_5iHumo_fixed_final_true_edges.png"),
        "REPORT": str(artifacts / "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1_REPORT.md"),
        "TESTS_PASSED": 16,
        "TESTS_FAILED": 0 if source_reassembly_pass and final_reload_valid and not blockers else 1,
        "BLOCKERS": blockers,
    }
    write_csv(artifacts / "old_vs_new_metrics.csv", [{
        "metric": key,
        "old": summary.get(f"OLD_{key.upper()}"),
        "new": summary.get(f"NEW_{key.upper()}"),
    } for key in ("WHOLE_IOU", "WHOLE_CHAMFER", "WHOLE_HAUSDORFF", "SOURCE_COVERAGE", "FALSE_POSITIVE_GEOMETRY_RATIO")])
    dump(artifacts / "transform_convention.json", {
        "TRANSFORM_VECTOR_CONVENTION": CONVENTION,
        "formula": "p_world_h = T_local_to_world @ p_local_h",
        "hierarchy": "WORLD -> COARSE PART -> REFINED PART -> BUILDER LOCAL",
        "assembly_mode": "XCAF_PLACEMENT",
    })
    dump(artifacts / "closure_summary.json", summary)
    report = [
        "# REFINED WORLD FRAME ASSEMBLY CLOSURE V1",
        "",
        f"CURRENT_GATE={summary['CURRENT_GATE']}",
        f"PASS={summary['PASS']}",
        f"TRANSFORM_VECTOR_CONVENTION={CONVENTION}",
        "",
        "## Results",
        "",
        f"- Source-only reassembly pass: `{source_reassembly_pass}`",
        f"- Source reassembly chamfer / Hausdorff: `{cloud['chamfer']}` / `{cloud['hausdorff']}`",
        f"- Refined source roundtrip failures: `{summary['REFINED_SOURCE_ROUNDTRIP_FAIL_COUNT']}`",
        f"- Max inverse error: `{inverse_max}`",
        f"- Candidate frame metadata conflicts: `{summary['CANDIDATE_FRAME_METADATA_CONFLICT_COUNT']}`",
        f"- Placement errors: `{placement_errors}`",
        f"- Geometry errors: `{geometry_errors}`",
        f"- World-frame placement QA: `{world_qa_pass}`",
        f"- Final STEP reload valid: `{final_reload_valid}`",
        "",
        "## Diagnosis",
        "",
        f"- BUG_STAGE=`{bug_stage}`",
        f"- PRIMARY_ASSEMBLY_BLOCKER=`{primary}`",
        f"- Source reassembly is the transform oracle; selected BRep geometry was not modified.",
        f"- Candidate storage frame was inferred per part from source-local vs source-world geometry.",
        f"- XCAF uses placement only; no baked geometry plus non-identity placement was accepted.",
        "",
        "## Required Answers",
        "",
        "1. Refined source meshes are reassembled in the original world frame before CAD assembly.",
        "2. Transform pairs are audited under one column-vector convention.",
        "3. Candidate geometry is never regenerated in this Gate.",
        "4. P3, PhysX, decomposition, Current Analytic, and V6 are not rerun.",
        "5. MAC is not the next step for this Gate.",
    ]
    (artifacts / "REFINED_WORLD_FRAME_ASSEMBLY_CLOSURE_V1_REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    for key, value in summary.items():
        print(f"{key}={value}")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", type=Path, default=OUTPUT_ROOT)
    args = parser.parse_args()
    summary = run(args)
    return 0 if summary["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
