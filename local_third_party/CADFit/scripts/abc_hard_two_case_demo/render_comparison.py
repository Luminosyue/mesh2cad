#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

from common import read_csv_dicts


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(path, force="mesh", process=False)


def normalized_vertices(mesh: trimesh.Trimesh, center: np.ndarray, scale: float) -> np.ndarray:
    return (np.asarray(mesh.vertices) - center) / scale


def render_mesh(ax, mesh: trimesh.Trimesh, center: np.ndarray, scale: float, color: str) -> None:
    verts = normalized_vertices(mesh, center, scale)
    faces = np.asarray(mesh.faces)
    # Isometric camera: project 3D to 2D with fixed basis.
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
    order = np.argsort(z[faces].mean(axis=1))
    tri = pts[faces[order]]
    shade = z[faces[order]].mean(axis=1)
    shade = (shade - shade.min()) / (shade.ptp() + 1e-9)
    from matplotlib.collections import PolyCollection
    base = np.array(matplotlib.colors.to_rgb(color))
    colors = np.clip(base * (0.55 + 0.45 * shade[:, None]), 0, 1)
    pc = PolyCollection(tri, facecolors=colors, edgecolors=(0, 0, 0, 0.03), linewidths=0.05)
    ax.add_collection(pc)
    ax.set_aspect("equal")
    ax.set_xlim(-0.72, 0.72)
    ax.set_ylim(-0.72, 0.72)
    ax.axis("off")


def render_case(case_dir: Path, row: dict) -> None:
    inp = case_dir / "input_high_mesh.stl"
    rec = case_dir / "reconstructed_cad.stl"
    m_in = load_mesh(inp)
    m_rec = load_mesh(rec)
    bounds = np.vstack([m_in.bounds, m_rec.bounds])
    center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2
    scale = float(np.linalg.norm(bounds.max(axis=0) - bounds.min(axis=0))) or 1.0
    for path, mesh, color, title in [
        (case_dir / "input_render.png", m_in, "#5b8fd9", "Input high-res STL"),
        (case_dir / "reconstructed_render.png", m_rec, "#d9904f", "Reconstructed CAD STL"),
    ]:
        fig, ax = plt.subplots(figsize=(5, 5), dpi=180)
        render_mesh(ax, mesh, center, scale, color)
        fig.text(0.02, 0.97, title, ha="left", va="top", fontsize=10)
        fig.savefig(path, bbox_inches="tight", pad_inches=0.03, facecolor="white")
        plt.close(fig)
    iou = ""
    runtime = ""
    try:
        iou = json.loads((case_dir / "final_iou.json").read_text()).get("final_iou", "")
    except Exception:
        pass
    try:
        runtime = json.loads((case_dir / "run_status.json").read_text()).get("runtime_seconds", "")
    except Exception:
        pass
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=180)
    render_mesh(axes[0], m_in, center, scale, "#5b8fd9")
    render_mesh(axes[1], m_rec, center, scale, "#d9904f")
    axes[0].set_title("Input high-res STL", fontsize=11)
    axes[1].set_title("Reconstructed CAD STL", fontsize=11)
    label = (
        f"ABC ID: {row.get('abc_id','')} | STEP faces: {row.get('step_face_count','')} | "
        f"Input triangles: {row.get('triangle_count','')} | IoU: {float(iou):.4f} | "
        f"Runtime: {float(runtime):.1f}s"
    ) if iou != "" and runtime != "" else f"ABC ID: {row.get('abc_id','')}"
    fig.text(0.5, 0.02, label, ha="center", fontsize=9)
    fig.savefig(case_dir / "comparison.png", bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="datasets/abc_hard_two_case_demo/manifests/selected_two_cases.csv")
    ap.add_argument("--artifacts-root", default="artifacts/abc_hard_two_case_demo")
    args = ap.parse_args()
    rows = {r["case_name"]: r for r in read_csv_dicts(args.manifest)}
    for case in ["case_a", "case_b"]:
        render_case(Path(args.artifacts_root) / case, rows.get(case, {}))
        print(f"RENDERED {case}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
