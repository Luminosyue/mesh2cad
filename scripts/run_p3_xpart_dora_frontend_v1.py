#!/usr/bin/env python3
"""P3-SAM + X-Part + Dora Front-End Canary V1 for tank mesh."""

from __future__ import annotations

import argparse
import os
import sys

# Bind GPU before importing torch.
_gpu = "3"
if "--gpu" in sys.argv:
    _gpu = sys.argv[sys.argv.index("--gpu") + 1]
os.environ["CUDA_VISIBLE_DEVICES"] = _gpu
os.environ.setdefault(
    "HY3DGEN_MODELS",
    "/data/home/cuiyuehan/project/mesh2cad/ours3/.cache/xpart",
)

import csv
import json
import shutil
import subprocess
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pytorch_lightning as pl
import torch
import trimesh
from PIL import Image, ImageDraw

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT_ROOT = ROOT / "ours3/p3_xpart_dora_frontend_v1"
SOURCE_MESH = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
FROZEN_P3 = ROOT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
HUNYUAN_ROOT = ROOT / "Hunyuan3D-Part"
DORA_ROOT = ROOT / "Dora"
MODEL_CACHE = ROOT / "ours3/.cache/xpart/tencent/Hunyuan3D-Part"
P3_WEIGHTS = HUNYUAN_ROOT / "P3-SAM/weights/p3sam.safetensors"

DORA_POINT_COUNTS = (5000, 10000, 20000)
DORA_PRIMARY_POINTS = 10000
DORA_ANGLE_DEG = 15.0


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2, default=str)
        handle.write("\n")


def git_commit(repo: Path) -> str:
    try:
        return (
            subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True)
            .strip()
        )
    except Exception:
        return "unknown"


def bootstrap_xpart_configs(model_dir: Path) -> None:
    infer = XPART_ROOT / "partgen/config/infer.yaml"
    try:
        import yaml

        cfg = yaml.safe_load(infer.read_text(encoding="utf-8"))
    except Exception:
        from partgen.utils.misc import get_config_from_file

        sys.path.insert(0, str(XPART_ROOT))
        cfg_obj = get_config_from_file(str(infer))
        cfg = {
            "model": cfg_obj.model,
            "shapevae": cfg_obj.shapevae,
            "conditioner": cfg_obj.conditioner,
            "scheduler": cfg_obj.scheduler,
            "bbox_predictor": cfg_obj.bbox_predictor,
        }
    mapping = {
        "model": cfg["model"],
        "shapevae": cfg["shapevae"],
        "conditioner": cfg["conditioner"],
        "scheduler": cfg["scheduler"],
        "p3sam": cfg["bbox_predictor"],
    }
    for name, body in mapping.items():
        sub = model_dir / name
        sub.mkdir(parents=True, exist_ok=True)
        write_json(sub / "config.json", body)
    root_cond = model_dir / "config.json"
    if root_cond.is_file() and not (model_dir / "conditioner/config.json").is_file():
        shutil.copy2(root_cond, model_dir / "conditioner/config.json")
    p3_target = model_dir / "p3sam/p3sam.safetensors"
    p3_target.parent.mkdir(parents=True, exist_ok=True)
    if P3_WEIGHTS.is_file() and not p3_target.is_file():
        p3_target.symlink_to(P3_WEIGHTS)


def mesh_audit(mesh: trimesh.Trimesh, part_id: str = "") -> dict:
    unique_edges, edge_counts = mesh.edges_unique, np.bincount(mesh.edges_unique_inverse)
    boundary_edges = int(np.sum(edge_counts == 1))
    nonmanifold = int(np.sum(edge_counts > 2))
    components = len(mesh.split(only_watertight=False))
    loops = boundary_edges  # proxy when no explicit loop counter
    bounds = mesh.bounds
    bbox_diag = float(np.linalg.norm(bounds[1] - bounds[0])) if bounds is not None else 0.0
    volume = float(mesh.volume) if mesh.is_watertight else None
    return {
        "part_id": part_id,
        "vertices": int(len(mesh.vertices)),
        "triangles": int(len(mesh.faces)),
        "connected_components": int(components),
        "boundary_edges": boundary_edges,
        "boundary_loops": int(loops),
        "watertight": bool(mesh.is_watertight),
        "winding_consistent": bool(mesh.is_winding_consistent),
        "manifold": bool(mesh.is_watertight and nonmanifold == 0),
        "surface_area": float(mesh.area),
        "volume": volume,
        "bbox_min": bounds[0].tolist(),
        "bbox_max": bounds[1].tolist(),
        "bbox_diagonal": bbox_diag,
    }


def export_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def render_mesh_png(mesh: trimesh.Trimesh, path: Path, title: str = "", color=(180, 185, 190)) -> None:
    angle_z, angle_x = np.deg2rad(-38), np.deg2rad(22)
    rz = np.array([[np.cos(angle_z), -np.sin(angle_z), 0], [np.sin(angle_z), np.cos(angle_z), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, np.cos(angle_x), -np.sin(angle_x)], [0, np.sin(angle_x), np.cos(angle_x)]])
    verts = np.asarray(mesh.vertices)
    centered = verts - (verts.min(0) + verts.max(0)) / 2
    proj = centered @ (rz @ rx).T
    xy = proj[:, :2]
    centers = proj[mesh.faces].mean(axis=1)
    span = np.ptp(centers[:, :2], axis=0)
    cxy = (centers[:, :2].min(0) + centers[:, :2].max(0)) / 2
    limit = max(span) * 0.55 + 1e-6
    res = 640
    px = np.clip(((centers[:, 0] - (cxy[0] - limit)) / (2 * limit) * (res - 1)).astype(int), 0, res - 1)
    py = np.clip(((cxy[1] + limit - centers[:, 1]) / (2 * limit) * (res - 1)).astype(int), 0, res - 1)
    order = np.lexsort((centers[:, 2], py * res + px))
    img = np.full((res, res, 3), 255, dtype=np.uint8)
    seen = {}
    for idx in order:
        key = (py[idx], px[idx])
        if key in seen:
            continue
        seen[key] = True
        img[key] = color
    canvas = Image.fromarray(img)
    if title:
        draw = ImageDraw.Draw(canvas)
        draw.text((8, 8), title, fill=(20, 20, 20))
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path)


def surface_sample(mesh: trimesh.Trimesh, count: int, rng: np.random.Generator) -> np.ndarray:
    pts, _ = trimesh.sample.sample_surface(mesh, count, seed=int(rng.integers(0, 2**31 - 1)))
    return np.asarray(pts, dtype=np.float64)


def chamfer_stats(src_pts: np.ndarray, gen_pts: np.ndarray) -> dict:
    from scipy.spatial import cKDTree

    if len(src_pts) == 0 or len(gen_pts) == 0:
        return {"s2g_mean": None, "g2s_mean": None, "s2g_p50": None, "s2g_p95": None, "hausdorff": None}
    t_gen = cKDTree(gen_pts)
    t_src = cKDTree(src_pts)
    s2g = t_gen.query(src_pts, k=1)[0]
    g2s = t_src.query(gen_pts, k=1)[0]
    return {
        "s2g_mean": float(np.mean(s2g)),
        "g2s_mean": float(np.mean(g2s)),
        "s2g_p50": float(np.percentile(s2g, 50)),
        "s2g_p95": float(np.percentile(s2g, 95)),
        "hausdorff": float(max(np.max(s2g), np.max(g2s))),
    }


def normalize_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True)
    n = np.where(n > 1e-12, n, 1.0)
    return x / n


def sample_sharp_features(mesh: trimesh.Trimesh, count: int, threshold_deg: float, rng: np.random.Generator):
    angles = np.degrees(mesh.face_adjacency_angles)
    adj_edges = mesh.face_adjacency_edges
    sharp_mask = angles >= threshold_deg
    sharp_edges = adj_edges[sharp_mask]
    if len(sharp_edges) == 0:
        thr = float(np.percentile(angles, 85))
        sharp_mask = angles >= thr
        sharp_edges = adj_edges[sharp_mask]
    edge_counts = np.bincount(mesh.edges_unique_inverse, minlength=len(mesh.edges_unique))
    boundary_idx = np.where(edge_counts == 1)[0]
    if len(boundary_idx):
        sharp_edges = np.concatenate([sharp_edges, mesh.edges_unique[boundary_idx]], axis=0)
    if len(sharp_edges) == 0:
        sharp_edges = mesh.edges_unique
    verts = mesh.vertices.astype(np.float64)
    lengths = np.linalg.norm(verts[sharp_edges[:, 0]] - verts[sharp_edges[:, 1]], axis=1)
    lengths = np.where(lengths > 1e-12, lengths, 1e-12)
    probs = lengths / lengths.sum()
    edge_idx = rng.choice(len(sharp_edges), size=count, replace=True, p=probs)
    t = rng.random(count)
    a = verts[sharp_edges[edge_idx, 0]]
    b = verts[sharp_edges[edge_idx, 1]]
    pts = ((1.0 - t)[:, None] * a + t[:, None] * b).astype(np.float32)
    edge_angles = angles[sharp_mask][edge_idx % max(len(angles[sharp_mask]), 1)] if len(angles[sharp_mask]) else np.full(count, 90.0, np.float32)
    scores = np.clip(edge_angles.astype(np.float32) / 180.0, 0.0, 1.0)
    return pts, scores, sharp_edges


def project_points_to_mesh(points: np.ndarray, mesh: trimesh.Trimesh) -> dict:
    closest, dist, tri = trimesh.proximity.closest_point(mesh, points)
    vid = mesh.faces[tri].reshape(-1)
    nearest_vertex = vid.reshape(len(points), 3)[:, 0]
    return {
        "nearest_vertex_id": nearest_vertex.astype(np.int64),
        "nearest_triangle_id": tri.astype(np.int64),
        "projection_distance": dist.astype(np.float32),
        "projected_points": closest.astype(np.float32),
    }


def pca_shape_stats(mesh: trimesh.Trimesh) -> dict:
    pts = np.asarray(mesh.vertices)
    c = pts.mean(0)
    _, s, _ = np.linalg.svd(pts - c, full_matrices=False)
    s = s / (s.sum() + 1e-12)
    bounds = mesh.bounds
    ext = bounds[1] - bounds[0]
    aspect = float(ext.max() / (ext.min() + 1e-12))
    return {"pca_ratios": s.tolist(), "aspect_ratio": aspect, "linear_ratio": float(s[0])}


def select_canaries(part_rows: list[dict], xpart_dir: Path) -> dict:
    scored = []
    for row in part_rows:
        pid = row["part_id"]
        mesh_path = xpart_dir / pid / "generated_mesh.obj"
        if not mesh_path.is_file():
            continue
        mesh = trimesh.load(mesh_path, force="mesh", process=False)
        stats = pca_shape_stats(mesh)
        scored.append({**row, **stats, "mesh_path": str(mesh_path)})
    if not scored:
        return {}
    planar = max(scored, key=lambda r: (1.0 - r["pca_ratios"][2]) * r["surface_area"])
    rotational = max(scored, key=lambda r: (1.0 - abs(r["pca_ratios"][0] - r["pca_ratios"][1])) * (1.0 / (r["aspect_ratio"] + 1e-6)))
    thin = max(scored, key=lambda r: r["pca_ratios"][0] / (r["pca_ratios"][2] + 1e-6))
    return {
        "CANARY_A_PLANAR": planar["part_id"],
        "CANARY_B_ROTATIONAL": rotational["part_id"],
        "CANARY_C_THIN": thin["part_id"],
        "details": {"planar": planar, "rotational": rotational, "thin": thin},
    }


def stage_p3_baseline(out: Path) -> tuple[list[dict], dict]:
    rows = []
    for obj in sorted(FROZEN_P3.glob("part_*.obj")):
        mesh = trimesh.load(obj, force="mesh", process=False)
        row = mesh_audit(mesh, part_id=f"PART_{int(obj.stem.split('_')[1]):03d}")
        row["source_path"] = str(obj)
        rows.append(row)
    export_csv(out / "mesh_qa/p3_part_mesh_audit.csv", rows)
    write_json(out / "mesh_qa/p3_part_mesh_audit.json", rows)
    wt = sum(1 for r in rows if r["watertight"])
    summary = {
        "source": "frozen_p3_max_367k_4000",
        "part_count": len(rows),
        "P3_WATERTIGHT_PARTS": wt,
        "P3_NON_WATERTIGHT_PARTS": len(rows) - wt,
        "P3_WATERTIGHT_RATE": wt / max(len(rows), 1),
    }
    write_json(out / "p3/baseline_frozen_summary.json", summary)
    return rows, summary


def stage_xpart(out: Path, gpu: int, seed: int) -> dict:
    os.environ.setdefault("HY3DGEN_MODELS", str(MODEL_CACHE.parent.parent))
    bootstrap_xpart_configs(MODEL_CACHE)
    sys.path.insert(0, str(HUNYUAN_ROOT / "P3-SAM"))
    sys.path.insert(0, str(XPART_ROOT))
    from partgen.partformer_pipeline import PartFormerPipeline
    from partgen.utils.mesh_utils import sample_bbox_points_from_trimesh
    import partgen.bbox_estimator.auto_mask_api as ama

    orig_get_mask = ama.get_mask

    def get_mask_chunked(model, feats, points, point_prompt, iter=1):
        chunk = 8
        if point_prompt.shape[0] <= chunk:
            return orig_get_mask(model, feats, points, point_prompt, iter)
        m1s, m2s, m3s, ious = [], [], [], []
        for i in range(0, point_prompt.shape[0], chunk):
            m1, m2, m3, iou = orig_get_mask(
                model, feats, points, point_prompt[i : i + chunk], iter
            )
            m1s.append(m1)
            m2s.append(m2)
            m3s.append(m3)
            ious.append(iou)
            torch.cuda.empty_cache()
        return (
            np.concatenate(m1s, axis=1),
            np.concatenate(m2s, axis=1),
            np.concatenate(m3s, axis=1),
            np.concatenate(ious, axis=0),
        )

    ama.get_mask = get_mask_chunked

    pl.seed_everything(seed, workers=True)
    pipeline = PartFormerPipeline.from_pretrained(model_path="tencent/Hunyuan3D-Part", verbose=True)
    pipeline.vae.cpu()
    pipeline.model.cpu()
    pipeline.conditioner.cpu()
    torch.cuda.empty_cache()

    source = trimesh.load(SOURCE_MESH, force="mesh", process=False)
    mesh_norm, center, scale = pipeline.normalize_mesh(source.copy())
    transform = {
        "center": center.tolist(),
        "scale": float(scale),
        "T_source_to_xpart_norm": {"center": center.tolist(), "scale": float(scale)},
        "T_xpart_to_source": {"multiply_scale": float(scale), "add_center": center.tolist()},
    }
    (out / "xpart").mkdir(parents=True, exist_ok=True)
    write_json(out / "xpart/coordinate_transform.json", transform)
    (out / "source").mkdir(parents=True, exist_ok=True)
    shutil.copy2(SOURCE_MESH, out / "source/yC4xcavDg89GZgqjJtUs5KYbrgz.obj")

    t0 = time.time()
    aabb, face_ids, mesh_p3 = pipeline.bbox_predictor.predict_aabb(
        mesh_norm, post_process=True, seed=seed, clean_mesh_flag=False
    )
    p3_dir = out / "p3/raw_output"
    p3_dir.mkdir(parents=True, exist_ok=True)
    np.save(p3_dir / "face_ids.npy", np.asarray(face_ids))
    np.save(p3_dir / "aabb.npy", np.asarray(aabb))
    part_count = int(np.max(face_ids)) + 1 if len(face_ids) else 0
    face_ids = np.asarray(face_ids, dtype=np.int64)
    mesh_faces = np.asarray(mesh_p3.faces)
    parts_manifest = []
    seg_dir = out / "p3/exported_segment_meshes"
    seg_dir.mkdir(parents=True, exist_ok=True)
    for pid in range(part_count):
        tri_mask = face_ids == pid
        faces = mesh_faces[tri_mask]
        if len(faces) == 0:
            continue
        part_mesh = trimesh.Trimesh(
            vertices=np.asarray(mesh_p3.vertices), faces=faces.copy(), process=False
        )
        part_path = seg_dir / f"PART_{pid:03d}.obj"
        part_mesh.export(part_path)
        bb = np.asarray(aabb[pid]) if pid < len(aabb) else part_mesh.bounds
        parts_manifest.append(
            {
                "part_id": f"PART_{pid:03d}",
                "bbox": bb.tolist(),
                "triangle_count": int(len(faces)),
                "vertex_count": int(len(part_mesh.vertices)),
                "source_triangle_ids": np.flatnonzero(tri_mask).tolist()[:200],
                "path": str(part_path),
            }
        )
    write_json(out / "p3/manifest.json", {"source_mesh": str(SOURCE_MESH), "part_count": part_count, "parts": parts_manifest})

    # Free P3 GPU memory before loading X-Part DiT/VAE.
    try:
        pipeline.bbox_predictor.model.cpu()
        pipeline.bbox_predictor.model_parallel.cpu()
    except Exception:
        pass
    torch.cuda.empty_cache()
    pipeline.to(device="cuda", dtype=torch.float32)

    aabb_t = torch.from_numpy(np.asarray(aabb)).float()
    part_surface, valid = sample_bbox_points_from_trimesh(mesh_norm, aabb_t, num_points=81920, seed=seed)
    aabb_t = aabb_t[valid].unsqueeze(0)
    part_surface = part_surface.unsqueeze(0)

    obj_mesh, aux = pipeline(
        mesh=mesh_norm,
        aabb=aabb_t,
        part_surface_inbbox=part_surface,
        octree_resolution=512,
        output_type="trimesh",
        seed=seed,
    )
    runtime = time.time() - t0
    obj_mesh.export(out / "xpart/xpart_assembly.glb")
    if aux:
        aux[0].export(out / "xpart/xpart_bbox.glb")
        aux[1].export(out / "xpart/xpart_input_bbox.glb")
        aux[2].export(out / "xpart/xpart_exploded.glb")

    xpart_manifest = []
    success = 0
    for idx, (name, geom) in enumerate(obj_mesh.geometry.items()):
        if not isinstance(geom, trimesh.Trimesh):
            continue
        part_id = f"PART_{idx:03d}"
        part_dir = out / "xpart" / part_id
        part_dir.mkdir(parents=True, exist_ok=True)
        geom_world = geom.copy()
        geom_world.vertices = geom_world.vertices * scale + center
        geom.export(part_dir / "generated_mesh_norm.obj")
        geom_world.export(part_dir / "generated_mesh.obj")
        audit = mesh_audit(geom_world, part_id=part_id)
        xpart_manifest.append({**audit, "selected": True, "transform_preserved": True})
        success += 1
    write_json(out / "xpart/manifest.json", {"parts": xpart_manifest, "runtime_seconds": runtime})
    return {
        "part_count": success,
        "runtime_seconds": runtime,
        "transform": transform,
        "P3_REEXECUTED": True,
        "P3_REEXECUTE_REASON": "No saved P3 semantic features; official X-Part requires live P3-SAM bbox+features",
    }


def compare_and_qa(out: Path, p3_rows: list[dict]) -> dict:
    x_manifest = json.loads((out / "xpart/manifest.json").read_text())["parts"]
    compare_rows = []
    chamfers = []
    p3_by_id = {r["part_id"]: r for r in p3_rows}
    for xrow in x_manifest:
        pid = xrow["part_id"]
        idx = int(pid.split("_")[1])
        frozen_id = f"PART_{idx:03d}"
        p3_path = FROZEN_P3 / f"part_{idx:03d}.obj"
        x_path = out / "xpart" / pid / "generated_mesh.obj"
        prow = p3_by_id.get(frozen_id)
        if p3_path.is_file() and x_path.is_file():
            p3m = trimesh.load(p3_path, force="mesh", process=False)
            xm = trimesh.load(x_path, force="mesh", process=False)
            rng = np.random.default_rng(42 + idx)
            c = chamfer_stats(surface_sample(p3m, 5000, rng), surface_sample(xm, 5000, rng))
            chamfers.append(c["s2g_p95"])
        else:
            c = {"s2g_p95": None}
        compare_rows.append(
            {
                "PART": pid,
                "P3_WATERTIGHT": prow["watertight"] if prow else None,
                "XPART_WATERTIGHT": xrow["watertight"],
                "P3_BOUNDARY_EDGES": prow["boundary_edges"] if prow else None,
                "XPART_BOUNDARY_EDGES": xrow["boundary_edges"],
                "P3_COMPONENTS": prow["connected_components"] if prow else None,
                "XPART_COMPONENTS": xrow["connected_components"],
                "OBSERVED_SURFACE_P95": c.get("s2g_p95"),
            }
        )
    export_csv(out / "mesh_qa/xpart_part_mesh_audit.csv", x_manifest)
    write_json(out / "mesh_qa/xpart_part_mesh_audit.json", x_manifest)
    export_csv(out / "mesh_qa/p3_vs_xpart_compare.csv", compare_rows)
    wt_x = sum(1 for r in x_manifest if r["watertight"])
    wt_p = sum(1 for r in p3_rows if r["watertight"])
    opened_to_wt = sum(
        1 for r in compare_rows if r["P3_WATERTIGHT"] is False and r["XPART_WATERTIGHT"] is True
    )
    valid_ch = [c for c in chamfers if c is not None]
    return {
        "P3_WATERTIGHT_RATE": wt_p / max(len(p3_rows), 1),
        "XPART_WATERTIGHT_RATE": wt_x / max(len(x_manifest), 1),
        "PARTS_COMPLETED": len(x_manifest),
        "PARTS_STILL_OPEN": sum(1 for r in x_manifest if not r["watertight"]),
        "PARTS_CHANGED_OPEN_TO_WATERTIGHT": opened_to_wt,
        "XPART_OBSERVED_SURFACE_P95": float(np.median(valid_ch)) if valid_ch else None,
    }


def stage_dora(out: Path, canaries: dict) -> dict:
    results = {}
    for key, label in [
        ("CANARY_A_PLANAR", "planar"),
        ("CANARY_B_ROTATIONAL", "wheel"),
        ("CANARY_C_THIN", "rod"),
    ]:
        pid = canaries.get(key)
        if not pid:
            continue
        mesh_path = out / "xpart" / pid / "generated_mesh.obj"
        ddir = out / "dora" / pid
        ddir.mkdir(parents=True, exist_ok=True)
        mesh = trimesh.load(mesh_path, force="mesh", process=False)
        rng = np.random.default_rng(2026)
        sample_pts = surface_sample(mesh, DORA_PRIMARY_POINTS, rng)
        sharp_pts, scores, sharp_edges = sample_sharp_features(mesh, DORA_PRIMARY_POINTS // 2, DORA_ANGLE_DEG, rng)
        proj = project_points_to_mesh(sharp_pts, mesh)
        p3_path = FROZEN_P3 / f"part_{int(pid.split('_')[1]):03d}.obj"
        p3_boundary_dist = None
        if p3_path.is_file():
            p3m = trimesh.load(p3_path, force="mesh", process=False)
            p3_pts = surface_sample(p3m, 3000, rng)
            from scipy.spatial import cKDTree

            d = cKDTree(p3_pts).query(sharp_pts, k=1)[0]
            p3_boundary_dist = float(np.mean(d))
        np.savez_compressed(
            ddir / "dora_feature_points.npz",
            points=sharp_pts,
            scores=scores,
            sampled_points=sample_pts,
        )
        np.savez_compressed(ddir / "dora_projection.npz", **proj)
        write_json(
            ddir / "manifest.json",
            {
                "part_id": pid,
                "canary_type": label,
                "INPUT_POINTS": int(len(sample_pts)),
                "DORA_FEATURE_POINTS": int(len(sharp_pts)),
                "DORA_FEATURE_RATIO": float(len(sharp_pts) / max(len(sample_pts), 1)),
                "DORA_SCORE_MEAN": float(np.mean(scores)),
                "DORA_SCORE_P95": float(np.percentile(scores, 95)),
                "PROJECTION_P95_DISTANCE": float(np.percentile(proj["projection_distance"], 95)),
                "DORA_NEAR_P3_CUT_RATIO": p3_boundary_dist,
            },
        )
        render_mesh_png(mesh, out / "renders" / f"06_dora_{label}_part.png", title=f"{pid} {label}")
        results[pid] = ddir / "manifest.json"
    return {"DORA_CANARY_PARTS": list(results.keys()), "DORA_RUN_SUCCESS": bool(results)}


def render_suite(out: Path, p3_rows: list[dict], canaries: dict) -> None:
    source = trimesh.load(SOURCE_MESH, force="mesh", process=False)
    render_mesh_png(source, out / "renders/01_original_tank.png", "original tank")
    # p3 assembly from frozen parts
    parts = [trimesh.load(p, force="mesh", process=False) for p in sorted(FROZEN_P3.glob("part_*.obj"))[:20]]
    if parts:
        scene = trimesh.util.concatenate(parts)
        render_mesh_png(scene, out / "renders/02_p3_parts.png", "p3 parts (subset)")
    open_parts = sorted([r for r in p3_rows if not r["watertight"]], key=lambda r: -r["boundary_edges"])[:3]
    for i, row in enumerate(open_parts):
        mesh = trimesh.load(row["source_path"], force="mesh", process=False)
        render_mesh_png(mesh, out / "renders" / f"03_p3_open_part_{i:03d}.png", row["part_id"])
    xparts = sorted((out / "xpart").glob("PART_*/generated_mesh.obj"))[:20]
    if xparts:
        scene = trimesh.util.concatenate([trimesh.load(p, force="mesh", process=False) for p in xparts])
        render_mesh_png(scene, out / "renders/04_xpart_complete_parts.png", "xpart parts (subset)")


def write_report(out: Path, meta: dict) -> None:
    lines = ["# P3-SAM + X-Part + Dora Front-End Canary V1\n"]
    for k, v in meta.items():
        lines.append(f"- **{k}**: `{v}`")
    lines.extend(
        [
            "\n## Gates",
            f"- P3_XPART_INTERFACE: {meta.get('P3_XPART_GATE')}",
            f"- XPART_COMPLETION: {meta.get('XPART_COMPLETION_GATE')}",
            f"- DORA_FRONTEND: {meta.get('DORA_FRONTEND_GATE')}",
            "\n## Q&A",
            "Q1 official链路: see P3_XPART_GATE",
            "Q2 更完整part mesh: compare watertight rates",
            "Q3 watertight提升: PARTS_CHANGED_OPEN_TO_WATERTIGHT",
            "Q4 visible surface: XPART_OBSERVED_SURFACE_P95",
            "Q5 Dora on X-Part: DORA_RUN_SUCCESS",
            "Q6 sharp on design features: inspect renders/06_*",
            "Q7 P3 cut response: DORA_NEAR_P3_CUT_RATIO in dora manifests",
        ]
    )
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=OUT_ROOT)
    parser.add_argument("--gpu", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-xpart", action="store_true")
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    meta = {
        "P3_REPO_FOUND": HUNYUAN_ROOT.is_dir(),
        "XPART_REPO_FOUND": XPART_ROOT.is_dir(),
        "P3_COMMIT": git_commit(HUNYUAN_ROOT),
        "XPART_COMMIT": git_commit(HUNYUAN_ROOT),
        "P3_WEIGHT_FOUND": P3_WEIGHTS.is_file(),
        "XPART_WEIGHT_FOUND": (MODEL_CACHE / "model/model.safetensors").is_file(),
        "XPART_RELEASE": "light",
        "SOURCE_CASE": SOURCE_MESH.name,
        "SOURCE_TRIANGLES": int(len(trimesh.load(SOURCE_MESH, force="mesh").faces)),
        "ARTIFACT_ROOT": str(out),
    }

    p3_rows, p3_summary = stage_p3_baseline(out)
    meta.update(p3_summary)

    if not args.skip_xpart:
        xpart_info = stage_xpart(out, args.gpu, args.seed)
        meta.update(xpart_info)
        qa = compare_and_qa(out, p3_rows)
        meta.update(qa)
        canaries = select_canaries(json.loads((out / "xpart/manifest.json").read_text())["parts"], out / "xpart")
        meta["DORA_CANARY_PARTS"] = canaries
        dora_info = stage_dora(out, canaries)
        meta.update(dora_info)
        render_suite(out, p3_rows, canaries)
        meta["P3_XPART_GATE"] = "PASS" if meta.get("PARTS_COMPLETED", 0) > 0 else "FAIL"
        meta["XPART_COMPLETION_GATE"] = "PASS" if meta.get("XPART_WATERTIGHT_RATE", 0) > meta.get("P3_WATERTIGHT_RATE", 0) else "PARTIAL"
        meta["DORA_FRONTEND_GATE"] = "PASS" if meta.get("DORA_RUN_SUCCESS") else "FAIL"
        meta["CURRENT_GATE"] = (
            "P3_XPART_DORA_FRONTEND_V1_PASS"
            if meta["P3_XPART_GATE"] == "PASS" and meta["DORA_FRONTEND_GATE"] == "PASS"
            else "P3_XPART_DORA_FRONTEND_V1_PARTIAL"
        )
    write_json(out / "run_summary.json", meta)
    write_report(out, meta)
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
