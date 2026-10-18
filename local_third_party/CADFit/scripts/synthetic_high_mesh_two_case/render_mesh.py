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

from common import CASES


def render(ax, mesh, color="#5b8fd9"):
    verts = np.asarray(mesh.vertices)
    center = (mesh.bounds[0] + mesh.bounds[1]) / 2
    scale = float(np.linalg.norm(mesh.bounds[1] - mesh.bounds[0])) or 1.0
    verts = (verts - center) / scale
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
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


def render_input(case_name: str) -> None:
    case_dir = Path("datasets/synthetic_high_mesh_two_case_v1") / case_name
    audit = json.loads((case_dir / "mesh_audit.json").read_text())
    mesh = trimesh.load(case_dir / "input_high_mesh.stl", force="mesh", process=False)
    fig, ax = plt.subplots(figsize=(6, 5.5), dpi=180)
    render(ax, mesh)
    bb = audit["bbox"]
    label = (
        f"{case_name}\ntriangles={audit['triangle_count']} | STEP faces={audit['ground_truth_step_faces']} | "
        f"watertight={audit['is_watertight']}\nbbox=[{bb[0]:.1f}, {bb[1]:.1f}, {bb[2]:.1f}]"
    )
    fig.text(0.02, 0.98, label, ha="left", va="top", fontsize=9)
    fig.savefig(case_dir / "input_render.png", bbox_inches="tight", pad_inches=0.04, facecolor="white")
    plt.close(fig)
    print(f"INPUT_RENDER={case_dir / 'input_render.png'}")


def main() -> int:
    argparse.ArgumentParser().parse_args()
    for case_name, _ in CASES:
        render_input(case_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
