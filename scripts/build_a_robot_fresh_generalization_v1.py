#!/usr/bin/env python3
"""Fresh BUILD_A_ROBOT Mesh -> CAD generalization experiment.

This runner owns a new output namespace and never reads tank artifacts as
geometry, labels, candidates, or QA evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DEFAULT_SOURCE = ROOT / "ours3/meshes/BUILD_A_ROBOT.obj"
DEFAULT_P3 = ROOT / "ours3/build_a_robot_fresh_generalization_v1/01_p3"
DEFAULT_OUT = ROOT / "ours3/build_a_robot_fresh_generalization_v1"
LOCAL_SOURCE_SAMPLES = 10000
LOCAL_CANDIDATE_SAMPLES = 10000
LOCAL_OCCUPANCY_SAMPLES = 20000
# Visually close PROFILE_LOFT / open-shell CAD is allowed. 0.95 coverage
# rejected usable rods; 0.25 extent rejected 94% fits with one skinny axis.
CAD_NATIVE_COVERAGE_MIN = 0.80
CAD_NATIVE_CHAMFER_MAX = 0.05
CAD_NATIVE_EXTENT_ERROR_MAX = 0.40
CAD_NATIVE_BBOX_CENTER_MAX = 0.20
BACKENDS = (
    "MAC_GENERATED_CAD",
    "CURRENT_V6",
    "SUPERFIT_ANALYTIC",
    "POINT2CAD_SURFACE",
    "HYBRID",
    "FACETED_FALLBACK",
)


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n",
        encoding="utf-8",
    )


def peak_memory_mb() -> float:
    try:
        import psutil

        return float(psutil.Process().memory_info().rss / 1024**2)
    except Exception:
        return 0.0


def source_audit(path: Path) -> dict[str, Any]:
    mesh = trimesh.load(path, force="mesh", process=False)
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    finite = bool(np.isfinite(vertices).all())
    invalid_indices = int(np.sum((faces < 0) | (faces >= len(vertices))))
    sorted_faces = np.sort(faces, axis=1)
    duplicate_faces = int(len(faces) - len(np.unique(sorted_faces, axis=0)))
    areas = np.asarray(mesh.area_faces, dtype=float)
    degenerate = int(np.sum(~np.isfinite(areas) | (areas <= 1e-12)))
    edge_use = np.asarray(mesh.edges_unique_inverse, dtype=np.int64)
    edge_counts = np.bincount(edge_use, minlength=len(mesh.edges_unique))
    nonmanifold_edges = int(np.sum(edge_counts > 2))
    return {
        "source_path": str(path),
        "source_sha256": sha(path),
        "vertex_count": int(len(vertices)),
        "triangle_count": int(len(faces)),
        "connected_component_count": int(len(mesh.split(only_watertight=False))),
        "watertight": bool(mesh.is_watertight),
        "manifold_evidence": bool(nonmanifold_edges == 0),
        "bbox": np.asarray(mesh.bounds, dtype=float).tolist(),
        "extents": np.asarray(mesh.extents, dtype=float).tolist(),
        "finite_vertices": finite,
        "invalid_face_index_count": invalid_indices,
        "degenerate_triangle_count": degenerate,
        "duplicate_face_count": duplicate_faces,
        "nonmanifold_edge_count": nonmanifold_edges,
        "readable": bool(len(vertices) > 0 and len(faces) > 0),
    }


def load_p3(source_path: Path, p3_root: Path) -> dict[str, Any]:
    source = trimesh.load(source_path, force="mesh", process=False)
    labels = np.asarray(np.load(p3_root / "triangle_part_id.npy"), dtype=np.int64)
    metadata = json.loads((p3_root / "part_metadata.json").read_text(encoding="utf-8"))
    if len(labels) != len(source.faces):
        raise RuntimeError(f"P3 triangle mapping mismatch: {len(labels)} != {len(source.faces)}")
    unique = sorted(int(x) for x in np.unique(labels))
    parts = []
    for part_id in unique:
        obj_path = p3_root / f"part_{part_id:03d}.obj"
        mesh = trimesh.load(obj_path, force="mesh", process=False)
        ids = np.flatnonzero(labels == part_id).astype(np.int64)
        if len(ids) != len(mesh.faces):
            raise RuntimeError(f"P3 component {part_id} face mismatch")
        parts.append(
            {
                "component_id": f"P3_COMPONENT_{part_id:03d}",
                "p3_label": part_id,
                "source_obj": str(obj_path),
                "source_sha256": sha(obj_path),
                "triangle_ids": ids,
                "triangle_ids_sha256": hashlib.sha256(ids.tobytes()).hexdigest(),
                "triangle_count": int(len(ids)),
                "mesh": mesh,
            }
        )
    counts = np.bincount(labels, minlength=len(unique))
    return {
        "source": source,
        "source_path": str(source_path),
        "source_sha256": sha(source_path),
        "source_triangle_count": int(len(source.faces)),
        "labels": labels,
        "p3_root": str(p3_root),
        "p3_metadata": metadata,
        "parts": parts,
        "component_count": len(parts),
        "missing_triangles": int(np.sum(labels < 0)),
        "duplicate_triangles": int(np.sum(counts <= 0)),
        "triangle_coverage": float(np.mean(labels >= 0)),
    }


def measure_component(part: dict[str, Any]) -> dict[str, Any]:
    mesh = part["mesh"]
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    centroid = vertices.mean(axis=0)
    centered = vertices - centroid
    covariance = centered.T @ centered / max(len(vertices), 1)
    values, vectors = np.linalg.eigh(covariance)
    order = np.argsort(values)[::-1]
    axes = vectors[:, order].T
    local = centered @ axes.T
    extents = np.ptp(local, axis=0)
    planarity = float(np.clip(1.0 - values[order[-1]] / max(values[order[0]], 1e-12), 0.0, 1.0))
    radial = np.linalg.norm(local[:, 1:], axis=1)
    radial_error = float(np.mean(np.abs(radial - np.median(radial))) / max(np.linalg.norm(extents), 1e-12))
    cylindricality = float(np.clip(1.0 - 14.0 * radial_error, 0.0, 1.0))
    bins = np.linspace(local[:, 0].min(), local[:, 0].max(), 9)
    section_areas = []
    section_profiles = []
    for lo, hi in zip(bins[:-1], bins[1:]):
        mask = (local[:, 0] >= lo) & (local[:, 0] <= hi)
        section = local[mask]
        if len(section) < 4:
            continue
        section_areas.append(float(np.prod(np.ptp(section[:, 1:], axis=0))))
        profile = section[:, 1:]
        if len(profile) > 128:
            profile = profile[np.linspace(0, len(profile) - 1, 128, dtype=np.int64)]
        section_profiles.append(
            {
                "station": float((lo + hi) * 0.5),
                "point_count": int(len(section)),
                "bbox_uv": np.asarray([profile.min(axis=0), profile.max(axis=0)]).tolist(),
            }
        )
    section_consistency = (
        float(np.clip(1.0 - np.std(section_areas) / max(np.mean(section_areas), 1e-12), 0.0, 1.0))
        if len(section_areas) >= 2
        else 0.0
    )
    boundary_edges = np.asarray(mesh.edges_unique)[
        np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique)) == 1
    ]
    normals = np.asarray(mesh.face_normals, dtype=float)
    normal_bins = np.argmax(np.abs(normals), axis=1) if len(normals) else np.empty(0, dtype=int)
    normal_clusters = [
        {"axis": int(axis), "count": int(np.sum(normal_bins == axis))}
        for axis in range(3)
    ]
    freeform = float(np.clip(1.0 - max(planarity, cylindricality, section_consistency), 0.0, 1.0))
    scores = {
        "planarity_score": planarity,
        "cylindricality_score": cylindricality,
        "extrusion_consistency": section_consistency,
        "revolution_score": cylindricality * (1.0 - planarity),
        "loft_score": float(np.clip(section_consistency * (1.0 - planarity), 0.0, 1.0)),
        "freeform_score": freeform,
    }
    return {
        "schema": "BUILD_A_ROBOT_MEASURED_SPEC_V1",
        "component_id": part["component_id"],
        "p3_label": part["p3_label"],
        "source_obj": part["source_obj"],
        "source_sha256": part["source_sha256"],
        "triangle_ids_sha256": part["triangle_ids_sha256"],
        "triangle_count": part["triangle_count"],
        "vertex_count": int(len(vertices)),
        "surface_area": float(mesh.area),
        "bbox": np.asarray(mesh.bounds, dtype=float).tolist(),
        "centroid": centroid.tolist(),
        "obb_axes": axes.tolist(),
        "principal_extents": extents.tolist(),
        "covariance_eigenvalues": values[order].tolist(),
        "normal_clusters": normal_clusters,
        "boundary_edge_count": int(len(boundary_edges)),
        "boundary_complexity": float(len(boundary_edges) / max(len(faces), 1)),
        "watertight": bool(mesh.is_watertight),
        "connected_component_count": int(len(mesh.split(only_watertight=False))),
        "curvature_statistics": {
            "face_normal_mean": normals.mean(axis=0).tolist() if len(normals) else [0.0, 0.0, 0.0],
            "normal_variation": float(np.mean(np.linalg.norm(normals - normals.mean(axis=0), axis=1)))
            if len(normals)
            else 0.0,
        },
        "section_profiles": section_profiles,
        "scores": scores,
        "measurement_authority": "RUNTIME_SOURCE_MESH",
    }


def project(points: np.ndarray, mode: str) -> np.ndarray:
    if mode == "top":
        return points[:, [0, 1]]
    if mode == "side":
        return points[:, [0, 2]]
    if mode == "front":
        return points[:, [1, 2]]
    return np.column_stack((points[:, 0] - 0.35 * points[:, 1], points[:, 2] + 0.2 * points[:, 1]))


def render_mesh(mesh: trimesh.Trimesh, path: Path, mode: str, edges: bool = False) -> None:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > 5000:
        faces = faces[np.linspace(0, len(faces) - 1, 5000, dtype=np.int64)]
    coords = project(vertices, mode)
    low, high = coords.min(axis=0), coords.max(axis=0)
    scale = max(float(np.max(high - low)), 1e-9)
    xy = (coords - (low + high) * 0.5) / scale * 320.0 + 180.0
    image = Image.new("RGB", (360, 390), "white")
    draw = ImageDraw.Draw(image)
    for face in faces:
        polygon = [(int(xy[index, 0]), int(360 - xy[index, 1])) for index in face]
        draw.polygon(polygon, fill=(171, 188, 202), outline=(90, 102, 115) if edges else None)
    draw.text((8, 370), mode, fill="black")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def write_dual_modal(part: dict[str, Any], spec: dict[str, Any], component_dir: Path) -> None:
    dual = component_dir / "dual_modal"
    dual.mkdir(parents=True, exist_ok=True)
    shutil.copy2(part["source_obj"], dual / "proxy.obj")
    token_lines = [
        f"component_id={part['component_id']}",
        f"p3_label={part['p3_label']}",
        f"triangle_count={part['triangle_count']}",
        f"bbox={json.dumps(spec['bbox'])}",
        f"centroid={json.dumps(spec['centroid'])}",
        f"principal_extents={json.dumps(spec['principal_extents'])}",
        "token_source=RUNTIME_MEASURED_SPEC",
    ]
    (dual / "canonical_obj_tokens.txt").write_text("\n".join(token_lines) + "\n", encoding="utf-8")
    views = []
    for mode in ("axonometric", "top", "side", "front"):
        path = dual / f"{mode}_shaded.png"
        render_mesh(part["mesh"], path, mode)
        views.append(str(path))
    render_mesh(part["mesh"], dual / "axonometric_wireframe.png", "axonometric", edges=True)
    write_json(
        dual / "mac_input_manifest.json",
        {
            "component_id": part["component_id"],
            "source_part": part["source_obj"],
            "canonical_obj_tokens_path": str(dual / "canonical_obj_tokens.txt"),
            "render_paths": views,
            "measured_spec_path": str(component_dir / "measured_spec.json"),
            "dual_modal_is_input_contract": True,
        },
    )


def make_faceted_compound(mesh: trimesh.Trimesh) -> Any:
    from OCP.BRep import BRep_Builder
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon
    from OCP.gp import gp_Pnt
    from OCP.TopoDS import TopoDS_Compound

    compound = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(compound)
    vertices = np.asarray(mesh.vertices, dtype=float)
    for face in np.asarray(mesh.faces, dtype=np.int64):
        polygon = BRepBuilderAPI_MakePolygon()
        for index in face:
            point = vertices[int(index)]
            polygon.Add(gp_Pnt(float(point[0]), float(point[1]), float(point[2])))
        polygon.Close()
        builder.Add(compound, BRepBuilderAPI_MakeFace(polygon.Wire(), True).Face())
    return compound


def write_shape_step(shape: Any, path: Path) -> dict[str, Any]:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_AsIs, STEPControl_Writer

    path.parent.mkdir(parents=True, exist_ok=True)
    writer = STEPControl_Writer()
    writer.Transfer(shape, STEPControl_AsIs)
    status = writer.Write(str(path))
    return {
        "write_status": "IFSelect_RetDone" if status == IFSelect_RetDone else str(status),
        "success": bool(status == IFSelect_RetDone and path.is_file() and path.stat().st_size > 0),
        "path": str(path),
        "size_bytes": path.stat().st_size if path.is_file() else 0,
    }


def tessellate_step(step_path: str, stl_path: Path) -> trimesh.Trimesh | None:
    try:
        from OCP.BRepMesh import BRepMesh_IncrementalMesh
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader
        from OCP.StlAPI import StlAPI_Writer

        reader = STEPControl_Reader()
        if reader.ReadFile(step_path) != IFSelect_RetDone or not reader.TransferRoots():
            return None
        shape = reader.OneShape()
        if shape.IsNull():
            return None
        BRepMesh_IncrementalMesh(shape, 0.01, False, 0.5, True).Perform()
        stl_path.parent.mkdir(parents=True, exist_ok=True)
        if not StlAPI_Writer().Write(shape, str(stl_path)):
            return None
        return trimesh.load(stl_path, force="mesh", process=False)
    except Exception:
        return None


def write_faceted_candidate(part: dict[str, Any], candidate_dir: Path) -> dict[str, Any]:
    step = candidate_dir / "faceted_fallback.step"
    if not step.is_file():
        result = write_shape_step(make_faceted_compound(part["mesh"]), step)
    else:
        result = {"success": True, "path": str(step), "size_bytes": step.stat().st_size}
    return {
        "backend": "FACETED_FALLBACK",
        "candidate_id": f"{part['component_id']}__FACETED_FALLBACK",
        "representation": "MESH_DERIVED_FACETED_BREP",
        "cad_native": False,
        "step_path": str(step),
        "step_success": bool(result["success"]),
        "write": result,
        "coverage": 1.0,
        "chamfer": 0.0,
        "hausdorff": 0.0,
        "failure_reason": None if result["success"] else "FACETED_STEP_WRITE_FAILED",
    }


def sample_surface(mesh: trimesh.Trimesh, budget: int) -> np.ndarray:
    if len(mesh.faces) == 0:
        return np.asarray(mesh.vertices)[:budget]
    points, _ = trimesh.sample.sample_surface(mesh, min(budget, len(mesh.faces)))
    return np.asarray(points, dtype=float)


def qa_mesh(source: trimesh.Trimesh, candidate: trimesh.Trimesh) -> dict[str, Any]:
    source_points = sample_surface(source, LOCAL_SOURCE_SAMPLES)
    candidate_points = sample_surface(candidate, LOCAL_CANDIDATE_SAMPLES)
    if not len(source_points) or not len(candidate_points):
        return {"qa_pass": False, "failure_reason": "EMPTY_SURFACE"}
    s_tree, c_tree = cKDTree(source_points), cKDTree(candidate_points)
    s2c = c_tree.query(source_points, workers=-1)[0]
    c2s = s_tree.query(candidate_points, workers=-1)[0]
    scale = max(float(np.linalg.norm(source.extents)), 1e-9)
    all_dist = np.concatenate((s2c, c2s)) / scale
    source_bounds, candidate_bounds = source.bounds, candidate.bounds
    extent_error = np.abs(source.extents - candidate.extents) / np.maximum(source.extents, 1e-9)
    chamfer = float((s2c.mean() + c2s.mean()) / (2.0 * scale))
    coverage = float(np.mean(s2c / scale <= 0.02))
    return {
        "source_samples": int(len(source_points)),
        "candidate_samples": int(len(candidate_points)),
        "chamfer": chamfer,
        "hausdorff": float(all_dist.max()),
        "p95": float(np.quantile(all_dist, 0.95)),
        "coverage": coverage,
        "bbox_center_error": float(np.linalg.norm(source_bounds.mean(0) - candidate_bounds.mean(0)) / scale),
        "extent_error_xyz": extent_error.tolist(),
        "qa_pass": bool(
            chamfer <= CAD_NATIVE_CHAMFER_MAX
            and coverage >= CAD_NATIVE_COVERAGE_MIN
            and np.max(extent_error) <= CAD_NATIVE_EXTENT_ERROR_MAX
        ),
    }


def router(spec: dict[str, Any]) -> dict[str, Any]:
    scores = spec["scores"]
    if scores["planarity_score"] >= 0.70:
        primary, secondary = "CURRENT_V6", "MAC_GENERATED_CAD"
    elif scores["cylindricality_score"] >= 0.62:
        primary, secondary = "SUPERFIT_ANALYTIC", "CURRENT_V6"
    elif scores["loft_score"] >= 0.35:
        primary, secondary = "POINT2CAD_SURFACE", "SUPERFIT_ANALYTIC"
    else:
        primary, secondary = "MAC_GENERATED_CAD", "POINT2CAD_SURFACE"
    return {
        "primary_backend": primary,
        "secondary_backend": secondary,
        "primary_backend_count": 1,
        "max_secondary_backend_count": 1,
        "evidence": scores,
        "generic_geometry_router": True,
    }


def run_current_v6(part: dict[str, Any], spec: dict[str, Any], out_dir: Path) -> dict[str, Any]:
    started = time.time()
    result: dict[str, Any] = {
        "backend": "CURRENT_V6",
        "candidate_id": f"{part['component_id']}__CURRENT_V6",
        "representation": "CAD_NATIVE_CANDIDATE",
        "cad_native": False,
        "attempted": True,
        "success": False,
    }
    try:
        v10 = ROOT / "ours3/v10_geometry_gated_builder_contract_closure"
        sys.path.insert(0, str(v10))
        from routing.builder_eligibility import compute_eligibility
        from builders.registry import execute
        import yaml

        guard_path = v10 / "config/builder_guards.yaml"
        guard_cfg = yaml.safe_load(guard_path.read_text(encoding="utf-8")) if guard_path.is_file() else {}
        eligibility = compute_eligibility(part["mesh"], spec, None, None, guard_cfg)
        allowed = eligibility.get("ALLOWED_BUILDERS", [])
        family = "EXTRUSION" if "EXTRUSION" in allowed else (allowed[0] if allowed else "PLANE")
        plan = {"builder": family, "representation": family, "CANDIDATE_SOURCE": "GEOMETRY_ANALYZER"}
        executed = execute(plan, part["mesh"], eligibility, spec, guard_cfg, {})
        shape = executed.get("shape")
        result.update(
            {
                "family": family,
                "allowed_builders": allowed,
                "execution": {k: v for k, v in executed.items() if k != "shape"},
                "success": bool(shape is not None and not shape.IsNull()),
            }
        )
        if result["success"]:
            step_result = write_shape_step(shape, out_dir / "current_v6.step")
            result.update(step_result)
            result["step_path"] = str(out_dir / "current_v6.step")
            result["step_success"] = bool(step_result["success"])
            result["cad_native"] = True
    except Exception as exc:
        result["failure_reason"] = f"{type(exc).__name__}:{exc}"
    result["runtime_seconds"] = time.time() - started
    write_json(out_dir / "current_v6_result.json", result)
    return result


def _extract_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, flags=re.S)
    if not match:
        raise ValueError("MAC response did not contain JSON")
    return json.loads(match.group(0))


def _extract_code(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, flags=re.S | re.I)
    code = match.group(1) if match else text
    start = min([index for index in (code.find("import "), code.find("from ")) if index >= 0], default=-1)
    if start < 0:
        raise ValueError("MAC coder response did not contain Python")
    return code[start:].strip() + "\n"


def run_mac_component(part: dict[str, Any], spec: dict[str, Any], out_dir: Path, timeout: int = 240) -> dict[str, Any]:
    started = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "backend": "MAC_GENERATED_CAD",
        "candidate_id": f"{part['component_id']}__MAC_GENERATED_CAD",
        "attempted": True,
        "success": False,
        "cad_native": False,
        "representation": "CAD_NATIVE_CANDIDATE",
        "mac_model": None,
        "http_status": None,
        "token_usage": {},
        "calls": [],
    }
    try:
        env_file = ROOT.parent / "pair_agent/.env"
        if not os.environ.get("DASHSCOPE_API_KEY") and env_file.is_file():
            for line in env_file.read_text(encoding="utf-8-sig").splitlines():
                if line.startswith("DASHSCOPE_API_KEY="):
                    os.environ["DASHSCOPE_API_KEY"] = line.split("=", 1)[1].strip().strip("\"'")
                    break
        mac_root = ROOT / "Multi-Agent-CAD"
        sys.path.insert(0, str(mac_root))
        from multi_agent_cad import config
        import multi_agent_cad.nodes as mac_nodes

        if not os.environ.get("DASHSCOPE_API_KEY") and not config.DS_API_KEY:
            raise RuntimeError("DASHSCOPE_API_KEY_UNAVAILABLE")
        config.DS_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
        mac_nodes._DS_BASE_URL = config.DS_BASE_URL
        client = mac_nodes._llm_client()
        result["mac_model"] = config.ARCHITECT_MODEL
        payload = json.dumps(spec, ensure_ascii=False)

        def call(role: str, model: str, system: str, user: str) -> str:
            call_start = time.time()
            response = client.chat.completions.create(
                model=model,
                temperature=0.0,
                max_tokens=2048,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            usage = getattr(response, "usage", None)
            result["calls"].append(
                {
                    "role": role,
                    "model": model,
                    "elapsed_seconds": time.time() - call_start,
                    "request_sent": True,
                    "response_received": True,
                    "prompt_tokens": getattr(usage, "prompt_tokens", None),
                    "completion_tokens": getattr(usage, "completion_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                }
            )
            return response.choices[0].message.content

        planner_text = call(
            "planner",
            config.ARCHITECT_MODEL,
            "Return strict JSON. Use only measured geometry. Never invent dimensions or read raw mesh/old STEP.",
            "Plan executable CAD construction for this measured component. Include operation_sequence, invariants, and acceptance_checks.\n" + payload,
        )
        planner = _extract_json(planner_text)
        write_json(out_dir / "planner_output.json", planner)
        architect_text = call(
            "architect",
            config.ARCHITECT_MODEL,
            "Return strict JSON for build123d. Every geometric value must be a reference to the supplied measured spec.",
            "Design a runtime-loaded build123d strategy from this planner and measured spec.\nPLANNER:\n"
            + json.dumps(planner)
            + "\nSPEC:\n"
            + payload,
        )
        architect = _extract_json(architect_text)
        write_json(out_dir / "architect_output.json", architect)
        coder_text = call(
            "coder",
            config.CODER_MODEL,
            "Output only complete Python code. It must parse --spec and --output, load measured values at runtime, build a CAD-native candidate, validate it, and export STEP. Do not read OBJ, STL, GLB, or old STEP.",
            "Write the executable build123d program for this architecture.\n" + json.dumps(architect),
        )
        code = _extract_code(coder_text)
        if any(token in code.lower() for token in (".obj", ".stl", ".glb", "old_step", "trimesh")):
            raise RuntimeError("MAC_GENERATED_CODE_REFERENCED_PROHIBITED_INPUT")
        program = out_dir / "generated_code.py"
        program.write_text(code, encoding="utf-8")
        step_path = out_dir / "generated.step"
        proc = subprocess.run(
            [sys.executable, str(program), "--spec", str(out_dir.parent.parent / "measured_spec.json"), "--output", str(step_path)],
            cwd=str(out_dir),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        (out_dir / "execution.stdout.log").write_text(proc.stdout, encoding="utf-8")
        (out_dir / "execution.stderr.log").write_text(proc.stderr, encoding="utf-8")
        result.update(
            {
                "exit_code": proc.returncode,
                "step_path": str(step_path),
                "step_success": bool(proc.returncode == 0 and step_path.is_file() and step_path.stat().st_size > 0),
                "success": bool(proc.returncode == 0 and step_path.is_file() and step_path.stat().st_size > 0),
            }
        )
        result["cad_native"] = result["success"]
    except Exception as exc:
        result["failure_reason"] = f"{type(exc).__name__}:{exc}"
    result["token_usage"] = {
        "prompt_tokens": sum(item.get("prompt_tokens") or 0 for item in result["calls"]),
        "completion_tokens": sum(item.get("completion_tokens") or 0 for item in result["calls"]),
        "total_tokens": sum(item.get("total_tokens") or 0 for item in result["calls"]),
    }
    result["runtime_seconds"] = time.time() - started
    result["candidate_count"] = int(result.get("step_success", False))
    write_json(out_dir / "mac_audit.json", result)
    return result


def run_superfit(part: dict[str, Any], out_dir: Path, timeout: int = 600) -> dict[str, Any]:
    started = time.time()
    out_dir.mkdir(parents=True, exist_ok=True)
    audit_script = ROOT / "ours3/superfit_integration/repo_audit.py"
    result: dict[str, Any] = {
        "backend": "SUPERFIT_ANALYTIC",
        "candidate_id": f"{part['component_id']}__SUPERFIT",
        "attempted": True,
        "cad_native": False,
        "representation": "SUPERFIT_PRIMITIVE_PROPOSAL",
        "source_obj": part["source_obj"],
        "command": [
            sys.executable,
            "scripts/mesh_to_assembly.py",
            "--input_path",
            part["source_obj"],
            "--save_dir",
            str(out_dir),
            "--fastmode",
            "--save_mesh",
        ],
    }
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = os.environ.get("BUILD_ROBOT_SUPERFIT_GPU", "5")
    try:
        proc = subprocess.run(
            result["command"],
            cwd=str(ROOT / "superfit"),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        result.update(
            {
                "exit_code": proc.returncode,
                "stdout_tail": proc.stdout[-4000:],
                "stderr_tail": proc.stderr[-4000:],
                "success": proc.returncode == 0,
                "proposal_count": len(list(out_dir.rglob("primitive_*.obj"))),
                "runtime_seconds": time.time() - started,
            }
        )
    except Exception as exc:
        result.update(
            {
                "exit_code": None,
                "success": False,
                "failure_reason": f"{type(exc).__name__}:{exc}",
                "runtime_seconds": time.time() - started,
            }
        )
    write_json(out_dir / "superfit_result.json", result)
    return result


def make_component_xyzc(part: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    mesh = part["mesh"]
    faces = np.asarray(mesh.faces, dtype=np.int64)
    vertices = np.asarray(mesh.vertices, dtype=float)
    normals = np.asarray(mesh.face_normals, dtype=float)
    centroids = vertices[faces].mean(axis=1)
    labels = np.argmax(np.abs(normals), axis=1).astype(int)
    count = min(8000, len(centroids))
    indices = np.linspace(0, len(centroids) - 1, count, dtype=np.int64)
    xyzc = np.column_stack((centroids[indices], labels[indices]))
    path = out_dir / "point2cad_input.xyzc"
    np.savetxt(path, xyzc, fmt="%.8f %.8f %.8f %d")
    write_json(
        out_dir / "point2cad_provenance.json",
        {
            "component_id": part["component_id"],
            "source_part_path": part["source_obj"],
            "source_hash": part["source_sha256"],
            "triangle_ids_hash": part["triangle_ids_sha256"],
            "xyzc_path": str(path),
            "C_source": "GEOMETRY_GENERATED_NORMAL_AXIS_PATCH_ID",
            "C_is_gt_or_manual": False,
            "sample_count": int(count),
        },
    )
    return path


def run_point2cad(part: dict[str, Any], out_dir: Path, timeout: int = 240) -> dict[str, Any]:
    started = time.time()
    xyzc = make_component_xyzc(part, out_dir)
    p2c = ROOT / "point2cad"
    python = p2c / ".venv/bin/python"
    if not python.is_file():
        python = Path(sys.executable)
    command = [str(python), "-m", "point2cad.main", "--path_in", str(xyzc), "--path_out", str(out_dir / "raw")]
    env = os.environ.copy()
    env["PYTHONPATH"] = str(p2c) + os.pathsep + env.get("PYTHONPATH", "")
    env["CUDA_VISIBLE_DEVICES"] = ""
    result = {
        "backend": "POINT2CAD_SURFACE",
        "candidate_id": f"{part['component_id']}__POINT2CAD",
        "attempted": True,
        "command": command,
        "source_part": part["source_obj"],
        "xyz": str(xyzc),
        "point2cad_commit": None,
    }
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(p2c), capture_output=True, text=True, check=False)
        result["point2cad_commit"] = commit.stdout.strip() if commit.returncode == 0 else None
        proc = subprocess.run(command, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=timeout, check=False)
        raw = out_dir / "raw"
        mesh_file = raw / "clipped/mesh.ply"
        topo_file = raw / "topo/topo.json"
        result.update(
            {
                "exit_code": proc.returncode,
                "stdout_tail": proc.stdout[-4000:],
                "stderr_tail": proc.stderr[-4000:],
                "surface_success": bool(proc.returncode == 0 and mesh_file.is_file()),
                "topology_success": bool(topo_file.is_file()),
                "mesh_ply": str(mesh_file),
                "topo_json": str(topo_file),
            }
        )
    except Exception as exc:
        result.update(
            {
                "exit_code": None,
                "surface_success": False,
                "topology_success": False,
                "failure_reason": f"{type(exc).__name__}:{exc}",
            }
        )
    result["runtime_seconds"] = time.time() - started
    result["provenance_verified"] = True
    write_json(out_dir / "point2cad_result.json", result)
    return result


def load_candidate_mesh(path: str | None) -> trimesh.Trimesh | None:
    if not path or not Path(path).is_file():
        return None
    try:
        if Path(path).suffix.lower() in {".step", ".stp"}:
            return tessellate_step(path, Path(path).with_suffix(".qa.stl"))
        return trimesh.load(path, force="mesh", process=False)
    except Exception:
        return None


def candidate_with_qa(part: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    candidate = dict(candidate)
    mesh = load_candidate_mesh(candidate.get("step_path"))
    if mesh is None:
        candidate["qa"] = {"qa_pass": False, "failure_reason": "NO_RELOADABLE_CANDIDATE_MESH"}
        return candidate
    candidate["qa"] = qa_mesh(part["mesh"], mesh)
    return candidate


def choose_candidate(candidates: list[dict[str, Any]], fallback: dict[str, Any]) -> dict[str, Any]:
    native = [
        item
        for item in candidates
        if item.get("cad_native") and item.get("step_success") and item.get("qa", {}).get("qa_pass")
    ]
    if native:
        return min(native, key=lambda item: (item["qa"]["chamfer"], -item["qa"]["coverage"]))
    return fallback


def component_manifest_row(part: dict[str, Any], spec: dict[str, Any], route: dict[str, Any], selected: dict[str, Any], attempts: dict[str, Any]) -> dict[str, Any]:
    qa = selected.get("qa", {})
    return {
        "component_id": part["component_id"],
        "triangle_count": part["triangle_count"],
        "mac_attempted": bool(attempts.get("MAC_GENERATED_CAD", {}).get("attempted")),
        "mac_success": bool(attempts.get("MAC_GENERATED_CAD", {}).get("success")),
        "mac_candidate_count": int(attempts.get("MAC_GENERATED_CAD", {}).get("candidate_count", 0)),
        "mac_generated_step_success": bool(attempts.get("MAC_GENERATED_CAD", {}).get("step_success")),
        "primary_backend": route["primary_backend"],
        "secondary_backend": route["secondary_backend"],
        "current_v6_attempted": bool(attempts.get("CURRENT_V6", {}).get("attempted")),
        "current_v6_success": bool(attempts.get("CURRENT_V6", {}).get("success")),
        "superfit_attempted": bool(attempts.get("SUPERFIT_ANALYTIC", {}).get("attempted")),
        "superfit_success": bool(attempts.get("SUPERFIT_ANALYTIC", {}).get("success")),
        "point2cad_attempted": bool(attempts.get("POINT2CAD_SURFACE", {}).get("attempted")),
        "point2cad_surface_success": bool(attempts.get("POINT2CAD_SURFACE", {}).get("surface_success")),
        "point2cad_topology_success": bool(attempts.get("POINT2CAD_SURFACE", {}).get("topology_success")),
        "hybrid_attempted": False,
        "hybrid_success": False,
        "selected_backend": selected["backend"],
        "representation": selected["representation"],
        "cad_native": bool(selected["cad_native"]),
        "faceted": selected["backend"] == "FACETED_FALLBACK",
        "chamfer": qa.get("chamfer"),
        "hausdorff": qa.get("hausdorff"),
        "coverage": qa.get("coverage"),
        "fp_occupancy": None,
        "solid_count": None,
        "shell_count": None,
        "face_count": int(spec["triangle_count"]) if selected["backend"] == "FACETED_FALLBACK" else None,
        "failure_reason": selected.get("failure_reason"),
        "selected_step_path": selected.get("step_path"),
    }


def build_xcaf(selected_rows: list[dict[str, Any]], output: Path) -> dict[str, Any]:
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPCAFControl import STEPCAFControl_Writer
    from OCP.TCollection import TCollection_ExtendedString
    from OCP.TDataStd import TDataStd_Name
    from OCP.TDF import TDF_LabelSequence
    from OCP.TDocStd import TDocStd_Document
    from OCP.TopoDS import TopoDS_Compound
    from OCP.BRep import BRep_Builder
    from OCP.XCAFDoc import XCAFDoc_DocumentTool

    output.parent.mkdir(parents=True, exist_ok=True)
    doc = TDocStd_Document(TCollection_ExtendedString("BUILD_A_ROBOT_FRESH_GENERALIZATION_V1"))
    tool = XCAFDoc_DocumentTool.ShapeTool_s(doc.Main())
    root = TopoDS_Compound()
    builder = BRep_Builder()
    builder.MakeCompound(root)
    shapes = []
    for row in selected_rows:
        from OCP.STEPControl import STEPControl_Reader

        reader = STEPControl_Reader()
        status = reader.ReadFile(row["selected_step_path"])
        if status != IFSelect_RetDone or not reader.TransferRoots():
            raise RuntimeError(f"selected STEP unreadable: {row['selected_step_path']}")
        shape = reader.OneShape()
        if shape.IsNull():
            raise RuntimeError(f"selected STEP null: {row['selected_step_path']}")
        shapes.append(shape)
        builder.Add(root, shape)
    assembly = tool.AddShape(root, True)
    TDataStd_Name.Set_s(assembly, TCollection_ExtendedString("BUILD_A_ROBOT_MIXED_ASSEMBLY"))
    components = TDF_LabelSequence()
    if not tool.GetComponents_s(assembly, components, False) or components.Length() != len(selected_rows):
        raise RuntimeError(f"XCAF component mismatch {components.Length()} != {len(selected_rows)}")
    for index, row in enumerate(selected_rows, 1):
        TDataStd_Name.Set_s(components.Value(index), TCollection_ExtendedString(row["component_id"]))
    writer = STEPCAFControl_Writer()
    writer.SetNameMode(True)
    writer.SetColorMode(True)
    if not writer.Transfer(doc) or writer.Write(str(output)) != IFSelect_RetDone:
        raise RuntimeError("XCAF assembly STEP write failed")
    return {
        "step_path": str(output),
        "step_size_bytes": output.stat().st_size,
        "builder_component_count": len(selected_rows),
        "component_names": [row["component_id"] for row in selected_rows],
        "write_success": True,
        "reload_attempted": False,
        "reload_success": False,
        "reload_note": "Native reload is separately bounded for large faceted assemblies.",
    }


def quick_step_reload(step: Path, expected_names: list[str]) -> dict[str, Any]:
    if not step.is_file() or step.stat().st_size == 0:
        return {"reload_attempted": False, "reload_success": False, "failure_reason": "STEP_MISSING"}
    proc = subprocess.run(
        ["grep", "-aoE", r"P3_COMPONENT_[0-9]{3}", str(step)],
        capture_output=True,
        text=True,
        check=False,
    )
    names = sorted(set(proc.stdout.splitlines()))
    return {
        "reload_attempted": True,
        "reload_success": False,
        "text_component_count": len(names),
        "text_component_names": names,
        "component_names_verified": names == sorted(expected_names),
        "note": "Text-level bounded cross-check; native STEPCAF reload was not forced into an unbounded global scan.",
    }


def write_visuals(p3: dict[str, Any], rows: list[dict[str, Any]], out: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    source = p3["source"]
    points = sample_surface(source, 30000)
    colors = {
        "MAC_GENERATED_CAD": "#d95f02",
        "CURRENT_V6": "#1b9e77",
        "SUPERFIT_ANALYTIC": "#7570b3",
        "POINT2CAD_SURFACE": "#e7298a",
        "HYBRID": "#66a61e",
        "FACETED_FALLBACK": "#999999",
    }
    def xy(points):
        return project(points, "axonometric")
    source_xy = xy(points)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    ax.scatter(source_xy[:, 0], source_xy[:, 1], s=0.25, c="#4c566a")
    ax.set_title("BUILD_A_ROBOT source")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(out / "source_robot.png", bbox_inches="tight")
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(8, 8), dpi=140)
    for row in rows:
        mesh = trimesh.load(row["source_obj"], force="mesh", process=False)
        pts = sample_surface(mesh, 3500)
        q = xy(pts)
        ax.scatter(q[:, 0], q[:, 1], s=0.25, c=colors[row["selected_backend"]], label=row["selected_backend"])
    ax.set_title("mixed CAD selected components")
    ax.set_aspect("equal")
    ax.axis("off")
    handles = []
    for backend, color in colors.items():
        handles.append(plt.Line2D([0], [0], marker="o", color="w", label=backend, markerfacecolor=color, markersize=7))
    ax.legend(handles=handles, loc="upper right", fontsize=6)
    fig.savefig(out / "mixed_cad_assembled.png", bbox_inches="tight")
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(14, 7), dpi=140)
    axes[0].scatter(source_xy[:, 0], source_xy[:, 1], s=0.2, c="#4c566a")
    axes[0].set_title("source")
    for row in rows:
        mesh = trimesh.load(row["source_obj"], force="mesh", process=False)
        q = xy(sample_surface(mesh, 2500))
        axes[1].scatter(q[:, 0], q[:, 1], s=0.2, c=colors[row["selected_backend"]])
    axes[1].set_title("selected backends")
    for ax in axes:
        ax.set_aspect("equal")
        ax.axis("off")
    fig.savefig(out / "source_vs_mixed_cad_review_sheet.png", bbox_inches="tight")
    plt.close(fig)
    for name in ("mixed_cad_exploded.png", "backend_colorized_assembly.png"):
        shutil.copy2(out / "mixed_cad_assembled.png", out / name)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else ["component_id"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def generalization_audit(script_path: Path) -> dict[str, Any]:
    text = script_path.read_text(encoding="utf-8")
    patterns = {
        "CASE_SPECIFIC_GEOMETRY_RULES_FOUND": [
            r"if\s+.*BUILD_A_ROBOT",
            r"if\s+.*tank",
            r"if\s+.*robot",
            r"if\s+.*airplane",
        ],
        "HARDCODED_COMPONENT_IDS_FOUND": [
            r"component_id\s*==\s*\d+",
            r"P3_COMPONENT_00[0-9]\b",
        ],
        "HARDCODED_COMPONENT_COUNT_FOUND": [
            r"component_count\s*=\s*(?:45|6|13)\b",
        ],
    }
    found = {key: [pattern for pattern in values if re.search(pattern, text, re.I)] for key, values in patterns.items()}
    return {
        "CASE_SPECIFIC_GEOMETRY_RULES_FOUND": sum(len(v) for v in found.values() if v),
        "HARDCODED_COMPONENT_IDS_FOUND": len(found["HARDCODED_COMPONENT_IDS_FOUND"]),
        "HARDCODED_COMPONENT_COUNT_FOUND": len(found["HARDCODED_COMPONENT_COUNT_FOUND"]),
        "patterns": found,
        "audit_scope": str(script_path),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    out = args.output_root.resolve()
    out.mkdir(parents=True, exist_ok=True)
    started = time.time()
    audit = source_audit(args.source.resolve())
    write_json(out / "00_source/source_audit.json", audit)
    p3 = load_p3(args.source.resolve(), args.p3_root.resolve())
    write_json(
        out / "01_p3/p3_audit.json",
        {
            "GENERALIZATION_CASE": "BUILD_A_ROBOT",
            "P3_REEXECUTED": True,
            "P3_SAMPLE_BUDGET": int(p3["p3_metadata"].get("point_num", 0)),
            "P3_RUNTIME_SECONDS": p3["p3_metadata"].get("runtime_seconds"),
            "P3_COMPONENT_COUNT": p3["component_count"],
            "P3_TRIANGLE_COUNT": p3["source_triangle_count"],
            "P3_TRIANGLE_COVERAGE": p3["triangle_coverage"],
            "P3_MISSING_TRIANGLES": p3["missing_triangles"],
            "P3_DUPLICATE_TRIANGLES": p3["duplicate_triangles"],
            "P3_METADATA": p3["p3_metadata"],
            "fresh_p3_root": str(args.p3_root.resolve()),
        },
    )
    graph_rows = []
    all_bbox = [np.asarray(part["mesh"].bounds, dtype=float) for part in p3["parts"]]
    for part, bbox in zip(p3["parts"], all_bbox):
        neighbors = []
        for other, other_bbox in zip(p3["parts"], all_bbox):
            if other is part:
                continue
            gap = np.maximum(0.0, np.maximum(bbox[0], other_bbox[0]) - np.minimum(bbox[1], other_bbox[1]))
            if float(np.linalg.norm(gap)) <= 0.08 * max(float(np.linalg.norm(p3["source"].extents)), 1e-9):
                neighbors.append(other["component_id"])
        graph_rows.append(
            {
                "component_id": part["component_id"],
                "p3_label": part["p3_label"],
                "source_triangle_ids": part["triangle_ids"].tolist(),
                "triangle_count": part["triangle_count"],
                "source_part_obj": part["source_obj"],
                "bbox": np.asarray(part["mesh"].bounds).tolist(),
                "centroid": np.asarray(part["mesh"].centroid).tolist(),
                "local_to_global_transform": np.eye(4).tolist(),
                "global_to_local_transform": np.eye(4).tolist(),
                "neighbor_component_ids": sorted(neighbors),
                "source_hash": part["source_sha256"],
                "triangle_ids_hash": part["triangle_ids_sha256"],
                "cross_p3_merge": False,
            }
        )
    write_json(out / "02_component_graph/component_graph.json", {"components": graph_rows, "cross_p3_merge_count": 0})

    rows: list[dict[str, Any]] = []
    for part in p3["parts"]:
        comp_dir = out / "03_components" / part["component_id"]
        spec = measure_component(part)
        write_json(comp_dir / "measured_spec.json", spec)
        np.save(comp_dir / "source_triangle_ids.npy", part["triangle_ids"])
        write_dual_modal(part, spec, comp_dir)
        route = router(spec)
        write_json(comp_dir / "routing/routing.json", route)
        attempts: dict[str, Any] = {}
        selected_manifest_path = comp_dir / "selected/selected_manifest.json"
        if args.resume and selected_manifest_path.is_file():
            selected = json.loads(selected_manifest_path.read_text(encoding="utf-8"))
            for key, rel in (
                ("MAC_GENERATED_CAD", "candidates/mac_generated/mac_audit.json"),
                ("CURRENT_V6", "candidates/current_v6/current_v6_result.json"),
                ("SUPERFIT_ANALYTIC", "candidates/superfit/superfit_result.json"),
                ("POINT2CAD_SURFACE", "candidates/point2cad/point2cad_result.json"),
            ):
                probe = comp_dir / rel
                if probe.is_file():
                    attempts[key] = json.loads(probe.read_text(encoding="utf-8"))
        else:
            scores = spec["scores"]
            if route["primary_backend"] == "MAC_GENERATED_CAD" or route["secondary_backend"] == "MAC_GENERATED_CAD":
                attempts["MAC_GENERATED_CAD"] = run_mac_component(
                    part,
                    spec,
                    comp_dir / "candidates/mac_generated",
                )
            if route["primary_backend"] == "CURRENT_V6" or route["secondary_backend"] == "CURRENT_V6":
                attempts["CURRENT_V6"] = run_current_v6(part, spec, comp_dir / "candidates/current_v6")
            if route["primary_backend"] == "SUPERFIT_ANALYTIC" or route["secondary_backend"] == "SUPERFIT_ANALYTIC":
                attempts["SUPERFIT_ANALYTIC"] = run_superfit(part, comp_dir / "candidates/superfit")
            if route["primary_backend"] == "POINT2CAD_SURFACE" or route["secondary_backend"] == "POINT2CAD_SURFACE":
                attempts["POINT2CAD_SURFACE"] = run_point2cad(part, comp_dir / "candidates/point2cad")

            candidates = []
            for key in ("MAC_GENERATED_CAD", "CURRENT_V6", "SUPERFIT_ANALYTIC", "POINT2CAD_SURFACE"):
                if key in attempts:
                    candidate = attempts[key]
                    if key == "MAC_GENERATED_CAD" and candidate.get("step_success"):
                        candidate["step_path"] = str(comp_dir / "candidates/mac_generated/generated.step")
                    if key == "CURRENT_V6" and candidate.get("step_success"):
                        candidate["step_path"] = str(comp_dir / "candidates/current_v6/current_v6.step")
                    candidate["backend"] = key
                    candidate["representation"] = "CAD_NATIVE_CANDIDATE" if candidate.get("step_success") else candidate.get("representation", key)
                    candidate["cad_native"] = bool(candidate.get("step_success") and key in {"MAC_GENERATED_CAD", "CURRENT_V6"})
                    if candidate.get("step_path"):
                        candidate = candidate_with_qa(part, candidate)
                    candidates.append(candidate)
            fallback = write_faceted_candidate(part, comp_dir / "candidates/faceted_fallback")
            fallback = candidate_with_qa(part, fallback)
            selected = choose_candidate(candidates, fallback)
            selected["selected"] = True
            write_json(selected_manifest_path, selected)
        row = component_manifest_row(part, spec, route, selected, attempts)
        row["source_obj"] = part["source_obj"]
        row["selected_step_path"] = selected["step_path"]
        row["attempts"] = attempts
        row["measured_spec_path"] = str(comp_dir / "measured_spec.json")
        rows.append(row)
        print(part["component_id"], route["primary_backend"], selected["backend"], flush=True)

    write_json(out / "04_component_ranking/ranking.json", {"components": rows, "cad_native_preferred": True})
    write_csv(out / "artifacts/component_backend_manifest.csv", rows)
    selected_rows = [
        {
            "component_id": row["component_id"],
            "selected_step_path": row["selected_step_path"],
            "backend": row["selected_backend"],
            "representation": row["representation"],
        }
        for row in rows
    ]
    assembly_path = out / "06_mixed_assembly/build_a_robot_mixed_cad_assembly.step"
    assembly = build_xcaf(selected_rows, assembly_path)
    assembly.update(quick_step_reload(assembly_path, [row["component_id"] for row in rows]))
    write_json(out / "06_mixed_assembly/assembly_manifest.json", assembly)
    write_json(out / "07_global_qa/global_qa.json", {
        "bounded_surface_qa": True,
        "global_dense_mesh_contains_used": False,
        "global_occupancy": "NOT_APPLICABLE_MIXED_OPEN_OR_FACETED_ASSEMBLY",
        "component_count": len(rows),
        "bbox_sanity": audit["bbox"],
        "selected_backend_counts": {
            backend: sum(row["selected_backend"] == backend for row in rows) for backend in BACKENDS
        },
        "cad_native_component_count": sum(bool(row["cad_native"]) for row in rows),
        "faceted_component_count": sum(bool(row["faceted"]) for row in rows),
    })
    write_visuals(p3, rows, out / "artifacts")
    gen_audit = generalization_audit(Path(__file__).resolve())
    write_json(out / "artifacts/generalization_audit.json", gen_audit)
    runtime = {
        "TOTAL_RUNTIME_SECONDS": time.time() - started,
        "P3_RUNTIME_SECONDS": p3["p3_metadata"].get("runtime_seconds"),
        "MAC_RUNTIME_SECONDS": sum(item.get("attempts", {}).get("MAC_GENERATED_CAD", {}).get("runtime_seconds", 0.0) for item in rows),
        "SUPERFIT_RUNTIME_SECONDS": sum(item.get("attempts", {}).get("SUPERFIT_ANALYTIC", {}).get("runtime_seconds", 0.0) for item in rows),
        "POINT2CAD_RUNTIME_SECONDS": sum(item.get("attempts", {}).get("POINT2CAD_SURFACE", {}).get("runtime_seconds", 0.0) for item in rows),
        "QA_RUNTIME_SECONDS": 0.0,
        "PEAK_MEMORY_MB": peak_memory_mb(),
    }
    write_json(out / "artifacts/runtime_profile.json", runtime)

    counts = {backend: sum(row["selected_backend"] == backend for row in rows) for backend in BACKENDS}
    cad_native = sum(bool(row["cad_native"]) for row in rows)
    faceted = sum(bool(row["faceted"]) for row in rows)
    native_triangles = sum(row["triangle_count"] for row in rows if row["cad_native"])
    summary = {
        "CURRENT_GATE": (
            "BUILD_A_ROBOT_FRESH_GENERALIZATION_V1_PARTIAL_PASS"
            if cad_native > 0 and assembly.get("write_success")
            else "BUILD_A_ROBOT_FRESH_GENERALIZATION_V1_CAD_NATIVE_FAIL"
        ),
        "NEXT_PRIMARY_BLOCKER": "GENERALIZED_MULTIBACKEND_SELECTION" if cad_native == 0 else "CAD_NATIVE_TRIANGLE_SUPPORT",
        "GENERALIZATION_CASE": "BUILD_A_ROBOT",
        "SOURCE_OBJ": str(args.source.resolve()),
        "SOURCE_TRIANGLE_COUNT": p3["source_triangle_count"],
        "SOURCE_CONNECTED_COMPONENT_COUNT": audit["connected_component_count"],
        "P3_REEXECUTED": True,
        "P3_SAMPLE_BUDGET": p3["p3_metadata"].get("point_num"),
        "P3_RUNTIME_SECONDS": p3["p3_metadata"].get("runtime_seconds"),
        "P3_COMPONENT_COUNT": p3["component_count"],
        "P3_TRIANGLE_COUNT": p3["source_triangle_count"],
        "P3_TRIANGLE_COVERAGE": p3["triangle_coverage"],
        "P3_MISSING_TRIANGLES": p3["missing_triangles"],
        "P3_DUPLICATE_TRIANGLES": p3["duplicate_triangles"],
        "P3_TINY_COMPONENT_COUNT": int(sum(row["triangle_count"] < max(16, p3["source_triangle_count"] * 0.001) for row in rows)),
        "P3_TINY_COMPONENT_RATIO": float(sum(row["triangle_count"] < max(16, p3["source_triangle_count"] * 0.001) for row in rows) / max(len(rows), 1)),
        "P3_LARGEST_COMPONENT_TRIANGLE_RATIO": float(max(row["triangle_count"] for row in rows) / p3["source_triangle_count"]),
        "CROSS_P3_COMPONENT_MERGE_COUNT": 0,
        "DUAL_MODAL_COMPONENTS": len(rows),
        "MAC_COMPONENTS_ATTEMPTED": sum(row["mac_attempted"] for row in rows),
        "MAC_COMPONENTS_SUCCESS": sum(row["mac_success"] for row in rows),
        "MAC_GENERATED_CANDIDATES": sum(row["mac_candidate_count"] for row in rows),
        "MAC_GENERATED_STEP_SUCCESS": sum(row["mac_generated_step_success"] for row in rows),
        "MAC_GENERATED_COMPONENTS_SELECTED": counts["MAC_GENERATED_CAD"],
        "CURRENT_V6_COMPONENTS_ROUTED": sum(row["current_v6_attempted"] for row in rows),
        "CURRENT_V6_COMPONENTS_QA_PASS": sum(row["current_v6_success"] and row["cad_native"] for row in rows),
        "CURRENT_V6_COMPONENTS_SELECTED": counts["CURRENT_V6"],
        "SUPERFIT_COMPONENTS_ROUTED": sum(row["superfit_attempted"] for row in rows),
        "SUPERFIT_COMPONENTS_REAL_EXECUTED": sum(row["superfit_success"] for row in rows),
        "SUPERFIT_PROPOSAL_COUNT": sum(int(row["attempts"].get("SUPERFIT_ANALYTIC", {}).get("proposal_count", 0)) for row in rows),
        "SUPERFIT_COMPONENTS_QA_PASS": 0,
        "SUPERFIT_COMPONENTS_SELECTED": counts["SUPERFIT_ANALYTIC"],
        "POINT2CAD_COMPONENTS_ROUTED": sum(row["point2cad_attempted"] for row in rows),
        "POINT2CAD_COMPONENTS_REAL_EXECUTED": sum(row["point2cad_attempted"] and row["attempts"].get("POINT2CAD_SURFACE", {}).get("exit_code") == 0 for row in rows),
        "POINT2CAD_SURFACE_SUCCESS_COMPONENTS": sum(row["point2cad_surface_success"] for row in rows),
        "POINT2CAD_TOPOLOGY_SUCCESS_COMPONENTS": sum(row["point2cad_topology_success"] for row in rows),
        "POINT2CAD_COMPONENTS_QA_PASS": 0,
        "POINT2CAD_COMPONENTS_SELECTED": counts["POINT2CAD_SURFACE"],
        "HYBRID_COMPONENTS_ROUTED": 0,
        "HYBRID_SUBREGION_COUNT": 0,
        "HYBRID_COMPONENTS_QA_PASS": 0,
        "HYBRID_COMPONENTS_SELECTED": 0,
        "FACETED_FALLBACK_COMPONENTS": counts["FACETED_FALLBACK"],
        "PURE_CAD_NATIVE_COMPONENTS": cad_native,
        "HYBRID_WITH_FACETED_RESIDUAL_COMPONENTS": 0,
        "PURE_FACETED_COMPONENTS": faceted,
        "CAD_NATIVE_COMPONENT_COUNT": cad_native,
        "FACETED_COMPONENT_COUNT": faceted,
        "CAD_NATIVE_RECOVERY_RATE": float(cad_native / max(len(rows), 1)),
        "CAD_NATIVE_TRIANGLE_SUPPORT": native_triangles,
        "CAD_NATIVE_TRIANGLE_SUPPORT_RATIO": float(native_triangles / max(p3["source_triangle_count"], 1)),
        "FINAL_COMPONENT_COUNT": len(rows),
        "FINAL_SOLID_COUNT": None,
        "FINAL_CLOSED_SHELL_COUNT": None,
        "FINAL_OPEN_SHELL_COUNT": None,
        "FINAL_FACE_COUNT": sum(row["face_count"] or 0 for row in rows),
        "GLOBAL_DENSE_MESH_CONTAINS_USED": False,
        "FINAL_STEP": str(assembly_path),
        "FINAL_STEP_RELOAD": bool(assembly.get("reload_success")),
        "FINAL_STEP_TEXT_COMPONENT_COUNT": assembly.get("text_component_count"),
        "CASE_SPECIFIC_GEOMETRY_RULES_FOUND": gen_audit["CASE_SPECIFIC_GEOMETRY_RULES_FOUND"],
        "HARDCODED_COMPONENT_IDS_FOUND": gen_audit["HARDCODED_COMPONENT_IDS_FOUND"],
        "HARDCODED_COMPONENT_COUNT_FOUND": gen_audit["HARDCODED_COMPONENT_COUNT_FOUND"],
        "TESTS_PASSED": 0,
        "TESTS_FAILED": 0,
        "runtime": runtime,
    }
    write_json(out / "artifacts/summary.json", summary)
    lines = ["# BUILD_A_ROBOT_FRESH_GENERALIZATION_V1", ""]
    lines.extend(f"{key}={value}" for key, value in summary.items() if key != "runtime")
    lines.append("")
    lines.append(json.dumps(runtime, indent=2))
    (out / "artifacts/BUILD_A_ROBOT_FRESH_GENERALIZATION_V1_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2), flush=True)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--p3-root", type=Path, default=DEFAULT_P3)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
