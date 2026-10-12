#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART_DIR = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
CADFIT_RAW = ROOT / "ours3/cadfit_xpart45_routea_v1/cadfit_raw"
RENDER_DIR = ROOT / "ours3/cadfit_xpart45_routea_v1/renders"


def _mesh_for_vis(mesh: trimesh.Trimesh, max_faces: int = 20000) -> trimesh.Trimesh:
    if len(mesh.faces) <= max_faces:
        return mesh
    idx = np.random.default_rng(42).choice(len(mesh.faces), size=max_faces, replace=False)
    return mesh.submesh([idx], append=True, repair=False)


def _setup_ax(ax, verts: np.ndarray) -> None:
    bmin, bmax = verts.min(axis=0), verts.max(axis=0)
    ctr = 0.5 * (bmin + bmax)
    ext = np.max(bmax - bmin) * 0.6 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_box_aspect([1, 1, 1])
    ax.axis("off")


def render_mesh(mesh: trimesh.Trimesh, out_path: Path, color: str, title: str) -> None:
    mv = _mesh_for_vis(mesh)
    tris = mv.vertices[mv.faces]
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(tris, linewidths=0.03, alpha=1.0)
    coll.set_facecolor(color)
    coll.set_edgecolor((0, 0, 0, 0.06))
    ax.add_collection3d(coll)
    _setup_ax(ax, mv.vertices)
    ax.view_init(elev=22, azim=42)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def render_overlay(mesh_a: trimesh.Trimesh, mesh_b: trimesh.Trimesh, out_path: Path, title: str) -> None:
    pa = mesh_a.sample(6000)
    pb = mesh_b.sample(6000)
    pts = np.vstack([pa, pb])
    pts0 = pts - pts.mean(axis=0, keepdims=True)
    _, _, vt = np.linalg.svd(pts0, full_matrices=False)
    u = vt[:2].T
    pa2 = (pa - pts.mean(axis=0)) @ u
    pb2 = (pb - pts.mean(axis=0)) @ u

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(pa2[:, 0], pa2[:, 1], s=1.0, c="#2E86DE", alpha=0.35, label="X-Part Source")
    ax.scatter(pb2[:, 0], pb2[:, 1], s=1.0, c="#E74C3C", alpha=0.35, label="CADFit Recon")
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.legend(loc="upper right", fontsize=8, frameon=False)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def render_feature_edges(mesh: trimesh.Trimesh, out_path: Path, title: str, deg_thresh: float = 30.0) -> None:
    mv = _mesh_for_vis(mesh)
    tris = mv.vertices[mv.faces]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(tris, linewidths=0.02, alpha=0.18)
    coll.set_facecolor("#95A5A6")
    coll.set_edgecolor((0, 0, 0, 0.02))
    ax.add_collection3d(coll)

    if hasattr(mv, "face_adjacency_edges") and len(mv.face_adjacency_edges) > 0:
        edges = mv.face_adjacency_edges
        angles_deg = np.degrees(mv.face_adjacency_angles)
        mask = angles_deg >= deg_thresh
        sel = edges[mask]
        if len(sel) > 6000:
            sel = sel[np.random.default_rng(7).choice(len(sel), 6000, replace=False)]
        for e in sel:
            p0, p1 = mv.vertices[e[0]], mv.vertices[e[1]]
            ax.plot([p0[0], p1[0]], [p0[1], p1[1]], [p0[2], p1[2]], color="#111111", lw=0.55, alpha=0.8)

    _setup_ax(ax, mv.vertices)
    ax.view_init(elev=22, azim=42)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180)
    plt.close(fig)


def main() -> None:
    rendered = []
    for i in range(45):
        pid = f"PART_{i:03d}"
        src = XPART_DIR / pid / f"complete_part_{i:03d}.obj"
        rec = CADFIT_RAW / pid / "best_greedy_parallel_iterative.stl"
        iou = CADFIT_RAW / pid / "final_iou.json"
        if not (src.is_file() and rec.is_file() and iou.is_file()):
            continue
        try:
            m_src = trimesh.load(str(src), force="mesh", process=False)
            m_rec = trimesh.load(str(rec), force="mesh", process=False)
            outp = RENDER_DIR / pid
            render_mesh(m_src, outp / "01_source_xpart.png", "#4C78A8", f"{pid} Source (X-Part)")
            render_mesh(m_rec, outp / "02_cadfit_recon.png", "#E45756", f"{pid} CADFit Reconstruction")
            render_overlay(m_src, m_rec, outp / "03_overlay_projection.png", f"{pid} Source vs CAD Overlay")
            render_feature_edges(m_rec, outp / "04_cad_feature_edges.png", f"{pid} CAD + Feature Edges")
            rendered.append(pid)
            print(f"rendered {pid}")
        except Exception as exc:
            print(f"skip {pid}: {exc}")

    (RENDER_DIR / "manifest.json").write_text(json.dumps({"rendered_parts": rendered, "count": len(rendered)}, indent=2) + "\n")
    print(f"DONE_RENDER count={len(rendered)}")


if __name__ == "__main__":
    main()
