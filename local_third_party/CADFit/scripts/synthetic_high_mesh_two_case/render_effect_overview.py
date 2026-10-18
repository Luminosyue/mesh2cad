#!/usr/bin/env python3
"""Effect overview: input vs baseline vs GPU run.

IMPORTANT: CADFit reconstructions live in normalized ~[-1,1] coords while the
input high mesh is engineering-scale. Sharing one center/scale across panels
makes reconstructions look like a single point. Each panel is therefore
independently centered and scaled for shape comparison, and labeled as such.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection


CASES = ["case_a_flange", "case_b_bracket"]


def load_mesh(path: Path) -> trimesh.Trimesh:
    return trimesh.load(path, force="mesh", process=False)


def panel_center_scale(mesh: trimesh.Trimesh) -> tuple[np.ndarray, float]:
    bmin, bmax = mesh.bounds
    center = 0.5 * (bmin + bmax)
    scale = float(np.linalg.norm(bmax - bmin)) or 1.0
    return center, scale


def draw(ax, mesh: trimesh.Trimesh, color: str) -> None:
    center, scale = panel_center_scale(mesh)
    verts = (np.asarray(mesh.vertices) - center) / scale
    faces = np.asarray(mesh.faces)
    if len(faces) > 80_000:
        faces = faces[np.linspace(0, len(faces) - 1, 80_000).astype(int)]
    view = np.array([[0.866, -0.5, 0.0], [0.2887, 0.5, -0.8165]])
    pts = verts @ view.T
    z = verts @ np.array([0.408, 0.408, 0.816])
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


def render_case(case: str, out_root: Path) -> None:
    input_path = Path("datasets/synthetic_high_mesh_two_case_v1") / case / "input_high_mesh.stl"
    base_path = Path("artifacts/synthetic_high_mesh_two_case_v1") / case / "reconstructed_cad.stl"
    gpu_path = (
        Path("outputs/synthetic_high_mesh_two_case_v1_gpu_workers4")
        / case
        / "input_high_mesh"
        / "best_greedy_parallel_iterative.stl"
    )
    meshes = [load_mesh(input_path), load_mesh(base_path), load_mesh(gpu_path)]
    audit = json.loads((Path("datasets/synthetic_high_mesh_two_case_v1") / case / "mesh_audit.json").read_text())
    base_iou = json.loads((Path("artifacts/synthetic_high_mesh_two_case_v1") / case / "final_iou.json").read_text()).get("final_iou")
    base_status = json.loads((Path("artifacts/synthetic_high_mesh_two_case_v1") / case / "run_status.json").read_text())
    gpu_iou = json.loads(
        (Path("outputs/synthetic_high_mesh_two_case_v1_gpu_workers4") / case / "input_high_mesh" / "final_iou.json").read_text()
    ).get("final_iou")
    gpu_status = json.loads(
        (Path("outputs/synthetic_high_mesh_two_case_v1_gpu_workers4") / case / "run_status.json").read_text()
    )

    fig, axes = plt.subplots(1, 3, figsize=(15, 5.6), dpi=180)
    titles = [
        f"Input high mesh\n{audit['triangle_count']} triangles",
        f"Baseline workers=1\nALIGNED IoU={base_iou:.4f}, {base_status['runtime_seconds']:.0f}s",
        f"GPU visible + workers=4\nALIGNED IoU={gpu_iou:.4f}, {gpu_status['runtime_seconds']:.0f}s",
    ]
    colors = ["#5b8fd9", "#d9904f", "#61a66b"]
    for ax, mesh, title, color in zip(axes, meshes, titles, colors):
        draw(ax, mesh, color)
        ax.set_title(title, fontsize=10)
    fig.suptitle(
        f"{case} | STEP faces={audit['ground_truth_step_faces']} | prior_mode=no_prior\n"
        "Each panel independently normalized for shape view (NOT raw shared camera)",
        fontsize=11,
    )
    out_root.mkdir(parents=True, exist_ok=True)
    fig.tight_layout(rect=[0, 0.02, 1, 0.92])
    fig.savefig(out_root / f"{case}_effect_overview.png", bbox_inches="tight", pad_inches=0.08, facecolor="white")
    plt.close(fig)


def main() -> int:
    out_root = Path("artifacts/synthetic_high_mesh_visualizations")
    for case in CASES:
        render_case(case, out_root)
        print(f"VISUAL={out_root / (case + '_effect_overview.png')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
