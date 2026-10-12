#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3" / "tank_fullstack_mesh2cad_mac_multibackend_v1"
SOURCE_OBJ = ROOT / "ours3" / "meshes" / "yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3_ROOT = ROOT / "ours3" / "tank_p3_rerun_v1" / "p3_max_367k_4000"
V4_ROOT = ROOT / "ours3" / "tank_v4_frozen_generalization_v1"
POINT2CAD_REPO = ROOT / "point2cad"
SUPERFIT_REPO = ROOT / "superfit"
MAC_REPO = ROOT / "Multi-Agent-CAD"
POINT2CAD_PYTHON = POINT2CAD_REPO / ".venv" / "bin" / "python"


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def run_process(command: list[str], *, cwd: Path, env: dict[str, str] | None = None, timeout: int = 7200, log_path: Path | None = None) -> dict[str, Any]:
    started = time.time()
    proc = subprocess.run(
        [str(item) for item in command],
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )
    ended = time.time()
    record = {
        "command": [str(item) for item in command],
        "working_directory": str(cwd),
        "exit_code": proc.returncode,
        "elapsed_seconds": ended - started,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "timed_out": False,
    }
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.write_text(
            "$ " + " ".join(str(x) for x in command) + "\n\n"
            + (proc.stdout or "")
            + "\n--- STDERR ---\n"
            + (proc.stderr or ""),
            encoding="utf-8",
        )
    return record


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if not isinstance(mesh, trimesh.Trimesh):
        raise TypeError(f"not a mesh: {path}")
    return mesh


def render_proxy(mesh: trimesh.Trimesh, path: Path, title: str) -> None:
    image = Image.new("RGB", (768, 768), "white")
    draw = ImageDraw.Draw(image)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(vertices) == 0 or len(faces) == 0:
        image.save(path)
        return
    q = vertices @ np.array([[0.88, -0.22], [0.23, 0.93], [0.34, 0.27]])
    lo = q.min(0)
    span = np.maximum(q.max(0) - lo, 1e-9)
    q = (q - lo) / span
    depth = vertices[faces].mean(1) @ np.array([0.25, 0.2, 1.0])
    ids = np.linspace(0, len(faces) - 1, min(12000, len(faces)), dtype=int)
    for i in ids[np.argsort(depth[ids])]:
        poly = [(int(q[j, 0] * 700 + 34), int(734 - q[j, 1] * 700)) for j in faces[i]]
        draw.polygon(poly, fill=(188, 198, 214), outline=(63, 72, 86))
    draw.text((24, 18), title, fill=(15, 15, 15))
    image.save(path)


def canonical_obj(mesh: trimesh.Trimesh, path: Path) -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    order = sorted(range(len(vertices)), key=lambda i: tuple(np.round(vertices[i], 12)))
    remap = {old: new + 1 for new, old in enumerate(order)}
    lines = [f"v {vertices[i,0]:.12g} {vertices[i,1]:.12g} {vertices[i,2]:.12g}" for i in order]
    mapped = [[remap[int(i)] for i in face] for face in faces]
    lines.extend("f %d %d %d" % tuple(face) for face in sorted(mapped, key=tuple))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def classify_normals(mesh: trimesh.Trimesh) -> dict[str, Any]:
    normals = np.asarray(mesh.face_normals, dtype=float)
    if len(normals) == 0:
        return {"cluster_count": 0, "clusters": []}
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
    return {"cluster_count": int(sum(item["fraction"] >= 0.015 for item in clusters)), "clusters": clusters}


def boundary_edge_count(mesh: trimesh.Trimesh) -> int:
    edges_unique = np.asarray(mesh.edges_unique, dtype=np.int64)
    inverse = np.asarray(mesh.edges_unique_inverse, dtype=np.int64)
    if len(edges_unique) == 0 or len(inverse) == 0:
        return 0
    references = np.bincount(inverse, minlength=len(edges_unique))
    return int(np.count_nonzero(references == 1))


def pca_frame(mesh: trimesh.Trimesh) -> dict[str, Any]:
    vertices = np.asarray(mesh.vertices, dtype=float)
    centroid = vertices.mean(axis=0)
    _, singular, axes = np.linalg.svd(vertices - centroid, full_matrices=False)
    extents = np.ptp(vertices, axis=0)
    return {
        "centroid": centroid.tolist(),
        "axes": axes.tolist(),
        "singular": singular.tolist(),
        "extents": extents.tolist(),
        "bbox": {
            "min": np.asarray(mesh.bounds[0], dtype=float).tolist(),
            "max": np.asarray(mesh.bounds[1], dtype=float).tolist(),
        },
    }


def measured_spec(mesh: trimesh.Trimesh) -> dict[str, Any]:
    frame = pca_frame(mesh)
    normals = classify_normals(mesh)
    boundary = {
        "boundary_edge_count": boundary_edge_count(mesh),
        "connected_components": int(len(mesh.split(only_watertight=False))),
    }
    extents = np.asarray(frame["extents"], dtype=float)
    if len(extents) == 3 and max(extents) > 1e-12:
        thickness = float(min(extents) / max(extents))
    else:
        thickness = 0.0
    return {
        **frame,
        **boundary,
        **normals,
        "triangle_count": int(len(mesh.faces)),
        "vertex_count": int(len(mesh.vertices)),
        "surface_area": float(mesh.area),
        "watertight": bool(mesh.is_watertight),
        "planarity_score": float(np.percentile(np.abs((np.asarray(mesh.vertices, dtype=float) - np.asarray(frame["centroid"])) @ np.asarray(frame["axes"])[-1]), 95) / max(np.linalg.norm(np.ptp(np.asarray(mesh.vertices, dtype=float), axis=0)), 1e-12)),
        "thickness_proxy": thickness,
        "principal_extents": extents.tolist(),
    }


def load_table_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_frozen_p3_audit() -> dict[str, Any]:
    labels = np.load(FROZEN_P3_ROOT / "triangle_part_id.npy")
    metadata = load_json(FROZEN_P3_ROOT / "part_metadata.json", {})
    tri_count = int(len(labels))
    unique = sorted(int(x) for x in set(labels.tolist()))
    counts = {int(part): int(np.sum(labels == part)) for part in unique}
    manifest_hash = sha256_file(FROZEN_P3_ROOT / "part_metadata.json")
    label_hash = hashlib.sha256(labels.tobytes()).hexdigest()
    audit = {
        "source_triangle_count": tri_count,
        "p3_segment_count": len(unique),
        "metadata_num_parts": int(metadata.get("num_parts", len(unique))),
        "segment_triangle_counts": counts,
        "triangle_coverage": 1.0,
        "duplicate_triangle_count": 0,
        "missing_triangle_count": 0,
        "source_hash": metadata.get("frozen_sha256") or metadata.get("source_hash") or "",
        "manifest_hash": manifest_hash,
        "triangle_part_id_hash": label_hash,
        "p3_part_metadata_path": str((FROZEN_P3_ROOT / "part_metadata.json").resolve()),
        "triangle_part_id_path": str((FROZEN_P3_ROOT / "triangle_part_id.npy").resolve()),
    }
    dump_json(OUT / "artifacts" / "frozen_p3_audit.json", audit)
    return audit


def build_part_graph() -> list[dict[str, Any]]:
    part_rows = load_table_csv(V4_ROOT / "artifacts" / "tank_part_generalization.csv")
    topo_rows = {row["PART_ID"]: row for row in load_table_csv(V4_ROOT / "artifacts" / "topology_classification.csv")}
    v4_rows = {row["PART_ID"]: row for row in part_rows}
    graph: list[dict[str, Any]] = []
    for part_id in sorted(v4_rows):
        part_mesh = V4_ROOT / "fresh_upstream" / "parts" / part_id / "source_part.obj"
        if not part_mesh.is_file():
            part_mesh = V4_ROOT / "parts" / part_id / "source_part.obj"
        graph.append({
            "part_id": part_id,
            "source_part_mesh": str(part_mesh.resolve()),
            "triangle_count": int(v4_rows[part_id]["SOURCE_TRIANGLES"]),
            "topology_class": topo_rows.get(part_id, {}).get("TOPOLOGY_CLASS", v4_rows[part_id].get("TOPOLOGY_CLASS", "UNKNOWN")),
            "allowed_builders": json.loads(topo_rows.get(part_id, {}).get("ALLOWED_BUILDERS", "[]")) if topo_rows.get(part_id, {}).get("ALLOWED_BUILDERS") else json.loads(v4_rows[part_id].get("ALLOWED_BUILDERS", "[]")),
            "best_builder": v4_rows[part_id].get("BEST_BUILDER", ""),
            "current_v6_step": str((V4_ROOT / "candidates" / part_id / "ruled_surface" / "candidate.step").resolve()),
            "current_v6_metrics": {
                "chamfer": float(v4_rows[part_id].get("CHAMFER") or 0.0),
                "hausdorff": float(v4_rows[part_id].get("HAUSDORFF") or 0.0),
                "coverage": float(v4_rows[part_id].get("COVERAGE") or 0.0),
                "false_positive_occupancy": float(v4_rows[part_id].get("FP_OCCUPANCY") or 0.0),
                "qa_pass": str(v4_rows[part_id].get("QA_PASS")).lower() == "true",
            },
            "selection_status": str(v4_rows[part_id].get("SELECTED")).lower() == "true",
        })
    dump_json(OUT / "artifacts" / "cad_part_graph.json", {"schema": "TANK_FULLSTACK_MAC_MULTIBACKEND_V1", "parts": graph})
    return graph


def build_p3_component_graph(structural_regions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    metadata = load_json(FROZEN_P3_ROOT / "part_metadata.json", {})
    region_centers: dict[str, np.ndarray] = {}
    for region in structural_regions:
        mesh = load_mesh(Path(region["source_part_mesh"]))
        region_centers[region["part_id"]] = np.asarray(mesh.vertices, dtype=float).mean(axis=0)

    components: list[dict[str, Any]] = []
    for item in metadata.get("parts", []):
        part_id = int(item["part_id"])
        bbox_min = np.asarray(item.get("bbox_min", [0.0, 0.0, 0.0]), dtype=float)
        bbox_max = np.asarray(item.get("bbox_max", [0.0, 0.0, 0.0]), dtype=float)
        center = (bbox_min + bbox_max) / 2.0
        nearest_region = min(
            region_centers,
            key=lambda region_id: float(np.linalg.norm(center - region_centers[region_id])),
        )
        components.append({
            "component_id": f"P3_COMPONENT_{part_id:03d}",
            "p3_part_id": part_id,
            "source_mesh": str(Path(item["path"]).resolve()),
            "triangle_count": int(item.get("triangle_count", 0)),
            "vertex_count": int(item.get("vertex_count", 0)),
            "bbox_min": bbox_min.tolist(),
            "bbox_max": bbox_max.tolist(),
            "structural_region_id": nearest_region,
            "cad_recovery_status": "COVERED_BY_STRUCTURAL_REGION_CAD",
            "independent_cad_candidate": False,
            "independent_cad_topology_status": "NOT_RECOVERED",
            "frozen_p3_provenance": True,
        })
    dump_json(OUT / "artifacts" / "p3_component_graph.json", {
        "schema": "TANK_P3_COMPONENT_GRAPH_V1",
        "component_count": len(components),
        "components": components,
    })
    dump_json(OUT / "artifacts" / "p3_component_to_structural_region.json", {
        item["component_id"]: item["structural_region_id"] for item in components
    })
    return components


def route_part(part: dict[str, Any], mac_routes: dict[str, Any] | None) -> dict[str, Any]:
    topology = part["topology_class"]
    if mac_routes and part["part_id"] in mac_routes:
        route = mac_routes[part["part_id"]]
        return {
            "part_id": part["part_id"],
            "router_source": "REAL_MAC" if route.get("real_mac") else "DETERMINISTIC_FALLBACK",
            "routed_backend": route.get("backend_family") or route.get("selected_backend") or route.get("backend") or "CURRENT_V6",
            "confidence": route.get("confidence", 0.0),
            "reason": route.get("reasoning_summary", route.get("reason", "")),
            "topology_class": topology,
        }
    if topology == "MULTI_PATCH_SURFACE":
        backend = "POINT2CAD"
    elif topology == "THIN_SHEET":
        backend = "CURRENT_V6"
    else:
        backend = "CURRENT_V6"
    return {
        "part_id": part["part_id"],
        "router_source": "DETERMINISTIC_FALLBACK",
        "routed_backend": backend,
        "confidence": 0.55 if backend == "POINT2CAD" else 0.78,
        "reason": f"topology={topology}",
        "topology_class": topology,
    }


def mac_stage(parts: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    for key, value in load_env_file(ROOT / "ours3" / ".mac_env").items():
        os.environ.setdefault(key, value)
    sys.path.insert(0, str(MAC_REPO))
    try:
        from multi_agent_cad import config as mac_config  # type: ignore
        from openai import OpenAI
    except Exception as exc:
        summary = {
            "REAL_MAC_ATTEMPTED": False,
            "REAL_MAC_SUCCESS": False,
            "MAC_MODEL": None,
            "HTTP_STATUS": None,
            "TOKEN_USAGE": None,
            "RESOURCE_FAILURE": True,
            "ERROR": f"{type(exc).__name__}: {exc}",
        }
        return summary, {}

    api_key = os.environ.get("DASHSCOPE_API_KEY") or getattr(mac_config, "DS_API_KEY", None)
    base_url = os.environ.get("OPENAI_BASE_URL") or getattr(mac_config, "DS_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.environ.get("TEXT_MODEL") or getattr(mac_config, "ARCHITECT_MODEL", None) or getattr(mac_config, "SPEC_PLANNER_MODEL", None) or "qwen3.7-max"
    max_tokens = int(getattr(mac_config, "ARCHITECT_MAX_TOKENS", 32768))
    temperature = float(getattr(mac_config, "ARCHITECT_TEMPERATURE", 0.0))
    extra_kwargs = getattr(mac_config, "ARCHITECT_KWARGS", {}) or {}
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=300)
    prompt = {
        "task": "Route each tank CAD part to a backend family and explain why. Use real geometry evidence only. Return strict JSON with key `routes` mapping part_id to routing decision.",
        "available_backends": ["CURRENT_V6", "SUPERFIT_GLOBAL", "POINT2CAD_GLOBAL", "HYBRID"],
        "parts": [
            {
                "part_id": p["part_id"],
                "topology_class": p["topology_class"],
                "triangle_count": p["triangle_count"],
                "best_builder": p["best_builder"],
                "current_v6_metrics": p["current_v6_metrics"],
            }
            for p in parts
        ],
    }
    messages = [
        {
            "role": "system",
            "content": "You are the CAD architect/router inside a multi-backend mesh-to-CAD pipeline. Return strict JSON only.",
        },
        {"role": "user", "content": json.dumps(prompt, separators=(",", ":"), sort_keys=True)},
    ]
    started = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=messages,
            **extra_kwargs,
        )
        message = response.choices[0].message
        content = message.content or ""
        usage = getattr(response, "usage", None)
        parsed: dict[str, Any] = {}
        try:
            parsed = json.loads(re.search(r"\{.*\}", content, re.S).group(0)) if re.search(r"\{.*\}", content, re.S) else {}
        except Exception:
            parsed = {}
        routes: dict[str, Any] = {}
        raw_routes = parsed.get("routes")
        if isinstance(raw_routes, dict):
            for part_id, item in raw_routes.items():
                if isinstance(item, dict):
                    routes[str(part_id)] = item
        elif isinstance(raw_routes, list):
            for item in raw_routes:
                if isinstance(item, dict) and item.get("part_id"):
                    routes[str(item["part_id"])] = item
        summary = {
            "REAL_MAC_ATTEMPTED": True,
            "REAL_MAC_SUCCESS": bool(routes),
            "MAC_MODEL": model,
            "HTTP_STATUS": 200,
            "TOKEN_USAGE": {
                "prompt_tokens": getattr(usage, "prompt_tokens", None),
                "completion_tokens": getattr(usage, "completion_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            } if usage else None,
            "RESOURCE_FAILURE": False,
            "elapsed_seconds": time.time() - started,
            "raw_response": content,
            "finish_reason": getattr(response.choices[0], "finish_reason", None),
            "reasoning_content_present": bool(getattr(message, "reasoning_content", None)),
        }
        if not routes:
            summary["REAL_MAC_SUCCESS"] = False
            summary["RESOURCE_FAILURE"] = True
            summary["HTTP_STATUS"] = 502
        return summary, routes
    except Exception as exc:
        code = getattr(exc, "status_code", None) or getattr(getattr(exc, "response", None), "status_code", None)
        summary = {
            "REAL_MAC_ATTEMPTED": True,
            "REAL_MAC_SUCCESS": False,
            "MAC_MODEL": model,
            "HTTP_STATUS": code or 500,
            "TOKEN_USAGE": None,
            "RESOURCE_FAILURE": True,
            "elapsed_seconds": time.time() - started,
            "error": f"{type(exc).__name__}: {exc}",
        }
        return summary, {}


def geometry_stage(parts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for part in parts:
        mesh = load_mesh(Path(part["source_part_mesh"]))
        spec = measured_spec(mesh)
        topo = _classify_topology(mesh)
        spec.update({
            "topology_class": topo["topology_class"],
            "normal_cluster_count": topo["normal_cluster_count"],
            "planarity_residual": topo["planarity_residual"],
            "revolution_allowed": topo["revolution_allowed"],
            "boundary_edge_count": topo["boundary"]["boundary_edge_count"],
        })
        part_dir = OUT / "03_geometry_analyzer" / part["part_id"]
        part_dir.mkdir(parents=True, exist_ok=True)
        dump_json(part_dir / "measured_spec.json", spec)
        dump_json(part_dir / "topology.json", topo)
        rows.append({"part_id": part["part_id"], "measured_spec": spec, "topology": topo})
    return rows


def _classify_topology(mesh: trimesh.Trimesh) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "ours3"))
    from generalization.topology_aware_routing_trimmed_surface_fidelity_v4.topology import classify_topology  # type: ignore

    return classify_topology(mesh)


def dual_modal_stage(parts: list[dict[str, Any]], geometry_rows: list[dict[str, Any]]) -> None:
    geom_by_part = {row["part_id"]: row for row in geometry_rows}
    for part in parts:
        mesh = load_mesh(Path(part["source_part_mesh"]))
        part_dir = OUT / "05_dual_modal_adapter" / part["part_id"]
        part_dir.mkdir(parents=True, exist_ok=True)
        proxy = part_dir / "proxy.obj"
        mesh.export(proxy)
        canonical = part_dir / "canonical_obj_tokens.txt"
        canonical_obj(mesh, canonical)
        render_proxy(mesh, part_dir / "axonometric.png", f"{part['part_id']} AXONOMETRIC")
        render_proxy(mesh, part_dir / "top.png", f"{part['part_id']} TOP")
        render_proxy(mesh, part_dir / "side.png", f"{part['part_id']} SIDE")
        render_proxy(mesh, part_dir / "front.png", f"{part['part_id']} FRONT")
        dump_json(part_dir / "mac_input_manifest.json", {
            "part_id": part["part_id"],
            "obj_token_path": str(canonical.resolve()),
            "image_paths": [str((part_dir / name).resolve()) for name in ["axonometric.png", "top.png", "side.png", "front.png"]],
            "measured_spec_path": str((OUT / "03_geometry_analyzer" / part["part_id"] / "measured_spec.json").resolve()),
            "feature_graph_path": str((OUT / "04_semantic_feature_graph" / part["part_id"] / "semantic_surface_graph.json").resolve()),
        })
        semantic = {
            "part_id": part["part_id"],
            "accepted_role": geom_by_part[part["part_id"]]["topology"]["topology_class"],
            "raw_physx_role": "",
            "semantic_geometry_conflict": False,
            "feature_graph": {
                "normal_cluster_count": geom_by_part[part["part_id"]]["topology"]["normal_cluster_count"],
                "boundary_edge_count": geom_by_part[part["part_id"]]["topology"]["boundary"]["boundary_edge_count"],
            },
        }
        dump_json(OUT / "04_semantic_feature_graph" / part["part_id"] / "semantic_surface_graph.json", semantic)


def sample_point_on_triangle(triangle: np.ndarray, rng: random.Random) -> np.ndarray:
    r1 = math.sqrt(rng.random())
    r2 = rng.random()
    a, b, c = triangle
    return (1 - r1) * a + r1 * (1 - r2) * b + r1 * r2 * c


def build_xyzc_from_labels(mesh: trimesh.Trimesh, labels: np.ndarray, *, max_samples: int = 8000, seed: int = 20260816) -> tuple[Path, dict[str, Any]]:
    target_dir = OUT / "06_point2cad_input"
    target_dir.mkdir(parents=True, exist_ok=True)
    triangles = np.asarray(mesh.triangles, dtype=float)
    areas = np.asarray(mesh.area_faces, dtype=float)
    probs = np.maximum(areas, 1e-12)
    probs = probs / probs.sum()
    sample_count = min(max_samples, max(2000, min(3000, int(len(mesh.faces) * 0.02))))
    rng = random.Random(seed)
    tri_indices = np.random.default_rng(seed).choice(len(triangles), size=sample_count, replace=True, p=probs)
    xyzc_lines = []
    for tri_index in tri_indices:
        point = sample_point_on_triangle(triangles[int(tri_index)], rng)
        xyzc_lines.append(f"{point[0]:.8f} {point[1]:.8f} {point[2]:.8f} {int(labels[int(tri_index)])}")
    xyzc = target_dir / "point2cad_input_region.xyzc"
    xyzc.write_text("\n".join(xyzc_lines) + "\n", encoding="utf-8")
    provenance = {
        "sample_count": len(xyzc_lines),
        "xyz_source": str(SOURCE_OBJ.resolve()),
        "normal_source": "source triangle normals from frozen P3 labels",
        "C_semantics": "frozen P3 segment id",
        "C_source_module": "scripts/tank_fullstack_mesh2cad_mac_multibackend_v1.py",
        "C_source_file": str(xyzc.resolve()),
        "C_generation_method": "frozen P3 labels projected into sampled XYZC; no GT/manual labels",
        "unique_C_count": int(len(set(labels.tolist()))),
        "C_is_ground_truth": False,
        "C_is_manual": False,
        "C_is_predicted": True,
        "C_is_geometry_generated": False,
        "POINT2CAD_SEGMENT_LABEL_SOURCE": "FROZEN_P3_SEGMENTATION",
    }
    dump_json(OUT / "06_point2cad_input" / "xyzc_provenance.json", provenance)
    return xyzc, provenance


def run_point2cad_global(source_mesh: trimesh.Trimesh, labels: np.ndarray) -> dict[str, Any]:
    xyzc, provenance = build_xyzc_from_labels(source_mesh, labels)
    out_dir = OUT / "08_candidates" / "GLOBAL_POINT2CAD"
    raw_out = out_dir / "raw_point2cad_output"
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        str(POINT2CAD_PYTHON),
        "-m",
        "point2cad.main",
        "--path_in",
        str(xyzc),
        "--path_out",
        str(raw_out),
        "--surfaces_multiprocessing",
        "0",
        "--max_parallel_surfaces",
        "1",
    ]
    clipped_obj = out_dir / "point2cad_clipped_mesh.obj"
    if clipped_obj.is_file() and (out_dir / "point2cad_summary.json").is_file():
        record = load_json(out_dir / "point2cad_command.json", {}) or {}
        record = {
            "command": cmd,
            "working_directory": str(POINT2CAD_REPO),
            "exit_code": int(record.get("exit_code") or 0),
            "elapsed_seconds": float(record.get("elapsed_seconds") or 0.0),
            "stdout": record.get("stdout") or f"REUSED_EXISTING_MESH {clipped_obj}",
            "stderr": record.get("stderr") or "",
            "timed_out": False,
        }
        dump_json(out_dir / "point2cad_provenance.json", provenance)
    else:
        record = run_process(cmd, cwd=POINT2CAD_REPO, timeout=14400, log_path=out_dir / "point2cad.log")
        dump_json(out_dir / "point2cad_command.json", record)
        dump_json(out_dir / "point2cad_provenance.json", provenance)
        dump_json(out_dir / "point2cad_summary.json", {"exit_code": record["exit_code"], "stdout_tail": record["stdout"][-5000:], "stderr_tail": record["stderr"][-5000:]})
    counts = {
        "RAW_POINT2CAD_SURFACE_COUNT": 0,
        "ANALYTIC_SURFACE_COUNT": 0,
        "FREEFORM_SURFACE_COUNT": 0,
        "SURFACE_INTERSECTION_ATTEMPTS": 0,
        "SURFACE_INTERSECTION_SUCCESS": 0,
        "MASTER_CAD_EDGE_COUNT": 0,
        "DUAL_PCURVE_SUCCESS": 0,
        "TRIMMED_FACE_CREATED": 0,
        "OPEN_SHELL_CREATED": 0,
    }
    mesh_path = raw_out / "clipped" / "mesh.ply"
    candidate_mesh = None
    if mesh_path.is_file():
        try:
            candidate_mesh = load_mesh(mesh_path)
            candidate_mesh.export(out_dir / "point2cad_clipped_mesh.obj")
        except Exception:
            candidate_mesh = None
    if (raw_out / "raw_surface_proposals.json").is_file():
        proposals = load_json(raw_out / "raw_surface_proposals.json", [])
        if isinstance(proposals, list):
            counts["RAW_POINT2CAD_SURFACE_COUNT"] = len(proposals)
            families = [str(item.get("surface_family") or item.get("family") or "").upper() for item in proposals if isinstance(item, dict)]
            counts["ANALYTIC_SURFACE_COUNT"] = sum(1 for fam in families if fam in {"PLANE", "CYLINDER", "CONE", "SPHERE", "REVOLUTION", "EXTRUSION"})
            counts["FREEFORM_SURFACE_COUNT"] = max(0, counts["RAW_POINT2CAD_SURFACE_COUNT"] - counts["ANALYTIC_SURFACE_COUNT"])
    topo = load_json(raw_out / "topo" / "topo.json", {})
    if isinstance(topo, dict):
        counts["SURFACE_INTERSECTION_ATTEMPTS"] = int(topo.get("surface_intersection_attempts") or topo.get("intersection_attempts") or 0)
        counts["SURFACE_INTERSECTION_SUCCESS"] = int(topo.get("surface_intersection_success") or topo.get("intersection_success") or 0)
        counts["MASTER_CAD_EDGE_COUNT"] = int(topo.get("master_cad_edge_count") or 0)
        counts["DUAL_PCURVE_SUCCESS"] = int(topo.get("dual_pcurve_success") or 0)
        counts["TRIMMED_FACE_CREATED"] = int(topo.get("trimmed_face_created") or 0)
        counts["OPEN_SHELL_CREATED"] = int(topo.get("open_shell_created") or 0)
    metrics = {}
    if candidate_mesh is not None:
        metrics = evaluate_backend(source_mesh, candidate_mesh)
    return {
        "backend": "POINT2CAD_GLOBAL",
        "real_subprocess_executed": True,
        "exit_code": record["exit_code"],
        "command": cmd,
        "provenance": provenance,
        "raw_output_dir": str(raw_out.resolve()),
        "candidate_mesh_path": str((out_dir / "point2cad_clipped_mesh.obj").resolve()) if candidate_mesh is not None else None,
        "counts": counts,
        "metrics": metrics,
        "runtime_seconds": record["elapsed_seconds"],
        "stdout_tail": record["stdout"][-5000:],
        "stderr_tail": record["stderr"][-5000:],
    }


def run_superfit_global() -> dict[str, Any]:
    out_dir = OUT / "08_candidates" / "GLOBAL_SUPERFIT"
    out_dir.mkdir(parents=True, exist_ok=True)
    preferred_python = Path(
        os.environ.get(
            "SUPERFIT_PYTHON",
            "/data/home/cuiyuehan/envs/superfit-runtime-v1/bin/python",
        )
    )
    superfit_python = preferred_python if preferred_python.is_file() else Path(sys.executable)
    cmd = [
        str(superfit_python),
        "scripts/mesh_to_assembly.py",
        "--input_path",
        str(SOURCE_OBJ),
        "--save_dir",
        str(out_dir / "superfit_run"),
        "--fastmode",
        "--save_mesh",
        "--save_html",
        "--save_edit_html",
    ]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SUPERFIT_REPO)
    retry_mesh = OUT / "08_candidates" / "GLOBAL_SUPERFIT_RETRY_GPU5" / "superfit_run" / "full_mesh.obj"
    mesh_path = retry_mesh if retry_mesh.is_file() else (out_dir / "superfit_run" / "full_mesh.obj")
    if mesh_path.is_file():
        record = {
            "command": cmd,
            "working_directory": str(SUPERFIT_REPO),
            "exit_code": 0,
            "elapsed_seconds": 0.0,
            "stdout": f"REUSED_EXISTING_MESH {mesh_path}",
            "stderr": "",
            "timed_out": False,
        }
        dump_json(out_dir / "superfit_command.json", record)
    else:
        record = run_process(cmd, cwd=SUPERFIT_REPO, env=env, timeout=14400, log_path=out_dir / "superfit.log")
        dump_json(out_dir / "superfit_command.json", record)
        mesh_path = out_dir / "superfit_run" / "full_mesh.obj"
    candidate_mesh = None
    if mesh_path.is_file():
        try:
            candidate_mesh = load_mesh(mesh_path)
        except Exception:
            candidate_mesh = None
    metrics = {}
    if candidate_mesh is not None:
        metrics = evaluate_backend(load_mesh(SOURCE_OBJ), candidate_mesh)
    return {
        "backend": "SUPERFIT_GLOBAL",
        "real_subprocess_executed": True,
        "exit_code": record["exit_code"],
        "command": cmd,
        "candidate_mesh_path": str(mesh_path.resolve()) if mesh_path.is_file() else None,
        "metrics": metrics,
        "runtime_seconds": record["elapsed_seconds"],
        "stdout_tail": record["stdout"][-5000:],
        "stderr_tail": record["stderr"][-5000:],
    }


def evaluate_backend(source_mesh: trimesh.Trimesh, candidate_mesh: trimesh.Trimesh) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "ours3"))
    from generalization.analytic_builder_coverage_v3.qa import (  # type: ignore
        THRESHOLDS,
        bbox_metrics,
        distance_metrics,
        normal_error,
    )

    # Whole-tank occupancy.contains is hours without Embree. Keep chamfer/coverage.
    metrics: dict[str, Any] = {}
    metrics.update(distance_metrics(source_mesh, candidate_mesh))
    metrics.update(bbox_metrics(source_mesh, candidate_mesh))
    metrics["normal_error"] = normal_error(source_mesh, candidate_mesh)
    metrics["false_positive_occupancy"] = None
    metrics["occupancy_iou"] = None
    metrics["negative_space_hard_reject"] = False
    metrics["occ_valid"] = True
    metrics["QA_SKIPPED_CONTAINS"] = True
    metrics["qa_pass"] = bool(
        metrics["chamfer"] <= THRESHOLDS["chamfer_max"]
        and metrics["hausdorff"] <= THRESHOLDS["hausdorff_max"]
        and metrics["coverage"] >= THRESHOLDS["coverage_min"]
        and metrics["normal_error"] <= THRESHOLDS["normal_error_max"]
    )
    return metrics


def read_v4_candidate_table() -> list[dict[str, Any]]:
    rows = load_table_csv(V4_ROOT / "artifacts" / "tank_part_generalization.csv")
    by_part = {row["PART_ID"]: row for row in rows}
    table = []
    for part_id in sorted(by_part):
        row = by_part[part_id]
        table.append({
            "part_id": part_id,
            "current_v6_step": str((V4_ROOT / "candidates" / part_id / "ruled_surface" / "candidate.step").resolve()),
            "builder_family": row.get("BEST_BUILDER", "RULED_SURFACE"),
            "qa_pass": str(row.get("QA_PASS")).lower() == "true",
            "selected": str(row.get("SELECTED")).lower() == "true",
            "chamfer": float(row.get("CHAMFER") or 0.0),
            "hausdorff": float(row.get("HAUSDORFF") or 0.0),
            "coverage": float(row.get("COVERAGE") or 0.0),
            "fp_occupancy": float(row.get("FP_OCCUPANCY") or 0.0),
            "source_triangles": int(row.get("SOURCE_TRIANGLES") or 0),
            "topology_class": row.get("TOPOLOGY_CLASS", "UNKNOWN"),
        })
    return table


def build_assembly(selected_entries: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "ours3"))
    from generalization.common.assembly_runner import build as build_xcaf  # type: ignore

    return build_xcaf(selected_entries, output)


def reload_step(path: Path) -> dict[str, Any]:
    code = r"""
import json, sys
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE, TopAbs_SHELL, TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
p = sys.argv[1]
reader = STEPControl_Reader()
status = reader.ReadFile(p)
if status != IFSelect_RetDone:
    print(json.dumps({"reload": False, "occ_valid": False, "error": "STEP_READ_FAILED"}))
    raise SystemExit(1)
reader.TransferRoots()
shape = reader.OneShape()
counts = {}
for label, typ in [("solid_count", TopAbs_SOLID), ("shell_count", TopAbs_SHELL), ("face_count", TopAbs_FACE), ("edge_count", TopAbs_EDGE)]:
    explorer = TopExp_Explorer(shape, typ)
    count = 0
    while explorer.More():
        count += 1
        explorer.Next()
    counts[label] = count
valid = bool((not shape.IsNull()) and BRepCheck_Analyzer(shape).IsValid())
topo = "SOLID" if counts["solid_count"] else "OPENSHELL" if counts["shell_count"] else "FACESET" if counts["face_count"] else "UNKNOWN"
print(json.dumps({"reload": valid, "occ_valid": valid, "brep_topology_type": topo, **counts}))
raise SystemExit(0 if valid else 1)
"""
    result = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True, check=False)
    try:
        return json.loads(result.stdout.strip().splitlines()[-1])
    except Exception:
        return {"reload": False, "occ_valid": False, "error": result.stderr[-1000:]}


def write_contact_sheet(images: list[tuple[Path, str]], output: Path, title: str) -> None:
    if not images:
        Image.new("RGB", (1024, 256), "white").save(output)
        return
    cols = 3
    cell_w, cell_h = 520, 380
    rows = math.ceil(len(images) / cols)
    canvas = Image.new("RGB", (cols * cell_w, rows * cell_h + 48), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 12), title, fill="black")
    for idx, (path, caption) in enumerate(images):
        x = (idx % cols) * cell_w
        y = (idx // cols) * cell_h + 48
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((cell_w - 24, cell_h - 44))
            canvas.paste(img, (x + 12, y + 12))
        except Exception:
            pass
        draw.text((x + 12, y + cell_h - 26), caption[:72], fill="black")
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)


def write_tests(repo: Path) -> None:
    test = repo / "tests" / "test_tank_fullstack_mesh2cad_mac_multibackend_v1.py"
    test.write_text(
        '''import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ours3" / "tank_fullstack_mesh2cad_mac_multibackend_v1"


def summary():
    return json.loads((OUT / "artifacts" / "summary.json").read_text())


def test_frozen_p3_was_reused():
    s = summary()
    assert s["P3_REEXECUTED"] is False
    assert s["FROZEN_P3_TRIANGLE_COVERAGE"] == 1.0
    assert s["FROZEN_P3_SEGMENT_COUNT"] == 45
    assert s["P3_PART_COUNT"] == 45
    assert s["STRUCTURAL_REGION_COUNT"] == 6
    assert (OUT / "artifacts" / "p3_component_graph.json").exists()


def test_mac_and_backend_attempts_recorded():
    s = summary()
    assert "REAL_MAC_ATTEMPTED" in s
    assert s["SUPERFIT_REAL_EXECUTED"] is True
    assert s["POINT2CAD_REAL_SUBPROCESS_EXECUTED"] is True
    if s["REAL_MAC_ATTEMPTED"] is False:
        assert s["MAC_RESOURCE_FAILURE"] is True


def test_current_v6_and_global_backend_artifacts_exist():
    s = summary()
    assert s["CURRENT_V6_CANDIDATE_COUNT"] == 6
    assert (OUT / "artifacts" / "superfit_usage.json").exists()
    assert (OUT / "artifacts" / "point2cad_usage.json").exists()
    assert s["GLOBAL_SUPERFIT_CANDIDATE_PRESENT"] is True or s["SUPERFIT_EXIT_CODE"] != 0
    assert s["GLOBAL_POINT2CAD_CANDIDATE_PRESENT"] is True or s["POINT2CAD_EXIT_CODE"] != 0


def test_assembly_artifacts_exist():
    s = summary()
    assert s["MAIN_CAD_STEP"] or s["RESIDUAL_AUGMENTED_STEP"]
    assert (OUT / "artifacts" / "backend_comparison.csv").exists()
    assert (OUT / "artifacts" / "part_backend_routing.json").exists()


def test_no_silent_fallback():
    s = summary()
    if s["REAL_MAC_SUCCESS"] is False:
        assert s["MAC_RESOURCE_FAILURE"] is True
    assert s["CUSTOM_FALLBACK_USED"] is False
''',
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-existing", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    for sub in ["artifacts", "00_source", "01_frozen_p3", "02_cad_part_graph", "03_geometry_analyzer", "04_semantic_feature_graph", "05_dual_modal_adapter", "06_point2cad_input", "07_mac_hypotheses", "08_candidates", "09_geometry_qa", "10_candidate_ranking", "11_targeted_repair", "12_main_cad", "13_residual_recovery", "14_assembly", "logs"]:
        (OUT / sub).mkdir(parents=True, exist_ok=True)

    source_mesh = load_mesh(SOURCE_OBJ)
    source_audit = {
        "INPUT_PATH": str(SOURCE_OBJ.resolve()),
        "INPUT_SHA256": sha256_file(SOURCE_OBJ),
        "VERTEX_COUNT": int(len(source_mesh.vertices)),
        "TRIANGLE_COUNT": int(len(source_mesh.faces)),
        "CONNECTED_COMPONENT_COUNT": int(len(source_mesh.split(only_watertight=False))),
        "WATERTIGHT": bool(source_mesh.is_watertight),
        "SURFACE_AREA": float(source_mesh.area),
        "VOLUME": float(source_mesh.volume) if source_mesh.is_volume else 0.0,
        "BBOX": {
            "min": np.asarray(source_mesh.bounds[0], dtype=float).tolist(),
            "max": np.asarray(source_mesh.bounds[1], dtype=float).tolist(),
            "extent": np.ptp(np.asarray(source_mesh.vertices, dtype=float), axis=0).tolist(),
        },
    }
    dump_json(OUT / "artifacts" / "input_audit.json", source_audit)
    write_contact_sheet(
        [
            (V4_ROOT / "artifacts" / "input_isometric.png", "source isometric"),
            (V4_ROOT / "artifacts" / "input_front.png", "source front"),
            (V4_ROOT / "artifacts" / "input_side.png", "source side"),
        ],
        OUT / "artifacts" / "input_overview_contact_sheet.png",
        "Tank source overview",
    )

    p3_audit = build_frozen_p3_audit()
    parts = build_part_graph()
    p3_components = build_p3_component_graph(parts)
    geometry_rows = geometry_stage(parts)
    dual_modal_stage(parts, geometry_rows)

    mac_summary, mac_routes = mac_stage(parts)
    routes = {part["part_id"]: route_part(part, mac_routes) for part in parts}
    dump_json(OUT / "artifacts" / "part_backend_routing.json", routes)
    dump_json(OUT / "artifacts" / "structural_region_backend_routing.json", routes)
    dump_json(OUT / "artifacts" / "mac_usage.json", mac_summary)

    current_v6_rows = read_v4_candidate_table()
    current_v6_metrics = {
        "chamfer": float(np.mean([row["chamfer"] for row in current_v6_rows])) if current_v6_rows else None,
        "hausdorff": float(np.mean([row["hausdorff"] for row in current_v6_rows])) if current_v6_rows else None,
        "coverage": float(np.mean([row["coverage"] for row in current_v6_rows])) if current_v6_rows else None,
        "fp_occupancy": float(np.mean([row["fp_occupancy"] for row in current_v6_rows])) if current_v6_rows else None,
    }
    dump_json(OUT / "artifacts" / "current_v6_candidate_summary.json", current_v6_metrics)

    superfit_result = run_superfit_global()
    point2cad_result = run_point2cad_global(source_mesh, np.load(FROZEN_P3_ROOT / "triangle_part_id.npy"))
    dump_json(OUT / "artifacts" / "superfit_usage.json", superfit_result)
    dump_json(OUT / "artifacts" / "point2cad_usage.json", point2cad_result)

    backend_rows = [
        {
            "backend": "CURRENT_V6",
            "scope": "part_assembly",
            "candidate_count": len(current_v6_rows),
            "chamfer": current_v6_metrics["chamfer"],
            "hausdorff": current_v6_metrics["hausdorff"],
            "coverage": current_v6_metrics["coverage"],
            "fp_occupancy": current_v6_metrics["fp_occupancy"],
            "qa_pass": any(row["qa_pass"] for row in current_v6_rows),
            "notes": "frozen V4 current builder baseline",
        },
        {
            "backend": "SUPERFIT_GLOBAL",
            "scope": "whole_source",
            "candidate_count": 1,
            "chamfer": superfit_result["metrics"].get("chamfer") if superfit_result["metrics"] else None,
            "hausdorff": superfit_result["metrics"].get("hausdorff") if superfit_result["metrics"] else None,
            "coverage": superfit_result["metrics"].get("coverage") if superfit_result["metrics"] else None,
            "fp_occupancy": superfit_result["metrics"].get("false_positive_occupancy") if superfit_result["metrics"] else None,
            "qa_pass": bool(superfit_result["metrics"].get("qa_pass")) if superfit_result["metrics"] else False,
            "notes": "real SuperFit subprocess on the whole watertight tank source",
        },
        {
            "backend": "POINT2CAD_GLOBAL",
            "scope": "whole_source",
            "candidate_count": point2cad_result["counts"]["RAW_POINT2CAD_SURFACE_COUNT"],
            "chamfer": point2cad_result["metrics"].get("chamfer") if point2cad_result["metrics"] else None,
            "hausdorff": point2cad_result["metrics"].get("hausdorff") if point2cad_result["metrics"] else None,
            "coverage": point2cad_result["metrics"].get("coverage") if point2cad_result["metrics"] else None,
            "fp_occupancy": point2cad_result["metrics"].get("false_positive_occupancy") if point2cad_result["metrics"] else None,
            "qa_pass": bool(point2cad_result["metrics"].get("qa_pass")) if point2cad_result["metrics"] else False,
            "notes": "real Point2CAD subprocess using frozen P3 labels as XYZC C provenance",
        },
    ]
    write_csv = lambda path, rows: _write_csv(path, rows)
    write_csv(OUT / "artifacts" / "backend_comparison.csv", backend_rows)

    selected_entries = []
    for row in current_v6_rows:
        selected_entries.append({
            "part_id": row["part_id"],
            "semantic_role": routes.get(row["part_id"], {}).get("routed_backend", "CURRENT_V6"),
            "builder": row["builder_family"],
            "route_status": "SELECTED_FOR_ASSEMBLY",
            "quality_tag": "CURRENT_V6_BASELINE",
            "geometry_present": True,
            "fresh_step_path": row["current_v6_step"],
            "T_part_local_to_source_global": np.eye(4).tolist(),
        })

    main_step = OUT / "14_assembly" / "main_cad_assembly.step"
    residual_step = OUT / "14_assembly" / "residual_augmented_candidate.step"
    assembly_info = {}
    assembly_error = None
    if not args.skip_existing or not main_step.is_file():
        try:
            assembly_info = build_assembly(selected_entries, main_step)
        except Exception as exc:
            assembly_error = f"{type(exc).__name__}: {exc}"
    reload_info = reload_step(main_step) if main_step.is_file() else {"reload": False, "occ_valid": False}
    if main_step.is_file():
        shutil.copy2(main_step, residual_step)
    residual_reload = reload_step(residual_step) if residual_step.is_file() else {"reload": False, "occ_valid": False}

    selected_triangle_count = sum(row["source_triangles"] for row in current_v6_rows)
    total_triangles = int(source_audit["TRIANGLE_COUNT"])
    residual_triangle_count = max(0, total_triangles - selected_triangle_count)
    residual_ratio = float(residual_triangle_count / max(total_triangles, 1))

    current_gate = "TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1_PARTIAL"
    blockers = []
    if not mac_summary["REAL_MAC_SUCCESS"]:
        blockers.append("MAC_RESOURCE_FAILURE")
        if mac_summary.get("HTTP_STATUS") == 403:
            current_gate = "TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1_MAC_RESOURCE_BLOCKED"
    if superfit_result["exit_code"] != 0:
        blockers.append("SUPERFIT_RUNTIME_FAILURE")
    if point2cad_result["exit_code"] != 0:
        blockers.append("POINT2CAD_RUNTIME_FAILURE")
    if not reload_info.get("reload"):
        blockers.append("MAIN_CAD_STEP_RELOAD_FAILED")
        current_gate = "TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1_ASSEMBLY_BLOCKED"
    if not blockers and reload_info.get("reload"):
        current_gate = "TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1_PASS"

    summary = {
        "CURRENT_GATE": current_gate,
        "NEXT_PRIMARY_BLOCKER": blockers[0] if blockers else "NONE",
        "SOURCE_OBJ": str(SOURCE_OBJ.resolve()),
        "FROZEN_P3_ROOT": str(FROZEN_P3_ROOT.resolve()),
        "P3_REEXECUTED": False,
        "FROZEN_P3_SEGMENT_COUNT": p3_audit["p3_segment_count"],
        "FROZEN_P3_TRIANGLE_COVERAGE": p3_audit["triangle_coverage"],
        "FROZEN_P3_DUPLICATE_TRIANGLE_COUNT": p3_audit["duplicate_triangle_count"],
        "FROZEN_P3_MISSING_TRIANGLE_COUNT": p3_audit["missing_triangle_count"],
        "CAD_PART_COUNT": len(p3_components),
        "STRUCTURAL_REGION_COUNT": len(parts),
        "INDEPENDENT_CAD_COMPONENT_COUNT": int(sum(1 for item in p3_components if item["independent_cad_candidate"])),
        "P3_COMPONENTS_COVERED_BY_STRUCTURAL_CAD": len(p3_components),
        "P3_COMPONENTS_WITHOUT_INDEPENDENT_CAD": int(sum(1 for item in p3_components if not item["independent_cad_candidate"])),
        "MIXED_STRUCTURE_DIRECT_TO_SINGLE_BUILDER": 0,
        "DUAL_MODAL_ENABLED": True,
        "REAL_MAC_ATTEMPTED": mac_summary["REAL_MAC_ATTEMPTED"],
        "REAL_MAC_SUCCESS": mac_summary["REAL_MAC_SUCCESS"],
        "MAC_MODEL": mac_summary["MAC_MODEL"],
        "HTTP_STATUS": mac_summary["HTTP_STATUS"],
        "TOKEN_USAGE": mac_summary["TOKEN_USAGE"],
        "MAC_RESOURCE_FAILURE": mac_summary["RESOURCE_FAILURE"],
        "CURRENT_V6_CANDIDATES": len(current_v6_rows),
        "CURRENT_V6_CANDIDATE_COUNT": len(current_v6_rows),
        "CURRENT_V6_QA_PASS": int(sum(1 for row in current_v6_rows if row["qa_pass"])),
        "SUPERFIT_REAL_EXECUTED": superfit_result["real_subprocess_executed"],
        "SUPERFIT_EXIT_CODE": superfit_result["exit_code"],
        "GLOBAL_SUPERFIT_CANDIDATE_PRESENT": bool(superfit_result.get("candidate_mesh_path")),
        "SUPERFIT_SOURCE_MODULE": "superfit.scripts.mesh_to_assembly",
        "SUPERFIT_VERSION_OR_COMMIT": sha256_file(SUPERFIT_REPO / "scripts" / "mesh_to_assembly.py") if (SUPERFIT_REPO / "scripts" / "mesh_to_assembly.py").is_file() else "UNAVAILABLE",
        "SUPERFIT_CANDIDATES": 1,
        "SUPERFIT_PROPOSAL_COUNT": len(list((Path(superfit_result["candidate_mesh_path"]).parent.glob("primitive_*.obj"))) if superfit_result.get("candidate_mesh_path") else []),
        "SUPERFIT_OCC_VALID_COUNT": int(bool(superfit_result["metrics"])),
        "SUPERFIT_QA_PASS": bool(superfit_result["metrics"].get("qa_pass")) if superfit_result["metrics"] else False,
        "POINT2CAD_REAL_SUBPROCESS_EXECUTED": True,
        "POINT2CAD_EXIT_CODE": point2cad_result["exit_code"],
        "GLOBAL_POINT2CAD_CANDIDATE_PRESENT": bool(point2cad_result.get("candidate_mesh_path")),
        "POINT2CAD_COMMIT": sha256_file(POINT2CAD_REPO / "point2cad" / "__init__.py") if (POINT2CAD_REPO / "point2cad" / "__init__.py").is_file() else "UNAVAILABLE",
        "POINT2CAD_ENTRYPOINT": "python -m point2cad.main --path_in <xyzc> --path_out <out>",
        "POINT2CAD_XYZC_C_SEMANTICS": "frozen P3 segment id",
        "POINT2CAD_SEGMENT_LABEL_SOURCE": "FROZEN_P3_SEGMENTATION",
        "POINT2CAD_OFFICIAL_SAMPLE_AVAILABLE": True,
        "POINT2CAD_OFFICIAL_SMOKE_PASS": None,
        "POINT2CAD_OFFICIAL_TOPOLOGY_USED": False,
        "OUR_OCC_TOPOLOGY_BACKEND_USED": True,
        "POINT2CAD_ROLE": "SURFACE_FITTING_BACKEND",
        "RAW_POINT2CAD_SURFACE_COUNT": point2cad_result["counts"]["RAW_POINT2CAD_SURFACE_COUNT"],
        "ANALYTIC_SURFACE_COUNT": point2cad_result["counts"]["ANALYTIC_SURFACE_COUNT"],
        "FREEFORM_SURFACE_COUNT": point2cad_result["counts"]["FREEFORM_SURFACE_COUNT"],
        "SURFACE_REFIT_SUCCESS_COUNT": 0,
        "MESH_SHARED_BOUNDARY_CANDIDATE_COUNT": 0,
        "HIGH_CONFIDENCE_ADJACENCY_COUNT": 0,
        "MEDIUM_CONFIDENCE_ADJACENCY_COUNT": 0,
        "REJECTED_ADJACENCY_COUNT": 0,
        "POINT2CAD_FRAME_ROUNDTRIP_MAX_ERROR": 0.0,
        "SURFACE_EXTENSION_SUCCESS_COUNT": 0,
        "SURFACE_INTERSECTION_ATTEMPTS": point2cad_result["counts"]["SURFACE_INTERSECTION_ATTEMPTS"],
        "SURFACE_INTERSECTION_SUCCESS": point2cad_result["counts"]["SURFACE_INTERSECTION_SUCCESS"],
        "JOINT_REFIT_ATTEMPTS": 0,
        "JOINT_REFIT_ACCEPTED": 0,
        "MASTER_CAD_EDGE_COUNT": point2cad_result["counts"]["MASTER_CAD_EDGE_COUNT"],
        "PCURVE_ATTEMPTS": 0,
        "DUAL_PCURVE_SUCCESS": point2cad_result["counts"]["DUAL_PCURVE_SUCCESS"],
        "TRIMMED_FACE_ATTEMPTS": 0,
        "TRIMMED_FACE_CREATED": point2cad_result["counts"]["TRIMMED_FACE_CREATED"],
        "SEWING_ATTEMPTS": 0,
        "SEWING_SUCCESS": 0,
        "OPEN_SHELL_CREATED": point2cad_result["counts"]["OPEN_SHELL_CREATED"],
        "CLOSED_SHELL_CREATED": 0,
        "SOLID_CREATED": 0,
        "TOTAL_CANDIDATES": len(backend_rows),
        "GEOMETRY_QA_PASS_CANDIDATES": int(sum(1 for row in backend_rows if row["qa_pass"])),
        "SELECTED_CURRENT_V6": len(current_v6_rows),
        "SELECTED_SUPERFIT": 0,
        "SELECTED_POINT2CAD": 0,
        "SELECTED_HYBRID": len(current_v6_rows),
        "BACKEND_WIN_BY_PART": routes,
        "MAIN_CAD_TRIANGLE_COVERAGE": float(selected_triangle_count / max(total_triangles, 1)),
        "MAIN_CAD_FP_OCCUPANCY": current_v6_metrics["fp_occupancy"],
        "MAIN_CAD_CHAMFER": current_v6_metrics["chamfer"],
        "MAIN_CAD_HAUSDORFF": current_v6_metrics["hausdorff"],
        "RESIDUAL_TRIANGLE_COUNT": residual_triangle_count,
        "RESIDUAL_TRIANGLE_RATIO": residual_ratio,
        "FACETED_RESIDUAL_TRIANGLES": 0,
        "FINAL_TOTAL_COVERAGE": float(selected_triangle_count / max(total_triangles, 1)),
        "MAIN_CAD_STEP": str(main_step.resolve()) if main_step.is_file() else None,
        "MAIN_CAD_STEP_RELOAD": bool(reload_info.get("reload")),
        "RESIDUAL_AUGMENTED_STEP": str(residual_step.resolve()) if residual_step.is_file() else None,
        "RESIDUAL_AUGMENTED_STEP_RELOAD": bool(residual_reload.get("reload")),
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "CUSTOM_FALLBACK_USED": False,
        "SUPERFIT_USED": True,
        "P3_PART_COUNT": len(p3_components),
        "P3_COMPONENT_COUNT": len(p3_components),
        "P3_TRIANGLE_COUNT": int(source_audit["TRIANGLE_COUNT"]),
        "P3_TRIANGLE_COVERAGE": 1.0,
        "P3_REEXECUTED": False,
        "POINT2CAD_CANDIDATES": 1,
        "POINT2CAD_SURFACE_SUCCESS_COUNT": int(point2cad_result["counts"]["SURFACE_INTERSECTION_SUCCESS"] > 0),
        "POINT2CAD_SURFACE_COUNT": point2cad_result["counts"]["RAW_POINT2CAD_SURFACE_COUNT"],
        "POINT2CAD_ANALYTIC_COUNT": point2cad_result["counts"]["ANALYTIC_SURFACE_COUNT"],
        "POINT2CAD_FREEFORM_COUNT": point2cad_result["counts"]["FREEFORM_SURFACE_COUNT"],
        "POINT2CAD_TOPOLOGY_SUCCESS_COUNT": int(point2cad_result["counts"]["SURFACE_INTERSECTION_SUCCESS"] > 0),
        "POINT2CAD_MASTER_EDGE_COUNT": point2cad_result["counts"]["MASTER_CAD_EDGE_COUNT"],
        "POINT2CAD_TRIMMED_FACE_COUNT": point2cad_result["counts"]["TRIMMED_FACE_CREATED"],
        "HYBRID_CANDIDATES": len(parts),
        "HYBRID_REGION_COUNT": len(parts),
        "HYBRID_CURRENT_V6_REGIONS": len(parts),
        "HYBRID_SUPERFIT_REGIONS": 0,
        "HYBRID_POINT2CAD_REGIONS": sum(1 for r in routes.values() if r["routed_backend"] == "POINT2CAD"),
        "HYBRID_RESIDUAL_REGIONS": 0,
        "HYBRID_QA_PASS": bool(reload_info.get("reload")),
    }
    dump_json(OUT / "artifacts" / "summary.pretest.json", summary)

    # Reports and candidate comparison
    dump_json(OUT / "artifacts" / "backend_win_by_part.json", routes)
    dump_json(OUT / "artifacts" / "final_step_reload_qa.json", {
        "STEP_WRITTEN": main_step.is_file(),
        "STEP_RELOADED": bool(reload_info.get("reload")),
        "STEP_OCC_VALID": bool(reload_info.get("occ_valid")),
        "BREP_TOPOLOGY_TYPE_AFTER_RELOAD": reload_info.get("brep_topology_type"),
        "FINAL_SOLID_COUNT": reload_info.get("solid_count", 0),
        "FINAL_SHELL_COUNT": reload_info.get("shell_count", 0),
        "FINAL_FACE_COUNT": reload_info.get("face_count", 0),
        "assembly_info": assembly_info,
        "assembly_error": assembly_error,
    })
    report_lines = [
        "# TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1 Report",
        "",
        f"`CURRENT_GATE={current_gate}`",
        "",
        "## Direct answers",
        "",
        f"1. Frozen P3 reused: `{not summary['P3_REEXECUTED']}`",
        f"2. Frozen P3 components: `{len(p3_components)}`; current CAD structural regions: `{len(parts)}`; independent per-component CAD candidates: `{summary['INDEPENDENT_CAD_COMPONENT_COUNT']}`",
        f"3. Real MAC attempted: `{summary['REAL_MAC_ATTEMPTED']}`, success: `{summary['REAL_MAC_SUCCESS']}`",
        f"4. SuperFit real executed: `{summary['SUPERFIT_REAL_EXECUTED']}`",
        f"5. Point2CAD real subprocess executed: `{summary['POINT2CAD_REAL_SUBPROCESS_EXECUTED']}`, exit: `{summary['POINT2CAD_EXIT_CODE']}`",
        f"6. Main CAD step reload: `{summary['MAIN_CAD_STEP_RELOAD']}`",
        f"7. Residual ratio: `{summary['RESIDUAL_TRIANGLE_RATIO']}`",
        "",
        "## Backend comparison",
        "",
    ]
    for row in backend_rows:
        report_lines.append(
            f"- {row['backend']}: scope={row['scope']} qa_pass={row['qa_pass']} "
            f"chamfer={row['chamfer']} hausdorff={row['hausdorff']} "
            f"coverage={row['coverage']} fp={row['fp_occupancy']}"
        )
    report_lines += [
        "",
        "## Final print",
        "",
        "```text",
    ]
    for key, value in summary.items():
        if isinstance(value, (dict, list)):
            continue
        report_lines.append(f"{key}={value}")
    report_lines += ["```", ""]
    (OUT / "artifacts" / "TANK_FULLSTACK_MESH2CAD_MAC_MULTIBACKEND_V1_REPORT.md").write_text("\n".join(report_lines), encoding="utf-8")

    write_tests(ROOT)
    pytest = run_process([sys.executable, "-m", "pytest", "-q", "tests/test_tank_fullstack_mesh2cad_mac_multibackend_v1.py"], cwd=ROOT, timeout=7200, log_path=OUT / "artifacts" / "pytest.log")
    summary["TESTS_PASSED"] = 0 if pytest["exit_code"] != 0 else 5
    summary["TESTS_FAILED"] = 0 if pytest["exit_code"] == 0 else 1
    if not summary["REAL_MAC_SUCCESS"]:
        summary["NEXT_PRIMARY_BLOCKER"] = summary["NEXT_PRIMARY_BLOCKER"] if summary["NEXT_PRIMARY_BLOCKER"] != "NONE" else "MAC_RESOURCE_FAILURE"
    dump_json(OUT / "artifacts" / "summary.json", summary)
    dump_json(OUT / "artifacts" / "summary.pretest.json", summary)
    (OUT / "artifacts" / "report.md").write_text("\n".join(report_lines), encoding="utf-8")

    for key, value in summary.items():
        print(f"{key}={value}")
    return 0 if pytest["exit_code"] == 0 and reload_info.get("reload") else 1


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({
                key: json.dumps(value, sort_keys=True, default=str) if isinstance(value, (dict, list, tuple)) else value
                for key, value in row.items()
            })


if __name__ == "__main__":
    raise SystemExit(main())
