from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from .io_utils import load_mesh


def _mesh_for_vis(mesh: trimesh.Trimesh, max_faces: int = 12000) -> trimesh.Trimesh:
    if len(mesh.faces) <= max_faces:
        return mesh
    idx = np.random.default_rng(42).choice(len(mesh.faces), size=max_faces, replace=False)
    return mesh.submesh([idx], append=True, repair=False)


def render_mesh(mesh: trimesh.Trimesh, out_path: Path, color: str, title: str, elev: float = 22, azim: float = 42) -> None:
    mv = _mesh_for_vis(mesh)
    tris = mv.vertices[mv.faces]
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(tris, linewidths=0.02, alpha=0.92)
    coll.set_facecolor(color)
    ax.add_collection3d(coll)
    verts = mv.vertices
    bmin, bmax = verts.min(0), verts.max(0)
    ctr = 0.5 * (bmin + bmax)
    ext = np.max(bmax - bmin) * 0.55 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    ax.axis("off")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def render_router_chart(routing: dict, out_path: Path) -> None:
    names = ["CADFIT", "ROUTEB", "DECOMPOSE"]
    vals = [routing["CADFIT_SCORE"], routing["ROUTEB_SCORE"], routing["DECOMPOSE_SCORE"]]
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.barh(names, vals, color=["#4C78A8", "#E45756", "#54A24B"])
    ax.set_xlim(0, max(vals) * 1.2 + 0.05)
    ax.set_title(f"Router: {routing['selected_route']}\nconf={routing['confidence']:.2f}")
    for i, v in enumerate(vals):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=9)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def render_overlay(a: trimesh.Trimesh, b: trimesh.Trimesh, out_path: Path, title: str) -> None:
    pa = a.sample(4000)
    pb = b.sample(4000)
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(pa[:, 0], pa[:, 1], pa[:, 2], s=0.5, c="#4C78A8", alpha=0.35)
    ax.scatter(pb[:, 0], pb[:, 1], pb[:, 2], s=0.5, c="#E45756", alpha=0.35)
    pts = np.vstack([pa, pb])
    ctr = pts.mean(0)
    ext = np.max(pts.max(0) - pts.min(0)) * 0.6 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_title(title, fontsize=10)
    ax.axis("off")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=160)
    plt.close(fig)


def render_assembly(meshes: list[tuple[trimesh.Trimesh, str]], out_path: Path, title: str) -> None:
    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    allv = []
    for mesh, color in meshes:
        mv = _mesh_for_vis(mesh)
        tris = mv.vertices[mv.faces]
        coll = Poly3DCollection(tris, linewidths=0.02, alpha=0.9)
        coll.set_facecolor(color)
        ax.add_collection3d(coll)
        allv.append(mv.vertices)
    v = np.vstack(allv)
    ctr = 0.5 * (v.min(0) + v.max(0))
    ext = np.max(v.max(0) - v.min(0)) * 0.55 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=22, azim=42)
    ax.set_title(title, fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
