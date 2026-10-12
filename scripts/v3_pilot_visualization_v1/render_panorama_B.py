#!/usr/bin/env python3
"""Turntable panorama for frozen V3 gallery B (B0 Chamfer better).

Reads existing visualization meshes only. Does not retrain, redecode,
or modify original jsonl / SUMMARY / gallery PNGs.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_v3_pilot_pano")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "pilot_eval_150_frozen_v1"
)
VIZ = EVAL / "visualization_v1"
OUT = VIZ / "panorama_B_v1"
SELECTED = VIZ / "selected_cases.json"
MESH_ROOT = VIZ / "meshes"

ARMS = ("gt", "b0", "b1", "m2")
ARM_LABEL = {"gt": "GT", "b0": "B0", "b1": "B1", "m2": "M2"}
ARM_COLOR = {
    "gt": np.array([0.62, 0.66, 0.70]),
    "b0": np.array([0.22, 0.45, 0.70]),
    "b1": np.array([0.90, 0.49, 0.13]),
    "m2": np.array([0.22, 0.62, 0.33]),
}
ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
ELEV_DEG = 26.0
FRAME = 0.78
MAX_FACES = 12000
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))


def load_mesh(path: Path):
    import trimesh

    if not path.is_file() or path.stat().st_size <= 0:
        return None
    m = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(m, trimesh.Scene):
        geoms = [g for g in m.geometry.values() if isinstance(g, trimesh.Trimesh)]
        if not geoms:
            return None
        m = trimesh.util.concatenate(geoms)
    if not isinstance(m, trimesh.Trimesh) or len(m.faces) == 0:
        return None
    return m


def normalize_independent(mesh):
    m = mesh.copy()
    c = (m.bounds[0] + m.bounds[1]) * 0.5
    m.apply_translation(-c)
    extent = float(np.max(m.bounds[1] - m.bounds[0]))
    if extent > 1e-12:
        m.apply_scale(1.0 / extent)
    return m


def eye_from_azim(azim_deg: float, elev_deg: float = ELEV_DEG) -> np.ndarray:
    az = np.deg2rad(azim_deg)
    el = np.deg2rad(elev_deg)
    return np.array(
        [np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), np.sin(el)],
        dtype=float,
    )


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right = right / float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def subsample_faces(faces: np.ndarray, n: int = MAX_FACES) -> np.ndarray:
    if len(faces) <= n:
        return faces
    return faces[np.random.default_rng(7).choice(len(faces), n, replace=False)]


def blank_ax(ax):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_mesh(ax, mesh, color: np.ndarray, eye: np.ndarray, alpha: float = 0.96):
    blank_ax(ax)
    if mesh is None:
        ax.text(0.0, 0.0, "STEP_FAIL", ha="center", va="center", fontsize=10, color="#b00020")
        return
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = subsample_faces(np.asarray(mesh.faces, dtype=int))
    tris = verts[faces]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    n = n / nn
    shade = 0.26 + 0.74 * np.clip(n @ WORLD_LIGHT, 0.0, 1.0)
    fc = np.clip(color.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(eye)
    cents = tris.mean(axis=1)
    order = np.argsort(cents @ fwd)
    p2 = np.stack([tris @ right, tris @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.12),
            linewidths=0.05,
        )
    )


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fmt(v, nd=3):
    if v is None:
        return "—"
    return f"{float(v):.{nd}f}"


def load_case_meshes(cad_id: str) -> dict:
    d = MESH_ROOT / cad_id
    meshes = {"gt": load_mesh(d / "gt.stl")}
    for k in ("b0", "b1", "m2"):
        meshes[k] = load_mesh(d / k / "pred.stl")
    return {k: (normalize_independent(m) if m is not None else None) for k, m in meshes.items()}


def render_case(case: dict, dest: Path) -> Path:
    meshes = load_case_meshes(case["cad_id"])
    fig, axes = plt.subplots(
        len(ARMS),
        len(ANGLES),
        figsize=(18.6, 8.6),
        dpi=120,
    )
    for r, arm in enumerate(ARMS):
        extra = ""
        if arm != "gt":
            a = case["arms"][arm]
            extra = f"  F1 {fmt(a['op_f1'])}  Ch {fmt(a['chamfer_norm'])}"
        for c, az in enumerate(ANGLES):
            ax = axes[r, c]
            draw_mesh(ax, meshes[arm], ARM_COLOR[arm], eye_from_azim(az))
            if r == 0:
                ax.set_title(f"{az}°", fontsize=8, pad=2)
            if c == 0:
                ax.set_ylabel(f"{ARM_LABEL[arm]}{extra}", fontsize=8)
    fig.suptitle(
        f"{case['cad_id']}  [{case['category']}]  GT ops: {case['gt_ops']}  "
        f"turntable elev={ELEV_DEG:.0f}°",
        fontsize=12,
        y=0.995,
    )
    fig.subplots_adjust(left=0.07, right=0.995, top=0.90, bottom=0.02, wspace=0.03, hspace=0.06)
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / "orbit_gt_b0_b1_m2.png"
    fig.savefig(path, facecolor="white")
    plt.close(fig)
    return path


def stack_gallery(paths: list[Path], labels: list[str], out: Path, title: str):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in imgs)
    h = max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    left = 8
    top = 48
    canvas = Image.new("RGB", (left + w, top + h * len(imgs)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 10), title, fill=(20, 20, 20), font=font(20))
    y = top
    for im in imgs:
        canvas.paste(im, (left, y))
        y += h
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    selected = json.loads(SELECTED.read_text())
    cases = selected["categories"]["B_b0_best"] + selected["extended"]["B_b0_best_more"]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "samples").mkdir(exist_ok=True)
    paths = []
    labels = []
    for case in cases:
        print(case["cad_id"], flush=True)
        dest = OUT / "samples" / case["cad_id"]
        paths.append(render_case(case, dest))
        labels.append(case["cad_id"])
    stack_gallery(
        paths,
        labels,
        OUT / "gallery_B_panorama.png",
        "V3 frozen  |  gallery B (B0 Chamfer better)  |  8-view turntable  |  GT gray / B0 blue / B1 orange / M2 green",
    )
    manifest = {
        "source_gallery": "figures/gallery_B_b0_best.png",
        "n": len(cases),
        "cad_ids": [c["cad_id"] for c in cases],
        "angles_deg": ANGLES,
        "elev_deg": ELEV_DEG,
        "meshes": "existing visualization_v1/meshes/*.stl (no redecode)",
        "original_results_modified": False,
        "gallery": str(OUT / "gallery_B_panorama.png"),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
