#!/usr/bin/env python3
"""Visualize curve100 decode reconstructions: GT vs B0 / B1 / M2.

Renders a grid of 3D mesh views (matplotlib). Each mesh is centered and scaled
by its bbox diagonal so shape is comparable even when Fusion360 inverse-transform
leaves a residual frame shift (exact DSL match can still have high Chamfer).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_curve100_viz")

import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

REPO = Path(__file__).resolve().parents[2]
DECODE = REPO / "ours3" / "spatiallm_curve_token_v1" / "decode"
OUT = REPO / "ours3" / "spatiallm_curve_token_v1" / "viz"
TRAIN = {
    "deepcad": REPO / "cad_spatial_dataset" / "DeepCAD" / "train",
    "fusion360": REPO / "cad_spatial_dataset" / "Fusion360" / "train",
}


def _load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.is_file():
        return None
    m = trimesh.load(str(path), force="mesh")
    if isinstance(m, trimesh.Scene):
        geoms = [g for g in m.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not geoms:
            return None
        m = trimesh.util.concatenate(geoms)
    if not isinstance(m, trimesh.Trimesh) or len(m.faces) == 0:
        return None
    return m


def _normalize(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    m = mesh.copy()
    c = (m.bounds[0] + m.bounds[1]) * 0.5
    m.apply_translation(-c)
    diag = float(np.linalg.norm(m.bounds[1] - m.bounds[0]))
    if diag > 1e-12:
        m.apply_scale(1.0 / diag)
    return m


def _plot_mesh(ax, mesh: trimesh.Trimesh | None, color: str, title: str) -> None:
    ax.set_title(title, fontsize=9)
    ax.set_axis_off()
    if mesh is None:
        ax.text2D(0.5, 0.5, "no mesh", transform=ax.transAxes, ha="center", color="red")
        return
    m = _normalize(mesh)
    # subsample faces for speed on dense Fusion meshes
    faces = m.faces
    if len(faces) > 8000:
        rng = np.random.default_rng(0)
        faces = faces[rng.choice(len(faces), 8000, replace=False)]
    tris = m.vertices[faces]
    poly = Poly3DCollection(
        tris, alpha=0.85, facecolor=color, edgecolor="k", linewidths=0.05
    )
    ax.add_collection3d(poly)
    ax.set_xlim(-0.6, 0.6)
    ax.set_ylim(-0.6, 0.6)
    ax.set_zlim(-0.6, 0.6)
    ax.view_init(elev=22, azim=35)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass


def _gt_path(row: dict) -> Path:
    ds = str(row["dataset"]).lower()
    return TRAIN[ds] / row["sample_id"] / "model.obj"


def _pick_samples() -> list[dict]:
    """Curated set: good DeepCAD, mid, Fusion high-Chamfer exact, failures."""
    m2_report = json.loads((DECODE / "m2" / "report.json").read_text())
    by_id = {r["id"]: r for r in m2_report["samples"]}
    ids = [
        "deepcad__0045_00454314",  # best chamfer
        "deepcad__0000_00002522",  # typical exact
        "deepcad__0013_00132335",  # multi-op exact
        "fusion360__99059_8a1d187a_0000",  # exact but high chamfer (frame)
        "fusion360__24032_d6172503_0026",  # M2 fail (exact False, step ok)
        "deepcad__0029_00298546",  # MAX_LENGTH fail all arms
    ]
    out = []
    for i in ids:
        if i in by_id:
            out.append(by_id[i])
    return out


def render_grid(samples: list[dict], out_path: Path) -> None:
    arms = [("GT", None, "#8ecae6"), ("B0", "b0", "#219ebc"), ("B1", "b1", "#fb8500"), ("M2", "m2", "#2a9d8f")]
    n = len(samples)
    fig = plt.figure(figsize=(14, 3.2 * n), dpi=140)
    for ri, row in enumerate(samples):
        gt = _load_mesh(_gt_path(row))
        for ci, (name, arm, color) in enumerate(arms):
            ax = fig.add_subplot(n, 4, ri * 4 + ci + 1, projection="3d")
            if arm is None:
                mesh = gt
                title = f"{row['id']}\nGT"
            else:
                mesh = _load_mesh(DECODE / arm / row["id"] / "pred.stl")
                meta = json.loads((DECODE / arm / row["id"] / "row.json").read_text())
                ch = meta.get("geometry", {}).get("chamfer_norm")
                ch_s = f"ch={ch:.3f}" if ch is not None else "ch=—"
                title = (
                    f"{name} exact={meta.get('exact_match')} "
                    f"step={meta.get('step_ok')}\n"
                    f"opF1={meta.get('op_f1', 0):.2f} {ch_s}"
                )
            _plot_mesh(ax, mesh, color, title)
    fig.suptitle(
        "Curve100 overfit decode — GT vs B0 / B1 / M2\n"
        "(each mesh centered+unit-scaled for shape view)",
        fontsize=12,
        y=0.995,
    )
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[wrote] {out_path}")


def render_overlay(sample_id: str, out_path: Path) -> None:
    """GT (blue wire) + M2 pred (green) overlay, raw coordinates."""
    row = json.loads((DECODE / "m2" / sample_id / "row.json").read_text())
    gt = _load_mesh(_gt_path(row))
    fig = plt.figure(figsize=(12, 4), dpi=140)
    for i, (arm, color) in enumerate([("b0", "#219ebc"), ("b1", "#fb8500"), ("m2", "#2a9d8f")]):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        pred = _load_mesh(DECODE / arm / sample_id / "pred.stl")
        ax.set_title(f"{sample_id}\nGT + {arm.upper()} overlay (raw coords)", fontsize=8)
        ax.set_axis_off()
        if gt is not None:
            g = _normalize(gt)
            faces = g.faces
            if len(faces) > 4000:
                faces = faces[np.linspace(0, len(faces) - 1, 4000).astype(int)]
            ax.add_collection3d(
                Poly3DCollection(
                    g.vertices[faces], alpha=0.25, facecolor="#8ecae6", edgecolor="none"
                )
            )
        if pred is not None:
            p = _normalize(pred)
            faces = p.faces
            if len(faces) > 4000:
                faces = faces[np.linspace(0, len(faces) - 1, 4000).astype(int)]
            ax.add_collection3d(
                Poly3DCollection(
                    p.vertices[faces], alpha=0.55, facecolor=color, edgecolor="k", linewidths=0.02
                )
            )
        ax.set_xlim(-0.6, 0.6)
        ax.set_ylim(-0.6, 0.6)
        ax.set_zlim(-0.6, 0.6)
        ax.view_init(elev=22, azim=35)
        try:
            ax.set_box_aspect((1, 1, 1))
        except Exception:
            pass
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)
    print(f"[wrote] {out_path}")


def main() -> int:
    samples = _pick_samples()
    render_grid(samples, OUT / "grid_gt_b0_b1_m2.png")
    render_overlay("deepcad__0000_00002522", OUT / "overlay_good_deepcad.png")
    render_overlay("deepcad__0045_00454314", OUT / "overlay_best_chamfer.png")
    # one-pager summary metrics bar
    fig, ax = plt.subplots(figsize=(8, 4), dpi=140)
    arms = ["B0", "B1", "M2"]
    metrics = {
        "exact": [],
        "op F1": [],
        "STEP": [],
        "Chamfer×10": [],
    }
    for a in arms:
        r = json.loads((DECODE / a.lower() / "report.json").read_text())
        metrics["exact"].append(r["exact_match_rate"])
        metrics["op F1"].append(r["mean_op_f1"])
        metrics["STEP"].append(r["step_valid_rate"])
        metrics["Chamfer×10"].append((r["mean_chamfer_norm"] or 0) * 10)
    x = np.arange(len(arms))
    w = 0.2
    for i, (name, vals) in enumerate(metrics.items()):
        ax.bar(x + (i - 1.5) * w, vals, width=w, label=name)
    ax.set_xticks(x)
    ax.set_xticklabels(arms)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("rate / scaled Chamfer")
    ax.set_title("Curve100 overfit decode summary")
    ax.legend(fontsize=8)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT / "summary_bars.png", bbox_inches="tight")
    plt.close(fig)
    print(f"[wrote] {OUT / 'summary_bars.png'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
