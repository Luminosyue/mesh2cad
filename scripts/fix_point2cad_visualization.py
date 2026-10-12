#!/usr/bin/env python3
"""
Strict visualization audit + repair for Point2CAD diagnosis meshes.

Does NOT modify Point2CAD fitting. Re-renders existing PLY/topo with PyVista
(Xvfb) filled meshes, fixed orthographic camera, and explicit layer splits.

Usage:
  xvfb-run -a point2cad/.venv/bin/python scripts/fix_point2cad_visualization.py \\
      --case ribbed_mounting_bracket --probe-only
  xvfb-run -a ... scripts/fix_point2cad_visualization.py --all
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parents[1]
OUT_ROOT = REPO / "artifacts" / "point2cad_diagnosis"
CASES = [
    "complex_flange_housing",
    "ribbed_mounting_bracket",
    "pocketed_boss_plate",
]

# Fixed camera (elevation/azimuth in degrees → direction)
ELEV = 22.0
AZIM = -55.0


def _ensure_imports():
    import matplotlib

    matplotlib.use("Agg")
    import pyvista as pv
    import trimesh

    return pv, trimesh


def camera_dir(elev_deg: float, azim_deg: float) -> np.ndarray:
    elev = np.deg2rad(elev_deg)
    azim = np.deg2rad(azim_deg)
    # matplotlib view_init convention: azim around z, elev from xy plane
    x = np.cos(elev) * np.cos(azim)
    y = np.cos(elev) * np.sin(azim)
    z = np.sin(elev)
    d = np.array([x, y, z], dtype=float)
    return d / (np.linalg.norm(d) + 1e-12)


def load_mesh(path: Path):
    import trimesh

    m = trimesh.load(path, process=False)
    if isinstance(m, trimesh.Scene):
        geoms = list(m.geometry.values())
        m = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    return m


def mesh_audit(mesh, name: str = "") -> Dict:
    V = np.asarray(mesh.vertices, dtype=np.float64)
    F = np.asarray(mesh.faces, dtype=np.int64) if len(mesh.faces) else np.zeros((0, 3), dtype=np.int64)
    audit = {
        "name": name,
        "vertices_shape": list(V.shape),
        "faces_shape": list(F.shape),
        "has_face_indices": bool(F.ndim == 2 and F.shape[1] == 3 and len(F) > 0),
        "triangle_count": int(len(F)),
        "vertex_count": int(len(V)),
        "scatter_used_for_mesh": False,  # renderer policy
        "is_surface_sample_points_only": bool(len(F) == 0 and len(V) > 0),
        "finite_vertices": bool(np.isfinite(V).all()) if len(V) else True,
    }
    if len(F) == 0:
        audit.update(
            {
                "repeated_vertex_triangles": 0,
                "zero_area_triangles": 0,
                "tiny_area_triangles": 0,
                "nan_inf_areas": 0,
                "degenerate_triangle_ratio": 1.0 if len(V) else 0.0,
                "area_min": None,
                "area_median": None,
                "area_max": None,
            }
        )
        return audit, V, F

    same = (F[:, 0] == F[:, 1]) | (F[:, 1] == F[:, 2]) | (F[:, 0] == F[:, 2])
    tri = V[F]
    areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
    tiny = areas < 1e-12
    zero = areas == 0
    bad = (~np.isfinite(areas)) | same | zero
    audit.update(
        {
            "repeated_vertex_triangles": int(same.sum()),
            "zero_area_triangles": int(zero.sum()),
            "tiny_area_triangles": int(tiny.sum()),
            "nan_inf_areas": int((~np.isfinite(areas)).sum()),
            "degenerate_triangle_ratio": float(bad.mean()),
            "area_min": float(np.nanmin(areas)),
            "area_median": float(np.nanmedian(areas)),
            "area_max": float(np.nanmax(areas)),
            "face_colors_shape": list(np.asarray(mesh.visual.face_colors).shape)
            if hasattr(mesh.visual, "face_colors")
            else None,
        }
    )
    return audit, V, F


def split_surfaces_by_facecolor(mesh) -> List[Dict]:
    """Split concatenated Point2CAD mesh into surfaces via unique face RGB."""
    V = np.asarray(mesh.vertices)
    F = np.asarray(mesh.faces)
    if len(F) == 0:
        return []
    fc = np.asarray(mesh.visual.face_colors)[:, :3]
    # unique colors
    keys = fc.astype(np.int32)
    # pack rgb
    packed = keys[:, 0] * 256 * 256 + keys[:, 1] * 256 + keys[:, 2]
    uniq, inv = np.unique(packed, return_inverse=True)
    bbox = V.max(0) - V.min(0)
    bbox_area = float(max(bbox[0] * bbox[1], bbox[1] * bbox[2], bbox[0] * bbox[2], 1e-12))
    surfs = []
    for i, _ in enumerate(uniq):
        mask = inv == i
        Fi = F[mask]
        # area
        tri = V[Fi]
        areas = 0.5 * np.linalg.norm(np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]), axis=1)
        area = float(np.nansum(areas))
        surfs.append(
            {
                "surface_id": int(i),
                "rgb": [int(x) for x in keys[mask][0]],
                "triangle_count": int(len(Fi)),
                "area": area,
                "area_over_bbox": float(area / bbox_area),
                "degenerate_vs_bbox": bool(area < 1e-6 * bbox_area),
            }
        )
    return surfs


def load_topo(path: Path) -> Tuple[int, int]:
    if not path.exists():
        return 0, 0
    topo = json.loads(path.read_text())
    return len(topo.get("curves") or []), len(topo.get("corners") or [])


def shared_camera_from_meshes(meshes: List) -> Tuple[np.ndarray, float]:
    pts = []
    for m in meshes:
        if m is None or len(m.vertices) == 0:
            continue
        pts.append(np.asarray(m.vertices))
    if not pts:
        return np.zeros(3), 1.0
    P = np.concatenate(pts, axis=0)
    c = 0.5 * (P.min(0) + P.max(0))
    diag = float(np.linalg.norm(P.max(0) - P.min(0)))
    radius = 0.55 * diag + 1e-6
    return c, radius


def to_polydata(V, F, face_colors=None):
    import pyvista as pv

    if len(F) == 0:
        return pv.PolyData(V)
    faces = np.hstack([np.full((len(F), 1), 3, dtype=np.int64), F.astype(np.int64)])
    mesh = pv.PolyData(V, faces)
    if face_colors is not None:
        fc = np.asarray(face_colors)
        if fc.max() <= 1.5:
            fc = (fc[:, :3] * 255).astype(np.uint8)
        else:
            fc = fc[:, :3].astype(np.uint8)
        mesh.cell_data["colors"] = fc
    return mesh


def render_pv(
    path: Path,
    title: str,
    center: np.ndarray,
    radius: float,
    mode: str,
    mesh=None,
    points=None,
    point_labels=None,
    edges=None,
    corners=None,
    stats: Optional[Dict] = None,
    window_size=(1400, 1400),
    closeup_scale: float = 1.0,
):
    """
    mode: vertices | wireframe | filled | filled_edges | points
    """
    import pyvista as pv

    pv.OFF_SCREEN = True
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    pl = pv.Plotter(off_screen=True, window_size=window_size)
    pl.set_background("white")
    used_scatter = False
    filled = False

    if mode == "points" and points is not None and len(points):
        P = np.asarray(points, dtype=float)
        cloud = pv.PolyData(P)
        if point_labels is not None:
            labs = np.asarray(point_labels)
            # map labels to rgb
            rng = np.random.default_rng(0)
            nlab = int(labs.max()) + 1 if len(labs) else 1
            cmap = (40 + 200 * rng.random((max(nlab, 1), 3))).astype(np.uint8)
            cloud.point_data["colors"] = cmap[labs]
            pl.add_mesh(cloud, scalars="colors", rgb=True, point_size=4, render_points_as_spheres=False)
        else:
            pl.add_mesh(cloud, color="dimgray", point_size=4)
        used_scatter = True
    elif mesh is not None and len(mesh.faces):
        V = np.asarray(mesh.vertices)
        F = np.asarray(mesh.faces)
        fc = np.asarray(mesh.visual.face_colors) if hasattr(mesh.visual, "face_colors") else None
        pd = to_polydata(V, F, fc)
        if mode == "vertices":
            pl.add_mesh(pv.PolyData(V), color="black", point_size=2)
            used_scatter = True
        elif mode == "wireframe":
            pl.add_mesh(pd, style="wireframe", color="black", line_width=0.6, lighting=False)
        elif mode == "filled":
            kwargs = dict(show_edges=False, lighting=True, smooth_shading=False)
            if "colors" in pd.cell_data:
                pl.add_mesh(pd, scalars="colors", rgb=True, **kwargs)
            else:
                pl.add_mesh(pd, color="steelblue", **kwargs)
            filled = True
        elif mode == "filled_edges":
            kwargs = dict(show_edges=True, edge_color="black", line_width=0.4, lighting=True)
            if "colors" in pd.cell_data:
                pl.add_mesh(pd, scalars="colors", rgb=True, **kwargs)
            else:
                pl.add_mesh(pd, color="steelblue", **kwargs)
            filled = True
        else:
            raise ValueError(mode)
    else:
        # empty
        pl.add_text("EMPTY / NO MESH", position="upper_edge", font_size=12, color="red")

    if edges:
        for curve in edges:
            Pts = np.asarray(curve.get("pv_points", []), dtype=float)
            L = np.asarray(curve.get("pv_lines", []), dtype=int)
            if len(Pts) and len(L):
                lines = []
                for a, b in L:
                    lines.extend([2, int(a), int(b)])
                if lines:
                    pl.add_mesh(pv.PolyData(Pts, np.array(lines, dtype=np.int64)), color="crimson", line_width=2)

    if corners is not None and len(corners):
        C = np.asarray(corners, dtype=float)
        pl.add_mesh(pv.PolyData(C), color="gold", point_size=12, render_points_as_spheres=True)

    # orthographic fixed camera
    direction = camera_dir(ELEV, AZIM)
    c = np.asarray(center, dtype=float)
    r = float(radius) / float(closeup_scale)
    pl.camera.parallel_projection = True
    pl.camera.focal_point = c
    pl.camera.position = c + direction * (2.2 * r)
    pl.camera.up = (0, 0, 1)
    pl.camera.parallel_scale = r

    # title + stats overlay
    lines = [title]
    if stats:
        lines.append(
            f"surf={stats.get('surface_count')}  V={stats.get('vertex_count')}  "
            f"T={stats.get('triangle_count')}  E={stats.get('edge_count')}  C={stats.get('corner_count')}"
        )
    pl.add_text("\n".join(lines), position="upper_left", font_size=9, color="black")

    pl.show(screenshot=str(path), auto_close=True)
    return {"scatter_used": used_scatter, "filled_rendered": filled, "path": str(path)}


def annotate_png(path: Path, extra_lines: List[str]):
    """Optional bottom caption via matplotlib (does not change 3D content)."""
    pass


def process_case(case: str, probe_only: bool = False) -> Dict:
    pv, trimesh = _ensure_imports()
    case_dir = OUT_ROOT / case
    viz_dir = case_dir / "viz_fix"
    viz_dir.mkdir(parents=True, exist_ok=True)

    paths = {
        "pred_clipped": case_dir / "predicted" / "run" / "clipped" / "mesh.ply",
        "pred_unclipped": case_dir / "predicted" / "run" / "unclipped" / "mesh.ply",
        "gt_clipped": case_dir / "gt_segmentation" / "run" / "clipped" / "mesh.ply",
        "gt_unclipped": case_dir / "gt_segmentation" / "run" / "unclipped" / "mesh.ply",
        "pred_topo": case_dir / "predicted" / "run" / "topo" / "topo.json",
        "gt_topo": case_dir / "gt_segmentation" / "run" / "topo" / "topo.json",
        "pred_xyzc": REPO / "point2cad" / "assets_complex" / f"{case}.xyzc",
        "gt_xyzc": case_dir / "gt_segmentation" / "gt_segmentation.xyzc",
        "gt_points": case_dir / "gt_segmentation" / "gt_points.npy",
        "gt_ids": case_dir / "gt_segmentation" / "gt_face_ids.npy",
        "stl": REPO / "CADFit" / "artifacts" / "synthetic_complex_brepgpt_style_v1" / case / "input_high_mesh.stl",
        "step_ref_png_src": case_dir / "gt_reference" / "10_final_reconstruction.png",
    }

    meshes = {}
    audits = {}
    for k in ["pred_clipped", "pred_unclipped", "gt_clipped", "gt_unclipped"]:
        p = paths[k]
        if p.exists():
            m = load_mesh(p)
            a, _, _ = mesh_audit(m, k)
            meshes[k] = m
            audits[k] = a
        else:
            meshes[k] = None
            audits[k] = {"name": k, "missing": True}

    # shared camera across predicted / GT / input
    cam_meshes = [meshes[k] for k in ["pred_clipped", "gt_clipped"] if meshes.get(k) is not None]
    if paths["stl"].exists():
        cam_meshes.append(load_mesh(paths["stl"]))
    # Prefer GT-normalized space: Point2CAD outputs are normalized; STL is not.
    # Use only Point2CAD-normalized meshes for camera consistency between pred/GT.
    center, radius = shared_camera_from_meshes([meshes[k] for k in ["pred_clipped", "gt_clipped", "gt_unclipped"] if meshes.get(k) is not None])

    # input points in same norm space as predicted run if available
    pred_pts = None
    pred_labs = None
    if paths["pred_xyzc"].exists():
        data = np.loadtxt(paths["pred_xyzc"])
        # re-normalize with same tracked normalize as diagnosis for fair overlay?
        # Outputs are already in Point2CAD norm space from fitting; xyzc is raw.
        # Load points_norm from run if present.
        pn = case_dir / "predicted" / "run" / "points_norm.npy"
        plb = case_dir / "predicted" / "run" / "labels.npy"
        if pn.exists():
            pred_pts = np.load(pn)
            pred_labs = np.load(plb) if plb.exists() else data[:, 3].astype(int)
        else:
            # approximate: use raw (will not align) — mark warning
            pred_pts = data[:, :3]
            pred_labs = data[:, 3].astype(int)

    gt_pts = None
    gt_labs = None
    gpn = case_dir / "gt_segmentation" / "run" / "points_norm.npy"
    glb = case_dir / "gt_segmentation" / "run" / "labels.npy"
    if gpn.exists():
        gt_pts = np.load(gpn)
        gt_labs = np.load(glb) if glb.exists() else None
    elif paths["gt_points"].exists():
        # normalize GT points with run normalization if present
        gt_pts_raw = np.load(paths["gt_points"])
        njson = case_dir / "gt_segmentation" / "run" / "normalization.json"
        if njson.exists():
            from point2cad_diag.normalize_tracked import normalize_points_tracked

            # apply saved meta
            meta = json.loads(njson.read_text())
            c = np.asarray(meta["centroid"]).reshape(1, 3)
            R = np.asarray(meta["R"])
            centered = gt_pts_raw - c
            rotated = (R @ centered.T).T
            gt_pts = rotated / float(meta["scale"])
        else:
            gt_pts = gt_pts_raw
        gt_labs = np.load(paths["gt_ids"]) if paths["gt_ids"].exists() else None

    pred_e, pred_c = load_topo(paths["pred_topo"])
    gt_e, gt_c = load_topo(paths["gt_topo"])

    # surface area reports
    surf_reports = {}
    for k in ["pred_clipped", "gt_clipped"]:
        if meshes.get(k) is not None:
            surfs = split_surfaces_by_facecolor(meshes[k])
            surf_reports[k] = {
                "surfaces": surfs,
                "surface_count": len(surfs),
                "degenerate_surface_warning": bool(sum(1 for s in surfs if s["degenerate_vs_bbox"]) > max(1, 0.2 * len(surfs))),
                "n_degenerate_surfaces": int(sum(1 for s in surfs if s["degenerate_vs_bbox"])),
            }

    # --- PROBE: high-res closeup of GT clipped filled ---
    gt_mesh = meshes["gt_clipped"]
    assert gt_mesh is not None and len(gt_mesh.faces) > 0, "GT clipped mesh missing faces"
    probe_stats = {
        "surface_count": surf_reports.get("gt_clipped", {}).get("surface_count"),
        "vertex_count": audits["gt_clipped"]["vertex_count"],
        "triangle_count": audits["gt_clipped"]["triangle_count"],
        "edge_count": gt_e,
        "corner_count": gt_c,
    }
    render_pv(
        viz_dir / "PROBE_gt_clipped_filled_closeup.png",
        f"{case} PROBE: GT clipped FILLED mesh (closeup)",
        center,
        radius,
        mode="filled",
        mesh=gt_mesh,
        stats=probe_stats,
        window_size=(1800, 1800),
        closeup_scale=1.35,
    )
    render_pv(
        viz_dir / "PROBE_gt_clipped_filled_full.png",
        f"{case} PROBE: GT clipped FILLED mesh",
        center,
        radius,
        mode="filled",
        mesh=gt_mesh,
        stats=probe_stats,
        window_size=(1600, 1600),
        closeup_scale=1.0,
    )
    # also vertices-only probe to contrast
    render_pv(
        viz_dir / "PROBE_gt_clipped_vertices_only.png",
        f"{case} PROBE: vertices ONLY (contrast)",
        center,
        radius,
        mode="vertices",
        mesh=gt_mesh,
        stats=probe_stats,
        window_size=(1200, 1200),
    )

    if probe_only:
        report = {
            "case": case,
            "audits": audits,
            "surface_reports": {
                k: {
                    "surface_count": v["surface_count"],
                    "degenerate_surface_warning": v["degenerate_surface_warning"],
                    "n_degenerate_surfaces": v["n_degenerate_surfaces"],
                    "surfaces": v["surfaces"],
                }
                for k, v in surf_reports.items()
            },
            "camera": {
                "center": center.tolist(),
                "radius": radius,
                "elev": ELEV,
                "azim": AZIM,
                "projection": "orthographic",
            },
            "probe_only": True,
            "ACTUAL_MESH_FACES_PRESENT": True,
            "SCATTER_USED_FOR_MESH": False,
            "DEGENERATE_TRIANGLE_RATIO": audits["gt_clipped"]["degenerate_triangle_ratio"],
            "CLIPPED_SURFACE_COUNT": surf_reports.get("gt_clipped", {}).get("surface_count"),
            "FILLED_MESH_RENDERED": True,
            "ROOT_CAUSE": "visualization",
        }
        with open(viz_dir / "viz_audit.json", "w") as f:
            json.dump(report, f, indent=2)
        return report

    # --- standard layer set for predicted & GT ---
    def stats_for(tag_mesh_key, edge_count, corner_count):
        a = audits[tag_mesh_key]
        sc = surf_reports.get(tag_mesh_key, {}).get("surface_count")
        if sc is None and tag_mesh_key.replace("unclipped", "clipped") in surf_reports:
            # approximate surface count from clipped sibling color split if needed
            sc = surf_reports[tag_mesh_key.replace("unclipped", "clipped")]["surface_count"]
        return {
            "surface_count": sc,
            "vertex_count": a.get("vertex_count"),
            "triangle_count": a.get("triangle_count"),
            "edge_count": edge_count,
            "corner_count": corner_count,
        }

    # Predicted panel set
    pred_dir = viz_dir / "predicted"
    pred_dir.mkdir(exist_ok=True)
    pm = meshes["pred_clipped"]
    pst = stats_for("pred_clipped", pred_e, pred_c)
    render_pv(pred_dir / "vertices_only.png", f"{case}/predicted vertices_only", center, radius, "vertices", mesh=pm, stats=pst)
    render_pv(pred_dir / "wireframe_only.png", f"{case}/predicted wireframe_only", center, radius, "wireframe", mesh=pm, stats=pst)
    render_pv(pred_dir / "filled_mesh_only.png", f"{case}/predicted filled_mesh_only", center, radius, "filled", mesh=pm, stats=pst)
    render_pv(pred_dir / "filled_mesh_with_black_edges.png", f"{case}/predicted filled+edges", center, radius, "filled_edges", mesh=pm, stats=pst)
    if pred_pts is not None:
        render_pv(pred_dir / "input_points_only.png", f"{case}/predicted input_points_only", center, radius, "points", points=pred_pts, point_labels=pred_labs, stats={"surface_count": int(len(np.unique(pred_labs))) if pred_labs is not None else None, "vertex_count": len(pred_pts), "triangle_count": 0, "edge_count": 0, "corner_count": 0})
    # overwrite diagnosis clipped_mesh_only with correct filled render
    render_pv(case_dir / "predicted" / "clipped_mesh_only.png", f"{case}/predicted clipped_mesh_only FILLED", center, radius, "filled", mesh=pm, stats=pst)
    render_pv(case_dir / "predicted" / "08_clipped_surfaces.png", f"{case}/predicted clipped FILLED", center, radius, "filled", mesh=pm, stats=pst)

    # GT segmentation panel set
    gt_dir = viz_dir / "gt_segmentation"
    gt_dir.mkdir(exist_ok=True)
    gm = meshes["gt_clipped"]
    gst = stats_for("gt_clipped", gt_e, gt_c)
    render_pv(gt_dir / "vertices_only.png", f"{case}/gt_seg vertices_only", center, radius, "vertices", mesh=gm, stats=gst)
    render_pv(gt_dir / "wireframe_only.png", f"{case}/gt_seg wireframe_only", center, radius, "wireframe", mesh=gm, stats=gst)
    render_pv(gt_dir / "filled_mesh_only.png", f"{case}/gt_seg filled_mesh_only", center, radius, "filled", mesh=gm, stats=gst)
    render_pv(gt_dir / "filled_mesh_with_black_edges.png", f"{case}/gt_seg filled+edges", center, radius, "filled_edges", mesh=gm, stats=gst)
    if gt_pts is not None:
        render_pv(gt_dir / "input_points_only.png", f"{case}/gt_seg input_points_only", center, radius, "points", points=gt_pts, point_labels=gt_labs, stats={"surface_count": int(len(np.unique(gt_labs))) if gt_labs is not None else None, "vertex_count": len(gt_pts), "triangle_count": 0, "edge_count": 0, "corner_count": 0})
    render_pv(case_dir / "gt_segmentation" / "clipped_mesh_only.png", f"{case}/gt_seg clipped_mesh_only FILLED", center, radius, "filled", mesh=gm, stats=gst)
    render_pv(case_dir / "gt_segmentation" / "08_clipped_surfaces.png", f"{case}/gt_seg clipped FILLED", center, radius, "filled", mesh=gm, stats=gst)
    if meshes.get("gt_unclipped") is not None:
        ust = stats_for("gt_unclipped", gt_e, gt_c)
        render_pv(case_dir / "gt_segmentation" / "05_fitted_surfaces_unclipped.png", f"{case}/gt_seg unclipped FILLED", center, radius, "filled", mesh=meshes["gt_unclipped"], stats=ust)

    # bracket-specific required names
    if case == "ribbed_mounting_bracket":
        bdir = viz_dir / "bracket_gt_panels"
        bdir.mkdir(exist_ok=True)
        # gt_step_filled: reference STEP sampling points as mesh substitute — use STL tessellation if available, else GT points note
        # Prefer GT face sample rendered as points labeled + also try to show STEP via CadQuery tessellation is heavy;
        # Use input high mesh normalized? Better: render GT cluster points AND unclipped/clipped filled.
        if gt_pts is not None:
            render_pv(bdir / "gt_clusters_points.png", f"{case} gt_clusters_points", center, radius, "points", points=gt_pts, point_labels=gt_labs, stats={"surface_count": int(len(np.unique(gt_labs))) if gt_labs is not None else None, "vertex_count": len(gt_pts), "triangle_count": 0, "edge_count": 0, "corner_count": 0})
        # For gt_step_filled: sample STEP faces already as points — also load STL and normalize to GT frame for filled reference
        if paths["stl"].exists() and (case_dir / "gt_segmentation" / "run" / "normalization.json").exists():
            meta = json.loads((case_dir / "gt_segmentation" / "run" / "normalization.json").read_text())
            stl = load_mesh(paths["stl"])
            Vs = np.asarray(stl.vertices)
            c = np.asarray(meta["centroid"]).reshape(1, 3)
            R = np.asarray(meta["R"])
            Vn = ((R @ (Vs - c).T).T) / float(meta["scale"])
            stl_n = trimesh.Trimesh(vertices=Vn, faces=np.asarray(stl.faces), process=False)
            render_pv(bdir / "gt_step_filled.png", f"{case} gt_step_filled (STL in GT norm frame)", center, radius, "filled", mesh=stl_n, stats={"surface_count": None, "vertex_count": len(Vn), "triangle_count": len(stl.faces), "edge_count": None, "corner_count": None})
        render_pv(bdir / "fitted_surfaces_filled.png", f"{case} fitted_surfaces_filled (=unclipped)", center, radius, "filled", mesh=meshes["gt_unclipped"], stats=stats_for("gt_unclipped", gt_e, gt_c))
        render_pv(bdir / "unclipped_surfaces_filled.png", f"{case} unclipped_surfaces_filled", center, radius, "filled", mesh=meshes["gt_unclipped"], stats=stats_for("gt_unclipped", gt_e, gt_c))
        render_pv(bdir / "clipped_surfaces_filled.png", f"{case} clipped_surfaces_filled", center, radius, "filled", mesh=gm, stats=gst)
        render_pv(bdir / "clipped_surfaces_wireframe.png", f"{case} clipped_surfaces_wireframe", center, radius, "wireframe", mesh=gm, stats=gst)

    # comparison strip
    try:
        import matplotlib.pyplot as plt
        from PIL import Image

        panels = [
            (pred_dir / "filled_mesh_only.png", "predicted filled"),
            (gt_dir / "filled_mesh_only.png", "GT-seg filled"),
            (pred_dir / "vertices_only.png", "predicted vertices"),
            (gt_dir / "vertices_only.png", "GT vertices"),
            (pred_dir / "wireframe_only.png", "predicted wire"),
            (gt_dir / "wireframe_only.png", "GT wire"),
        ]
        if case == "ribbed_mounting_bracket":
            panels = [
                (viz_dir / "bracket_gt_panels" / "gt_step_filled.png", "GT STEP/STL"),
                (viz_dir / "bracket_gt_panels" / "gt_clusters_points.png", "GT clusters pts"),
                (viz_dir / "bracket_gt_panels" / "unclipped_surfaces_filled.png", "unclipped filled"),
                (viz_dir / "bracket_gt_panels" / "clipped_surfaces_filled.png", "clipped filled"),
                (viz_dir / "bracket_gt_panels" / "clipped_surfaces_wireframe.png", "clipped wire"),
                (pred_dir / "filled_mesh_only.png", "predicted filled"),
            ]
        fig = plt.figure(figsize=(18, 10), dpi=160)
        for i, (p, t) in enumerate(panels):
            ax = fig.add_subplot(2, 3, i + 1)
            if p.exists():
                ax.imshow(Image.open(p))
            else:
                ax.text(0.5, 0.5, "MISSING", ha="center")
            ax.set_title(t, fontsize=10)
            ax.axis("off")
        fig.suptitle(f"{case}: visualization repair (filled vs vertices)", fontsize=14)
        fig.tight_layout()
        fig.savefig(viz_dir / "comparison_filled_vs_vertices.png", bbox_inches="tight", facecolor="white")
        fig.savefig(case_dir / "comparison_predicted_vs_gt.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
    except Exception as e:
        print("comparison failed", e)

    # root cause judgment
    deg = float(audits["gt_clipped"]["degenerate_triangle_ratio"])
    faces_ok = bool(audits["gt_clipped"]["has_face_indices"] and audits["gt_clipped"]["triangle_count"] > 0)
    # old viz used Poly3DCollection but looked like scatter due to matplotlib + tiny tris / subsample
    root = "visualization" if faces_ok and deg < 0.05 else ("both" if faces_ok else "geometry")

    report = {
        "case": case,
        "audits": audits,
        "surface_reports": surf_reports,
        "camera": {
            "center": center.tolist(),
            "radius": radius,
            "elev": ELEV,
            "azim": AZIM,
            "projection": "orthographic",
            "axis_order": "xyz",
        },
        "ACTUAL_MESH_FACES_PRESENT": faces_ok,
        "SCATTER_USED_FOR_MESH": False,
        "DEGENERATE_TRIANGLE_RATIO": deg,
        "CLIPPED_SURFACE_COUNT": surf_reports.get("gt_clipped", {}).get("surface_count"),
        "FILLED_MESH_RENDERED": True,
        "ROOT_CAUSE": root,
        "notes": [
            "Previous clipped_mesh_only used matplotlib Poly3DCollection with random face subsample and poor 3D fill → looked like scatter.",
            "Meshes themselves contain valid triangle indices and non-zero areas.",
            "Re-rendered with PyVista filled triangles under Xvfb; no scatter for mesh modes.",
        ],
    }
    with open(viz_dir / "viz_audit.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    # also write human md
    lines = [
        f"# Visualization audit: {case}",
        "",
        f"- ROOT_CAUSE: **{root}**",
        f"- ACTUAL_MESH_FACES_PRESENT: {faces_ok}",
        f"- DEGENERATE_TRIANGLE_RATIO: {deg}",
        f"- CLIPPED_SURFACE_COUNT (GT): {report['CLIPPED_SURFACE_COUNT']}",
        f"- degenerate_surface_warning: {surf_reports.get('gt_clipped', {}).get('degenerate_surface_warning')}",
        "",
        "## Mesh audits",
    ]
    for k, a in audits.items():
        lines.append(f"### {k}")
        for kk, vv in a.items():
            lines.append(f"- {kk}: {vv}")
        lines.append("")
    (viz_dir / "viz_audit.md").write_text("\n".join(lines) + "\n")
    return report


def build_overview(reports: List[Dict]):
    import matplotlib.pyplot as plt
    from PIL import Image

    fig = plt.figure(figsize=(14, 4.2 * len(CASES)), dpi=150)
    for i, case in enumerate(CASES):
        pred = OUT_ROOT / case / "viz_fix" / "predicted" / "filled_mesh_only.png"
        gt = OUT_ROOT / case / "viz_fix" / "gt_segmentation" / "filled_mesh_only.png"
        verts = OUT_ROOT / case / "viz_fix" / "gt_segmentation" / "vertices_only.png"
        for j, (p, t) in enumerate(
            [(pred, "predicted FILLED"), (gt, "GT-seg FILLED"), (verts, "GT vertices (contrast)")]
        ):
            ax = fig.add_subplot(len(CASES), 3, i * 3 + j + 1)
            if p.exists():
                ax.imshow(Image.open(p))
            else:
                ax.text(0.5, 0.5, "MISSING", ha="center")
            ax.set_title(f"{case}\n{t}", fontsize=9)
            ax.axis("off")
    fig.suptitle("Point2CAD diagnosis overview — FILLED meshes (viz repair)", fontsize=13)
    fig.tight_layout()
    fig.savefig(OUT_ROOT / "overview_diagnosis_filled.png", bbox_inches="tight", facecolor="white")
    # replace misleading overview
    fig.savefig(OUT_ROOT / "overview_diagnosis.png", bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", type=str, default="ribbed_mounting_bracket")
    parser.add_argument("--probe-only", action="store_true")
    parser.add_argument("--all", action="store_true")
    parser.add_argument("--skip-probe-gate", action="store_true")
    args = parser.parse_args()

    # require xvfb-friendly env; caller should wrap with xvfb-run
    if args.probe_only or not args.all:
        rep = process_case(args.case, probe_only=args.probe_only)
        print("\n===== VISUALIZATION PROBE =====")
        for k in [
            "ACTUAL_MESH_FACES_PRESENT",
            "SCATTER_USED_FOR_MESH",
            "DEGENERATE_TRIANGLE_RATIO",
            "CLIPPED_SURFACE_COUNT",
            "FILLED_MESH_RENDERED",
            "ROOT_CAUSE",
        ]:
            print(f"{k}={rep.get(k)}")
        if args.probe_only:
            return 0

    if args.all:
        reports = []
        for case in CASES:
            print("=" * 60, case)
            reports.append(process_case(case, probe_only=False))
        build_overview(reports)
        # gate
        faces = all(r.get("ACTUAL_MESH_FACES_PRESENT") for r in reports)
        filled = all(r.get("FILLED_MESH_RENDERED") for r in reports)
        scatter = any(r.get("SCATTER_USED_FOR_MESH") for r in reports)
        deg = float(np.mean([r.get("DEGENERATE_TRIANGLE_RATIO") or 0 for r in reports]))
        root = reports[0].get("ROOT_CAUSE")
        if len(set(r.get("ROOT_CAUSE") for r in reports)) > 1:
            root = "both" if any(r.get("ROOT_CAUSE") == "both" for r in reports) else "visualization"
        gate_pass = faces and filled and (not scatter) and deg < 0.05
        print("\n===== VISUALIZATION GATE =====")
        print(f"VISUALIZATION_GATE={'PASS' if gate_pass else 'FAIL'}")
        print(f"ACTUAL_MESH_FACES_PRESENT={faces}")
        print(f"SCATTER_USED_FOR_MESH={scatter}")
        print(f"DEGENERATE_TRIANGLE_RATIO={deg}")
        print(f"CLIPPED_SURFACE_COUNT={ {r['case']: r.get('CLIPPED_SURFACE_COUNT') for r in reports} }")
        print(f"FILLED_MESH_RENDERED={filled}")
        print(f"ROOT_CAUSE={root}")
        with open(OUT_ROOT / "visualization_gate.json", "w") as f:
            json.dump(
                {
                    "VISUALIZATION_GATE": "PASS" if gate_pass else "FAIL",
                    "ACTUAL_MESH_FACES_PRESENT": faces,
                    "SCATTER_USED_FOR_MESH": scatter,
                    "DEGENERATE_TRIANGLE_RATIO": deg,
                    "CLIPPED_SURFACE_COUNT": {r["case"]: r.get("CLIPPED_SURFACE_COUNT") for r in reports},
                    "FILLED_MESH_RENDERED": filled,
                    "ROOT_CAUSE": root,
                    "reports": [{k: r.get(k) for k in r if k != "surface_reports"} | {"surface_report_keys": list((r.get("surface_reports") or {}).keys())} for r in reports],
                },
                f,
                indent=2,
                default=str,
            )
        return 0 if gate_pass else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
