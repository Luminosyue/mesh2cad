#!/usr/bin/env python3
"""Run the latest mesh2cad fullstack pipe on two new high-poly OBJs.

Operational path is V6 fullstack (P3 + PhysX + part graph + geometry analyzer +
dual-modal Qwen3-VL + MAC + OCC runtime + QA + nativeness TTS + XCAF), with V9
automatic part merge / primitive bank and a frozen-structure parameter search
wired in. Wing-only V8 intersection topology is recorded as PARTIAL for
non-planar generic parts.

Use --mainline to add geometry_class-driven V6 backend candidates (no aircraft
ROLE_CONFIG) and emit a relaxed best_available assembly alongside hard-gate XCAF.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw
from scipy.spatial import cKDTree

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "two_mesh_fullstack_latest"
P3_RUNNER = ROOT / "case09_fullstack_mesh2cad_mac_v6/scripts/p3_fresh_v6.py"
PHYSX_RUNNER = ROOT / "case09_aircraft_end2end_cad_v1/scripts/run_physx.py"
RENDER_RUNNER = ROOT / "fusion_pipeline/scripts/render_obj_for_physx.py"
MAC_RUNNER = OUT / "scripts/mac_candidates.py"
RUNTIME = OUT / "scripts/runtime.py"
HUNYUAN = Path("/data/miniconda3/envs/hunyuan/bin/python")
MACPY = Path("/data/miniconda3/envs/multi_agent_cad/bin/python")
V9 = ROOT / "v9_fullstack_architecture_closure"

CASES = [
    {
        "case_id": "CASE_5IHUMO",
        "source": ROOT / "meshes/5iHumoHAKIPuELpWrRd3Vr3mk38.obj",
        "short": "5iHumo",
    },
    {
        "case_id": "CASE_YC4XCA",
        "source": ROOT / "meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj",
        "short": "yC4xca",
    },
]


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(cmd, log_path: Path, env=None, timeout=None):
    log_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.time()
    result = subprocess.run(cmd, text=True, capture_output=True, env=env, timeout=timeout)
    log_path.write_text(
        "$ " + " ".join(str(x) for x in cmd) + "\n\n" + result.stdout + "\n--- STDERR ---\n" + result.stderr,
        encoding="utf-8",
    )
    if result.returncode != 0:
        raise RuntimeError(f"command failed ({result.returncode}): {cmd[0]} ... see {log_path}")
    return {"exit_code": result.returncode, "elapsed_seconds": time.time() - started, "log": str(log_path)}


def pick_gpu(min_free_mb=10000, avoid=(1,)):
    """Prefer a GPU that is not hosting the local Qwen3-VL server (GPU 1)."""
    out = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,memory.used,memory.total,utilization.gpu", "--format=csv,noheader,nounits"],
        text=True,
    )
    rows = []
    for line in out.strip().splitlines():
        idx, used, total, util = [int(float(x.strip())) for x in line.split(",")]
        rows.append({"index": idx, "free": total - used, "used": used, "total": total, "util": util})
    eligible = [r for r in rows if r["index"] not in avoid and r["free"] >= min_free_mb]
    if not eligible:
        eligible = [r for r in rows if r["free"] >= min_free_mb]
    if not eligible:
        raise RuntimeError(f"no GPU with {min_free_mb}MB free: {rows}")
    eligible.sort(key=lambda r: (-r["free"], r["util"], r["index"]))
    chosen = eligible[0]
    dump(OUT / "artifacts/gpu_choice.json", {"chosen": chosen, "all": rows, "avoid": list(avoid)})
    return chosen["index"]


def pca(vertices):
    center = vertices.mean(0)
    _, values, axes = np.linalg.svd(vertices - center, full_matrices=False)
    return center, axes, values


def geometry_class(mesh):
    ext = np.sort(np.maximum(mesh.extents, 1e-12))[::-1]
    ratios = [float(ext[1] / ext[0]), float(ext[2] / ext[0])]
    components = len(mesh.split(only_watertight=False))
    if ratios[1] < 0.08:
        return "THIN_EXTRUSION", ratios, components
    if ratios[0] < 0.22:
        return "AXIAL_REVOLUTION_OR_SWEEP", ratios, components
    if components > 1:
        return "MULTI_FEATURE", ratios, components
    if mesh.is_watertight and ratios[1] > 0.55:
        return "VOLUMETRIC_FREEFORM", ratios, components
    return "GLOBAL_LOFT_OR_FREEFORM", ratios, components


def source_part(source, labels, segments):
    ids = np.flatnonzero(np.isin(labels, np.asarray(segments)))
    selected = np.asarray(source.faces)[ids]
    vertex_ids, inverse = np.unique(selected.reshape(-1), return_inverse=True)
    mesh = trimesh.Trimesh(
        vertices=np.asarray(source.vertices)[vertex_ids],
        faces=inverse.reshape(-1, 3),
        process=False,
    )
    return mesh, ids


def canonical_obj(mesh, path):
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    order = sorted(range(len(vertices)), key=lambda i: tuple(np.round(vertices[i], 12)))
    remap = {old: new + 1 for new, old in enumerate(order)}
    lines = ["v %.12g %.12g %.12g" % tuple(vertices[i]) for i in order]
    mapped = [[remap[int(i)] for i in face] for face in faces]
    lines.extend("f %d %d %d" % tuple(face) for face in sorted(mapped, key=tuple))
    path.write_text("\n".join(lines) + "\n", encoding="ascii")


def render_proxy(mesh, path):
    image = Image.new("RGB", (512, 512), "white")
    draw = ImageDraw.Draw(image)
    vertices = np.asarray(mesh.vertices)
    faces = np.asarray(mesh.faces)
    q = vertices @ np.array([[0.82, -0.35], [0.38, 0.90], [0.42, 0.22]])
    lo = q.min(0)
    span = np.maximum(q.max(0) - lo, 1e-9)
    q = (q - lo) / span
    depth = vertices[faces].mean(1) @ np.array([0.3, 0.2, 1.0])
    ids = np.linspace(0, len(faces) - 1, min(8000, len(faces)), dtype=int)
    for i in ids[np.argsort(depth[ids])]:
        poly = [(int(q[j, 0] * 456 + 28), int(484 - q[j, 1] * 456)) for j in faces[i]]
        draw.polygon(poly, fill=(188, 199, 214), outline=(65, 75, 88))
    image.save(path)


def stage0_source_audit(case):
    source = Path(case["source"])
    dest = OUT / "00_source" / case["case_id"]
    dest.mkdir(parents=True, exist_ok=True)
    mesh = trimesh.load(source, force="mesh", process=False)
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise TypeError(f"{case['case_id']} is not a triangular mesh")
    frozen = dest / "source_frozen.obj"
    shutil.copy2(source, frozen)
    faces = np.asarray(mesh.faces)
    vertices = np.asarray(mesh.vertices, float)
    normals = np.asarray(mesh.face_normals)
    edges = np.sort(np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]])), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    bbox = np.asarray(mesh.bounds, float)
    diag = float(np.linalg.norm(bbox[1] - bbox[0]))
    audit = {
        "schema": "SourceAuditV0",
        "case_id": case["case_id"],
        "SOURCE_OBJ": str(source),
        "SOURCE_SHA256": sha(source),
        "frozen_obj": str(frozen),
        "frozen_sha256": sha(frozen),
        "vertices": int(len(vertices)),
        "triangles": int(len(faces)),
        "connected_components": int(len(mesh.split(only_watertight=False))),
        "bbox": bbox,
        "bbox_diagonal": diag,
        "centroid": np.asarray(mesh.centroid, float),
        "mesh_area": float(mesh.area),
        "watertight": bool(mesh.is_watertight),
        "manifold": bool(np.all(counts <= 2)),
        "boundary_edges": int(np.sum(counts == 1)),
        "nonmanifold_edges": int(np.sum(counts > 2)),
        "scale": diag,
        "geometry_modified": False,
        "normal_status": (
            "FINITE_UNIT"
            if bool(np.isfinite(normals).all() and np.allclose(np.linalg.norm(normals, axis=1), 1.0, atol=1e-5))
            else "REQUIRES_SAFE_NORMAL_NORMALIZATION"
        ),
    }
    dump(dest / "source_audit.json", audit)
    dump(dest / "coordinate_frame.json", {"SOURCE_TO_WORLD": np.eye(4).tolist(), "WORLD_TO_SOURCE": np.eye(4).tolist()})
    print(case["case_id"], "triangles", audit["triangles"], "manifold", audit["manifold"], flush=True)
    return audit


def stage1_p3(case, gpu):
    dest = OUT / "01_part_discovery" / case["case_id"] / "p3"
    dest.mkdir(parents=True, exist_ok=True)
    labels_path = dest / "triangle_part_id.npy"
    if labels_path.is_file() and (dest / "part_metadata.json").is_file():
        meta = load(dest / "part_metadata.json")
        print(case["case_id"], "P3 already present", meta.get("num_parts"), flush=True)
        return meta
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    env["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
    run(
        [str(HUNYUAN), str(P3_RUNNER), str(case["source"]), str(dest), "--prompt-bs", "4"],
        OUT / "logs" / f"p3_{case['case_id']}.log",
        env=env,
        timeout=3600,
    )
    meta = load(dest / "part_metadata.json")
    labels = np.load(labels_path, allow_pickle=False)
    source = trimesh.load(case["source"], force="mesh", process=False)
    if len(labels) != len(source.faces):
        raise RuntimeError(f"{case['case_id']} P3 label count mismatch")
    print(case["case_id"], "P3_PARTS", meta["num_parts"], flush=True)
    return meta


def stage1_physx(case, gpu):
    dest = OUT / "01_part_discovery" / case["case_id"] / "physx"
    render_dir = dest / "input"
    render_dir.mkdir(parents=True, exist_ok=True)
    png = render_dir / f"{case['case_id']}.png"
    meta_path = render_dir / "render_metadata.json"
    if not png.is_file():
        env = os.environ.copy()
        env["MPLBACKEND"] = "Agg"
        run(
            [
                str(MACPY),
                str(RENDER_RUNNER),
                str(case["source"]),
                str(png),
                "--metadata",
                str(meta_path),
                "--views",
                "isometric,side,top,front",
                "--shaded",
            ],
            OUT / "logs" / f"physx_render_{case['case_id']}.log",
            env=env,
            timeout=600,
        )
    images = [render_dir / f"{case['case_id']}_{view}.png" for view in ("isometric", "side", "top", "front")]
    if not images[0].is_file():
        images = [png]
    if (dest / "physx_global.json").is_file() and (dest / "provenance.json").is_file():
        print(case["case_id"], "PhysX already present", flush=True)
        return load(dest / "physx_global.json")
    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = str(gpu)
    env["HF_HUB_OFFLINE"] = "1"
    env["TRANSFORMERS_OFFLINE"] = "1"
    env["TOKENIZERS_PARALLELISM"] = "false"
    cmd = [str(HUNYUAN), str(PHYSX_RUNNER), "--output-dir", str(dest), "--images"] + [str(p) for p in images]
    run(cmd, OUT / "logs" / f"physx_{case['case_id']}.log", env=env, timeout=1800)
    parsed = load(dest / "physx_global.json")
    print(case["case_id"], "PHYSX", parsed.get("object_name"), "parts", len(parsed.get("parts") or []), flush=True)
    return parsed


def reliability_gate(case, p3_meta, physx):
    p3_n = int(p3_meta["num_parts"])
    physx_parts = physx.get("parts") or []
    aligned = len(physx_parts) == p3_n and p3_n > 0
    gate = {
        "schema": "ReliabilityGateV1",
        "case_id": case["case_id"],
        "p3_segment_count": p3_n,
        "physx_part_count": len(physx_parts),
        "ONE_TO_ONE_COUNT_MATCH": aligned,
        "physx_policy": "ONE_TO_ONE_COUNT_MATCH" if aligned else "SOFT_OBJECT_LEVEL_PRIOR_ONLY",
        "object_name": physx.get("object_name"),
        "object_category": physx.get("object_category"),
        "semantic_prior_is_soft": True,
        "geometry_owns_measurements": True,
        "physx_may_override_bbox_or_scale": False,
        "final_semantic_roles": (
            [{"p3_segment": i, "role": physx_parts[i].get("part_name") or f"P3_PART_{i:03d}"} for i in range(p3_n)]
            if aligned
            else [{"p3_segment": i, "role": f"P3_PART_{i:03d}"} for i in range(p3_n)]
        ),
    }
    dump(OUT / "01_part_discovery" / case["case_id"] / "reliability_gate.json", gate)
    return gate


def stage2_part_graph(case, gate):
    sys.path.insert(0, str(V9))
    from part_graph.automatic_graph import build_automatic_part_graph

    p3_dir = OUT / "01_part_discovery" / case["case_id"] / "p3"
    graph_dir = OUT / "02_cad_part_graph" / case["case_id"]
    auto = build_automatic_part_graph(p3_dir, graph_dir / "automatic", threshold=0.65)
    source = trimesh.load(case["source"], force="mesh", process=False)
    labels = np.load(p3_dir / "triangle_part_id.npy", allow_pickle=False)
    role_by_seg = {row["p3_segment"]: row["role"] for row in gate["final_semantic_roles"]}
    nodes = []
    for k, auto_node in enumerate(auto["nodes"]):
        pid = f"CADPART_{k:03d}"
        segments = auto_node["segments"]
        mesh, ids = source_part(source, labels, segments)
        path = graph_dir / pid / "source_part.obj"
        path.parent.mkdir(parents=True, exist_ok=True)
        mesh.export(path)
        center, axes, values = pca(np.asarray(mesh.vertices, float))
        gclass, ratios, components = geometry_class(mesh)
        roles = [role_by_seg.get(s, f"P3_PART_{s:03d}") for s in segments]
        semantic = roles[0] if len(set(roles)) == 1 else "+".join(roles)
        axis_index = int(np.argmax(np.ptp((np.asarray(mesh.vertices, float) - center) @ axes.T, axis=0)))
        nodes.append(
            {
                "part_id": pid,
                "p3_segments": segments,
                "semantic_label": semantic,
                "geometry_role": gclass,
                "physx_alignment_policy": gate["physx_policy"],
                "geometry_class": gclass,
                "shape_ratios": ratios,
                "connected_components": components,
                "support_triangle_ids": ids.tolist(),
                "support_triangle_count": len(ids),
                "source_part_mesh": str(path),
                "source_part_mesh_sha256": sha(path),
                "bbox": mesh.bounds,
                "centroid": mesh.centroid,
                "area": mesh.area,
                "local_coordinate_frame": axes,
                "principal_values": values,
                "longitudinal_axis_index": axis_index,
                "local_to_global_transform": np.eye(4),
                "T_part_to_source": np.eye(4).tolist(),
                "fusion_evidence": [
                    "VERIFIED_P3_TRIANGLE_SUPPORT",
                    "PHYSX_SOFT_PRIOR",
                    "HIGH_POLY_GEOMETRY",
                    "CONNECTIVITY",
                    "V9_AUTOMATIC_MERGE",
                ],
                "old_step_used_for_reconstruction": False,
            }
        )
    graph = {
        "schema": "CADPartGraphFusionV6_V9Merge",
        "case_id": case["case_id"],
        "CAD_PART_GRAPH_FRESH": True,
        "source_obj": str(case["source"]),
        "source_obj_sha256": sha(case["source"]),
        "p3_artifact": str(p3_dir / "triangle_part_id.npy"),
        "p3_artifact_sha256": sha(p3_dir / "triangle_part_id.npy"),
        "physx_artifact": str(OUT / "01_part_discovery" / case["case_id"] / "physx/physx_global.json"),
        "p3_segment_count": auto["p3_segment_count"],
        "part_count": len(nodes),
        "automatic_part_merge_used": True,
        "merge_decisions": auto["merge_decisions"],
        "hierarchy": auto["hierarchy"],
        "nodes": nodes,
        "geometry_source_policy": "ORIGINAL_OBJ_TRIANGLES_ONLY",
        "historical_step_used": False,
        "transform_restore_effective": False,
    }
    dump(graph_dir / "cad_part_graph.json", graph)
    print(case["case_id"], "CAD_PARTS", len(nodes), "from P3", auto["p3_segment_count"], flush=True)
    return graph


def exact_analysis(case_id, node):
    mesh = trimesh.load(node["source_part_mesh"], force="mesh", process=False)
    vertices = np.asarray(mesh.vertices, float)
    center, axes, values = pca(vertices)
    local = (vertices - center) @ axes.T
    axis = int(node["longitudinal_axis_index"])
    lo, hi = local[:, axis].min(), local[:, axis].max()
    stations = []
    for coordinate in np.linspace(lo, hi, 32):
        window = max((hi - lo) / 64, 1e-8)
        points = local[np.abs(local[:, axis] - coordinate) <= window]
        stations.append(
            {
                "coordinate": float(coordinate),
                "sample_count": int(len(points)),
                "local_bbox": [points.min(0), points.max(0)] if len(points) else None,
                "topology_role": "FITTING_CONSTRAINT_ONLY",
            }
        )
    angles = np.asarray(mesh.face_adjacency_angles)
    analysis = {
        "schema": "GeometryAnalyzerV6",
        "case_id": case_id,
        "part_id": node["part_id"],
        "measurement_source": "ORIGINAL_HIGH_POLY_SOURCE_TRIANGLES",
        "source_part_mesh": node["source_part_mesh"],
        "source_part_mesh_sha256": node["source_part_mesh_sha256"],
        "proxy_used_for_measurement": False,
        "triangle_count": len(mesh.faces),
        "vertex_count": len(mesh.vertices),
        "bbox": mesh.bounds,
        "extents": mesh.extents,
        "centroid": mesh.centroid,
        "area": mesh.area,
        "watertight": mesh.is_watertight,
        "principal_axes": axes,
        "principal_values": values,
        "longitudinal_axis_index": axis,
        "profiles": stations,
        "span": float(hi - lo),
        "thickness": float(np.min(mesh.extents)),
        "sharp_boundary_count": int(np.sum(angles > np.radians(30))),
        "holes": [],
        "slots": [],
        "pattern_evidence": {"component_count": node["connected_components"]},
    }
    dump(OUT / "03_geometry_analyzer" / case_id / node["part_id"] / "geometry_analysis.json", analysis)
    return analysis


def semantic_features_intent(case_id, node, analysis):
    gclass = node["geometry_class"]
    if gclass == "THIN_EXTRUSION":
        hypotheses = ["PROFILE_EXTRUSION", "GLOBAL_UPPER_LOWER_SKINS", "GLOBAL_LOFT"]
        roles = ["UPPER_SKIN", "LOWER_SKIN", "ROOT_CAP", "TIP_CAP"]
    elif gclass == "AXIAL_REVOLUTION_OR_SWEEP":
        hypotheses = ["REVOLUTION", "SWEEP", "PERIODIC_GLOBAL_BSPLINE"]
        roles = ["AXIAL_BODY", "START_CAP", "END_CAP"]
    elif gclass == "MULTI_FEATURE":
        hypotheses = ["SUBFEATURE_EXTRUSIONS", "SUBFEATURE_LOFT_UNION", "HYBRID_ANALYTIC_FREEFORM"]
        roles = [f"SUBFEATURE_{i:03d}" for i in range(min(max(node["connected_components"], 1), 16))]
    elif gclass == "VOLUMETRIC_FREEFORM":
        hypotheses = ["SEMANTIC_FREEFORM_SKINS", "PERIODIC_GLOBAL_BSPLINE", "CLOSED_GLOBAL_LOFT"]
        roles = ["GLOBAL_SEMANTIC_SKIN", "CAP_A", "CAP_B"]
    else:
        hypotheses = ["GLOBAL_LOFT", "SEMANTIC_FREEFORM_SKINS", "HYBRID_ANALYTIC_FREEFORM"]
        roles = ["GLOBAL_SEMANTIC_SKIN", "CAP_A", "CAP_B"]
    semantic = {
        "schema": "SemanticSurfaceAnalyzerV2",
        "case_id": case_id,
        "part_id": node["part_id"],
        "part_semantics": node["semantic_label"],
        "geometry_class": gclass,
        "input_mesh": node["source_part_mesh"],
        "input_mesh_sha256": node["source_part_mesh_sha256"],
        "sampling_topology_is_constraint_only": True,
        "mesh_patch_boundaries_final_topology": False,
        "section_sampling_boundaries_final_topology": False,
        "allowed_final_boundaries": [
            "PART_BOUNDARY",
            "SHARP_FEATURE",
            "ANALYTIC_SURFACE_TRANSITION",
            "HOLE",
            "SLOT",
            "TRIM_BOUNDARY",
            "ROOT_TIP",
            "DESIGN_FEATURE_BOUNDARY",
            "REQUIRED_PERIODIC_SEAM",
        ],
        "semantic_surfaces": [
            {"semantic_surface_id": f"SS{i:03d}", "design_role": role, "source": "HIGH_POLY_GEOMETRY+P3+PHYSX_SOFT_PRIOR"}
            for i, role in enumerate(roles)
        ],
    }
    feature = {
        "schema": "CADFeatureGraphV6",
        "case_id": case_id,
        "part_id": node["part_id"],
        "part_semantics": node["semantic_label"],
        "features": [{"feature_id": f"F{i:03d}", "type": role, "source": "semantic_surface_graph+exact_measurement"} for i, role in enumerate(roles)],
        "P3_PHYSX_PART_GRAPH_PRESERVED": True,
    }
    measured = {k: analysis[k] for k in (
        "schema", "case_id", "part_id", "measurement_source", "source_part_mesh", "source_part_mesh_sha256",
        "proxy_used_for_measurement", "triangle_count", "vertex_count", "bbox", "extents", "centroid", "area",
        "watertight", "principal_axes", "principal_values", "longitudinal_axis_index", "span", "thickness",
        "sharp_boundary_count", "holes", "slots", "pattern_evidence",
    )}
    measured["schema"] = "MeasuredCADSpecV6"
    measured["profiles"] = analysis["profiles"]
    intent = {
        "schema": "DesignIntentHypothesisGeneratorV6",
        "case_id": case_id,
        "part_id": node["part_id"],
        "part_semantics": node["semantic_label"],
        "hypotheses": [
            {"hypothesis_id": f"H{i+1}", "representation": h, "sampling_topology_is_constraint_only": True}
            for i, h in enumerate(hypotheses)
        ],
    }
    dump(OUT / "04_semantic_surface" / case_id / node["part_id"] / "semantic_surface_graph.json", semantic)
    dump(OUT / "08_cad_feature_graph" / case_id / node["part_id"] / "cad_feature_graph.json", feature)
    dump(OUT / "05_feature_graph" / case_id / node["part_id"] / "cad_feature_graph.json", feature)
    dump(OUT / "05_feature_graph" / case_id / node["part_id"] / "measured_cad_spec.json", measured)
    dump(OUT / "09_measured_cad_spec" / case_id / node["part_id"] / "measured_cad_spec.json", measured)
    dump(OUT / "07_design_intent" / case_id / node["part_id"] / "design_intent_hypotheses.json", intent)
    dump(OUT / "10_design_intent" / case_id / node["part_id"] / "design_intent_hypotheses.json", intent)
    return semantic, intent


def primitive_bank(case_id, node):
    sys.path.insert(0, str(V9))
    from surface_primitives.primitive_selector import fit_primitive_bank

    mesh = trimesh.load(node["source_part_mesh"], force="mesh", process=False)
    bank = fit_primitive_bank(mesh, node["part_id"], node["source_part_mesh"])
    dump(OUT / "05_surface_primitive_bank" / case_id / node["part_id"] / "primitive_bank.json", bank)
    return bank


def dual_modal(case_id, node):
    mesh = trimesh.load(node["source_part_mesh"], force="mesh", process=False)
    target = 512 if len(mesh.faces) > 30000 else 256
    try:
        proxy = mesh.simplify_quadric_decimation(face_count=target, aggression=7)
    except Exception:
        ids = np.linspace(0, len(mesh.faces) - 1, min(target, len(mesh.faces)), dtype=int)
        proxy = trimesh.Trimesh(vertices=mesh.vertices.copy(), faces=mesh.faces[ids].copy(), process=False)
        proxy.remove_unreferenced_vertices()
    directory = OUT / "06_dual_modal_adapter" / case_id / node["part_id"]
    directory.mkdir(parents=True, exist_ok=True)
    proxy_path = directory / "proxy.obj"
    proxy.export(proxy_path)
    tokens = directory / "canonical_obj_tokens.txt"
    canonical_obj(proxy, tokens)
    image = directory / "axonometric_render.png"
    render_proxy(proxy, image)
    nearest = cKDTree(np.asarray(mesh.triangles_center)).query(np.asarray(proxy.triangles_center))[1]
    np.save(directory / "proxy_to_source_face.npy", nearest, allow_pickle=False)
    dump(
        directory / "dual_modal_mesh_adapter.json",
        {
            "schema": "DualModalMeshAdapterV6",
            "case_id": case_id,
            "part_id": node["part_id"],
            "source_mesh": node["source_part_mesh"],
            "source_triangle_count": len(mesh.faces),
            "proxy_mesh": str(proxy_path),
            "proxy_triangle_count": len(proxy.faces),
            "target_triangle_count": target,
            "canonical_obj_tokens": str(tokens),
            "canonical_obj_sha256": sha(tokens),
            "axonometric_render": str(image),
            "axonometric_render_sha256": sha(image),
            "preserve_original_part_scale": True,
            "proxy_measurements_may_override_exact": False,
        },
    )


def prepare_case(case, graph):
    rows = []
    for node in graph["nodes"]:
        analysis = exact_analysis(case["case_id"], node)
        semantic_features_intent(case["case_id"], node, analysis)
        try:
            primitive_bank(case["case_id"], node)
        except Exception as exc:
            dump(
                OUT / "05_surface_primitive_bank" / case["case_id"] / node["part_id"] / "primitive_bank.json",
                {"part_id": node["part_id"], "error": f"{type(exc).__name__}: {exc}", "status": "PARTIAL"},
            )
        dual_modal(case["case_id"], node)
        rows.append({"part_id": node["part_id"], "geometry_class": node["geometry_class"], "triangles": node["support_triangle_count"]})
        print(case["case_id"], node["part_id"], node["geometry_class"], flush=True)
    return rows


def stage_mac(case_id=None):
    cmd = [str(MACPY), str(MAC_RUNNER)]
    if case_id:
        cmd += ["--case", case_id]
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    run(cmd, OUT / "logs" / f"mac_{case_id or 'all'}.log", env=env, timeout=None)


def verify_candidate(manifest_path, source_mesh, semantic_count):
    Q = module("qa_worker", ROOT / "part_to_cad_recovery_fix_v1/scripts/run_recovery.py")
    N = module("native_worker", ROOT / "batch10_semantic_mesh2cad_tts_v5/scripts/pipeline.py")
    manifest = load(manifest_path)
    step = Path(manifest["step"])
    if manifest.get("execution_exit_code") != 0 or not step.is_file():
        return {**manifest, "PROGRAM_STATUS": "INVALID_PROGRAM", "BREP_VALID": False, "HARD_GATE_PASS": False}
    try:
        qa = Q.qa_step(step, source_mesh)
        nat = N.occ_nativeness(step, 1)
        faces = int(qa.get("FACE_COUNT") or 0)
        edges = int(qa.get("EDGE_COUNT") or 0)
        feature_pass = qa.get("GEOMETRY_Q") in ("Q1", "Q2") and float(qa.get("COVERAGE02") or 0) >= 0.85
        fragmentation = float(
            min(
                1.0,
                nat.get("MESH_LIKE_BREP_SCORE", 1)
                + 0.25 * nat.get("TINY_FACE_RATIO", 0)
                + 0.2 * nat.get("SHORT_EDGE_RATIO", 0)
                + 0.15 * min(1, faces / max(semantic_count * 12, 1)),
            )
        )
        row = {
            **manifest,
            "PROGRAM_STATUS": "VALID_PROGRAM",
            "BREP_VALID": bool(qa.get("BRep_valid")),
            "GEOM_Q": qa.get("GEOMETRY_Q"),
            "CHAMFER": qa.get("NORMALIZED_SYMMETRIC_CHAMFER"),
            "P95": qa.get("P95"),
            "COVERAGE02": qa.get("COVERAGE02"),
            "FACES": faces,
            "EDGES": edges,
            "ARTIFICIAL_EDGES": nat.get("ARTIFICIAL_EDGE_COUNT"),
            "TINY_FACE_RATIO": qa.get("TINY_FACE_RATIO"),
            "SHORT_EDGE_RATIO": qa.get("SHORT_EDGE_RATIO"),
            "MESH_LIKE_BREP_SCORE": nat.get("MESH_LIKE_BREP_SCORE"),
            "FRAGMENTATION_SCORE": fragmentation,
            "ANALYTIC_RATIO": qa.get("ANALYTIC_FACE_RATIO"),
            "BSPLINE_RATIO": qa.get("BSPLINE_FACE_RATIO"),
        }
        row["CAD_NATIVENESS_Q"] = "PASS" if row["MESH_LIKE_BREP_SCORE"] is not None and row["MESH_LIKE_BREP_SCORE"] < 0.45 and fragmentation < 0.6 else "FAIL"
        row["HARD_GATE_PASS"] = bool(row["BREP_VALID"] and row["GEOM_Q"] in ("Q1", "Q2") and feature_pass)
        return row
    except Exception as exc:
        return {**manifest, "PROGRAM_STATUS": "INVALID_PROGRAM", "BREP_VALID": False, "HARD_GATE_PASS": False, "verification_error": f"{type(exc).__name__}: {exc}"}


def optimize_part(case_id, node, selected):
    """Freeze representation; search a few section/profile counts against chamfer."""
    Q = module("qa_opt", ROOT / "part_to_cad_recovery_fix_v1/scripts/run_recovery.py")
    representation = selected.get("hypothesis", {}).get("representation") or selected.get("candidate_id", "")
    if "CANDIDATE_" in str(representation) or not representation:
        name = selected.get("candidate_id", "")
        representation = name.split("_", 2)[-1] if "CANDIDATE_" in name else "GLOBAL_LOFT"
    dest = OUT / "13_parameter_optimization" / case_id / node["part_id"]
    dest.mkdir(parents=True, exist_ok=True)
    history = []
    best = None
    for sections, profiles in ((8, 8), (10, 10), (12, 12), (14, 12), (16, 14)):
        step = dest / f"trial_s{sections}_p{profiles}.step"
        try:
            subprocess.run(
                [
                    str(MACPY),
                    str(RUNTIME),
                    "--source-mesh",
                    node["source_part_mesh"],
                    "--representation",
                    representation,
                    "--output",
                    str(step),
                    "--sections",
                    str(sections),
                    "--profile-count",
                    str(profiles),
                    "--tolerance",
                    "0.001",
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=180,
            )
            qa = Q.qa_step(step, node["source_part_mesh"])
            row = {"sections": sections, "profile_count": profiles, "chamfer": qa.get("NORMALIZED_SYMMETRIC_CHAMFER"), "geom_q": qa.get("GEOMETRY_Q"), "step": str(step), "valid": bool(qa.get("BRep_valid"))}
        except Exception as exc:
            row = {"sections": sections, "profile_count": profiles, "error": f"{type(exc).__name__}: {exc}", "valid": False}
        history.append(row)
        if row.get("valid") and row.get("chamfer") is not None:
            if best is None or row["chamfer"] < best["chamfer"]:
                best = row
    if best:
        shutil.copy2(best["step"], dest / "optimized.step")
    dump(dest / "optimization_provenance.json", {"structure_frozen": True, "representation": representation, "history": history, "best": best})
    return best


def ground_part(case_id, node, step_path, semantic):
    V = module("end2end", ROOT / "case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py")
    sys.path.insert(0, str(ROOT / "v8_missing_architecture_completion"))
    from grounding.grounding import ground_query, index_entities

    ok, _roots, shape = V.read_step(Path(step_path)) if hasattr(V, "read_step") else (False, 0, None)
    if not ok or shape is None:
        from OCP.IFSelect import IFSelect_RetDone
        from OCP.STEPControl import STEPControl_Reader

        reader = STEPControl_Reader()
        if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
            return {"status": "UNRESOLVED", "reason": "STEP_READ_FAILED"}
        reader.TransferRoots()
        shape = reader.OneShape()
    index = index_entities(shape, {})
    results = []
    for surface in semantic.get("semantic_surfaces", [])[:4]:
        query = f"{surface['design_role']} face"
        results.append(ground_query(index, query, {}, min_conf=0.35))
    payload = {"part_id": node["part_id"], "queries": results, "face_count": len(index["FACE"]), "edge_count": len(index["EDGE"])}
    dump(OUT / "17_grounding" / case_id / node["part_id"] / "grounding_results.json", payload)
    return payload


def _candidate_manifests(part_dir: Path):
    if not part_dir.is_dir():
        return []
    return sorted(part_dir.glob("*/candidate_manifest.json"))


def _pick_candidate(rows, *, hard_gate: bool):
    qrank = {"Q1": 0, "Q2": 1, "Q3": 2, "S1": 3, None: 4}
    pool = [r for r in rows if r.get("HARD_GATE_PASS")] if hard_gate else [
        r for r in rows if r.get("PROGRAM_STATUS") == "VALID_PROGRAM" and r.get("BREP_VALID")
    ]
    if not pool:
        return None
    return min(
        pool,
        key=lambda r: (
            qrank.get(r.get("GEOM_Q"), 4),
            r.get("CHAMFER") if r.get("CHAMFER") is not None else 1e9,
            r.get("P95") if r.get("P95") is not None else 1e9,
        ),
    )


def _assemble_selected(case, graph, chosen_by_part, label_suffix):
    V = module("end2end", ROOT / "case09_aircraft_end2end_cad_v1/scripts/end2end_pipeline.py")
    Q = module("qa_main", ROOT / "part_to_cad_recovery_fix_v1/scripts/run_recovery.py")
    N = module("native_main", ROOT / "batch10_semantic_mesh2cad_tts_v5/scripts/pipeline.py")
    selected = []
    selection_rows = []
    nodes = {node["part_id"]: node for node in graph["nodes"]}
    for part_id, chosen in chosen_by_part.items():
        node = nodes[part_id]
        step = Path(chosen["step"])
        ok, _roots, shape = (False, 0, None)
        try:
            ok, _roots, shape = V.read_step(step)
        except Exception:
            from OCP.IFSelect import IFSelect_RetDone
            from OCP.STEPControl import STEPControl_Reader

            reader = STEPControl_Reader()
            if reader.ReadFile(str(step)) == IFSelect_RetDone:
                reader.TransferRoots()
                shape = reader.OneShape()
                ok = True
        if ok and shape is not None:
            selected.append((part_id, shape))
            selection_rows.append(
                {
                    "part_id": part_id,
                    "candidate": chosen.get("candidate_id"),
                    "GEOM_Q": chosen.get("GEOM_Q"),
                    "CHAMFER": chosen.get("CHAMFER"),
                }
            )
    final = OUT / "20_xcaf_assembly" / case["case_id"] / f"{case['case_id']}_{label_suffix}.step"
    xcaf = False
    assembly_error = None
    whole = {}
    nat = {}
    if selected:
        final.parent.mkdir(parents=True, exist_ok=True)
        xcaf, assembly_error = V.write_xcaf(selected, final)
        if final.is_file():
            whole = Q.qa_step(final, Path(graph["source_obj"]))
            nat = N.occ_nativeness(final, max(len(selected), 1))
    return {
        "step": str(final) if final.is_file() else None,
        "xcaf": xcaf,
        "error": assembly_error,
        "parts": len(selected),
        "selection": selection_rows,
        "GEOM_Q": whole.get("GEOMETRY_Q"),
        "CHAMFER": whole.get("NORMALIZED_SYMMETRIC_CHAMFER"),
        "P95": whole.get("P95"),
        "COVERAGE02": whole.get("COVERAGE02"),
        "TOTAL_FACES": whole.get("FACE_COUNT"),
        "TOTAL_EDGES": whole.get("EDGE_COUNT"),
        "MESH_LIKE_BREP_SCORE": nat.get("MESH_LIKE_BREP_SCORE"),
    }


def assemble_and_rank(case, graph, *, mainline: bool = False):
    rankings = []
    relaxed_choices = {}
    for node in graph["nodes"]:
        semantic = load(OUT / "04_semantic_surface" / case["case_id"] / node["part_id"] / "semantic_surface_graph.json")
        rows = []
        for manifest in _candidate_manifests(OUT / "08_multi_candidate_mac" / case["case_id"] / node["part_id"]):
            row = verify_candidate(manifest, node["source_part_mesh"], len(semantic["semantic_surfaces"]))
            dump(manifest.parent / "cad_nativeness_verifier.json", row)
            rows.append(row)
        hard = _pick_candidate(rows, hard_gate=True)
        relaxed = _pick_candidate(rows, hard_gate=False)
        ranking = {
            "case_id": case["case_id"],
            "part_id": node["part_id"],
            "candidates": rows,
            "GEOMETRY_OPTIMAL_CANDIDATE": hard and hard.get("candidate_id"),
            "CAD_NATIVE_OPTIMAL_CANDIDATE": hard and hard.get("candidate_id"),
            "SELECTED_CANDIDATE": hard and hard.get("candidate_id"),
            "BEST_AVAILABLE_CANDIDATE": relaxed and relaxed.get("candidate_id"),
        }
        dump(OUT / "09_candidate_ranking" / case["case_id"] / node["part_id"] / "ranking.json", ranking)
        dump(OUT / "16_nativeness_tts" / case["case_id"] / node["part_id"] / "ranking.json", ranking)
        rankings.append(ranking)
        if relaxed:
            relaxed_choices[node["part_id"]] = relaxed
        chosen = hard
        if not chosen:
            continue
        opt = optimize_part(case["case_id"], node, chosen)
        step = Path(opt["step"]) if opt else Path(chosen["step"])
        accepted = OUT / "10_selected_parts" / case["case_id"] / node["part_id"]
        accepted.mkdir(parents=True, exist_ok=True)
        shutil.copy2(step, accepted / "selected.step")
        if Path(chosen.get("program", "")).is_file():
            shutil.copy2(chosen["program"], accepted / "generated_code.py")
        try:
            ground_part(case["case_id"], node, step, semantic)
        except Exception as exc:
            dump(OUT / "17_grounding" / case["case_id"] / node["part_id"] / "grounding_results.json", {"error": f"{type(exc).__name__}: {exc}"})
    dump(
        OUT / "19_transform_restore" / case["case_id"] / "transforms.json",
        {
            "policy": "SOURCE_GLOBAL_IDENTITY",
            "reason": "parts were measured and built in source coordinates; no localization was applied",
            "T_part_to_source": {n["part_id"]: n["T_part_to_source"] for n in graph["nodes"]},
        },
    )
    hard_gate_choices = {}
    for node in graph["nodes"]:
        sel = OUT / "10_selected_parts" / case["case_id"] / node["part_id"] / "selected.step"
        if not sel.is_file():
            continue
        ranking = load(OUT / "09_candidate_ranking" / case["case_id"] / node["part_id"] / "ranking.json")
        cid = ranking.get("SELECTED_CANDIDATE")
        if not cid:
            continue
        for row in ranking["candidates"]:
            if row.get("candidate_id") == cid:
                chosen = dict(row)
                chosen["step"] = str(sel)
                hard_gate_choices[node["part_id"]] = chosen
                break
    hard_assembly = _assemble_selected(case, graph, hard_gate_choices, "fullstack")
    best_assembly = _assemble_selected(case, graph, relaxed_choices, "best_available")
    dump(
        OUT / "artifacts" / case["case_id"] / "best_available.json",
        {
            "case_id": case["case_id"],
            "parts": best_assembly["parts"],
            "xcaf": best_assembly["xcaf"],
            "error": best_assembly["error"],
            "step": best_assembly["step"],
            "selection": best_assembly["selection"],
        },
    )
    summary = {
        "case_id": case["case_id"],
        "PIPELINE": "TWO_MESH_MAINLINE_V1" if mainline else "TWO_MESH_FULLSTACK_LATEST",
        "MAINLINE_V6_BACKEND": mainline,
        "PART_COUNT": len(graph["nodes"]),
        "PARTS_HARD_GATE_PASS": hard_assembly["parts"],
        "PARTS_BEST_AVAILABLE": best_assembly["parts"],
        "FINAL_STEP": hard_assembly["step"],
        "BEST_AVAILABLE_STEP": best_assembly["step"],
        "XCAF_ASSEMBLY_PRESENT": hard_assembly["xcaf"],
        "XCAF_ERROR": hard_assembly["error"],
        "GEOM_Q": hard_assembly.get("GEOM_Q"),
        "CHAMFER": hard_assembly.get("CHAMFER"),
        "P95": hard_assembly.get("P95"),
        "COVERAGE02": hard_assembly.get("COVERAGE02"),
        "TOTAL_FACES": hard_assembly.get("TOTAL_FACES"),
        "TOTAL_EDGES": hard_assembly.get("TOTAL_EDGES"),
        "MESH_LIKE_BREP_SCORE": hard_assembly.get("MESH_LIKE_BREP_SCORE"),
        "CAD_NATIVENESS_Q": "PASS" if (hard_assembly.get("MESH_LIKE_BREP_SCORE") or 1) < 0.45 else "FAIL",
        "rankings": [{"part_id": r["part_id"], "selected": r["SELECTED_CANDIDATE"]} for r in rankings],
    }
    dump(OUT / "artifacts" / case["case_id"] / "summary.json", summary)
    print(
        case["case_id"],
        "ASSEMBLY",
        summary["FINAL_STEP"],
        "hard",
        f"{hard_assembly['parts']}/{len(graph['nodes'])}",
        "best",
        f"{best_assembly['parts']}/{len(graph['nodes'])}",
        flush=True,
    )
    return summary


def stage_v6_backend(case_id=None):
    backend = module("generic_v6_backend", OUT / "scripts/generic_v6_backend.py")
    return backend.stage_v6_backend(case_id)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--stage",
        choices=["all", "0", "1p3", "1physx", "2", "mac", "v6_backend", "finalize"],
        default="all",
    )
    parser.add_argument("--case", default=None)
    parser.add_argument("--gpu", type=int, default=None)
    parser.add_argument(
        "--mainline",
        action="store_true",
        help="Add geometry_class V6 backend candidates and best_available assembly.",
    )
    return parser.parse_args()


def selected_cases(case_id):
    if not case_id:
        return CASES
    match = [c for c in CASES if c["case_id"] == case_id]
    if not match:
        raise SystemExit(f"unknown case {case_id}")
    return match


def main():
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    cases = selected_cases(args.case)
    dump(OUT / "00_source/manifest.json", {"schema": "TwoMeshFullstackLatest", "cases": cases})
    if args.stage in ("all", "0"):
        for case in cases:
            stage0_source_audit(case)
    gpu = args.gpu
    if args.stage in ("all", "1p3", "1physx") and gpu is None:
        gpu = pick_gpu()
        print("GPU", gpu, flush=True)
    if args.stage in ("all", "1p3"):
        for case in cases:
            stage1_p3(case, gpu)
    if args.stage in ("all", "1physx"):
        for case in cases:
            stage1_physx(case, gpu)
    if args.stage in ("all", "2"):
        for case in cases:
            p3_meta = load(OUT / "01_part_discovery" / case["case_id"] / "p3/part_metadata.json")
            physx = load(OUT / "01_part_discovery" / case["case_id"] / "physx/physx_global.json")
            gate = reliability_gate(case, p3_meta, physx)
            graph = stage2_part_graph(case, gate)
            prepare_case(case, graph)
    if args.stage in ("all", "mac"):
        for case in cases:
            stage_mac(case["case_id"])
    if args.mainline and args.stage in ("all", "v6_backend"):
        stage_v6_backend(args.case)
    if args.stage in ("all", "finalize"):
        summaries = []
        for case in cases:
            graph = load(OUT / "02_cad_part_graph" / case["case_id"] / "cad_part_graph.json")
            summaries.append(assemble_and_rank(case, graph, mainline=args.mainline))
        gate = "TWO_MESH_MAINLINE_V1" if args.mainline else "TWO_MESH_FULLSTACK_LATEST"
        dump(OUT / "artifacts/final_summary.json", {"CURRENT_GATE": gate, "cases": summaries})
        print(json.dumps({"cases": summaries}, indent=2, default=str))


if __name__ == "__main__":
    main()
