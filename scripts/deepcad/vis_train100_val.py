#!/usr/bin/env python3
"""Visualize train100 val: GT | Baseline | Ours mesh panels."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = Path(__file__).resolve().parents[2]
DECODE = Path(os.environ.get("DECODE_ROOT", str(ROOT / "ours3/deepcad_train100_val_decode")))
TRAIN = ROOT / "cad_spatial_dataset/DeepCAD/train"
OUT = DECODE / "vis"


def _load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.exists():
        return None
    m = trimesh.load(str(path), force="mesh")
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)
    if m is None or len(getattr(m, "faces", [])) == 0:
        return None
    return m


def _draw(ax, mesh: trimesh.Trimesh | None, title: str, color: str, metrics: str = ""):
    ax.set_title(title + (f"\n{metrics}" if metrics else ""), fontsize=9)
    ax.set_axis_off()
    if mesh is None:
        ax.text(0.5, 0.5, 0.5, "N/A", ha="center", va="center", transform=ax.transAxes)
        return
    # center & scale
    v = mesh.vertices - mesh.vertices.mean(axis=0)
    scale = np.linalg.norm(v, axis=1).max()
    if scale > 0:
        v = v / scale
    faces = mesh.faces
    # subsample faces for speed
    if len(faces) > 8000:
        rng = np.random.default_rng(0)
        faces = faces[rng.choice(len(faces), 8000, replace=False)]
    tris = v[faces]
    coll = Poly3DCollection(tris, alpha=0.92, linewidths=0.05, edgecolors=(0.15, 0.15, 0.15, 0.25))
    coll.set_facecolor(color)
    ax.add_collection3d(coll)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_zlim(-1.1, 1.1)
    ax.view_init(elev=22, azim=35)
    try:
        ax.set_box_aspect((1, 1, 1))
    except Exception:
        pass


def render_row(sid: str, out_path: Path, metrics: dict | None = None):
    gt = _load_mesh(TRAIN / sid / "model.obj")
    b = _load_mesh(DECODE / "baseline" / sid / "pred.stl")
    o = _load_mesh(DECODE / "ours" / sid / "pred.stl")
    bm = metrics.get("baseline", {}) if metrics else {}
    om = metrics.get("ours", {}) if metrics else {}

    def mstr(d):
        parts = []
        if d.get("chamfer") is not None:
            parts.append(f"Ch={d['chamfer']:.3f}")
        if d.get("hausdorff95") is not None:
            parts.append(f"H95={d['hausdorff95']:.3f}")
        if d.get("op_recall") is not None:
            parts.append(f"op={d['op_recall']:.2f}")
        return "  ".join(parts)

    fig = plt.figure(figsize=(12, 4.2), facecolor="white")
    for i, (mesh, title, color, met) in enumerate(
        [
            (gt, "GT", "#7aa2c8", ""),
            (b, "Baseline", "#c47a6a", mstr(bm)),
            (o, "Ours (+edge)", "#6aab7a", mstr(om)),
        ]
    ):
        ax = fig.add_subplot(1, 3, i + 1, projection="3d")
        _draw(ax, mesh, title, color, met)
    fig.suptitle(sid, fontsize=11, y=0.98)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def render_grid(samples: list[dict], out_path: Path, title: str):
    n = len(samples)
    fig = plt.figure(figsize=(12, 3.6 * n), facecolor="white")
    for r, p in enumerate(samples):
        sid = p["sample_id"]
        gt = _load_mesh(TRAIN / sid / "model.obj")
        b = _load_mesh(DECODE / "baseline" / sid / "pred.stl")
        o = _load_mesh(DECODE / "ours" / sid / "pred.stl")
        bm, om = p["baseline"], p["ours"]
        for c, (mesh, name, color) in enumerate(
            [
                (gt, "GT", "#7aa2c8"),
                (b, f"Base Ch={bm.get('chamfer', float('nan')):.3f}", "#c47a6a"),
                (o, f"Ours Ch={om.get('chamfer', float('nan')):.3f}", "#6aab7a"),
            ]
        ):
            ax = fig.add_subplot(n, 3, r * 3 + c + 1, projection="3d")
            _draw(ax, mesh, f"{sid}\n{name}" if c == 0 else name, color)
    fig.suptitle(title, fontsize=13, y=0.995)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=120, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    global DECODE, OUT
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--decode-root",
        type=Path,
        default=Path(os.environ.get("DECODE_ROOT", str(ROOT / "ours3/deepcad_train100_val_decode"))),
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    DECODE = args.decode_root
    OUT = args.out or (DECODE / "vis")
    OUT.mkdir(parents=True, exist_ok=True)

    cmp_path = DECODE / "comparison.json"
    paired_path = DECODE / "paired_common_valid.json"
    if not cmp_path.exists():
        raise SystemExit(f"missing {cmp_path}")
    cmp = json.loads(cmp_path.read_text())

    # Prefer paired_common_valid if present; else all samples where both have STEP+chamfer
    if paired_path.exists():
        paired = json.loads(paired_path.read_text())
        samples = paired["per_sample"]
    else:
        samples = []
        for p in cmp["per_sample"]:
            b, o = p["baseline"], p["ours"]
            if b.get("step_ok") and o.get("step_ok") and b.get("chamfer") is not None and o.get("chamfer") is not None:
                samples.append(p)

    for p in samples:
        sid = p["sample_id"]
        render_row(sid, OUT / "per_sample" / f"{sid}.png", p)
        print("wrote", sid)

    if samples:
        render_grid(samples, OUT / "common_grid.png", f"COMMON_VALID (n={len(samples)}): GT | Baseline | Ours")

    wins = [p for p in samples if (p["ours"].get("chamfer") or 1e9) < (p["baseline"].get("chamfer") or 1e9) - 1e-6]
    loses = [p for p in samples if (p["ours"].get("chamfer") or 0) > (p["baseline"].get("chamfer") or 0) + 1e-6]
    if wins:
        render_grid(wins, OUT / "ours_better.png", "Ours better Chamfer (paired)")
    if loses:
        render_grid(loses, OUT / "ours_worse.png", "Ours worse Chamfer (paired)")

    ours_only = [
        p for p in cmp["per_sample"]
        if p["ours"].get("step_ok") and not p["baseline"].get("step_ok")
    ]
    oo = []
    for p in ours_only:
        oo.append({
            "sample_id": p["sample_id"],
            "baseline": {"chamfer": float("nan")},
            "ours": {"chamfer": p["ours"].get("chamfer") or float("nan")},
        })
    if oo:
        render_grid(oo, OUT / "ours_only_step.png", "Ours STEP-ok where Baseline failed")

    # Full gallery of all val samples that have any pred.stl
    all_rows = []
    for p in cmp["per_sample"]:
        all_rows.append({
            "sample_id": p["sample_id"],
            "baseline": {"chamfer": p["baseline"].get("chamfer") if p["baseline"].get("chamfer") is not None else float("nan")},
            "ours": {"chamfer": p["ours"].get("chamfer") if p["ours"].get("chamfer") is not None else float("nan")},
        })
    if all_rows:
        render_grid(all_rows, OUT / "all_val_grid.png", f"All val (n={len(all_rows)}): GT | Baseline | Ours")

    print(json.dumps({
        "out": str(OUT),
        "n_common": len(samples),
        "wins": len(wins),
        "loses": len(loses),
        "ours_only": len(oo),
        "n_all": len(all_rows),
    }, indent=2))


if __name__ == "__main__":
    main()
