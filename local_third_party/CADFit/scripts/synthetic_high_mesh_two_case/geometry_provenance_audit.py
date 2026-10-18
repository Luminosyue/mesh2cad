#!/usr/bin/env python3
"""Independent geometry provenance audit, triple comparison renders, RAW vs ALIGNED metrics.

Does NOT re-run CADFit. Uses existing artifacts only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import shutil
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np
import trimesh

ROOT = Path(__file__).resolve().parents[2]
ART = ROOT / "artifacts/synthetic_high_mesh_two_case_v1"
OUT = ROOT / "outputs/synthetic_high_mesh_two_case_v1"
DS = ROOT / "datasets/synthetic_high_mesh_two_case_v1"

sys.path.insert(0, str(ROOT))
from iou import mesh_iou_cpu_boolean, normalize_mesh  # noqa: E402


def mesh_chamfer_distance(mesh_path_a: str, mesh_path_b: str, normalize: bool = False, n: int = 4096) -> float:
    """Symmetric mean nearest-neighbor distance between surface samples."""
    ma = trimesh.load(mesh_path_a, force="mesh")
    mb = trimesh.load(mesh_path_b, force="mesh")
    if isinstance(ma, trimesh.Scene):
        ma = trimesh.util.concatenate([g for g in ma.geometry.values() if isinstance(g, trimesh.Trimesh)])
    if isinstance(mb, trimesh.Scene):
        mb = trimesh.util.concatenate([g for g in mb.geometry.values() if isinstance(g, trimesh.Trimesh)])
    ma = ma.copy()
    mb = mb.copy()
    if normalize:
        normalize_mesh(ma)
        normalize_mesh(mb)
    pa = ma.sample(n)
    pb = mb.sample(n)
    try:
        from scipy.spatial import cKDTree

        da, _ = cKDTree(pb).query(pa, k=1)
        db, _ = cKDTree(pa).query(pb, k=1)
    except Exception:
        # brute-force fallback (n~4k is fine)
        da = np.linalg.norm(pa[:, None, :] - pb[None, :, :], axis=2).min(axis=1)
        db = np.linalg.norm(pb[:, None, :] - pa[None, :, :], axis=2).min(axis=1)
    return float(0.5 * (da.mean() + db.mean()))


CASES = {
    "case_a_flange": {
        "label": "Case A Flange",
        "run_dir": OUT / "case_a_flange" / "input_high_mesh",
        "art_dir": ART / "case_a_flange",
        "input_ds": DS / "case_a_flange" / "input_high_mesh.stl",
    },
    "case_b_bracket": {
        "label": "Case B Bracket",
        "run_dir": OUT / "case_b_bracket" / "input_high_mesh",
        "art_dir": ART / "case_b_bracket",
        "input_ds": DS / "case_b_bracket" / "input_high_mesh.stl",
    },
}


def sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def file_mtime(path: Path) -> str:
    if not path.exists():
        return ""
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()


def load_mesh(path: Path) -> Optional[trimesh.Trimesh]:
    if not path.exists():
        return None
    try:
        m = trimesh.load(str(path), force="mesh")
        if isinstance(m, trimesh.Scene):
            geoms = [g for g in m.geometry.values() if isinstance(g, trimesh.Trimesh)]
            if not geoms:
                return None
            m = trimesh.util.concatenate(geoms)
        if not isinstance(m, trimesh.Trimesh):
            return None
        return m
    except Exception:
        return None


@dataclass
class GeomAudit:
    case: str
    role: str
    path: str
    exists: bool = False
    sha256: str = ""
    size_bytes: int = 0
    vertex_count: int = 0
    triangle_count: int = 0
    solid_count: int = 0
    face_count: int = 0
    connected_component_count: int = 0
    is_watertight: bool = False
    volume: float = 0.0
    surface_area: float = 0.0
    centroid: str = ""
    bounds_min: str = ""
    bounds_max: str = ""
    extents: str = ""
    bbox_diagonal: float = 0.0
    step_reopen_ok: Optional[bool] = None
    notes: str = ""


def audit_mesh(case: str, role: str, path: Path, is_step: bool = False) -> GeomAudit:
    a = GeomAudit(case=case, role=role, path=str(path.resolve()) if path.exists() else str(path))
    if not path.exists():
        a.notes = "missing"
        return a
    a.exists = True
    a.sha256 = sha256(path)
    a.size_bytes = path.stat().st_size

    if is_step:
        try:
            import cadquery as cq
            cq.importers.importStep(str(path))
            a.step_reopen_ok = True
            # also tessellate for geometry stats
            solid = cq.importers.importStep(str(path))
            tmp = path.with_suffix(".audit_tmp.stl")
            cq.exporters.export(solid, str(tmp))
            mesh = load_mesh(tmp)
            tmp.unlink(missing_ok=True)
        except Exception as e:
            a.step_reopen_ok = False
            a.notes = f"step_fail:{e!r}"
            return a
    else:
        mesh = load_mesh(path)

    if mesh is None:
        a.notes = "load_failed"
        return a

    a.vertex_count = int(len(mesh.vertices))
    a.triangle_count = int(len(mesh.faces))
    a.face_count = a.triangle_count
    try:
        comps = mesh.split(only_watertight=False)
        a.connected_component_count = len(comps)
        a.solid_count = sum(1 for c in comps if getattr(c, "is_volume", False) or c.is_watertight)
    except Exception:
        a.connected_component_count = 1
        a.solid_count = 1 if mesh.is_watertight else 0
    a.is_watertight = bool(mesh.is_watertight)
    try:
        a.volume = float(mesh.volume)
    except Exception:
        a.volume = 0.0
    try:
        a.surface_area = float(mesh.area)
    except Exception:
        a.surface_area = 0.0
    c = mesh.centroid
    a.centroid = f"{c[0]:.6g},{c[1]:.6g},{c[2]:.6g}"
    bmin, bmax = mesh.bounds
    a.bounds_min = f"{bmin[0]:.6g},{bmin[1]:.6g},{bmin[2]:.6g}"
    a.bounds_max = f"{bmax[0]:.6g},{bmax[1]:.6g},{bmax[2]:.6g}"
    ext = mesh.extents
    a.extents = f"{ext[0]:.6g},{ext[1]:.6g},{ext[2]:.6g}"
    a.bbox_diagonal = float(np.linalg.norm(ext))
    return a


def similarity_align_pred_to_gt(pred: trimesh.Trimesh, gt: trimesh.Trimesh) -> trimesh.Trimesh:
    """Same spirit as CADFit demo alignment: normalize both, then optional ICP-ish centroid+scale match.

    For evaluation-aligned visuals we apply the SAME transform CADFit IoU effectively uses:
    - GT independently normalized to [-1,1]
    - Pred is already in CADFit normalized space; for fair side-by-side we normalize pred the same way
      independently (as done for shape comparison) OR map pred via normalize_mesh.
    Here we independently normalize both to [-1,1] cube (matching iou.normalize_mesh).
    """
    # Build transform that maps pred vertices to normalized space independently
    p = pred.copy()
    g = gt.copy()
    # Record raw pred transform to normalized
    pc = p.centroid
    p.vertices -= pc
    scale_p = float(np.max(np.abs(p.vertices))) or 1.0
    p.vertices /= scale_p
    # GT normalize for reference frame of "evaluation aligned" overlay
    gc = g.centroid
    g.vertices -= gc
    scale_g = float(np.max(np.abs(g.vertices))) or 1.0
    g.vertices /= scale_g
    # Place pred into GT-normalized frame (already both in [-1,1] centered)
    # Optional: apply scale ratio so extents match on max axis
    return p, g, {
        "pred_centroid": pc.tolist(),
        "pred_scale": scale_p,
        "gt_centroid": gc.tolist(),
        "gt_scale": scale_g,
    }


def _project_mesh(mesh, center, scale):
    verts = (np.asarray(mesh.vertices) - center) / scale
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
    return pts, z


def _draw_panel(ax, mesh, center, scale, color):
    import matplotlib
    from matplotlib.collections import PolyCollection

    pts, z = _project_mesh(mesh, center, scale)
    faces = np.asarray(mesh.faces)
    if len(faces) > 80000:
        idx = np.linspace(0, len(faces) - 1, 80000).astype(int)
        faces = faces[idx]
    order = np.argsort(z[faces].mean(axis=1))
    tri = pts[faces[order]]
    shade = z[faces[order]].mean(axis=1)
    shade = (shade - shade.min()) / (np.ptp(shade) + 1e-9)
    base = np.array(matplotlib.colors.to_rgb(color))
    colors = np.clip(base * (0.56 + 0.44 * shade[:, None]), 0, 1)
    ax.add_collection(PolyCollection(tri, facecolors=colors, edgecolors=(0, 0, 0, 0.035), linewidths=0.05))
    ax.set_aspect("equal")
    ax.set_xlim(-0.85, 0.85)
    ax.set_ylim(-0.85, 0.85)
    ax.axis("off")


def render_pair(
    mesh_l: trimesh.Trimesh,
    mesh_r: trimesh.Trimesh,
    out_path: Path,
    title_l: str,
    title_r: str,
    mode_label: str,
    shared_bounds: bool,
) -> bool:
    """Side-by-side Agg render (same projector as render_comparison.py). No VTK."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fig, axes = plt.subplots(1, 2, figsize=(11, 5.2), dpi=160)
        label_color = {
            "RAW": "darkred",
            "NORMALIZED": "darkgreen",
            "EVALUATION-ALIGNED": "darkblue",
        }.get(mode_label, "black")

        if shared_bounds:
            bounds = np.vstack([mesh_l.bounds, mesh_r.bounds])
            center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2
            scale = float(np.linalg.norm(bounds.max(axis=0) - bounds.min(axis=0))) or 1.0
            _draw_panel(axes[0], mesh_l, center, scale, "#5b8fd9")
            _draw_panel(axes[1], mesh_r, center, scale, "#d9904f")
        else:
            for ax, mesh, color in (
                (axes[0], mesh_l, "#5b8fd9"),
                (axes[1], mesh_r, "#d9904f"),
            ):
                center = (mesh.bounds.min(axis=0) + mesh.bounds.max(axis=0)) / 2
                scale = float(np.linalg.norm(mesh.bounds.max(axis=0) - mesh.bounds.min(axis=0))) or 1.0
                _draw_panel(ax, mesh, center, scale, color)

        axes[0].set_title(title_l, fontsize=11)
        axes[1].set_title(title_r, fontsize=11)
        fig.suptitle(f"{mode_label}", fontsize=14, fontweight="bold", color=label_color)
        fig.text(
            0.98,
            0.98,
            mode_label,
            ha="right",
            va="top",
            fontsize=12,
            fontweight="bold",
            color=label_color,
            transform=fig.transFigure,
        )
        fig.tight_layout(rect=[0, 0.02, 1, 0.94])
        fig.savefig(out_path, bbox_inches="tight", pad_inches=0.06, facecolor="white")
        plt.close(fig)
        return out_path.exists()
    except Exception as e:
        print(f"render failed: {e}", file=sys.stderr)
        return False


def raw_bbox_overlap(a: trimesh.Trimesh, b: trimesh.Trimesh) -> float:
    amin, amax = a.bounds
    bmin, bmax = b.bounds
    inter_min = np.maximum(amin, bmin)
    inter_max = np.minimum(amax, bmax)
    inter = np.maximum(0.0, inter_max - inter_min)
    inter_vol = float(np.prod(inter))
    vol_a = float(np.prod(np.maximum(amax - amin, 0)))
    vol_b = float(np.prod(np.maximum(bmax - bmin, 0)))
    union = vol_a + vol_b - inter_vol
    return inter_vol / union if union > 0 else 0.0


def safe_iou(path_a: Path, path_b: Path, normalize: bool) -> dict:
    out = {"ok": False, "iou": None, "error": ""}
    try:
        v = float(mesh_iou_cpu_boolean(str(path_a), str(path_b), normalize=normalize, verbose=False))
        out["ok"] = True
        out["iou"] = v
    except Exception as e:
        out["error"] = repr(e)
    return out


def safe_chamfer(path_a: Path, path_b: Path, normalize: bool) -> dict:
    out = {"ok": False, "chamfer": None, "error": ""}
    try:
        v = float(mesh_chamfer_distance(str(path_a), str(path_b), normalize=normalize))
        out["ok"] = True
        out["chamfer"] = v
    except Exception as e:
        out["error"] = repr(e)
    return out


def analyze_generated_cad(path: Path) -> dict:
    info = {
        "path": str(path),
        "exists": path.exists(),
        "final_var_candidates": [],
        "likely_export_var": None,
        "exports_only_intermediate": False,
        "notes": "",
    }
    if not path.exists():
        return info
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    assigns = []
    for i, line in enumerate(lines):
        s = line.strip()
        if s.startswith("result ") or s.startswith("result="):
            assigns.append(("result", i + 1, s[:120]))
        if s.startswith("final_result"):
            assigns.append(("final_result", i + 1, s[:120]))
    info["final_var_candidates"] = assigns
    # generated programs typically end with result = solid_1.add(...)
    if "result =" in text or "result=" in text:
        info["likely_export_var"] = "result"
        # check if result is residual-like
        last_result = [a for a in assigns if a[0] == "result"]
        if last_result:
            snippet = last_result[-1][2].lower()
            bad = any(k in snippet for k in ("residual", "cutter", "edge"))
            info["exports_only_intermediate"] = bad and "add(" not in snippet and "union" not in snippet
            info["notes"] = last_result[-1][2]
    return info


def process_case(case_key: str, meta: dict) -> dict:
    art = meta["art_dir"]
    run = meta["run_dir"]
    audit_rows: list[GeomAudit] = []

    paths = {
        "input_high_mesh": art / "input_high_mesh.stl" if (art / "input_high_mesh.stl").exists() else meta["input_ds"],
        "original_best_stl": run / "best_greedy_parallel_iterative.stl",
        "artifact_recon_stl": art / "reconstructed_cad.stl",
        "artifact_recon_step": art / "reconstructed_cad.step",
        "clean_stl": art / "clean_reexport" / "clean_reconstructed.stl",
        "clean_step": art / "clean_reexport" / "clean_reconstructed.step",
        "generated_cad": art / "generated_cad.py",
        "final_iou_json": art / "final_iou.json" if (art / "final_iou.json").exists() else run / "final_iou.json",
    }

    for role, p in [
        ("input_high_mesh.stl", paths["input_high_mesh"]),
        ("CADFit_original_best.stl", paths["original_best_stl"]),
        ("artifact_reconstructed_cad.stl", paths["artifact_recon_stl"]),
        ("artifact_reconstructed_cad.step", paths["artifact_recon_step"]),
        ("clean_reconstructed.stl", paths["clean_stl"]),
        ("clean_reconstructed.step", paths["clean_step"]),
    ]:
        is_step = p.suffix.lower() in {".step", ".stp"}
        audit_rows.append(audit_mesh(case_key, role, p, is_step=is_step))

    by_role = {r.role: r for r in audit_rows}
    input_m = load_mesh(paths["input_high_mesh"])
    best_m = load_mesh(paths["original_best_stl"])
    art_m = load_mesh(paths["artifact_recon_stl"])
    clean_m = load_mesh(paths["clean_stl"]) if paths["clean_stl"].exists() else None

    # ratios
    scale_ratio = None
    volume_ratio = None
    centroid_distance = None
    extent_ratios = None
    if input_m is not None and art_m is not None:
        scale_ratio = art_m.bounding_box.extents.max() and (
            float(np.linalg.norm(art_m.extents)) / float(np.linalg.norm(input_m.extents))
        )
        # use bbox diagonal
        scale_ratio = by_role["artifact_reconstructed_cad.stl"].bbox_diagonal / max(
            by_role["input_high_mesh.stl"].bbox_diagonal, 1e-12
        )
        iv = abs(by_role["input_high_mesh.stl"].volume) or 1e-12
        rv = abs(by_role["artifact_reconstructed_cad.stl"].volume)
        volume_ratio = rv / iv
        ic = np.array([float(x) for x in by_role["input_high_mesh.stl"].centroid.split(",")])
        rc = np.array([float(x) for x in by_role["artifact_reconstructed_cad.stl"].centroid.split(",")])
        centroid_distance = float(np.linalg.norm(rc - ic))
        ie = np.array([float(x) for x in by_role["input_high_mesh.stl"].extents.split(",")])
        re = np.array([float(x) for x in by_role["artifact_reconstructed_cad.stl"].extents.split(",")])
        extent_ratios = (re / np.maximum(ie, 1e-12)).tolist()

    raw_scale_valid = (
        scale_ratio is not None
        and 0.25 <= scale_ratio <= 4.0
        and volume_ratio is not None
        and 0.01 <= volume_ratio <= 100.0
    )

    sha_same = (
        by_role["CADFit_original_best.stl"].sha256
        and by_role["CADFit_original_best.stl"].sha256 == by_role["artifact_reconstructed_cad.stl"].sha256
    )
    clean_vs_best_diag = None
    if clean_m is not None and best_m is not None:
        clean_vs_best_diag = {
            "best_diag": by_role["CADFit_original_best.stl"].bbox_diagonal,
            "clean_diag": by_role["clean_reconstructed.stl"].bbox_diagonal,
            "diag_ratio": by_role["clean_reconstructed.stl"].bbox_diagonal
            / max(by_role["CADFit_original_best.stl"].bbox_diagonal, 1e-12),
            "sha_same": by_role["CADFit_original_best.stl"].sha256 == by_role["clean_reconstructed.stl"].sha256,
        }

    # IoU provenance
    iou_path = paths["final_iou_json"]
    iou_data = {}
    if iou_path.exists():
        try:
            iou_data = json.loads(iou_path.read_text(encoding="utf-8"))
        except Exception:
            iou_data = {"_raw": iou_path.read_text(encoding="utf-8")[:500]}

    # Trace code: run_pipeline uses mesh_iou_cpu_boolean(original_stl, final_output, normalize=True)
    # which normalizes GT (A) only; reconstruction assumed already normalized by CADFit.
    gt_from_json = str(iou_data.get("ground_truth", "")) if isinstance(iou_data, dict) else ""
    recon_from_json = str(iou_data.get("reconstruction", "")) if isinstance(iou_data, dict) else ""
    iou_prov = {
        "IOU_SOURCE_INPUT_PATH": gt_from_json or str(paths["input_high_mesh"].resolve()),
        "IOU_SOURCE_RECONSTRUCTION_PATH": recon_from_json
        or (str(paths["original_best_stl"].resolve()) if paths["original_best_stl"].exists() else ""),
        "IOU_USES_ALIGNMENT": True,  # normalize_mesh: center + isotropic scale to [-1,1] on GT
        "IOU_USES_GLOBAL_SCALE": True,
        "IOU_TIMESTAMP": file_mtime(iou_path),
        "IOU_JSON_PATH": str(iou_path.resolve()) if iou_path.exists() else "",
        "IOU_JSON_CONTENT": iou_data,
        "IOU_CODE_LOCATION": "run_pipeline.py -> mesh_iou_cpu_boolean(..., normalize=True); iou.py:normalize_mesh",
        "IOU_IS_STALE": False,
        "IOU_PROVENANCE_VALID": False,
        "IOU_PROVENANCE_VALID_FOR_RAW_DISPLAY": False,
    }
    if paths["original_best_stl"].exists() and iou_path.exists():
        try:
            iou_prov["IOU_IS_STALE"] = iou_path.stat().st_mtime + 1 < paths["original_best_stl"].stat().st_mtime
        except Exception:
            iou_prov["IOU_IS_STALE"] = True

    # Prove reconstruction path resolves to same SHA as displayed artifact STL.
    recon_resolved = None
    if recon_from_json:
        cand = Path(recon_from_json)
        if not cand.is_absolute():
            cand = ROOT / cand
        if cand.exists():
            recon_resolved = cand
    recon_sha_ok = bool(
        recon_resolved
        and sha256(recon_resolved) == by_role["artifact_reconstructed_cad.stl"].sha256
        and sha_same
    )
    # Input path in JSON is often cadfit_input copy — compare SHA to displayed input.
    input_sha_ok = False
    if gt_from_json:
        cand = Path(gt_from_json)
        if not cand.is_absolute():
            cand = ROOT / cand
        if cand.exists() and by_role["input_high_mesh.stl"].sha256:
            input_sha_ok = sha256(cand) == by_role["input_high_mesh.stl"].sha256
    # Provenance valid for *aligned* IoU claim if paths+sha match and not stale.
    # Still NOT valid as a raw-coordinate success metric.
    iou_prov["IOU_PROVENANCE_VALID"] = bool(
        iou_path.exists()
        and not iou_prov["IOU_IS_STALE"]
        and recon_sha_ok
        and input_sha_ok
        and isinstance(iou_data, dict)
        and "final_iou" in iou_data
    )

    gen_info = analyze_generated_cad(paths["generated_cad"])

    # --- Triple renders ---
    render_dir = art / "audit_renders"
    render_dir.mkdir(parents=True, exist_ok=True)
    render_ok = {"raw": False, "normalized": False, "aligned": False}
    render_bug = False
    geometry_recon_valid = False
    export_bug = False

    if input_m is not None and art_m is not None:
        render_ok["raw"] = render_pair(
            input_m,
            art_m,
            render_dir / "raw_coordinate_comparison.png",
            "input (raw)",
            "reconstructed (raw)",
            "RAW",
            shared_bounds=True,
        )
        # independently normalize
        in_n = input_m.copy()
        ar_n = art_m.copy()
        in_n.vertices = in_n.vertices - in_n.centroid
        ar_n.vertices = ar_n.vertices - ar_n.centroid
        in_scale = float(np.max(np.abs(in_n.vertices))) or 1.0
        ar_scale = float(np.max(np.abs(ar_n.vertices))) or 1.0
        in_n.vertices /= in_scale
        ar_n.vertices /= ar_scale
        render_ok["normalized"] = render_pair(
            in_n,
            ar_n,
            render_dir / "independently_normalized_comparison.png",
            "input (indep. norm)",
            "reconstructed (indep. norm)",
            "NORMALIZED",
            shared_bounds=False,
        )
        # evaluation aligned: apply CADFit-style normalize to both; save aligned recon
        pred_n, gt_n, xform = similarity_align_pred_to_gt(art_m, input_m)
        aligned_path = art / "aligned_reconstructed.stl"
        pred_n.export(str(aligned_path))
        (art / "evaluation_alignment_transform.json").write_text(json.dumps(xform, indent=2), encoding="utf-8")
        render_ok["aligned"] = render_pair(
            gt_n,
            pred_n,
            render_dir / "evaluation_aligned_comparison.png",
            "input (eval-aligned)",
            "reconstructed (eval-aligned)",
            "EVALUATION-ALIGNED",
            shared_bounds=True,
        )
        # also refresh comparison.png as explicitly labeled evaluation-aligned (not as raw success)
        shutil.copy2(render_dir / "evaluation_aligned_comparison.png", art / "comparison_evaluation_aligned.png")

        # visual validity heuristics
        if by_role["artifact_reconstructed_cad.stl"].vertex_count >= 50 and by_role[
            "artifact_reconstructed_cad.stl"
        ].triangle_count >= 50 and by_role["artifact_reconstructed_cad.stl"].bbox_diagonal > 1e-6:
            # if normalized render exists and mesh non-degenerate, treat visual as likely valid
            geometry_recon_valid = render_ok["normalized"] and abs(by_role["artifact_reconstructed_cad.stl"].volume) > 0
        # render bug: normalized ok but raw looks tiny
        if geometry_recon_valid and scale_ratio is not None and scale_ratio < 0.25:
            render_bug = True

    if clean_vs_best_diag and clean_vs_best_diag["diag_ratio"] > 0:
        # export bug if clean differs wildly from best OR if generated exports intermediate
        if gen_info.get("exports_only_intermediate"):
            export_bug = True
        if clean_vs_best_diag["diag_ratio"] < 0.1 or clean_vs_best_diag["diag_ratio"] > 10:
            export_bug = True

    # --- Independent metrics ---
    metrics = {
        "RAW_BBOX_OVERLAP": None,
        "RAW_IOU": None,
        "RAW_IOU_OK": False,
        "RAW_IOU_ERROR": "",
        "ALIGNED_IOU": None,
        "ALIGNED_IOU_OK": False,
        "ALIGNED_IOU_ERROR": "",
        "RAW_CHAMFER": None,
        "ALIGNED_CHAMFER": None,
        "CLEAN_RAW_IOU": None,
        "CLEAN_ALIGNED_IOU": None,
        "volume_ratio": volume_ratio,
        "scale_ratio": scale_ratio,
        "centroid_distance": centroid_distance,
        "extent_ratios": extent_ratios,
    }
    if input_m is not None and art_m is not None:
        metrics["RAW_BBOX_OVERLAP"] = raw_bbox_overlap(input_m, art_m)
        r = safe_iou(paths["input_high_mesh"], paths["artifact_recon_stl"], normalize=False)
        metrics["RAW_IOU_OK"] = r["ok"]
        metrics["RAW_IOU"] = r["iou"]
        metrics["RAW_IOU_ERROR"] = r["error"]
        a = safe_iou(paths["input_high_mesh"], paths["artifact_recon_stl"], normalize=True)
        metrics["ALIGNED_IOU_OK"] = a["ok"]
        metrics["ALIGNED_IOU"] = a["iou"]
        metrics["ALIGNED_IOU_ERROR"] = a["error"]
        rc = safe_chamfer(paths["input_high_mesh"], paths["artifact_recon_stl"], normalize=False)
        ac = safe_chamfer(paths["input_high_mesh"], paths["artifact_recon_stl"], normalize=True)
        metrics["RAW_CHAMFER"] = rc.get("chamfer")
        metrics["RAW_CHAMFER_OK"] = rc.get("ok")
        metrics["ALIGNED_CHAMFER"] = ac.get("chamfer")
        metrics["ALIGNED_CHAMFER_OK"] = ac.get("ok")
        if paths["clean_stl"].exists():
            cr = safe_iou(paths["input_high_mesh"], paths["clean_stl"], normalize=False)
            ca = safe_iou(paths["input_high_mesh"], paths["clean_stl"], normalize=True)
            metrics["CLEAN_RAW_IOU"] = cr.get("iou")
            metrics["CLEAN_ALIGNED_IOU"] = ca.get("iou")
        if (art / "aligned_reconstructed.stl").exists():
            # aligned file is already normalized; compare to independently normalized input saved temporarily
            tmp_gt = render_dir / "_gt_norm_for_iou.stl"
            gt_n.export(str(tmp_gt))
            aa = safe_iou(tmp_gt, art / "aligned_reconstructed.stl", normalize=False)
            metrics["EVAL_ALIGNED_FILE_IOU"] = aa.get("iou")
            metrics["EVAL_ALIGNED_FILE_IOU_OK"] = aa.get("ok")

    # Gates
    code_exec = (art / "clean_reexport" / "exec_report.json").exists() and json.loads(
        (art / "clean_reexport" / "exec_report.json").read_text()
    ).get("success", False)
    out_solid = by_role["artifact_reconstructed_cad.stl"].exists and by_role[
        "artifact_reconstructed_cad.stl"
    ].triangle_count > 0
    nondeg = (
        by_role["artifact_reconstructed_cad.stl"].vertex_count >= 50
        and by_role["artifact_reconstructed_cad.stl"].triangle_count >= 50
        and abs(by_role["artifact_reconstructed_cad.stl"].volume) > 0
        and by_role["artifact_reconstructed_cad.stl"].bbox_diagonal > 1e-6
    )
    prov = bool(sha_same)
    gates = {
        "CODE_EXECUTION_VALID": bool(code_exec),
        "OUTPUT_SOLID_VALID": bool(out_solid),
        "OUTPUT_NONDEGENERATE": bool(nondeg),
        "ARTIFACT_PROVENANCE_VALID": prov,
        "RAW_SCALE_VALID": bool(raw_scale_valid),
        "RAW_GEOMETRY_SCALE_VALID": bool(raw_scale_valid),
        "NORMALIZED_VISUAL_VALID": bool(geometry_recon_valid),
        "IOU_PROVENANCE_VALID": bool(iou_prov["IOU_PROVENANCE_VALID"]),
        "COMPARISON_RENDER_VALID": bool(render_ok["raw"] and render_ok["normalized"] and render_ok["aligned"]),
        "GEOMETRY_RECONSTRUCTION_VALID": bool(geometry_recon_valid),
        "RENDER_OR_TRANSFORM_BUG": bool(render_bug),
        "EXPORT_BUG": bool(export_bug),
    }
    all_success = all(
        [
            gates["CODE_EXECUTION_VALID"],
            gates["OUTPUT_SOLID_VALID"],
            gates["OUTPUT_NONDEGENERATE"],
            gates["ARTIFACT_PROVENANCE_VALID"],
            gates["RAW_SCALE_VALID"],
            gates["NORMALIZED_VISUAL_VALID"],
            gates["IOU_PROVENANCE_VALID"],
            gates["COMPARISON_RENDER_VALID"],
        ]
    )
    # User success requires comparison not a point + raw scale etc.
    # With scale mismatch, CASE fails validation even if shape is good under normalize.
    case_status = "success" if all_success else "failed_validation"

    return {
        "case": case_key,
        "audit_rows": [asdict(r) for r in audit_rows],
        "comparisons": {
            "A_original_best_sha_eq_artifact_recon": sha_same,
            "B_original_best_vs_clean_reexec": clean_vs_best_diag,
            "C_step_reopen": by_role["artifact_reconstructed_cad.step"].step_reopen_ok,
            "D_path_cross_contamination": False,  # filled later
        },
        "scale": {
            "scale_ratio": scale_ratio,
            "volume_ratio": volume_ratio,
            "centroid_distance": centroid_distance,
            "extent_ratios": extent_ratios,
            "RAW_GEOMETRY_SCALE_VALID": raw_scale_valid,
        },
        "iou_provenance": iou_prov,
        "generated_cad_analysis": gen_info,
        "renders": render_ok,
        "metrics": metrics,
        "gates": gates,
        "CASE_STATUS": case_status,
        "original_best_bbox": by_role["CADFit_original_best.stl"].bounds_min
        + " | "
        + by_role["CADFit_original_best.stl"].bounds_max,
        "original_best_diag": by_role["CADFit_original_best.stl"].bbox_diagonal,
        "artifact_bbox": by_role["artifact_reconstructed_cad.stl"].bounds_min
        + " | "
        + by_role["artifact_reconstructed_cad.stl"].bounds_max,
        "artifact_diag": by_role["artifact_reconstructed_cad.stl"].bbox_diagonal,
        "input_diag": by_role["input_high_mesh.stl"].bbox_diagonal,
        "original_best_exists": by_role["CADFit_original_best.stl"].exists,
        "sha_best": by_role["CADFit_original_best.stl"].sha256,
        "sha_artifact": by_role["artifact_reconstructed_cad.stl"].sha256,
        "sha_input": by_role["input_high_mesh.stl"].sha256,
    }


def main() -> int:
    # ensure clean reexport exists
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from execute_generated_program_clean import execute_case

    for case_key in CASES:
        print(f"[clean-exec] {case_key} ...", flush=True)
        execute_case(case_key, ART)

    results = {}
    all_rows = []
    for case_key, meta in CASES.items():
        print(f"[audit] processing {case_key} ...", flush=True)
        results[case_key] = process_case(case_key, meta)
        all_rows.extend(results[case_key]["audit_rows"])

    # path cross-contamination check
    sha_a_in = results["case_a_flange"]["sha_input"]
    sha_b_in = results["case_b_bracket"]["sha_input"]
    sha_a_best = results["case_a_flange"]["sha_best"]
    sha_b_best = results["case_b_bracket"]["sha_best"]
    cross = (
        (sha_a_best and sha_a_best == sha_b_best)
        or (sha_a_in and sha_a_in == sha_b_in)
        or (results["case_a_flange"]["sha_artifact"] == results["case_b_bracket"]["sha_best"] and sha_a_best != sha_b_best)
    )
    for k in results:
        results[k]["comparisons"]["D_path_cross_contamination"] = bool(cross)
        if cross:
            results[k]["gates"]["ARTIFACT_PROVENANCE_VALID"] = False
            results[k]["CASE_STATUS"] = "failed_validation"

    # CSV
    csv_path = ART / "geometry_provenance_audit.csv"
    fields = list(all_rows[0].keys()) if all_rows else []
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for row in all_rows:
            w.writerow(row)

    # Markdown report
    md_path = ART / "geometry_provenance_report.md"
    lines = [
        "# Geometry Provenance Audit — Synthetic-High-Mesh-Two-Case-Demo-v1",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Root cause (preliminary)",
        "",
        "CADFit optimizes and stores reconstruction in **normalized coordinates** (~[-1, 1]).",
        "Input `input_high_mesh.stl` remains in **engineering / mm-scale** coordinates.",
        "`final_iou.json` is computed via `mesh_iou_cpu_boolean(..., normalize=True)`, which",
        "centers/scales the GT mesh; high IoU therefore reflects **shape similarity after alignment**,",
        "not raw-coordinate overlap. The previous `comparison.png` used a **shared camera** on raw",
        "coordinates, so the reconstruction appears as a near-point — a **render/transform presentation bug**,",
        "not proof that CADFit produced an empty solid.",
        "",
        "## Comparisons required",
        "",
    ]
    for case_key, r in results.items():
        lines.append(f"### {case_key}")
        lines.append("")
        c = r["comparisons"]
        lines.append(f"- A. original best SHA == artifact reconstructed STL: **{c['A_original_best_sha_eq_artifact_recon']}**")
        lines.append(f"- B. clean re-exec vs best: `{json.dumps(c['B_original_best_vs_clean_reexec'])}`")
        lines.append(f"- C. STEP reopen ok: **{c['C_step_reopen']}**")
        lines.append(f"- D. path cross-contamination: **{c['D_path_cross_contamination']}**")
        lines.append("")
        lines.append("#### Scale / position")
        lines.append(f"- scale_ratio: `{r['scale']['scale_ratio']}`")
        lines.append(f"- volume_ratio: `{r['scale']['volume_ratio']}`")
        lines.append(f"- centroid_distance: `{r['scale']['centroid_distance']}`")
        lines.append(f"- extent_ratios: `{r['scale']['extent_ratios']}`")
        lines.append(f"- RAW_GEOMETRY_SCALE_VALID: **{r['scale']['RAW_GEOMETRY_SCALE_VALID']}**")
        lines.append("")
        lines.append("#### IoU provenance")
        for kk, vv in r["iou_provenance"].items():
            if kk == "IOU_JSON_CONTENT":
                lines.append(f"- {kk}: `{json.dumps(vv)[:300]}`")
            else:
                lines.append(f"- {kk}: `{vv}`")
        lines.append("")
        lines.append("#### Metrics (recomputed)")
        for kk, vv in r["metrics"].items():
            lines.append(f"- {kk}: `{vv}`")
        lines.append("")
        lines.append("#### Gates")
        for kk, vv in r["gates"].items():
            lines.append(f"- {kk}: **{vv}**")
        lines.append(f"- CASE_STATUS: **{r['CASE_STATUS']}**")
        lines.append("")
        lines.append("#### generated_cad.py")
        lines.append(f"```json\n{json.dumps(r['generated_cad_analysis'], indent=2)}\n```")
        lines.append("")

    lines.append("## Per-file audit table")
    lines.append("")
    lines.append("See `geometry_provenance_audit.csv`.")
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    # Update per-case status + final gate
    for case_key, r in results.items():
        case_dir = CASES[case_key]["art_dir"]
        (case_dir / "validation_gates.json").write_text(json.dumps(r["gates"], indent=2), encoding="utf-8")
        (case_dir / "independent_metrics.json").write_text(json.dumps(r["metrics"], indent=2), encoding="utf-8")
        status = {
            "CASE_STATUS": r["CASE_STATUS"],
            "gates": r["gates"],
            "metrics": r["metrics"],
            "scale": r["scale"],
            "iou_provenance": {k: v for k, v in r["iou_provenance"].items() if k != "IOU_JSON_CONTENT"},
        }
        (case_dir / "case_validation_status.json").write_text(json.dumps(status, indent=2), encoding="utf-8")

    a = results["case_a_flange"]
    b = results["case_b_bracket"]
    both_success = a["CASE_STATUS"] == "success" and b["CASE_STATUS"] == "success"
    any_success = a["CASE_STATUS"] == "success" or b["CASE_STATUS"] == "success"
    # With validation failures due to raw scale / render, FINAL_GATE = FAIL (not PASS).
    # PARTIAL if geometry exists and normalized visual valid but raw scale fails.
    if both_success:
        final_gate = "PASS"
    elif a["gates"].get("NORMALIZED_VISUAL_VALID") or b["gates"].get("NORMALIZED_VISUAL_VALID"):
        final_gate = "PARTIAL"
    else:
        final_gate = "FAIL"

    root_cause = (
        "CADFit reconstruction is in normalized ~[-1,1] coordinates while input_high_mesh is engineering-scale; "
        "final_iou uses normalize=True (aligned shape IoU). Prior comparison.png used shared raw camera bounds, "
        "making reconstruction appear as a point (RENDER_OR_TRANSFORM_BUG). "
        "RAW_GEOMETRY_SCALE_VALID=false; CASE_STATUS=failed_validation until raw-scale export/alignment is fixed for display."
    )

    summary = {
        "FINAL_GATE": final_gate,
        "CASE_A": {
            "ORIGINAL_BEST_STL_EXISTS": a["original_best_exists"],
            "ORIGINAL_BEST_BBOX": a["original_best_bbox"],
            "ARTIFACT_BBOX": a["artifact_bbox"],
            "SCALE_RATIO": a["scale"]["scale_ratio"],
            "RAW_IOU": a["metrics"]["RAW_IOU"],
            "ALIGNED_IOU": a["metrics"]["ALIGNED_IOU"],
            "RENDER_BUG": a["gates"]["RENDER_OR_TRANSFORM_BUG"],
            "EXPORT_BUG": a["gates"]["EXPORT_BUG"],
            "PROVENANCE_VALID": a["gates"]["ARTIFACT_PROVENANCE_VALID"],
            "FINAL_STATUS": a["CASE_STATUS"],
        },
        "CASE_B": {
            "ORIGINAL_BEST_STL_EXISTS": b["original_best_exists"],
            "ORIGINAL_BEST_BBOX": b["original_best_bbox"],
            "ARTIFACT_BBOX": b["artifact_bbox"],
            "SCALE_RATIO": b["scale"]["scale_ratio"],
            "RAW_IOU": b["metrics"]["RAW_IOU"],
            "ALIGNED_IOU": b["metrics"]["ALIGNED_IOU"],
            "RENDER_BUG": b["gates"]["RENDER_OR_TRANSFORM_BUG"],
            "EXPORT_BUG": b["gates"]["EXPORT_BUG"],
            "PROVENANCE_VALID": b["gates"]["ARTIFACT_PROVENANCE_VALID"],
            "FINAL_STATUS": b["CASE_STATUS"],
        },
        "ROOT_CAUSE": root_cause,
        "FILES_MODIFIED": [
            "artifacts/synthetic_high_mesh_two_case_v1/final_gate.json",
            "artifacts/synthetic_high_mesh_two_case_v1/geometry_provenance_audit.csv",
            "artifacts/synthetic_high_mesh_two_case_v1/geometry_provenance_report.md",
            "artifacts/synthetic_high_mesh_two_case_v1/audit_summary.json",
            "scripts/synthetic_high_mesh_two_case/execute_generated_program_clean.py",
            "scripts/synthetic_high_mesh_two_case/geometry_provenance_audit.py",
            "case_*/audit_renders/*.png",
            "case_*/clean_reexport/*",
            "case_*/validation_gates.json",
            "case_*/independent_metrics.json",
        ],
        "TESTS_PASSED": False,
        "BLOCKERS": [
            "RAW_GEOMETRY_SCALE_VALID=false for both cases (reconstructed in normalized coords vs mm-scale input)",
            "Prior comparison.png false-positive vs report IoU (shared raw camera)",
            "CASE_STATUS=failed_validation until display/export uses explicit RAW vs ALIGNED metrics",
        ],
    }
    (ART / "audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (ART / "final_gate.json").write_text(
        json.dumps(
            {
                "FINAL_GATE": final_gate,
                "reason": root_cause,
                "cases": {k: v["CASE_STATUS"] for k, v in results.items()},
                "updated_at": datetime.now(timezone.utc).isoformat(),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Print required block
    print()
    print(f"FINAL_GATE={final_gate}")
    print(f"CASE_A_ORIGINAL_BEST_STL_EXISTS={a['original_best_exists']}")
    print(f"CASE_A_ORIGINAL_BEST_BBOX={a['original_best_bbox']}")
    print(f"CASE_A_ARTIFACT_BBOX={a['artifact_bbox']}")
    print(f"CASE_A_SCALE_RATIO={a['scale']['scale_ratio']}")
    print(f"CASE_A_RAW_IOU={a['metrics']['RAW_IOU']}")
    print(f"CASE_A_ALIGNED_IOU={a['metrics']['ALIGNED_IOU']}")
    print(f"CASE_A_RENDER_BUG={a['gates']['RENDER_OR_TRANSFORM_BUG']}")
    print(f"CASE_A_EXPORT_BUG={a['gates']['EXPORT_BUG']}")
    print(f"CASE_A_PROVENANCE_VALID={a['gates']['ARTIFACT_PROVENANCE_VALID']}")
    print(f"CASE_A_FINAL_STATUS={a['CASE_STATUS']}")
    print()
    print(f"CASE_B_ORIGINAL_BEST_STL_EXISTS={b['original_best_exists']}")
    print(f"CASE_B_ORIGINAL_BEST_BBOX={b['original_best_bbox']}")
    print(f"CASE_B_ARTIFACT_BBOX={b['artifact_bbox']}")
    print(f"CASE_B_SCALE_RATIO={b['scale']['scale_ratio']}")
    print(f"CASE_B_RAW_IOU={b['metrics']['RAW_IOU']}")
    print(f"CASE_B_ALIGNED_IOU={b['metrics']['ALIGNED_IOU']}")
    print(f"CASE_B_RENDER_BUG={b['gates']['RENDER_OR_TRANSFORM_BUG']}")
    print(f"CASE_B_EXPORT_BUG={b['gates']['EXPORT_BUG']}")
    print(f"CASE_B_PROVENANCE_VALID={b['gates']['ARTIFACT_PROVENANCE_VALID']}")
    print(f"CASE_B_FINAL_STATUS={b['CASE_STATUS']}")
    print()
    print(f"ROOT_CAUSE={root_cause}")
    print(f"FILES_MODIFIED={summary['FILES_MODIFIED']}")
    print(f"TESTS_PASSED={summary['TESTS_PASSED']}")
    print(f"BLOCKERS={summary['BLOCKERS']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
