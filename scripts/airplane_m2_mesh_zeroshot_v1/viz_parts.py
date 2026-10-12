#!/usr/bin/env python3
"""Per-part 5-panel viz + comparison grid for airplane M2 zero-shot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh

REPO = Path(__file__).resolve().parents[2]
OUT_ROOT = REPO / "ours3" / "airplane_m2_mesh_zeroshot_v1"

TYPE_COLOR = {
    "LINE": "#2ca02c",
    "CIRCLE": "#d62728",
    "ELLIPSE": "#9467bd",
    "BSPLINE": "#bcbd22",
}


def _load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.is_file():
        return None
    m = trimesh.load(path, force="mesh", process=False)
    if not isinstance(m, trimesh.Trimesh):
        m = trimesh.util.concatenate(tuple(m.geometry.values()))
    return m


def render_mesh(ax, mesh: trimesh.Trimesh, color, alpha=0.35, label=None):
    # simple projected wire/scatter for headless
    v = np.asarray(mesh.vertices)
    # PCA-ish view: XY of longest two axes
    ax.scatter(v[:: max(1, len(v) // 4000), 0], v[:: max(1, len(v) // 4000), 1], s=1, c=color, alpha=alpha, label=label)
    ax.set_aspect("equal")
    ax.axis("off")


def viz_part(part_id: str) -> Path:
    pdir = OUT_ROOT / "parts" / part_id
    viz_dir = OUT_ROOT / "viz" / part_id
    viz_dir.mkdir(parents=True, exist_ok=True)
    mesh = _load_mesh(pdir / "mesh_canonical.obj")
    meta = json.loads((pdir / "curves_meta.json").read_text())
    sharp = np.load(pdir / "mesh_sharp_edges.npz")

    # 1 input
    fig, ax = plt.subplots(figsize=(4, 4))
    render_mesh(ax, mesh, "#888888", 0.4)
    ax.set_title(f"{part_id} input")
    fig.savefig(viz_dir / "01_input.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 2 edges + curve types (midpoints colored by assigned type if available)
    fig, ax = plt.subplots(figsize=(4, 4))
    render_mesh(ax, mesh, "#bbbbbb", 0.15)
    mids = 0.5 * (sharp["v0"] + sharp["v1"])
    ax.scatter(mids[:: max(1, len(mids) // 2000), 0], mids[:: max(1, len(mids) // 2000), 1], s=2, c="#1f77b4", alpha=0.6)
    ax.set_title(f"sharp+curves K={meta['n_curves_kept']}")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(viz_dir / "02_curves.png", dpi=140, bbox_inches="tight")
    plt.close(fig)

    # 3/4 B0 M2 STEP meshes
    for arm, color, name in [("B0", "#1f77b4", "03_b0"), ("M2", "#ff7f0e", "04_m2")]:
        fig, ax = plt.subplots(figsize=(4, 4))
        render_mesh(ax, mesh, "#cccccc", 0.2)
        stl = OUT_ROOT / "decode" / arm.lower() / part_id / "pred.stl"
        pm = _load_mesh(stl)
        if pm is not None and len(pm.faces):
            render_mesh(ax, pm, color, 0.55)
            ax.set_title(f"{arm} STEP")
        else:
            ax.set_title(f"{arm} STEP (invalid)")
        fig.savefig(viz_dir / f"{name}.png", dpi=140, bbox_inches="tight")
        plt.close(fig)

    # 5 error heatmap proxy: color pred points by distance to input
    fig, ax = plt.subplots(figsize=(4, 4))
    render_mesh(ax, mesh, "#aaaaaa", 0.15)
    stl = OUT_ROOT / "decode" / "m2" / part_id / "pred.stl"
    pm = _load_mesh(stl)
    if pm is not None and len(pm.faces):
        from scipy.spatial import cKDTree

        ref, _ = trimesh.sample.sample_surface(mesh, 4000, seed=0)
        pred, _ = trimesh.sample.sample_surface(pm, 4000, seed=0)
        d, _ = cKDTree(ref).query(pred, k=1)
        sc = ax.scatter(pred[:, 0], pred[:, 1], c=d, s=2, cmap="coolwarm", vmin=0, vmax=max(0.05, np.percentile(d, 95)))
        plt.colorbar(sc, ax=ax, fraction=0.046)
        ax.set_title("M2 error heat")
    else:
        ax.set_title("M2 error (n/a)")
    ax.set_aspect("equal")
    ax.axis("off")
    fig.savefig(viz_dir / "05_error.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    return viz_dir


def make_grid(parts: list[str]) -> Path:
    # 5 columns: Input Curves B0 M2 Error
    n = len(parts)
    fig, axes = plt.subplots(n, 5, figsize=(15, 3 * n))
    if n == 1:
        axes = np.array([axes])
    titles = ["Input", "Curves", "B0", "M2", "Error"]
    files = ["01_input.png", "02_curves.png", "03_b0.png", "04_m2.png", "05_error.png"]
    for i, p in enumerate(parts):
        for j, (t, f) in enumerate(zip(titles, files)):
            ax = axes[i, j]
            img_path = OUT_ROOT / "viz" / p / f
            ax.axis("off")
            if img_path.is_file():
                ax.imshow(plt.imread(img_path))
            if i == 0:
                ax.set_title(t)
            if j == 0:
                ax.set_ylabel(p, rotation=90, size=10)
    out = OUT_ROOT / "viz" / "GRID_CANARY.png"
    fig.tight_layout()
    fig.savefig(out, dpi=120)
    plt.close(fig)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--parts", nargs="+", default=None)
    args = ap.parse_args()
    parts = args.parts or sorted(p.name for p in (OUT_ROOT / "parts").iterdir() if p.is_dir())
    for p in parts:
        print("viz", p, viz_part(p))
    print("grid", make_grid(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
