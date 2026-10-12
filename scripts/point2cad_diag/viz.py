"""Matplotlib visualization helpers with fixed camera / scale."""
from __future__ import annotations

from pathlib import Path
from typing import Optional, Sequence, Tuple

import numpy as np

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection


def _ensure_mplot3d():
    # noop import side-effect for Axes3D registration
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401


_ensure_mplot3d()


def set_equal_axes(ax, center: np.ndarray, radius: float):
    c = np.asarray(center, dtype=float).reshape(3)
    r = float(radius)
    ax.set_xlim(c[0] - r, c[0] + r)
    ax.set_ylim(c[1] - r, c[1] + r)
    ax.set_zlim(c[2] - r, c[2] + r)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass
    ax.set_axis_off()


def camera_from_points(points: np.ndarray, pad: float = 1.08):
    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        return np.zeros(3), 1.0
    c = points.mean(0)
    r = np.max(np.linalg.norm(points - c, axis=1)) * pad + 1e-6
    return c, r


def save_failed_panel(path: Path, title: str, reason: str = "NOT GENERATED"):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7, 7), dpi=140)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.text(0.5, 0.58, "FAILED / NOT GENERATED", ha="center", va="center", fontsize=16, color="crimson", fontweight="bold")
    ax.text(0.5, 0.42, reason, ha="center", va="center", fontsize=11, wrap=True)
    ax.set_title(title, fontsize=11)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_mesh(
    mesh_vertices,
    mesh_faces,
    path: Path,
    title: str,
    center,
    radius,
    face_colors=None,
    elev: float = 22,
    azim: float = -55,
    max_faces: int = 45000,
    alpha: float = 0.95,
):
    """
    DEPRECATED for diagnosis delivery images.

    Matplotlib Poly3DCollection on dense tiny triangles looks like scatter even
    when face indices exist. Prefer scripts/fix_point2cad_visualization.py
    (PyVista + Xvfb filled render). This helper still draws Poly3DCollection
    (never scatter) but raises max_faces and uses ortho projection.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    V = np.asarray(mesh_vertices, dtype=float)
    F = np.asarray(mesh_faces, dtype=np.int64)
    if len(V) == 0 or len(F) == 0:
        save_failed_panel(path, title, "empty mesh")
        return
    fig = plt.figure(figsize=(8, 8), dpi=160)
    ax = fig.add_subplot(111, projection="3d")
    try:
        ax.set_proj_type("ortho")
    except Exception:
        pass
    fc = face_colors
    if fc is None:
        fc = np.tile(np.array([[0.55, 0.72, 0.88]]), (len(F), 1))
    else:
        fc = np.asarray(fc, dtype=float)
        if fc.max() > 1.5:
            fc = fc[:, :3] / 255.0
        else:
            fc = fc[:, :3]
    # Do NOT random-subsample faces for viz — that creates scatter-like holes.
    # If extremely large, keep a contiguous prefix rather than random holes.
    if len(F) > max_faces:
        F = F[:max_faces]
        fc = fc[:max_faces]
        title = title + f"\n[matplotlib fallback truncated to {max_faces} faces; use viz_fix PyVista]"
    coll = Poly3DCollection(V[F], linewidths=0.0, edgecolors="none", alpha=alpha)
    coll.set_facecolor(fc)
    ax.add_collection3d(coll)
    set_equal_axes(ax, center, radius)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title + "\n[renderer=matplotlib Poly3DCollection — NOT scatter]", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_points_colored(
    points: np.ndarray,
    labels: Optional[np.ndarray],
    path: Path,
    title: str,
    center,
    radius,
    elev: float = 22,
    azim: float = -55,
    max_points: int = 14000,
    filtered_mask: Optional[np.ndarray] = None,
    point_size: float = 2.5,
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        save_failed_panel(path, title, "empty point cloud")
        return
    fig = plt.figure(figsize=(7, 7), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    rng = np.random.default_rng(0)
    idx = np.arange(len(points))
    if len(idx) > max_points:
        idx = rng.choice(idx, max_points, replace=False)
    P = points[idx]
    if labels is None:
        c = np.full((len(P), 3), 0.3)
    else:
        labels = np.asarray(labels)
        nlab = int(labels.max()) + 1 if len(labels) else 1
        cmap = 0.3 + 0.7 * rng.random((max(nlab, 1), 3))
        c = cmap[labels[idx]]
        if filtered_mask is not None:
            fm = np.asarray(filtered_mask, dtype=bool)[idx]
            c[fm] = np.array([0.65, 0.65, 0.65])
    ax.scatter(P[:, 0], P[:, 1], P[:, 2], c=c, s=point_size, linewidths=0, depthshade=False)
    set_equal_axes(ax, center, radius)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_points_with_normals(
    points: np.ndarray,
    normals: np.ndarray,
    path: Path,
    title: str,
    center,
    radius,
    elev: float = 22,
    azim: float = -55,
    max_points: int = 4000,
    normal_scale: Optional[float] = None,
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    points = np.asarray(points, dtype=float)
    normals = np.asarray(normals, dtype=float)
    if len(points) == 0:
        save_failed_panel(path, title, "empty points/normals")
        return
    fig = plt.figure(figsize=(7, 7), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    rng = np.random.default_rng(0)
    idx = np.arange(len(points))
    if len(idx) > max_points:
        idx = rng.choice(idx, max_points, replace=False)
    P = points[idx]
    N = normals[idx]
    if normal_scale is None:
        normal_scale = 0.04 * float(radius)
    ax.scatter(P[:, 0], P[:, 1], P[:, 2], c="steelblue", s=2.0, linewidths=0, depthshade=False)
    # subsample normals for clarity
    nshow = min(800, len(P))
    sidx = rng.choice(len(P), nshow, replace=False)
    starts = P[sidx]
    ends = starts + N[sidx] * normal_scale
    segs = np.stack([starts, ends], axis=1)
    ax.add_collection3d(Line3DCollection(segs, colors="tomato", linewidths=0.6))
    set_equal_axes(ax, center, radius)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_histogram(values: Sequence[float], path: Path, title: str, xlabel: str):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7, 4.5), dpi=140)
    ax = fig.add_subplot(111)
    vals = np.asarray(list(values), dtype=float)
    if len(vals) == 0:
        ax.text(0.5, 0.5, "NO DATA", ha="center")
    else:
        ax.hist(vals, bins=min(40, max(5, len(vals))), color="steelblue", edgecolor="white")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("count")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_topology_overlay(
    mesh_vertices,
    mesh_faces,
    curves,
    corners,
    path: Path,
    title: str,
    center,
    radius,
    elev: float = 22,
    azim: float = -55,
):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    V = np.asarray(mesh_vertices, dtype=float)
    F = np.asarray(mesh_faces, dtype=np.int64)
    fig = plt.figure(figsize=(7, 7), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    if len(F):
        rng = np.random.default_rng(0)
        Ff = F
        if len(Ff) > 18000:
            Ff = Ff[rng.choice(len(Ff), 18000, replace=False)]
        coll = Poly3DCollection(V[Ff], linewidths=0, alpha=0.12)
        coll.set_facecolor((0.72, 0.76, 0.8))
        ax.add_collection3d(coll)
    segs = []
    for curve in curves or []:
        P = np.asarray(curve.get("pv_points", []), dtype=float)
        L = np.asarray(curve.get("pv_lines", []), dtype=int)
        if len(P) and len(L):
            segs.extend(P[L])
    if len(segs) > 60000:
        rng = np.random.default_rng(0)
        segs = [segs[i] for i in rng.choice(len(segs), 60000, replace=False)]
    if segs:
        ax.add_collection3d(Line3DCollection(segs, colors="crimson", linewidths=1.1, label="edges"))
    C = np.asarray(corners or [], dtype=float)
    if len(C):
        ax.scatter(C[:, 0], C[:, 1], C[:, 2], c="gold", s=28, edgecolors="k", linewidths=0.3, label="corners")
    set_equal_axes(ax, center, radius)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=10)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def plot_layer_debug(
    path: Path,
    title: str,
    center,
    radius,
    mesh=None,
    input_points=None,
    edges=None,
    elev: float = 22,
    azim: float = -55,
):
    """Explicit multi-layer debug figure with legend-like title tags."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = plt.figure(figsize=(7, 7), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    tags = []
    if mesh is not None and len(mesh.faces):
        V = np.asarray(mesh.vertices)
        F = np.asarray(mesh.faces)
        rng = np.random.default_rng(0)
        if len(F) > 25000:
            F = F[rng.choice(len(F), 25000, replace=False)]
        coll = Poly3DCollection(V[F], linewidths=0.01, alpha=0.55)
        coll.set_facecolor((0.55, 0.72, 0.88))
        ax.add_collection3d(coll)
        tags.append("mesh")
    if input_points is not None and len(input_points):
        P = np.asarray(input_points)
        rng = np.random.default_rng(0)
        if len(P) > 8000:
            P = P[rng.choice(len(P), 8000, replace=False)]
        ax.scatter(P[:, 0], P[:, 1], P[:, 2], c="0.35", s=1.5, linewidths=0, depthshade=False)
        tags.append("input_points")
    if edges:
        segs = []
        for curve in edges:
            Pts = np.asarray(curve.get("pv_points", []), dtype=float)
            L = np.asarray(curve.get("pv_lines", []), dtype=int)
            if len(Pts) and len(L):
                segs.extend(Pts[L])
        if segs:
            ax.add_collection3d(Line3DCollection(segs[:40000], colors="crimson", linewidths=1.0))
            tags.append("edges")
    if not tags:
        save_failed_panel(path, title, "no layers provided")
        plt.close(fig)
        return
    set_equal_axes(ax, center, radius)
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title + "\nlayers=[" + ", ".join(tags) + "]", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
