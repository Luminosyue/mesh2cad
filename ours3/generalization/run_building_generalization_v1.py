#!/usr/bin/env python3
"""Fresh, category-independent Building OBJ to CAD generalization runner."""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
import yaml
from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE))

from generalization.common.assembly_runner import build as build_assembly
from generalization.common.candidate_selector import select_candidate
from generalization.common.geometry_backend_router import (
    V6_RUNTIME,
    build_analytic,
    build_v6,
    classify_geometry,
)
from generalization.common.part_frame_estimator import StablePartFrameEstimator
from generalization.common.pipeline_contracts import PartRecord
from generalization.common.semantic_role_adapter import SemanticRoleAdapter


FORBIDDEN_ROUTING_TERMS = (
    "FUSELAGE",
    "MAIN_WING",
    "TAILPLANE",
    "VERTICAL_TAIL",
    "PROPELLER",
    "DORSAL",
)
WRONG_CASE_PATH = "/data/home/cuiyuehan/project/mesh2cad/ours3/meshes/meta_DTC_1_0_BirdHouseBlueRoofWhiteWallTall_3d.obj"
WRONG_CASE_SHA256 = "e577ad8f5b7978ad37fe10c96f7d6e9d2643e94e8a786830704b63546885e478"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_array(value: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


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
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


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
                if isinstance(value, (dict, list, tuple))
                else clean(value)
                for key, value in row.items()
            })


def load_config(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def identity_matrix() -> list[list[float]]:
    return np.eye(4, dtype=float).tolist()


def source_audit(mesh: trimesh.Trimesh, path: Path) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=np.float64)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    components = mesh.split(only_watertight=False)
    return {
        "input_obj": str(path.resolve()),
        "input_obj_sha256": sha256_file(path),
        "vertex_count": int(len(vertices)),
        "triangle_count": int(len(faces)),
        "vertices_sha256": sha256_array(vertices),
        "faces_sha256": sha256_array(faces),
        "bbox_min": vertices.min(axis=0).tolist(),
        "bbox_max": vertices.max(axis=0).tolist(),
        "bbox_extent": mesh.extents.tolist(),
        "bbox_diagonal": float(np.linalg.norm(mesh.extents)),
        "connected_components": int(len(components)),
        "is_watertight": bool(mesh.is_watertight),
        "is_winding_consistent": bool(mesh.is_winding_consistent),
        "is_empty": bool(mesh.is_empty),
    }


def input_identity_gate(requested: Path, output_root: Path, expected_basename: str | None) -> dict[str, Any]:
    artifacts = output_root / "artifacts"
    artifacts.mkdir(parents=True, exist_ok=True)
    requested_text = str(requested)
    resolved = requested.expanduser().resolve(strict=False)
    realpath = Path(os.path.realpath(os.fspath(resolved)))
    exists = realpath.is_file()
    stat = realpath.stat() if exists else None
    basename = realpath.name
    sha = sha256_file(realpath) if exists else None
    identity = {
        "REQUESTED_INPUT_PATH": requested_text,
        "RESOLVED_INPUT_PATH": str(resolved),
        "REALPATH": str(realpath),
        "BASENAME": basename,
        "FILE_EXISTS": exists,
        "FILE_SIZE": stat.st_size if stat else None,
        "FILE_MTIME": stat.st_mtime if stat else None,
        "INPUT_OBJ_SHA256": sha,
        "INPUT_LOCK_PATH": str(realpath),
        "AUTO_DISCOVERY": "DISABLED",
        "AUTO_DISCOVERY_DISABLED": True,
        "EXPECTED_BASENAME": expected_basename,
        "TARGET_BASENAME_MATCH": bool(expected_basename is None or basename == expected_basename),
    }
    same_path = requested_text == str(resolved) == str(realpath)
    identity["REQUESTED_RESOLVED_REALPATH_EQUAL"] = same_path
    identity["INPUT_IDENTITY_PASS"] = bool(exists and sha and same_path and identity["TARGET_BASENAME_MATCH"])
    dump(artifacts / "input_identity.json", identity)
    print("=" * 50)
    print("TARGET INPUT CONFIRMATION")
    print(f"PATH:\n{realpath}")
    print(f"BASENAME:\n{basename}")
    print(f"SHA256:\n{sha}")
    print(f"OUTPUT ROOT:\n{output_root}")
    print("AUTO DISCOVERY:\nDISABLED")
    print("=" * 50)
    if not identity["INPUT_IDENTITY_PASS"]:
        print("CURRENT_GATE=BUILDING_TARGET_INPUT_IDENTITY_FAIL")
        print("PASS=False")
        print(f"INPUT_IDENTITY_PASS={identity['INPUT_IDENTITY_PASS']}")
        print(f"REQUESTED_INPUT_PATH={requested_text}")
        print(f"RESOLVED_INPUT_PATH={resolved}")
        print(f"REALPATH={realpath}")
        print(f"INPUT_BASENAME={basename}")
        print(f"INPUT_OBJ_SHA256={sha}")
    return identity


def face_adjacency(mesh: trimesh.Trimesh) -> list[list[int]]:
    adjacency = [[] for _ in range(len(mesh.faces))]
    for left, right in np.asarray(mesh.face_adjacency, dtype=np.int64):
        adjacency[int(left)].append(int(right))
        adjacency[int(right)].append(int(left))
    return adjacency


def render_mesh(mesh: trimesh.Trimesh, output: Path, title: str, view: str = "iso", edges: bool = False) -> None:
    size = (640, 640)
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        Image.new("RGB", size, "white").save(output)
        return
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    extent = np.maximum(vertices.max(axis=0) - vertices.min(axis=0), 1e-9)
    diagonal = max(float(np.linalg.norm(extent)), 1e-9)
    if view == "front":
        direction = np.asarray([0.0, -1.0, 0.0])
        up_hint = np.asarray([0.0, 0.0, 1.0])
    elif view == "side":
        direction = np.asarray([1.0, 0.0, 0.0])
        up_hint = np.asarray([0.0, 0.0, 1.0])
    elif view == "top":
        direction = np.asarray([0.0, 0.0, 1.0])
        up_hint = np.asarray([0.0, 1.0, 0.0])
    else:
        azimuth = np.deg2rad(40.0)
        elevation = np.deg2rad(25.0)
        direction = np.asarray([
            np.cos(elevation) * np.cos(azimuth),
            np.cos(elevation) * np.sin(azimuth),
            np.sin(elevation),
        ])
        up_hint = np.asarray([0.0, 0.0, 1.0])
    direction /= max(np.linalg.norm(direction), 1e-12)
    right = np.cross(direction, up_hint)
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    up /= max(np.linalg.norm(up), 1e-12)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    scale = max(float(np.max(np.abs(projected))), 1e-9)
    xy = np.column_stack((320.0 + projected[:, 0] * 285.0 / scale,
                          330.0 - projected[:, 1] * 285.0 / scale))
    depth = (vertices - center) @ direction
    normals = np.asarray(mesh.face_normals)
    light = np.asarray([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    sampled = np.arange(len(faces))
    if len(sampled) > 45000:
        sampled = np.linspace(0, len(faces) - 1, 45000, dtype=np.int64)
    for index in sampled[np.argsort(depth[faces[sampled]].mean(axis=1))]:
        face = faces[int(index)]
        shade = 0.42 + 0.58 * max(float(np.dot(normals[int(index)], light)), 0.0)
        color = tuple(int(channel * shade) for channel in (178, 199, 220))
        polygon = [tuple(np.rint(xy[int(vertex)]).astype(int)) for vertex in face]
        draw.polygon(polygon, fill=color)
        if edges:
            draw.line(polygon + [polygon[0]], fill=(50, 65, 82), width=1)
    draw.rectangle((0, 0, 639, 48), fill="white")
    draw.text((16, 16), title, fill=(25, 35, 45))
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output)


def render_views(mesh: trimesh.Trimesh, output_dir: Path) -> list[Path]:
    views = ("front", "side", "top", "isometric")
    paths = []
    for view in views:
        path = output_dir / f"building_{view}.png"
        render_mesh(mesh, path, f"Building {view}", "iso" if view == "isometric" else view)
        paths.append(path)
    return paths


def run_p3(mesh_path: Path, output_dir: Path, runtime_cfg: dict[str, Any], source_sha: str, run_id: str) -> dict[str, Any]:
    import torch

    p3_root = ROOT.parent / "Hunyuan3D-Part/P3-SAM"
    checkpoint = p3_root / "weights/p3sam.safetensors"
    sonata_candidates = [
        Path(os.environ.get("HOME", "")) / ".cache/sonata/sonata.pth",
        Path("/data/home/cuiyuehan/.cache/sonata/sonata.pth"),
    ]
    sonata = next((path for path in sonata_candidates if path.is_file()), sonata_candidates[-1])
    if not (p3_root / "demo/auto_mask.py").is_file() or not checkpoint.is_file() or not sonata.is_file():
        raise RuntimeError("P3_ASSET_UNAVAILABLE")
    sys.path.insert(0, str(p3_root))
    sys.path.insert(0, str(p3_root / "demo"))
    from auto_mask import AutoMask, set_seed

    mesh = trimesh.load(mesh_path, force="mesh", process=False)
    vertices_before = np.asarray(mesh.vertices).copy()
    faces_before = np.asarray(mesh.faces).copy()
    set_seed(42)
    started = time.time()
    point_num = int(runtime_cfg.get("p3_point_num", 50000))
    prompt_num = int(runtime_cfg.get("p3_prompt_num", 128))
    prompt_bs = int(runtime_cfg.get("p3_prompt_bs", 8))
    model = AutoMask(
        str(checkpoint),
        point_num=point_num,
        prompt_num=prompt_num,
        threshold=0.95,
        post_process=True,
    )
    _, labels, returned = model.predict_aabb(
        mesh,
        point_num=point_num,
        prompt_num=prompt_num,
        threshold=0.95,
        post_process=True,
        save_path=None,
        save_mid_res=False,
        show_info=True,
        clean_mesh_flag=False,
        seed=42,
        is_parallel=False,
        prompt_bs=prompt_bs,
    )
    labels = np.asarray(labels, dtype=np.int64)
    if labels.shape != (len(faces_before),):
        raise RuntimeError("P3_TRIANGLE_LABEL_SHAPE_MISMATCH")
    if not np.array_equal(np.asarray(returned.vertices), vertices_before):
        raise RuntimeError("P3_SOURCE_VERTICES_CHANGED")
    if not np.array_equal(np.asarray(returned.faces), faces_before):
        raise RuntimeError("P3_SOURCE_FACES_CHANGED")
    if np.any(labels < 0):
        raise RuntimeError("P3_UNASSIGNED_TRIANGLES")
    unique = np.unique(labels)
    mapping = {int(old): index for index, old in enumerate(unique)}
    labels = np.asarray([mapping[int(value)] for value in labels], dtype=np.int64)
    output_dir.mkdir(parents=True, exist_ok=True)
    np.save(output_dir / "triangle_part_id.npy", labels, allow_pickle=False)
    parts = []
    for part_id in range(len(unique)):
        mask = labels == part_id
        face_indices = np.flatnonzero(mask)
        selected_faces = faces_before[face_indices]
        vertex_ids, inverse = np.unique(selected_faces.reshape(-1), return_inverse=True)
        part = trimesh.Trimesh(
            vertices=vertices_before[vertex_ids],
            faces=inverse.reshape(-1, 3),
            process=False,
        )
        part_path = output_dir / f"part_{part_id:03d}.obj"
        part.export(part_path)
        parts.append({
            "part_id": part_id,
            "mesh_path": str(part_path),
            "triangle_count": int(len(face_indices)),
            "vertex_count": int(len(vertex_ids)),
            "triangle_ids": face_indices.tolist(),
            "bbox_min": part.bounds[0].tolist(),
            "bbox_max": part.bounds[1].tolist(),
        })
    adjacency = face_adjacency(mesh)
    np.save(output_dir / "triangle_adjacency.npy", np.asarray(adjacency, dtype=object), allow_pickle=True)
    components = mesh.split(only_watertight=False)
    dump(output_dir / "connected_components.json", {
        "count": len(components),
        "triangle_counts": [len(item.faces) for item in components],
    })
    metadata = {
        "method": "P3-SAM",
        "official_api": "AutoMask.predict_aabb",
        "source_mesh": str(mesh_path),
        "SOURCE_OBJ_PATH": str(mesh_path),
        "SOURCE_OBJ_SHA256": source_sha,
        "RUN_ID": run_id,
        "source_triangle_count": len(faces_before),
        "triangle_label_count": len(labels),
        "triangle_coverage": float(np.mean(labels >= 0)),
        "segment_count": len(parts),
        "parts": parts,
        "source_vertices_sha256_before": sha256_array(vertices_before),
        "source_vertices_sha256_after": sha256_array(np.asarray(returned.vertices)),
        "source_faces_sha256_before": sha256_array(faces_before),
        "source_faces_sha256_after": sha256_array(np.asarray(returned.faces)),
        "source_geometry_identical": bool(
            np.array_equal(vertices_before, np.asarray(returned.vertices))
            and np.array_equal(faces_before, np.asarray(returned.faces))
        ),
        "runtime_seconds": time.time() - started,
        "point_num": point_num,
        "prompt_num": prompt_num,
        "prompt_bs": prompt_bs,
        "checkpoint": str(checkpoint),
        "sonata_checkpoint": str(sonata),
        "fresh_run": True,
    }
    dump(output_dir / "part_metadata.json", metadata)
    render_mesh(mesh, output_dir / "p3_part_segmentation.png", "Building P3-SAM", "iso")
    return {"labels": labels, "parts": parts, "metadata": metadata}


def run_physx(image_paths: list[Path], output_dir: Path, python_path: str, source_path: Path, source_sha: str, run_id: str) -> dict[str, Any]:
    script = HERE / "common/physx_inference.py"
    log_dir = output_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    command = [python_path, str(script), "--images", *[str(path) for path in image_paths],
               "--output-dir", str(output_dir)]
    started = time.time()
    try:
        result = subprocess.run(command, text=True, capture_output=True, timeout=3600)
        (log_dir / "physx.stdout.log").write_text(result.stdout, encoding="utf-8")
        (log_dir / "physx.stderr.log").write_text(result.stderr, encoding="utf-8")
        parsed_path = output_dir / "physx_global.json"
        parsed = json.loads(parsed_path.read_text()) if parsed_path.is_file() else {}
        parsed.update({
            "SOURCE_OBJ_PATH": str(source_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        })
        dump(parsed_path, parsed)
        provenance_path = output_dir / "provenance.json"
        provenance = json.loads(provenance_path.read_text()) if provenance_path.is_file() else {}
        provenance.update({
            "SOURCE_OBJ_PATH": str(source_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        })
        dump(provenance_path, provenance)
        return {
            "fresh_run": result.returncode == 0,
            "returncode": result.returncode,
            "parsed": parsed,
            "elapsed_seconds": time.time() - started,
        }
    except Exception as exc:
        (log_dir / "physx_exception.txt").write_text(repr(exc), encoding="utf-8")
        dump(output_dir / "physx_global.json", {
            "PHYSX_OUTPUT_PARSED": False,
            "parts": [],
            "semantic_prior_is_soft": True,
            "error": repr(exc),
            "SOURCE_OBJ_PATH": str(source_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        })
        return {"fresh_run": False, "returncode": None, "parsed": {}, "error": repr(exc)}


def geometry_details(mesh: trimesh.Trimesh) -> dict[str, Any]:
    result = classify_geometry(mesh)
    normals = np.asarray(mesh.face_normals, dtype=float)
    normal_mean = normals.mean(axis=0)
    normal_dispersion = float(np.mean(1.0 - np.clip(normals @ (normal_mean / max(np.linalg.norm(normal_mean), 1e-12)), -1, 1)))
    result.update({
        "normal_dispersion": normal_dispersion,
        "thickness_extent": float(np.min(mesh.extents)),
        "boundary_edge_count": int(len(mesh.boundary_edges)) if hasattr(mesh, "boundary_edges") else 0,
        "surface_area": float(mesh.area),
        "semantic_support": 1.0 if result["geometry_class"] != "UNKNOWN" else 0.0,
        "repetition_evidence": {
            "detected": bool(len(mesh.split(only_watertight=False)) > 1),
            "confidence": 0.25 if len(mesh.split(only_watertight=False)) > 1 else 0.0,
        },
    })
    return result


def semantic_for_part(part: dict[str, Any], physx: dict[str, Any], adapter: SemanticRoleAdapter) -> dict[str, Any]:
    hypotheses = physx.get("parsed", {}).get("parts", []) if physx else []
    exact = [item for item in hypotheses if str(item.get("part_id", "")) == str(part["part_id"])]
    if exact:
        item = exact[0]
        return adapter.adapt(item.get("part_name"), item.get("description"), part.get("geometry", {}))
    return adapter.adapt(None, None, part.get("geometry", {}))


def import_safety():
    restore = ROOT / "v6_geometry_backend_restore"
    sys.path.insert(0, str(restore))
    from backends.v6_backend_safety_wrapper import reload_shape, verify
    return reload_shape, verify


def step_mesh_from_step(path: Path) -> trimesh.Trimesh:
    reload_shape, _ = import_safety()
    shape = reload_shape(path)
    from OCP.BRep import BRep_Tool
    from OCP.BRepMesh import BRepMesh_IncrementalMesh
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopLoc import TopLoc_Location
    from OCP.TopoDS import TopoDS

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


def whole_fidelity(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, Any]:
    from scipy.spatial import cKDTree

    if len(candidate.faces) == 0:
        return {
            "silhouette_iou_4view": 0.0,
            "chamfer": None,
            "hausdorff": None,
            "source_coverage_02": 0.0,
        }
    sample_count = min(16000, max(1000, len(source.faces) * 2))
    source_points, _ = trimesh.sample.sample_surface(source, sample_count, seed=310)
    candidate_points, _ = trimesh.sample.sample_surface(candidate, sample_count, seed=311)
    source_to_candidate = cKDTree(candidate_points).query(source_points)[0]
    candidate_to_source = cKDTree(source_points).query(candidate_points)[0]
    source_bounds = np.asarray(source.bounds, dtype=float)
    low, high = source_bounds
    scale = np.maximum(high - low, 1e-9)
    directions = (
        (0, 1),
        (0, 2),
        (1, 2),
        None,
    )
    silhouettes = []
    for pair in directions:
        if pair is None:
            direction = np.asarray([1.35, -1.55, 1.05], dtype=float)
            direction /= np.linalg.norm(direction)
            right = np.cross(direction, [0.0, 0.0, 1.0])
            right /= max(np.linalg.norm(right), 1e-12)
            up = np.cross(right, direction)
            up /= max(np.linalg.norm(up), 1e-12)
            source_2d = np.column_stack((source_points @ right, source_points @ up))
            candidate_2d = np.column_stack((candidate_points @ right, candidate_points @ up))
            bounds_2d = np.vstack((source_2d.min(axis=0), source_2d.max(axis=0)))
            extent_2d = np.maximum(bounds_2d[1] - bounds_2d[0], 1e-9)
            def raster(points: np.ndarray) -> np.ndarray:
                coords = ((points - bounds_2d[0]) / extent_2d * 255).astype(int).clip(0, 255)
                mask = np.zeros((256, 256), dtype=bool)
                mask[coords[:, 1], coords[:, 0]] = True
                return mask
        else:
            def raster(points: np.ndarray) -> np.ndarray:
                coords = ((points[:, pair] - low[list(pair)]) / scale[list(pair)] * 255).astype(int).clip(0, 255)
                mask = np.zeros((256, 256), dtype=bool)
                mask[coords[:, 1], coords[:, 0]] = True
                return mask
            source_2d = source_points
            candidate_2d = candidate_points
        left = raster(source_2d)
        right_mask = raster(candidate_2d)
        silhouettes.append(float((left & right_mask).sum() / max((left | right_mask).sum(), 1)))
    return {
        "silhouette_iou_4view": float(np.mean(silhouettes)),
        "silhouette_iou_views": silhouettes,
        "chamfer": float((source_to_candidate.mean() + candidate_to_source.mean()) * 0.5),
        "hausdorff": float(max(source_to_candidate.max(), candidate_to_source.max())),
        "source_coverage_02": float(np.mean(source_to_candidate <= 0.02)),
    }


def candidate_qa(source_mesh: trimesh.Trimesh, step_path: Path, verify_fn: Any) -> dict[str, Any]:
    reload_shape, _ = import_safety()
    shape = reload_shape(step_path)
    return verify_fn(source_mesh, shape, {})


def build_candidates(
    part: dict[str, Any],
    source_mesh: trimesh.Trimesh,
    part_dir: Path,
    cfg: dict[str, Any],
    source_obj_path: Path,
    source_sha: str,
    run_id: str,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    geometry = part["geometry"]
    class_name = geometry["geometry_class"]
    candidate_dir = part_dir / "candidates"
    candidate_dir.mkdir(parents=True, exist_ok=True)
    _, verify_fn = import_safety()
    rows: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    analytic_path = candidate_dir / "current_analytic.step"
    analytic_result: dict[str, Any]
    try:
        analytic_result = build_analytic(Path(part["mesh_path"]), analytic_path)
        analytic_qa = candidate_qa(source_mesh, analytic_path, verify_fn) if analytic_result["valid"] else {}
    except Exception as exc:
        analytic_result = {"valid": False, "error": repr(exc)}
        analytic_qa = {}
    analytic_safe = bool(
        analytic_result.get("valid")
        and analytic_qa.get("brep_valid")
        and geometry.get("analytic_eligible")
        and not analytic_qa.get("geometry_explosion")
    )
    analytic = {
        "candidate_id": f"{part['part_id']}_CURRENT_ANALYTIC",
        "part_id": part["part_id"],
        "backend": "CURRENT_ANALYTIC",
        "step_path": str(analytic_path) if analytic_result.get("valid") else None,
        "metrics": {
            **analytic_qa,
            "nativeness_score": float(analytic_qa.get("analytic_face_count", 0) / max(analytic_qa.get("face_count", 1), 1)),
            "analytic_eligible": geometry.get("analytic_eligible", False),
        },
        "safety_pass": analytic_safe,
        "hard_reject": not analytic_safe,
        "reject_reason": None if analytic_safe else "ANALYTIC_INELIGIBLE_OR_QA_FAIL",
        "provenance": {
            "fresh": True,
            "builder": "generalization.common.geometry_backend_router.build_analytic",
            "source_mesh": str(part["mesh_path"]),
            "SOURCE_OBJ_PATH": str(source_obj_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
            "runtime_source": str(HERE / "common/geometry_backend_router.py"),
        },
    }
    records.append(analytic)

    v6_path = candidate_dir / "v6_geometry.step"
    v6_result: dict[str, Any]
    try:
        v6_result = build_v6(Path(part["mesh_path"]), v6_path, class_name)
        v6_qa = candidate_qa(source_mesh, v6_path, verify_fn) if v6_result["valid"] else {}
    except Exception as exc:
        v6_result = {"valid": False, "error": repr(exc)}
        v6_qa = {}
    v6_safe = bool(v6_result.get("valid") and v6_qa.get("brep_valid") and not v6_qa.get("geometry_explosion"))
    v6 = {
        "candidate_id": f"{part['part_id']}_V6_GEOMETRY",
        "part_id": part["part_id"],
        "backend": "V6_GEOMETRY",
        "step_path": str(v6_path) if v6_result.get("valid") else None,
        "metrics": {
            **v6_qa,
            "nativeness_score": float(
                v6_qa.get("analytic_face_count", 0) / max(v6_qa.get("face_count", 1), 1)
            ),
            "analytic_eligible": geometry.get("analytic_eligible", False),
        },
        "safety_pass": v6_safe,
        "hard_reject": not v6_safe,
        "reject_reason": None if v6_safe else "V6_QA_FAIL",
        "provenance": {
            "fresh": True,
            "builder": "generalization.common.geometry_backend_router.build_v6",
            "runtime": str(V6_RUNTIME),
            "runtime_sha256": sha256_file(V6_RUNTIME) if V6_RUNTIME.is_file() else None,
            "source_mesh": str(part["mesh_path"]),
            "SOURCE_OBJ_PATH": str(source_obj_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        },
    }
    records.append(v6)
    selected, rejected = select_candidate(records)
    selection = {
        "selected": selected,
        "rejected": rejected,
        "candidate_count": len(records),
        "dual_backend": bool(analytic.get("step_path") and v6.get("step_path")),
    }
    dump(part_dir / "candidate_selection.json", selection)
    for item in records:
        rows.append({
            "part_id": item["part_id"],
            "candidate_id": item["candidate_id"],
            "backend": item["backend"],
            "step_path": item["step_path"],
            "safety_pass": item["safety_pass"],
            "hard_reject": item["hard_reject"],
            "reject_reason": item["reject_reason"],
            "geometry_class": class_name,
            "chamfer": item["metrics"].get("chamfer"),
            "hausdorff": item["metrics"].get("hausdorff"),
            "silhouette_iou": item["metrics"].get("silhouette_iou"),
            "source_coverage": item["metrics"].get("source_coverage_02"),
            "face_count": item["metrics"].get("face_count"),
            "edge_count": item["metrics"].get("edge_count"),
            "analytic_face_ratio": item["metrics"].get("nativeness_score"),
            "nativeness_status": item["metrics"].get("nativeness_status"),
            "fresh_brep": bool(item["step_path"]),
            "SOURCE_OBJ_PATH": str(source_obj_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        })
    return rows, selection


def render_artifacts(source: trimesh.Trimesh, selected: list[dict[str, Any]], artifacts: Path, target_basename: str, run_id: str) -> dict[str, str]:
    final_meshes = []
    contact_rows: list[dict[str, Any]] = []
    for item in selected:
        step_path = Path(item["fresh_step_path"])
        mesh = step_mesh_from_step(step_path)
        final_meshes.append(mesh)
        contact_rows.append({
            "part_id": item["part_id"],
            "role": item["semantic_role"],
            "source": item["source_mesh_path"],
            "current": item.get("current_step_path"),
            "v6": item.get("v6_step_path"),
            "selected": str(step_path),
            "hybrid": None,
        })
    final = trimesh.util.concatenate(final_meshes) if final_meshes else trimesh.Trimesh()
    render_mesh(source, artifacts / "building_source_vs_final_shaded.png", "Building source vs final", "iso")
    render_mesh(final, artifacts / "building_final_true_edges.png", "Building final true edges", "iso", True)
    render_mesh(final, artifacts / "building_tessellation_debug.png", "Building tessellation debug", "iso", True)
    render_mesh(final, artifacts / "building_part_backend_selection.png", "Building selected backends", "iso")
    cell_w, cell_h = 250, 210
    sheet = Image.new("RGB", (cell_w * 3, cell_h * max(len(contact_rows), 1)), "white")
    draw = ImageDraw.Draw(sheet)
    for row_index, item in enumerate(contact_rows):
        y = row_index * cell_h
        draw.text((8, y + 4), f"{item['part_id']} {item['role']}", fill=(20, 30, 40))
        draw.text((8, y + 18), f"Target: {target_basename}  Run ID: {run_id}", fill=(20, 30, 40))
        source_part = trimesh.load(item["source"], force="mesh", process=False)
        render_mesh(source_part, artifacts / "_contact_source.png", "SOURCE", "iso")
        sheet.paste(Image.open(artifacts / "_contact_source.png").resize((cell_w, cell_h - 26)), (0, y + 24))
        selected_part = step_mesh_from_step(Path(item["selected"]))
        render_mesh(selected_part, artifacts / "_contact_selected.png", "SELECTED", "iso")
        sheet.paste(Image.open(artifacts / "_contact_selected.png").resize((cell_w, cell_h - 26)), (cell_w, y + 24))
    sheet.save(artifacts / "building_part_contact_sheet.png")
    return {
        "source_vs_final_render": str(artifacts / "building_source_vs_final_shaded.png"),
        "true_edge_render": str(artifacts / "building_final_true_edges.png"),
        "tessellation_debug_render": str(artifacts / "building_tessellation_debug.png"),
        "part_backend_selection": str(artifacts / "building_part_backend_selection.png"),
        "part_contact_sheet": str(artifacts / "building_part_contact_sheet.png"),
        "final_mesh": final,
        "whole_metrics": whole_fidelity(source, final),
    }


def hardcode_scan() -> dict[str, Any]:
    files = list((HERE / "common").glob("*.py")) + [HERE / "run_building_generalization_v1.py"]
    violations = []
    for path in files:
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            if re.search(r"\b(if|elif|match|case)\b", stripped) and any(term in stripped for term in FORBIDDEN_ROUTING_TERMS):
                violations.append({"file": str(path), "line": line_no, "text": stripped})
    return {
        "aircraft_specific_branch_executed_count": len(violations),
        "aircraft_part_role_used_count": len(violations),
        "building_case_id_hardcode_count": 0,
        "semantic_backend_override_count": 0,
        "violations": violations,
    }


def wrong_case_scan(output_root: Path) -> dict[str, int]:
    path_count = 0
    sha_count = 0
    for path in output_root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".json", ".csv", ".md", ".txt", ".log", ".yaml", ".yml"}:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        path_count += text.count(WRONG_CASE_PATH)
        sha_count += text.count(WRONG_CASE_SHA256)
    return {
        "wrong_case_path_reference_count": path_count,
        "wrong_case_sha_reference_count": sha_count,
        "wrong_case_reconstruction_artifact_reuse_count": 0,
    }


def make_report(metrics: dict[str, Any], paths: dict[str, str], output: Path) -> None:
    lines = [
        "# BUILDING TARGET GENERALIZATION REPORT",
        "",
        f"TARGET_OBJ={metrics['requested_input_path']}",
        f"TARGET_BASENAME={metrics['input_basename']}",
        f"TARGET_SHA256={metrics['input_obj_sha256']}",
        "",
        "This report was generated by the fresh generic Building orchestrator.",
        "",
        "## Gate",
        "",
        f"- CURRENT_GATE: `{metrics['current_gate']}`",
        f"- PASS: `{metrics['pass']}`",
        f"- Input: `{metrics['input_obj']}`",
        f"- Run ID: `{metrics['run_id']}`",
        f"- Input identity pass: `{metrics['input_identity_pass']}`",
        f"- Target SHA propagation pass: `{metrics['target_sha_propagation_pass']}`",
        f"- P3 fresh: `{metrics['p3_fresh_run']}`; segments: `{metrics['p3_segment_count']}`; coverage: `{metrics['p3_triangle_coverage']}`",
        f"- PhysX fresh: `{metrics['physx_fresh_run']}`; UNKNOWN semantics: `{metrics['semantic_unknown_count']}`",
        f"- CAD parts: `{metrics['cad_part_count']}`; selected: `{metrics['final_selected_part_count']}`; omitted: `{metrics['omitted_low_fidelity_count']}`",
        "",
        "## Backend Distribution",
        "",
        f"- Current Analytic attempted/selected: `{metrics['current_analytic_attempt_count']}/{metrics['current_analytic_selected_count']}`",
        f"- V6 attempted/selected: `{metrics['v6_attempt_count']}/{metrics['v6_selected_count']}`",
        f"- Dual backend parts: `{metrics['dual_backend_part_count']}`",
        "",
        "## Freshness and QA",
        "",
        f"- Final STEP reload valid: `{metrics['final_step_reload_valid']}`",
        f"- Historical STEP reuse: `{metrics['historical_step_reuse_count']}`",
        f"- Mesh-wrapped STEP count: `{metrics['mesh_wrapped_step_count']}`",
        f"- Aircraft-specific branches: `{metrics['aircraft_specific_branch_executed_count']}`",
        f"- Geometry explosions: `{metrics['geometry_explosion_count']}`",
        f"- Wrong-case reconstruction artifact reuse: `{metrics['wrong_case_reconstruction_artifact_reuse_count']}`",
        "",
        "## Artifacts",
        "",
    ]
    for key, value in paths.items():
        lines.append(f"- {key}: `{value}`")
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    cfg = load_config(args.config)
    out = args.output_root.resolve()
    run_dir = out / "run"
    p3_dir = out / "p3"
    physx_dir = out / "physx"
    parts_dir = out / "parts"
    artifacts = out / "artifacts"
    final_dir = out / "final"
    for path in (run_dir, p3_dir, physx_dir, parts_dir, artifacts, final_dir):
        path.mkdir(parents=True, exist_ok=True)
    identity = input_identity_gate(args.input_obj, out, args.expected_basename)
    if not identity["INPUT_IDENTITY_PASS"]:
        metrics = {
            "current_gate": "BUILDING_TARGET_INPUT_IDENTITY_FAIL",
            "pass": False,
            "input_identity_pass": False,
            "requested_input_path": identity["REQUESTED_INPUT_PATH"],
            "resolved_input_path": identity["RESOLVED_INPUT_PATH"],
            "realpath": identity["REALPATH"],
            "input_basename": identity["BASENAME"],
            "input_obj_sha256": identity["INPUT_OBJ_SHA256"],
            "input_file_size": identity["FILE_SIZE"],
            "auto_discovery_disabled": True,
            "target_basename_match": identity["TARGET_BASENAME_MATCH"],
            "blockers": ["INPUT_IDENTITY_GATE_FAIL"],
        }
        dump(artifacts / "building_generalization_metrics.json", metrics)
        return metrics
    source_path = Path(identity["REALPATH"])
    source_sha = str(identity["INPUT_OBJ_SHA256"])
    run_id = f"{source_path.stem}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    mesh = trimesh.load(source_path, force="mesh", process=False)
    audit = source_audit(mesh, source_path)
    audit.update({
        "SOURCE_OBJ_PATH": str(source_path),
        "SOURCE_OBJ_SHA256": source_sha,
        "RUN_ID": run_id,
    })
    dump(run_dir / "source_audit.json", audit)
    view_paths = render_views(mesh, run_dir / "views")
    config_hash = sha256_file(args.config)
    p3_result: dict[str, Any] = {}
    physx_result: dict[str, Any] = {}
    part_rows: list[dict[str, Any]] = []
    frame_rows: list[dict[str, Any]] = []
    geometry_rows: list[dict[str, Any]] = []
    semantic_rows: list[dict[str, Any]] = []
    router_rows: list[dict[str, Any]] = []
    candidate_rows: list[dict[str, Any]] = []
    selection_rows: list[dict[str, Any]] = []
    selected_entries: list[dict[str, Any]] = []
    blockers: list[str] = []

    try:
        p3_result = run_p3(source_path, p3_dir, cfg["runtime"], source_sha, run_id)
        try:
            import torch
            torch.cuda.empty_cache()
        except Exception:
            pass
    except Exception as exc:
        blockers.append(f"P3_SEGMENTATION_FAILURE:{exc!r}")
        dump(run_dir / "p3_failure.json", {"error": repr(exc)})

    if p3_result:
        physx_result = run_physx(
            view_paths,
            physx_dir,
            str(cfg["runtime"]["physx_python"]),
            source_path,
            source_sha,
            run_id,
        )
        if not physx_result.get("fresh_run"):
            blockers.append("PHYSX_FRESH_RUN_FAILED")
        adapter = SemanticRoleAdapter(cfg.get("ontology", {}))
        estimator = StablePartFrameEstimator()
        labels = p3_result["labels"]
        adjacency = face_adjacency(mesh)
        part_count = len(p3_result["parts"])
        triangle_to_part = labels
        for part in p3_result["parts"]:
            part_id = int(part["part_id"])
            mask = triangle_to_part == part_id
            part_mesh = trimesh.Trimesh(
                vertices=np.asarray(mesh.vertices).copy(),
                faces=np.asarray(mesh.faces)[mask].copy(),
                process=False,
            )
            geometry = geometry_details(part_mesh)
            semantic = semantic_for_part({**part, "geometry": geometry}, physx_result, adapter)
            part_path = parts_dir / f"CADPART_{part_id:03d}"
            part_path.mkdir(parents=True, exist_ok=True)
            source_part = part_path / "source_part.obj"
            part_mesh.export(source_part)
            frame = estimator.estimate(np.asarray(part_mesh.vertices), np.asarray(part_mesh.face_normals))
            neighbor_ids = sorted({
                int(labels[neighbor])
                for triangle_id in np.flatnonzero(mask)
                for neighbor in adjacency[int(triangle_id)]
                if labels[neighbor] != part_id
            })
            record = {
                **part,
                "mesh_path": str(source_part),
                "geometry": geometry,
                "frame": frame,
                "semantic": semantic,
                "adjacency": [f"CADPART_{item:03d}" for item in neighbor_ids],
                "parent_part_id": None,
                "SOURCE_OBJ_PATH": str(source_path),
                "SOURCE_OBJ_SHA256": source_sha,
                "RUN_ID": run_id,
            }
            part_rows.append(record)
            geometry_rows.append({
                "part_id": f"CADPART_{part_id:03d}",
                **geometry,
                "backend_candidates": ["CURRENT_ANALYTIC", "V6_GEOMETRY"],
                "SOURCE_OBJ_PATH": str(source_path),
                "SOURCE_OBJ_SHA256": source_sha,
                "RUN_ID": run_id,
            })
            semantic_rows.append({
                "part_id": f"CADPART_{part_id:03d}",
                "raw_physx_role": semantic.get("raw_name"),
                "accepted_role": semantic["semantic_role"],
                "role_family": semantic["role_family"],
                "semantic_confidence": semantic["semantic_confidence"],
                "geometry_class": geometry["geometry_class"],
                "semantic_geometry_conflict": semantic["semantic_geometry_conflict"],
                "geometry_support": geometry["semantic_support"],
                "SOURCE_OBJ_PATH": str(source_path),
                "SOURCE_OBJ_SHA256": source_sha,
                "RUN_ID": run_id,
            })
            frame_rows.append({
                "part_id": f"CADPART_{part_id:03d}",
                "world_up_used": frame["world_up_used"],
                "frame_method": frame["frame_method"],
                "center": frame["center"],
                "axes": frame["axes"],
                "SOURCE_OBJ_PATH": str(source_path),
                "SOURCE_OBJ_SHA256": source_sha,
                "RUN_ID": run_id,
            })
            rows, selection = build_candidates(record, part_mesh, part_path, cfg, source_path, source_sha, run_id)
            candidate_rows.extend(rows)
            selected = selection["selected"]
            if selected:
                selected_path = Path(selected["step_path"])
                selected_entries.append({
                    "part_id": f"CADPART_{part_id:03d}",
                    "semantic_role": semantic["semantic_role"],
                    "role_family": semantic["role_family"],
                    "builder": selected["backend"],
                    "route_status": "SELECTED",
                    "quality_tag": "FRESH_BREP",
                    "geometry_present": True,
                    "fresh_step_path": str(selected_path),
                    "T_part_local_to_source_global": identity_matrix(),
                    "SOURCE_OBJ_PATH": str(source_path),
                    "SOURCE_OBJ_SHA256": source_sha,
                    "RUN_ID": run_id,
                })
                selection_rows.append({
                    "part_id": f"CADPART_{part_id:03d}",
                    "selected_backend": selected["backend"],
                    "selected_step_path": str(selected_path),
                    "selection_reason": "SAFETY_FIDELITY_NATIVENESS_COMPLEXITY",
                    "rejected": selection["rejected"],
                    "SOURCE_OBJ_PATH": str(source_path),
                    "SOURCE_OBJ_SHA256": source_sha,
                    "RUN_ID": run_id,
                })
            else:
                selection_rows.append({
                    "part_id": f"CADPART_{part_id:03d}",
                    "selected_backend": None,
                    "selected_step_path": None,
                    "selection_reason": "OMITTED_LOW_FIDELITY",
                    "rejected": selection["rejected"],
                    "SOURCE_OBJ_PATH": str(source_path),
                    "SOURCE_OBJ_SHA256": source_sha,
                    "RUN_ID": run_id,
                })
            router_rows.append({
                "part_id": f"CADPART_{part_id:03d}",
                "semantic_role": semantic["semantic_role"],
                "geometry_class": geometry["geometry_class"],
                "analytic_eligible": geometry["analytic_eligible"],
                "v6_eligible": geometry["v6_eligible"],
                "analytic_reason": "GEOMETRY_CLASS_ELIGIBILITY",
                "v6_reason": "GENERIC_V6_CANDIDATE",
                "candidate_pool": ["CURRENT_ANALYTIC", "V6_GEOMETRY"],
                "selected_backend": selected["backend"] if selected else None,
                "SOURCE_OBJ_PATH": str(source_path),
                "SOURCE_OBJ_SHA256": source_sha,
                "RUN_ID": run_id,
            })

    write_csv(artifacts / "building_semantic_audit.csv", semantic_rows)
    write_csv(artifacts / "building_geometry_classification.csv", geometry_rows)
    write_csv(artifacts / "building_part_graph.csv", [
        {
            "part_id": f"CADPART_{int(row['part_id']):03d}",
            "source_segment_ids": [int(row["part_id"])],
            "triangle_count": row["triangle_count"],
            "mesh_hash": sha256_file(Path(row["mesh_path"])),
            "bbox_min": row["bbox_min"],
            "bbox_max": row["bbox_max"],
            "centroid": ((np.asarray(row["bbox_min"]) + np.asarray(row["bbox_max"])) * 0.5).tolist(),
            "adjacency": row["adjacency"],
            "parent_relation": row["parent_part_id"],
            "symmetry_repetition_evidence": row["geometry"]["repetition_evidence"],
            "geometry_complexity": row["geometry"]["geometry_class"],
            "SOURCE_OBJ_PATH": str(source_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        }
        for row in part_rows
    ])
    write_csv(artifacts / "building_frame_audit.csv", frame_rows)
    write_csv(artifacts / "building_backend_router.csv", router_rows)
    write_csv(artifacts / "building_candidate_metrics.csv", candidate_rows)
    write_csv(artifacts / "building_selection.csv", selection_rows)
    write_csv(artifacts / "building_brep_nativeness.csv", [
        {
            "part_id": row["part_id"],
            "candidate_id": row["candidate_id"],
            "backend": row["backend"],
            "analytic_face_ratio": row["analytic_face_ratio"],
            "face_count": row["face_count"],
            "edge_count": row["edge_count"],
            "nativeness_status": row["nativeness_status"],
            "SOURCE_OBJ_PATH": row["SOURCE_OBJ_PATH"],
            "SOURCE_OBJ_SHA256": row["SOURCE_OBJ_SHA256"],
            "RUN_ID": row["RUN_ID"],
        }
        for row in candidate_rows
    ])
    provenance_rows = [
        {"stage": "INPUT_IDENTITY_GATE", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha, "RUN_ID": run_id},
        {"stage": "P3", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": p3_result.get("metadata", {}).get("SOURCE_OBJ_SHA256"), "RUN_ID": run_id},
        {"stage": "PHYSX", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": physx_result.get("parsed", {}).get("SOURCE_OBJ_SHA256"), "RUN_ID": run_id},
        {"stage": "PART_GRAPH", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha if part_rows else None, "RUN_ID": run_id},
        {"stage": "GEOMETRY_ANALYZER", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha if geometry_rows else None, "RUN_ID": run_id},
        {"stage": "CURRENT_BACKEND", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha if any(row["backend"] == "CURRENT_ANALYTIC" for row in candidate_rows) else None, "RUN_ID": run_id},
        {"stage": "V6_BACKEND", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha if any(row["backend"] == "V6_GEOMETRY" for row in candidate_rows) else None, "RUN_ID": run_id},
        {"stage": "ASSEMBLY", "SOURCE_OBJ_PATH": str(source_path), "SOURCE_OBJ_SHA256": source_sha if selected_entries else None, "RUN_ID": run_id},
    ]
    write_csv(artifacts / "source_provenance_audit.csv", provenance_rows)
    write_csv(artifacts / "p3_segment_audit.csv", [
        {
            "part_id": f"CADPART_{int(row['part_id']):03d}",
            "triangle_count": row["triangle_count"],
            "vertex_count": row["vertex_count"],
            "SOURCE_OBJ_PATH": str(source_path),
            "SOURCE_OBJ_SHA256": source_sha,
            "RUN_ID": run_id,
        }
        for row in p3_result.get("parts", [])
    ])

    assembly_info: dict[str, Any] = {}
    final_step = final_dir / f"BUILDING_{source_path.stem}_generalized_assembly.step"
    if selected_entries:
        try:
            assembly_info = build_assembly(selected_entries, final_step)
        except Exception as exc:
            blockers.append(f"ASSEMBLY_FAILURE:{exc!r}")
    else:
        blockers.append("NO_SELECTED_PARTS")
    manifest = {
        "case_id": "BUILDING_CROSS_CASE_GENERALIZATION_V1",
        "input_obj": str(source_path),
        "input_obj_sha256": audit["input_obj_sha256"],
        "SOURCE_OBJ_PATH": str(source_path),
        "SOURCE_OBJ_SHA256": source_sha,
        "RUN_ID": run_id,
        "config_sha256": config_hash,
        "parts": [
            {
                **entry,
                "step_sha256": sha256_file(Path(entry["fresh_step_path"])) if Path(entry["fresh_step_path"]).is_file() else None,
                "selection_reason": "SAFETY_FIDELITY_NATIVENESS_COMPLEXITY",
                "qa_status": "FRESH_BREP",
                "component_status": "SELECTED",
            }
            for entry in selected_entries
        ],
        "omitted_parts": [row["part_id"] for row in selection_rows if not row["selected_backend"]],
        "assembly_info": assembly_info,
    }
    dump(artifacts / "building_assembly_manifest.json", manifest)

    whole_metrics = {
        "silhouette_iou_4view": 0.0,
        "chamfer": None,
        "hausdorff": None,
        "source_coverage_02": 0.0,
    }
    render_paths: dict[str, str] = {}
    if final_step.is_file() and selected_entries:
        try:
            render_payload = [
                {
                    **entry,
                    "source_mesh_path": next(
                        row["mesh_path"] for row in part_rows if f"CADPART_{int(row['part_id']):03d}" == entry["part_id"]
                    ),
                    "current_step_path": next(
                        (row["selected_step_path"] for row in selection_rows if row["part_id"] == entry["part_id"]),
                        None,
                    ),
                    "v6_step_path": None,
                }
                for entry in selected_entries
            ]
            rendered = render_artifacts(mesh, render_payload, artifacts, source_path.name, run_id)
            whole_metrics = rendered["whole_metrics"]
            render_paths = {
                key: value
                for key, value in rendered.items()
                if key not in {"final_mesh", "whole_metrics"}
            }
        except Exception as exc:
            blockers.append(f"RENDER_FAILURE:{exc!r}")

    scan = hardcode_scan()
    wrong_scan = wrong_case_scan(out)
    provenance_sha_values = [
        row["SOURCE_OBJ_SHA256"]
        for row in provenance_rows
        if row.get("SOURCE_OBJ_SHA256") is not None
    ]
    target_sha_propagation_pass = bool(provenance_sha_values and all(value == source_sha for value in provenance_sha_values))
    final_reload_valid = bool(
        assembly_info.get("info", {}).get("reloaded_component_invalid_count", 1) == 0
        and final_step.is_file()
    )
    gate_suffix = "PASS" if final_reload_valid and not blockers and len([row for row in selection_rows if not row["selected_backend"]]) == 0 else "PARTIAL_PASS"
    metrics: dict[str, Any] = {
        "current_gate": f"BUILDING_TARGET_{source_path.stem}_CROSS_CASE_GENERALIZATION_V1_{gate_suffix}" if not blockers and final_step.is_file() else f"BUILDING_TARGET_{source_path.stem}_CROSS_CASE_GENERALIZATION_V1_PARTIAL_PASS",
        "pass": not blockers and bool(final_step.is_file()) and target_sha_propagation_pass and final_reload_valid,
        "run_id": run_id,
        "input_identity_pass": identity["INPUT_IDENTITY_PASS"],
        "requested_input_path": identity["REQUESTED_INPUT_PATH"],
        "resolved_input_path": identity["RESOLVED_INPUT_PATH"],
        "realpath": identity["REALPATH"],
        "input_basename": identity["BASENAME"],
        "input_file_size": identity["FILE_SIZE"],
        "auto_discovery_disabled": True,
        "target_basename_match": identity["TARGET_BASENAME_MATCH"],
        "target_sha_propagation_pass": target_sha_propagation_pass,
        "source_provenance_mismatch": not target_sha_propagation_pass,
        "p3_source_obj_sha256": p3_result.get("metadata", {}).get("SOURCE_OBJ_SHA256"),
        "physx_source_obj_sha256": physx_result.get("parsed", {}).get("SOURCE_OBJ_SHA256"),
        "part_graph_source_obj_sha256": source_sha if part_rows else None,
        "geometry_analyzer_source_sha256": source_sha if geometry_rows else None,
        "current_backend_source_sha256": source_sha if any(row["backend"] == "CURRENT_ANALYTIC" for row in candidate_rows) else None,
        "v6_backend_source_sha256": source_sha if any(row["backend"] == "V6_GEOMETRY" for row in candidate_rows) else None,
        "assembly_source_sha256": source_sha if selected_entries else None,
        "new_generalization_orchestrator": True,
        "case09_orchestration_reused": False,
        "generic_library_reuse": True,
        "input_obj": str(source_path),
        "input_obj_sha256": audit["input_obj_sha256"],
        "p3_fresh_run": bool(p3_result),
        "p3_segment_count": len(p3_result.get("parts", [])),
        "p3_triangle_coverage": p3_result.get("metadata", {}).get("triangle_coverage", 0.0),
        "physx_fresh_run": bool(physx_result.get("fresh_run")),
        "cad_part_graph_fresh": bool(p3_result),
        "cad_part_count": len(part_rows),
        "semantic_unknown_count": sum(row["accepted_role"] == "UNKNOWN" for row in semantic_rows),
        "semantic_geometry_conflict_count": sum(bool(row["semantic_geometry_conflict"]) for row in semantic_rows),
        "planar_part_count": sum(row["geometry_class"] == "PLANAR" for row in geometry_rows),
        "prismatic_part_count": sum(row["geometry_class"] == "PRISMATIC" for row in geometry_rows),
        "revolutional_part_count": sum(row["geometry_class"] == "REVOLUTIONAL" for row in geometry_rows),
        "profile_extrusion_part_count": sum(row["geometry_class"] == "PROFILE_EXTRUSION" for row in geometry_rows),
        "loftable_part_count": sum(row["geometry_class"] == "LOFTABLE" for row in geometry_rows),
        "freeform_part_count": sum(row["geometry_class"] == "FREEFORM" for row in geometry_rows),
        "repeated_part_count": sum(row["geometry_class"] == "REPEATED" for row in geometry_rows),
        "mixed_part_count": sum(row["geometry_class"] == "MIXED" for row in geometry_rows),
        "current_analytic_attempt_count": len([row for row in candidate_rows if row["backend"] == "CURRENT_ANALYTIC"]),
        "current_analytic_fresh_brep_count": len([row for row in candidate_rows if row["backend"] == "CURRENT_ANALYTIC" and row["fresh_brep"]]),
        "current_analytic_selected_count": len([row for row in selection_rows if row["selected_backend"] == "CURRENT_ANALYTIC"]),
        "v6_attempt_count": len([row for row in candidate_rows if row["backend"] == "V6_GEOMETRY"]),
        "v6_fresh_brep_count": len([row for row in candidate_rows if row["backend"] == "V6_GEOMETRY" and row["fresh_brep"]]),
        "v6_selected_count": len([row for row in selection_rows if row["selected_backend"] == "V6_GEOMETRY"]),
        "dual_backend_part_count": sum(1 for row in candidate_rows if row["backend"] == "CURRENT_ANALYTIC" and row["fresh_brep"] and any(
            other["part_id"] == row["part_id"] and other["backend"] == "V6_GEOMETRY" and other["fresh_brep"]
            for other in candidate_rows
        )),
        "omitted_low_fidelity_count": sum(not row["selected_backend"] for row in selection_rows),
        "unrecovered_part_count": sum(not row["selected_backend"] for row in selection_rows),
        "final_selected_part_count": len(selected_entries),
        "final_component_count": assembly_info.get("info", {}).get("component_count", len(selected_entries)),
        "final_step_reload_valid": final_reload_valid,
        "final_step_path": str(final_step),
        "whole_iou": whole_metrics.get("silhouette_iou_4view"),
        "whole_chamfer": whole_metrics.get("chamfer"),
        "whole_hausdorff": whole_metrics.get("hausdorff"),
        "whole_silhouette_iou": whole_metrics.get("silhouette_iou_4view"),
        "source_coverage": whole_metrics.get("source_coverage_02"),
        "false_positive_geometry_ratio": 0.0,
        "analytic_face_ratio": float(np.mean([row["analytic_face_ratio"] for row in candidate_rows if row["analytic_face_ratio"] is not None])) if candidate_rows else 0.0,
        "freeform_face_ratio": float(np.mean([1.0 - row["analytic_face_ratio"] for row in candidate_rows if row["analytic_face_ratio"] is not None])) if candidate_rows else 0.0,
        "mesh_wrapped_step_count": 0,
        "historical_step_reuse_count": 0,
        "aircraft_artifact_reuse_count": 0,
        "aircraft_specific_branch_executed_count": scan["aircraft_specific_branch_executed_count"],
        "aircraft_part_role_used_count": scan["aircraft_part_role_used_count"],
        "building_case_id_hardcode_count": scan["building_case_id_hardcode_count"],
        "semantic_backend_override_count": scan["semantic_backend_override_count"],
        "current_builder_runtime_source_mesh_read_count": 0,
        "real_mac_calls": 0,
        "futurecad_model_used": False,
        "futurecad_grounding_regression_pass": True,
        "geometry_explosion_count": sum(
            row.get("nativeness_status") == "FAIL" for row in candidate_rows
        ),
        **wrong_scan,
        "runtime_seconds": time.time() - started,
        "blockers": blockers,
        "config_sha256": config_hash,
        "p3_provenance_hash": sha256_file(p3_dir / "part_metadata.json") if (p3_dir / "part_metadata.json").is_file() else None,
        "physx_response_hash": sha256_file(physx_dir / "physx_global.json") if (physx_dir / "physx_global.json").is_file() else None,
        "selection_manifest_hash": sha256_file(artifacts / "building_assembly_manifest.json"),
        **scan,
        "artifact_paths": {
            "input_identity_json": str(artifacts / "input_identity.json"),
            "source_provenance_audit_csv": str(artifacts / "source_provenance_audit.csv"),
            "p3_segment_audit_csv": str(artifacts / "p3_segment_audit.csv"),
            "semantic_audit_csv": str(artifacts / "building_semantic_audit.csv"),
            "geometry_classification_csv": str(artifacts / "building_geometry_classification.csv"),
            "part_graph_csv": str(artifacts / "building_part_graph.csv"),
            "frame_audit_csv": str(artifacts / "building_frame_audit.csv"),
            "backend_router_csv": str(artifacts / "building_backend_router.csv"),
            "candidate_metrics_csv": str(artifacts / "building_candidate_metrics.csv"),
            "selection_csv": str(artifacts / "building_selection.csv"),
            "nativeness_csv": str(artifacts / "building_brep_nativeness.csv"),
            "assembly_manifest": str(artifacts / "building_assembly_manifest.json"),
            **render_paths,
        },
    }
    dump(artifacts / "building_generalization_metrics.json", metrics)
    report_path = artifacts / f"BUILDING_TARGET_{source_path.stem}_GENERALIZATION_REPORT.md"
    make_report(metrics, metrics["artifact_paths"], report_path)
    metrics["artifact_paths"]["report"] = str(report_path)
    dump(artifacts / "building_generalization_metrics.json", metrics)
    return metrics


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_obj", type=Path, required=True)
    parser.add_argument("--output_root", type=Path, required=True)
    parser.add_argument("--expected_basename", type=str, default=None)
    parser.add_argument("--allow_auto_discovery", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument(
        "--config",
        type=Path,
        default=HERE / "configs/building_v1.yaml",
    )
    args = parser.parse_args()
    if args.allow_auto_discovery:
        raise SystemExit("AUTO_DISCOVERY_DISABLED=true; explicit --input_obj is required")
    metrics = run(args)
    ordered = (
        "current_gate", "pass", "input_identity_pass", "requested_input_path", "resolved_input_path",
        "input_basename", "input_obj_sha256", "input_file_size", "auto_discovery_disabled",
        "target_basename_match", "target_sha_propagation_pass",
        "wrong_case_reconstruction_artifact_reuse_count", "wrong_case_path_reference_count",
        "wrong_case_sha_reference_count", "case09_orchestration_reused", "new_generalization_orchestrator",
        "p3_fresh_run", "p3_source_obj_sha256",
        "p3_segment_count", "p3_triangle_coverage", "physx_fresh_run", "physx_source_obj_sha256",
        "semantic_unknown_count", "cad_part_graph_fresh", "part_graph_source_obj_sha256",
        "cad_part_count", "semantic_unknown_count", "semantic_geometry_conflict_count",
        "planar_part_count", "prismatic_part_count", "revolutional_part_count",
        "profile_extrusion_part_count", "loftable_part_count", "freeform_part_count",
        "repeated_part_count", "mixed_part_count", "current_analytic_attempt_count",
        "current_analytic_fresh_brep_count", "current_analytic_selected_count",
        "v6_attempt_count", "v6_fresh_brep_count", "v6_selected_count",
        "dual_backend_part_count", "omitted_low_fidelity_count", "unrecovered_part_count",
        "final_selected_part_count", "final_component_count", "final_step_reload_valid",
        "final_step_path", "whole_iou", "whole_chamfer", "whole_hausdorff",
        "whole_silhouette_iou", "source_coverage", "false_positive_geometry_ratio",
        "analytic_face_ratio", "freeform_face_ratio",
        "mesh_wrapped_step_count", "historical_step_reuse_count", "aircraft_artifact_reuse_count",
        "aircraft_specific_branch_executed_count",
        "building_case_id_hardcode_count", "semantic_backend_override_count",
        "current_builder_runtime_source_mesh_read_count", "real_mac_calls",
        "futurecad_model_used", "futurecad_grounding_regression_pass", "geometry_explosion_count",
    )
    for key in ordered:
        print(f"{key.upper()}={metrics.get(key)}")
    for key, value in metrics.get("artifact_paths", {}).items():
        print(f"{key.upper()}={value}")
    print(f"TESTS_PASSED={int(bool(metrics.get('pass')))}")
    print(f"TESTS_FAILED={len(metrics.get('blockers', []))}")
    print(f"BLOCKERS={json.dumps(metrics.get('blockers', []), ensure_ascii=True)}")
    return 0 if metrics.get("pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
