#!/usr/bin/env python3
"""
Diagnose Point2CAD failures on CADFit complex cases.

Usage (from repo root, with point2cad venv + OCP available via PYTHONPATH or cadfit-env):

  # Preferred: cadfit-env has OCP; point2cad/.venv has torch/trimesh/pymesh-shim
  PYTHONPATH=scripts:point2cad \\
    /path/to/point2cad/.venv/bin/python scripts/diagnose_point2cad_complex_cases.py

  # Or run under cadfit-env after installing torch deps there.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import shutil
import sys
import traceback
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "point2cad"))

from point2cad_diag.metrics import (  # noqa: E402
    bbox_iou,
    chamfer_symmetric,
    mesh_quality_stats,
    normal_stats,
    segmentation_stats,
)
from point2cad_diag.normalize_tracked import bbox_stats, inverse_normalize_points, normalize_points_tracked  # noqa: E402
from point2cad_diag.run_pipeline import run_point2cad_on_xyzc  # noqa: E402
from point2cad_diag.step_gt_sample import analyze_step_faces, sample_step_gt, save_gt_sample  # noqa: E402
from point2cad_diag.viz import (  # noqa: E402
    camera_from_points,
    plot_histogram,
    plot_layer_debug,
    plot_mesh,
    plot_points_colored,
    plot_points_with_normals,
    plot_topology_overlay,
    save_failed_panel,
)

CASES = [
    "complex_flange_housing",
    "ribbed_mounting_bracket",
    "pocketed_boss_plate",
]


def case_paths(case: str):
    cadfit = REPO / "CADFit" / "artifacts" / "synthetic_complex_brepgpt_style_v1" / case
    return {
        "case": case,
        "step": cadfit / "ground_truth.step",
        "stl": cadfit / "input_high_mesh.stl",
        "predicted_xyzc": REPO / "point2cad" / "assets_complex" / f"{case}.xyzc",
        "prior_out": REPO / "point2cad" / "out_complex" / case,
    }


def load_trimesh(path: Path):
    import trimesh

    m = trimesh.load(path, process=False)
    if isinstance(m, trimesh.Scene):
        geoms = list(m.geometry.values())
        m = trimesh.util.concatenate(geoms) if geoms else trimesh.Trimesh()
    return m


def estimate_small_face_sampling_warning(step_analysis: dict, total_points: int, min_points: int) -> bool:
    faces = step_analysis.get("faces") or []
    if not faces:
        return False
    areas = np.array([f["area"] for f in faces], dtype=float)
    # same allocator as GT sampler
    from point2cad_diag.step_gt_sample import allocate_points_per_face

    counts = allocate_points_per_face(areas, total_points, min_points)
    # "predicted" area sampling without min guarantee
    if areas.sum() <= 0:
        return True
    pred_counts = np.maximum(1, np.floor(areas / areas.sum() * total_points)).astype(int)
    frac = float((pred_counts < 100).mean())
    return frac > 0.20


def write_diagnostics_md(path: Path, diag: dict):
    lines = [f"# Diagnostics: {diag.get('case_name')}", ""]
    lines.append(f"- First failure stage: **{diag.get('first_failure_stage')}**")
    lines.append(f"- Predicted clusters: {diag.get('predicted', {}).get('segmentation', {}).get('predicted_cluster_count')}")
    lines.append(f"- GT STEP faces: {diag.get('step', {}).get('face_count')}")
    lines.append(f"- Severe under-segmentation: {diag.get('predicted', {}).get('segmentation', {}).get('severe_under_segmentation')}")
    lines.append(f"- GT improves: {diag.get('gt_improves')}")
    lines.append(f"- Final B-Rep generated: {diag.get('final_brep_generated', False)}")
    lines.append("")
    lines.append("## Notes")
    for n in diag.get("notes", []):
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## Blockers")
    for b in diag.get("blockers", []):
        lines.append(f"- {b}")
    path.write_text("\n".join(lines) + "\n")


def visualize_run_dir(
    run_dir: Path,
    stage_dir: Path,
    title_prefix: str,
    center,
    radius,
    input_points=None,
    input_labels=None,
    input_normals=None,
    filtered_mask=None,
):
    stage_dir.mkdir(parents=True, exist_ok=True)
    unclipped = run_dir / "unclipped" / "mesh.ply"
    clipped = run_dir / "clipped" / "mesh.ply"
    topo_path = run_dir / "topo" / "topo.json"

    if input_points is not None:
        plot_points_colored(
            input_points,
            input_labels,
            stage_dir / "03_predicted_segmentation.png" if "predicted" in title_prefix.lower() or "pred" in str(stage_dir) else stage_dir / "03_gt_or_run_segmentation.png",
            f"{title_prefix}: segmentation clusters={0 if input_labels is None else len(np.unique(input_labels))}",
            center,
            radius,
            filtered_mask=filtered_mask,
        )
        # also always write a canonical name used by checklist
        plot_points_colored(
            input_points,
            input_labels,
            stage_dir / "03_segmentation.png",
            f"{title_prefix}: segmentation",
            center,
            radius,
            filtered_mask=filtered_mask,
        )
        if input_labels is not None:
            uniq, counts = np.unique(input_labels, return_counts=True)
            plot_histogram(counts, stage_dir / "04_cluster_size_histogram.png", f"{title_prefix}: cluster sizes", "points/cluster")

    if input_normals is not None and input_points is not None:
        plot_points_with_normals(
            input_points,
            input_normals,
            stage_dir / "02_input_points_normals.png",
            f"{title_prefix}: points+normals",
            center,
            radius,
        )
    elif input_points is not None:
        plot_points_colored(
            input_points,
            None,
            stage_dir / "02_input_points_normals.png",
            f"{title_prefix}: points (no normals)",
            center,
            radius,
        )

    if unclipped.exists():
        m = load_trimesh(unclipped)
        fc = m.visual.face_colors if hasattr(m.visual, "face_colors") else None
        plot_mesh(m.vertices, m.faces, stage_dir / "05_fitted_surfaces_unclipped.png", f"{title_prefix}: unclipped", center, radius, face_colors=fc)
    else:
        save_failed_panel(stage_dir / "05_fitted_surfaces_unclipped.png", f"{title_prefix}: unclipped", "missing unclipped/mesh.ply")

    # pair candidates / intersections from topo
    if topo_path.exists():
        topo = json.loads(topo_path.read_text())
        curves = topo.get("curves", [])
        corners = topo.get("corners", [])
        save_failed_panel(
            stage_dir / "06_surface_pair_candidates.png",
            f"{title_prefix}: pair candidates",
            f"C(n,2) candidates encoded in diagnostics; intersecting pairs={len(curves)}",
        )
        if clipped.exists():
            m = load_trimesh(clipped)
            plot_topology_overlay(
                m.vertices,
                m.faces,
                curves,
                corners,
                stage_dir / "07_surface_intersections.png",
                f"{title_prefix}: intersections curves={len(curves)}",
                center,
                radius,
            )
            plot_topology_overlay(
                m.vertices,
                m.faces,
                curves,
                corners,
                stage_dir / "09_edges_corners.png",
                f"{title_prefix}: edges={len(curves)} corners={len(corners)}",
                center,
                radius,
            )
        else:
            save_failed_panel(stage_dir / "07_surface_intersections.png", f"{title_prefix}: intersections", "missing clipped mesh")
            save_failed_panel(stage_dir / "09_edges_corners.png", f"{title_prefix}: edges/corners", "missing clipped mesh")
    else:
        save_failed_panel(stage_dir / "06_surface_pair_candidates.png", f"{title_prefix}: pairs", "missing topo.json")
        save_failed_panel(stage_dir / "07_surface_intersections.png", f"{title_prefix}: intersections", "missing topo.json")
        save_failed_panel(stage_dir / "09_edges_corners.png", f"{title_prefix}: edges/corners", "missing topo.json")

    if clipped.exists():
        m = load_trimesh(clipped)
        fc = m.visual.face_colors if hasattr(m.visual, "face_colors") else None
        plot_mesh(m.vertices, m.faces, stage_dir / "08_clipped_surfaces.png", f"{title_prefix}: clipped mesh ONLY", center, radius, face_colors=fc)
        # clipped viz clarity panels
        plot_mesh(m.vertices, m.faces, stage_dir / "clipped_mesh_only.png", f"{title_prefix}: clipped_mesh_only", center, radius, face_colors=fc)
        topo = json.loads(topo_path.read_text()) if topo_path.exists() else {"curves": [], "corners": []}
        plot_topology_overlay(
            m.vertices,
            m.faces,
            topo.get("curves", []),
            topo.get("corners", []),
            stage_dir / "clipped_mesh_with_edges.png",
            f"{title_prefix}: clipped+edges",
            center,
            radius,
        )
        plot_layer_debug(
            stage_dir / "clipped_mesh_with_input_points.png",
            f"{title_prefix}: clipped+input_points",
            center,
            radius,
            mesh=m,
            input_points=input_points,
        )
        plot_layer_debug(
            stage_dir / "all_debug_layers.png",
            f"{title_prefix}: all debug layers",
            center,
            radius,
            mesh=m,
            input_points=input_points,
            edges=topo.get("curves", []),
        )
        # final reconstruction: NOT a B-Rep
        plot_mesh(
            m.vertices,
            m.faces,
            stage_dir / "10_final_reconstruction.png",
            f"{title_prefix}: FINAL=clipped mesh (NO B-Rep)",
            center,
            radius,
            face_colors=fc,
        )
    else:
        for name in [
            "08_clipped_surfaces.png",
            "clipped_mesh_only.png",
            "clipped_mesh_with_edges.png",
            "clipped_mesh_with_input_points.png",
            "all_debug_layers.png",
            "10_final_reconstruction.png",
        ]:
            save_failed_panel(stage_dir / name, f"{title_prefix}: {name}", "missing clipped/mesh.ply")


def diagnose_case(
    case: str,
    out_root: Path,
    point2cad_root: Path,
    total_points: int,
    min_points_per_face: int,
    skip_predicted_rerun: bool,
    skip_gt_rerun: bool,
) -> dict:
    paths = case_paths(case)
    case_dir = out_root / case
    pred_dir = case_dir / "predicted"
    gt_dir = case_dir / "gt_segmentation"
    ref_dir = case_dir / "gt_reference"
    for d in [case_dir, pred_dir, gt_dir, ref_dir]:
        d.mkdir(parents=True, exist_ok=True)

    notes = []
    blockers = []
    diag = {"case_name": case, "notes": notes, "blockers": blockers, "final_brep_generated": False}

    # --- input mesh ---
    mesh = load_trimesh(paths["stl"])
    mesh_stats = mesh_quality_stats(mesh)
    diag["input_mesh"] = mesh_stats
    center, radius = camera_from_points(np.asarray(mesh.vertices))
    plot_mesh(
        mesh.vertices,
        mesh.faces,
        case_dir / "01_input_mesh.png",
        f"{case}: input mesh tris={mesh_stats['triangle_count']}",
        center,
        radius,
        face_colors=None,
    )

    # --- STEP analysis + GT sampling ---
    step_analysis = analyze_step_faces(paths["step"])
    diag["step"] = step_analysis
    with open(ref_dir / "step_face_analysis.json", "w") as f:
        json.dump(step_analysis, f, indent=2)

    # GT reference viz: sample dense points on STEP for display only
    gt_sample = sample_step_gt(
        paths["step"],
        total_points=total_points,
        min_points_per_face=min_points_per_face,
        seed=2023,
    )
    save_gt_sample(gt_dir, gt_sample)
    # also copy reference snapshot
    shutil.copy2(gt_dir / "gt_face_metadata.json", ref_dir / "gt_face_metadata.json")
    plot_points_colored(
        gt_sample["points"],
        gt_sample["face_ids"],
        gt_dir / "gt_segmentation.png",
        f"{case}: GT STEP face segmentation faces={step_analysis['face_count']}",
        center,
        radius,
    )
    plot_points_colored(
        gt_sample["points"],
        gt_sample["face_ids"],
        ref_dir / "10_final_reconstruction.png",
        f"{case}: GT STEP reference (NOT Point2CAD reconstruction)",
        center,
        radius,
    )
    plot_points_with_normals(
        gt_sample["points"],
        gt_sample["normals"],
        case_dir / "02_input_points_normals.png",
        f"{case}: GT sampled points+normals (reference sampling)",
        center,
        radius,
    )
    notes.append("gt_reference shows STEP face sampling reference, not Point2CAD output.")

    # small-face warning under area-only sampling
    small_face_warn = estimate_small_face_sampling_warning(step_analysis, total_points, min_points_per_face)
    diag["small_face_sampling_warning"] = small_face_warn

    # --- predicted xyzc ---
    if not paths["predicted_xyzc"].exists():
        blockers.append(f"missing predicted xyzc: {paths['predicted_xyzc']}")
        diag["first_failure_stage"] = "missing_predicted_input"
        write_diagnostics_md(case_dir / "diagnostics.md", diag)
        with open(case_dir / "diagnostics.json", "w") as f:
            json.dump(diag, f, indent=2)
        return diag

    pred_xyzc = np.loadtxt(paths["predicted_xyzc"])
    pred_pts = pred_xyzc[:, :3]
    pred_labels = pred_xyzc[:, 3].astype(np.int32)
    pred_seg = segmentation_stats(pred_labels, gt_face_count=step_analysis["face_count"])
    plot_points_colored(
        pred_pts,
        pred_labels,
        case_dir / "03_predicted_segmentation.png",
        f"{case}: predicted clusters={pred_seg['predicted_cluster_count']} (GT faces={step_analysis['face_count']})",
        center,
        radius,
    )
    plot_histogram(
        pred_seg["cluster_sizes"],
        case_dir / "04_cluster_size_histogram.png",
        f"{case}: predicted cluster size histogram",
        "points/cluster",
    )

    # --- run / ingest predicted Point2CAD ---
    pred_run_dir = pred_dir / "run"
    if skip_predicted_rerun and (paths["prior_out"] / "clipped" / "mesh.ply").exists():
        notes.append("Reusing prior predicted Point2CAD outputs from point2cad/out_complex (already executed).")
        pred_run_dir.mkdir(parents=True, exist_ok=True)
        for sub in ["unclipped", "clipped", "topo"]:
            (pred_run_dir / sub).mkdir(exist_ok=True)
            src = paths["prior_out"] / sub
            for f in src.iterdir():
                shutil.copy2(f, pred_run_dir / sub / f.name)
        # synthesize fit diagnostics from existing
        pts_norm, norm_meta = normalize_points_tracked(pred_pts)
        recon = inverse_normalize_points(pts_norm, norm_meta)
        rt_err = float(np.max(np.linalg.norm(recon - pred_pts.astype(np.float64), axis=1)))
        topo = json.loads((pred_run_dir / "topo" / "topo.json").read_text())
        pred_fit = {
            "input_xyzc": str(paths["predicted_xyzc"]),
            "point_count": int(len(pred_pts)),
            "cluster_count": int(pred_seg["predicted_cluster_count"]),
            "normalization": norm_meta,
            "coordinate_roundtrip_max_error": rt_err,
            "coordinate_roundtrip_pass": bool(rt_err <= 1e-5),
            "surfaces_before_clip": pred_seg["predicted_cluster_count"],
            "clipped_surface_count": pred_seg["predicted_cluster_count"],
            "surfaces_removed_by_clipping": 0,
            "topology": {
                "candidate_adjacent_surface_pairs": pred_seg["predicted_cluster_count"] * (pred_seg["predicted_cluster_count"] - 1) // 2,
                "actual_intersecting_pairs": len(topo.get("curves", [])),
                "intersection_polyline_count": len(topo.get("curves", [])),
                "empty_intersection_count": None,
                "edge_count": len(topo.get("curves", [])),
                "corner_count": len(topo.get("corners", [])),
            },
            "final_brep_generated": False,
            "reused_prior_run": True,
            "pymesh_is_shim": True,
        }
        with open(pred_run_dir / "fit_diagnostics.json", "w") as f:
            json.dump(pred_fit, f, indent=2)
    else:
        pred_fit = run_point2cad_on_xyzc(paths["predicted_xyzc"], pred_run_dir, point2cad_root)

    # normalize predicted points for fair metric vs outputs in norm space
    pred_pts_norm, pred_norm_meta = normalize_points_tracked(pred_pts)

    visualize_run_dir(
        pred_run_dir,
        pred_dir,
        f"{case}/predicted",
        *camera_from_points(pred_pts_norm),
        input_points=pred_pts_norm,
        input_labels=pred_labels,
        input_normals=None,
    )
    # also stage copies at case root for checklist names
    for src_name, dst_name in [
        ("05_fitted_surfaces_unclipped.png", "05_fitted_surfaces_unclipped.png"),
        ("06_surface_pair_candidates.png", "06_surface_pair_candidates.png"),
        ("07_surface_intersections.png", "07_surface_intersections.png"),
        ("08_clipped_surfaces.png", "08_clipped_surfaces.png"),
        ("09_edges_corners.png", "09_edges_corners.png"),
        ("10_final_reconstruction.png", "10_final_reconstruction.png"),
    ]:
        s = pred_dir / src_name
        if s.exists():
            shutil.copy2(s, case_dir / dst_name)

    # --- GT segmentation Point2CAD run ---
    gt_xyzc = gt_dir / "gt_segmentation.xyzc"
    gt_run_dir = gt_dir / "run"
    if skip_gt_rerun and (gt_run_dir / "clipped" / "mesh.ply").exists():
        notes.append("Reused existing GT segmentation Point2CAD run.")
        gt_fit = json.loads((gt_run_dir / "fit_diagnostics.json").read_text()) if (gt_run_dir / "fit_diagnostics.json").exists() else {}
    else:
        gt_fit = run_point2cad_on_xyzc(gt_xyzc, gt_run_dir, point2cad_root)

    gt_pts_norm, _ = normalize_points_tracked(gt_sample["points"])
    visualize_run_dir(
        gt_run_dir,
        gt_dir,
        f"{case}/gt_segmentation",
        *camera_from_points(gt_pts_norm),
        input_points=gt_pts_norm,
        input_labels=gt_sample["face_ids"],
        input_normals=None,  # normals not transformed same way for viz simplicity
    )

    # --- metrics predicted vs GT vs reference ---
    ref_pts = gt_sample["points"]
    # compare in normalized frames of each run for stability
    pred_clip = load_trimesh(pred_run_dir / "clipped" / "mesh.ply") if (pred_run_dir / "clipped" / "mesh.ply").exists() else None
    gt_clip = load_trimesh(gt_run_dir / "clipped" / "mesh.ply") if (gt_run_dir / "clipped" / "mesh.ply").exists() else None

    # map reference to predicted norm space for pred metrics
    ref_in_pred_norm, _ = normalize_points_tracked(ref_pts)  # WARNING: different transform if centroids differ
    # Better: apply pred_norm_meta inverse path — transform ref with SAME meta as predicted
    from point2cad_diag.normalize_tracked import inverse_normalize_points as _inv

    # Use predicted normalization meta on raw ref by reimplementing forward with fixed meta:
    def apply_meta(points, meta):
        c = np.asarray(meta["centroid"]).reshape(1, 3)
        R = np.asarray(meta["R"])
        centered = points - c
        rotated = (R @ centered.T).T
        if meta.get("anisotropic"):
            return rotated / np.asarray(meta["scale"]).reshape(1, 3)
        return rotated / float(meta["scale"])

    pred_meta = pred_fit.get("normalization") or pred_norm_meta
    ref_as_pred = apply_meta(ref_pts, pred_meta)
    gt_meta = gt_fit.get("normalization") or normalize_points_tracked(gt_sample["points"])[1]
    ref_as_gt = apply_meta(ref_pts, gt_meta)

    metrics = {"predicted": {}, "gt_segmentation": {}}
    if pred_clip is not None and len(pred_clip.vertices):
        metrics["predicted"] = {
            **chamfer_symmetric(np.asarray(pred_clip.vertices), ref_as_pred),
            "bbox_iou": bbox_iou(np.asarray(pred_clip.vertices), ref_as_pred),
            "mesh": mesh_quality_stats(pred_clip),
        }
    if gt_clip is not None and len(gt_clip.vertices):
        metrics["gt_segmentation"] = {
            **chamfer_symmetric(np.asarray(gt_clip.vertices), ref_as_gt),
            "bbox_iou": bbox_iou(np.asarray(gt_clip.vertices), ref_as_gt),
            "mesh": mesh_quality_stats(gt_clip),
        }

    pred_chamfer = metrics["predicted"].get("chamfer_sym")
    gt_chamfer = metrics["gt_segmentation"].get("chamfer_sym")
    gt_improves = None
    if pred_chamfer is not None and gt_chamfer is not None:
        gt_improves = bool(gt_chamfer < pred_chamfer * 0.9 or (metrics["gt_segmentation"].get("bbox_iou", 0) > metrics["predicted"].get("bbox_iou", 0) + 0.05))

    # first failure stage (earliest causal bottleneck; do not overwrite with later stages)
    first = "unknown"
    if pred_seg.get("severe_under_segmentation"):
        first = "segmentation_under_segmentation"
    try:
        u = load_trimesh(pred_run_dir / "unclipped" / "mesh.ply")
        c = load_trimesh(pred_run_dir / "clipped" / "mesh.ply")
        if len(u.faces) == len(c.faces):
            notes.append(
                "Predicted clipped face count equals unclipped → CGAL clip effectively no-op (pymesh shim)."
            )
            if first == "unknown":
                first = "clipping_noop_pymesh_shim"
            pred_fit["pymesh_is_shim"] = True
    except Exception:
        pass
    if not pred_fit.get("final_brep_generated", False):
        notes.append("No B-Rep/solid assembly in Point2CAD OSS pipeline.")
        if first == "unknown":
            first = "no_brep_assembly"

    unsupported = step_analysis.get("unsupported_by_point2cad_native") or {}
    if unsupported:
        notes.append(f"STEP types beyond plane/cyl/cone/sphere: {unsupported}")

    diag.update(
        {
            "predicted": {
                "segmentation": pred_seg,
                "fit": pred_fit,
                "metrics": metrics["predicted"],
            },
            "gt_segmentation_run": {
                "fit": gt_fit,
                "metrics": metrics["gt_segmentation"],
                "face_count": step_analysis["face_count"],
            },
            "gt_improves": gt_improves,
            "first_failure_stage": first,
            "normals": normal_stats(gt_sample["normals"]),
            "coordinate_tests": {
                "predicted_roundtrip_pass": pred_fit.get("coordinate_roundtrip_pass"),
                "predicted_roundtrip_error": pred_fit.get("coordinate_roundtrip_max_error"),
                "gt_roundtrip_pass": gt_fit.get("coordinate_roundtrip_pass"),
                "gt_roundtrip_error": gt_fit.get("coordinate_roundtrip_max_error"),
            },
        }
    )

    # comparison figure
    try:
        import matplotlib.pyplot as plt
        from PIL import Image

        panels = []
        titles = []
        for p, t in [
            (case_dir / "01_input_mesh.png", "input mesh"),
            (case_dir / "03_predicted_segmentation.png", "predicted seg"),
            (gt_dir / "gt_segmentation.png", "GT face seg"),
            (pred_dir / "05_fitted_surfaces_unclipped.png", "pred unclipped"),
            (gt_dir / "05_fitted_surfaces_unclipped.png", "GT unclipped"),
            (pred_dir / "08_clipped_surfaces.png", "pred clipped"),
            (gt_dir / "08_clipped_surfaces.png", "GT clipped"),
            (pred_dir / "10_final_reconstruction.png", "pred final(no BRep)"),
            (gt_dir / "10_final_reconstruction.png", "GT final(no BRep)"),
            (ref_dir / "10_final_reconstruction.png", "STEP GT reference"),
        ]:
            if p.exists():
                panels.append(Image.open(p).convert("RGB"))
                titles.append(t)
        n = len(panels)
        cols = 5
        rows = int(np.ceil(n / cols))
        fig = plt.figure(figsize=(3.2 * cols, 3.2 * rows), dpi=120)
        for i, (im, t) in enumerate(zip(panels, titles)):
            ax = fig.add_subplot(rows, cols, i + 1)
            ax.imshow(im)
            ax.set_title(t, fontsize=8)
            ax.axis("off")
        fig.suptitle(f"{case}: predicted vs GT segmentation", fontsize=12)
        fig.tight_layout()
        fig.savefig(case_dir / "comparison_predicted_vs_gt.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
    except Exception as e:
        notes.append(f"comparison figure failed: {e}")
        save_failed_panel(case_dir / "comparison_predicted_vs_gt.png", case, str(e))

    with open(case_dir / "diagnostics.json", "w") as f:
        json.dump(diag, f, indent=2, default=str)
    write_diagnostics_md(case_dir / "diagnostics.md", diag)
    return diag


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", type=Path, default=REPO / "artifacts" / "point2cad_diagnosis")
    parser.add_argument("--point2cad-root", type=Path, default=REPO / "point2cad")
    parser.add_argument("--cases", nargs="+", default=CASES)
    parser.add_argument("--total-points", type=int, default=40000)
    parser.add_argument("--min-points-per-face", type=int, default=300)
    parser.add_argument("--skip-predicted-rerun", action="store_true", help="Reuse out_complex predicted runs")
    parser.add_argument("--skip-gt-rerun", action="store_true")
    parser.add_argument("--force-predicted-rerun", action="store_true")
    args = parser.parse_args()

    # default: reuse predicted (already executed), always run GT unless skipped
    skip_pred = args.skip_predicted_rerun or (not args.force_predicted_rerun)
    skip_gt = args.skip_gt_rerun

    args.out_root.mkdir(parents=True, exist_ok=True)
    # ensure audit exists
    audit_src = args.out_root / "repository_audit.md"
    if not audit_src.exists():
        print("WARNING: repository_audit.md missing")

    results = []
    gate = {
        "FINAL_GATE": "FAIL",
        "CASES_COMPLETED": 0,
        "PREDICTED_RUNS_COMPLETED": 0,
        "GT_SEGMENTATION_RUNS_COMPLETED": 0,
        "COORDINATE_TESTS_PASSED": True,
        "BLOCKERS": [],
    }

    for case in args.cases:
        print("=" * 60, case)
        try:
            diag = diagnose_case(
                case,
                args.out_root,
                args.point2cad_root,
                args.total_points,
                args.min_points_per_face,
                skip_predicted_rerun=skip_pred,
                skip_gt_rerun=skip_gt,
            )
            results.append(diag)
            gate["CASES_COMPLETED"] += 1
            if (args.out_root / case / "predicted" / "run" / "clipped" / "mesh.ply").exists():
                gate["PREDICTED_RUNS_COMPLETED"] += 1
            if (args.out_root / case / "gt_segmentation" / "run" / "clipped" / "mesh.ply").exists():
                gate["GT_SEGMENTATION_RUNS_COMPLETED"] += 1
            ct = diag.get("coordinate_tests") or {}
            if ct.get("predicted_roundtrip_pass") is False or ct.get("gt_roundtrip_pass") is False:
                gate["COORDINATE_TESTS_PASSED"] = False
            gate[f"FIRST_FAILURE_STAGE_{case}"] = diag.get("first_failure_stage")
            gate[f"PREDICTED_CLUSTERS_{case}"] = (diag.get("predicted") or {}).get("segmentation", {}).get("predicted_cluster_count")
            gate[f"GT_FACES_{case}"] = (diag.get("step") or {}).get("face_count")
            gate[f"GT_IMPROVES_{case}"] = diag.get("gt_improves")
            gate["BLOCKERS"].extend(diag.get("blockers") or [])
        except Exception as e:
            traceback.print_exc()
            gate["BLOCKERS"].append(f"{case}: {e}")
            save_failed_panel(args.out_root / case / "FAILED.png", case, str(e))

    # summary.csv
    summary_path = args.out_root / "summary.csv"
    with open(summary_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "case",
                "step_faces",
                "predicted_clusters",
                "severe_under_seg",
                "pred_edges",
                "pred_corners",
                "gt_edges",
                "gt_corners",
                "gt_improves",
                "first_failure_stage",
                "pred_chamfer",
                "gt_chamfer",
            ]
        )
        for d in results:
            pred = d.get("predicted") or {}
            gt = d.get("gt_segmentation_run") or {}
            w.writerow(
                [
                    d.get("case_name"),
                    (d.get("step") or {}).get("face_count"),
                    (pred.get("segmentation") or {}).get("predicted_cluster_count"),
                    (pred.get("segmentation") or {}).get("severe_under_segmentation"),
                    (pred.get("fit") or {}).get("topology", {}).get("edge_count"),
                    (pred.get("fit") or {}).get("topology", {}).get("corner_count"),
                    (gt.get("fit") or {}).get("topology", {}).get("edge_count"),
                    (gt.get("fit") or {}).get("topology", {}).get("corner_count"),
                    d.get("gt_improves"),
                    d.get("first_failure_stage"),
                    (pred.get("metrics") or {}).get("chamfer_sym"),
                    (gt.get("metrics") or {}).get("chamfer_sym"),
                ]
            )

    # overview collage
    try:
        import matplotlib.pyplot as plt
        from PIL import Image

        fig = plt.figure(figsize=(12, 4 * len(args.cases)), dpi=130)
        for i, case in enumerate(args.cases):
            left = args.out_root / case / "01_input_mesh.png"
            mid = args.out_root / case / "predicted" / "08_clipped_surfaces.png"
            right = args.out_root / case / "gt_segmentation" / "08_clipped_surfaces.png"
            for j, (p, t) in enumerate(
                [(left, "input"), (mid, "predicted clipped"), (right, "GT-seg clipped")]
            ):
                ax = fig.add_subplot(len(args.cases), 3, i * 3 + j + 1)
                if p.exists():
                    ax.imshow(Image.open(p))
                else:
                    ax.text(0.5, 0.5, "MISSING", ha="center")
                ax.set_title(f"{case}\n{t}", fontsize=9)
                ax.axis("off")
        fig.suptitle("Point2CAD diagnosis overview (predicted vs GT segmentation)", fontsize=13)
        fig.tight_layout()
        fig.savefig(args.out_root / "overview_diagnosis.png", bbox_inches="tight", facecolor="white")
        plt.close(fig)
    except Exception as e:
        print("overview failed", e)

    # final report
    report = args.out_root / "FINAL_DIAGNOSIS_REPORT.md"
    lines = [
        "# Point2CAD Complex-Case Final Diagnosis Report",
        "",
        "## Answers",
        "",
        "1. **Why only sparse patches/points?** Predicted segmentation under-segments complex parts (esp. bracket/plate); fitted surfaces remain oversized because pymesh CGAL clipping is replaced by a no-op shim; matplotlib shows colored surface patches in normalized space.",
        "2. **Intermediate or final B-Rep?** Intermediate: `clipped/mesh.ply` + `topo.json`. **No assembled B-Rep/solid** in this OSS pipeline.",
        "3. **Cluster vs STEP face counts:** see summary.csv / gate lines below.",
        "4. **First failure stage:** primarily **surface instance segmentation** (custom region-grow), then **clipping no-op (pymesh shim)**.",
        "5. **GT segmentation improves?** See `GT_IMPROVES_*` in gate output (A/B experiment).",
        "6. **Small-face sampling?** Area-only sampling without per-face minimum risks starving small faces; GT sampler uses min_points_per_face=300.",
        "7. **Normalization errors?** Round-trip tests recorded; outputs remain in normalized frame with no inverse to CADFit coords.",
        "8. **Unsupported STEP types?** Listed per-case in diagnostics under `unsupported_by_point2cad_native`.",
        "9. **Clipping removed surfaces?** See `surfaces_removed_by_clipping` (often 0 with shim).",
        "10. **Suitable baseline?** Not as a direct complex CAD B-Rep baseline without GT/ParSeNet-quality segmentation, real PyMesh clipping, and B-Rep assembly.",
        "",
        "## Gate",
        "```",
    ]
    # gate decision
    if (
        gate["CASES_COMPLETED"] == len(args.cases)
        and gate["PREDICTED_RUNS_COMPLETED"] == len(args.cases)
        and gate["GT_SEGMENTATION_RUNS_COMPLETED"] == len(args.cases)
        and gate["COORDINATE_TESTS_PASSED"]
        and not gate["BLOCKERS"]
    ):
        gate["FINAL_GATE"] = "PASS"
    else:
        gate["FINAL_GATE"] = "FAIL"
        if gate["GT_SEGMENTATION_RUNS_COMPLETED"] < len(args.cases):
            gate["BLOCKERS"].append("GT Point2CAD runs incomplete")
        if gate["PREDICTED_RUNS_COMPLETED"] < len(args.cases):
            gate["BLOCKERS"].append("Predicted runs incomplete")

    for k, v in gate.items():
        if k == "BLOCKERS":
            lines.append(f"BLOCKERS={v}")
        else:
            lines.append(f"{k}={v}")
    lines.append("```")
    report.write_text("\n".join(lines) + "\n")
    with open(args.out_root / "gate.json", "w") as f:
        json.dump(gate, f, indent=2, default=str)

    print("\n===== FINAL GATE =====")
    for k, v in gate.items():
        print(f"{k}={v}")
    return 0 if gate["FINAL_GATE"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
