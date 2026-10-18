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
from matplotlib.collections import PolyCollection

from common import CASES, count_ops


def project_mesh(mesh, center, scale):
    verts = (np.asarray(mesh.vertices) - center) / scale
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
    return pts, z


def draw(ax, mesh, center, scale, color):
    pts, z = project_mesh(mesh, center, scale)
    faces = np.asarray(mesh.faces)
    order = np.argsort(z[faces].mean(axis=1))
    tri = pts[faces[order]]
    shade = z[faces[order]].mean(axis=1)
    shade = (shade - shade.min()) / (np.ptp(shade) + 1e-9)
    base = np.array(matplotlib.colors.to_rgb(color))
    colors = np.clip(base * (0.56 + 0.44 * shade[:, None]), 0, 1)
    ax.add_collection(PolyCollection(tri, facecolors=colors, edgecolors=(0, 0, 0, 0.035), linewidths=0.05))
    ax.set_aspect("equal")
    ax.set_xlim(-0.72, 0.72)
    ax.set_ylim(-0.72, 0.72)
    ax.axis("off")


def render_case(case_name: str) -> None:
    case_dir = Path("artifacts/synthetic_high_mesh_two_case_v1") / case_name
    inp = trimesh.load(case_dir / "input_high_mesh.stl", force="mesh", process=False)
    rec = trimesh.load(case_dir / "reconstructed_cad.stl", force="mesh", process=False)
    bounds = np.vstack([inp.bounds, rec.bounds])
    center = (bounds.min(axis=0) + bounds.max(axis=0)) / 2
    scale = float(np.linalg.norm(bounds.max(axis=0) - bounds.min(axis=0))) or 1.0
    fig, ax = plt.subplots(figsize=(6, 5.5), dpi=180)
    draw(ax, rec, center, scale, "#d9904f")
    fig.text(0.02, 0.98, f"{case_name}\nCADFit Reconstructed CAD", ha="left", va="top", fontsize=9)
    fig.savefig(case_dir / "reconstructed_render.png", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    audit = json.loads((case_dir / "mesh_audit.json").read_text())
    status = json.loads((case_dir / "run_status.json").read_text())
    iou = json.loads((case_dir / "final_iou.json").read_text()).get("final_iou", "")
    ops = count_ops(case_dir / "generated_cad.py")
    fig, axes = plt.subplots(1, 2, figsize=(10, 5), dpi=180)
    draw(axes[0], inp, center, scale, "#5b8fd9")
    draw(axes[1], rec, center, scale, "#d9904f")
    axes[0].set_title("Input High-Poly Mesh", fontsize=11)
    axes[1].set_title("CADFit Reconstructed CAD", fontsize=11)
    label = (
        f"{case_name} | input triangles={audit['triangle_count']} | STEP faces={audit['ground_truth_step_faces']} | "
        f"IoU={float(iou):.4f} | runtime={float(status.get('runtime_seconds', 0)):.1f}s | "
        f"prior_mode=no_prior | generated lines={ops['program_line_count']}"
    )
    fig.text(0.5, 0.02, label, ha="center", fontsize=8.5)
    fig.savefig(case_dir / "comparison.png", bbox_inches="tight", pad_inches=0.06, facecolor="white")
    plt.close(fig)
    print(f"COMPARISON={case_dir / 'comparison.png'}")


def main() -> int:
    argparse.ArgumentParser().parse_args()
    for case_name, _ in CASES:
        if (Path("artifacts/synthetic_high_mesh_two_case_v1") / case_name / "reconstructed_cad.stl").exists():
            render_case(case_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
