#!/usr/bin/env python3
"""Turntable panorama of cad_spatial Dora training parts.

Reads existing sample packs only. Does not re-run Dora or touch frozen eval.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw, ImageFont

SCRIPTS = Path("/data/home/cuiyuehan/project/mesh2cad/scripts")
sys.path.insert(0, str(SCRIPTS))
from viz_cad_spatial_dora_train_v1 import (  # noqa: E402
    MAX_EDGES,
    MAX_FACES,
    MESH_COLOR,
    OUT,
    SAMPLES,
    font,
    load_sample,
    subsample,
)

ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
ELEV_DEG = 26.0
FRAME = 0.78
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))


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


def blank_ax(ax):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.96):
    blank_ax(ax)
    faces = faces[subsample(len(faces), MAX_FACES, 7)]
    tris = verts[faces]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    n = n / nn
    shade = 0.26 + 0.74 * np.clip(n @ WORLD_LIGHT, 0.0, 1.0)
    fc = np.clip(MESH_COLOR.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(eye)
    x = (tris - center) / scale
    cents = x.mean(axis=1)
    order = np.argsort(cents @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.10),
            linewidths=0.05,
        )
    )


def project_pts(pts, center, scale, eye):
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def draw_edges(ax, xyz0, xyz1, dih, center, scale, eye):
    n = len(xyz0)
    if n == 0:
        return
    idx = subsample(n, MAX_EDGES, 3)
    segs = np.stack(
        [
            project_pts(xyz0[idx], center, scale, eye),
            project_pts(xyz1[idx], center, scale, eye),
        ],
        axis=1,
    )
    t = np.clip((dih[idx] - 15.0) / 60.0, 0.0, 1.0)
    colors = plt.cm.plasma(t)
    ax.add_collection(LineCollection(segs, colors=colors, linewidths=0.85, alpha=0.95))


def fit_frame(verts: np.ndarray) -> tuple[np.ndarray, float]:
    center = verts.mean(axis=0)
    x = verts - center
    scale = float(np.abs(x).max()) or 1.0
    return center, scale


def render_orbit(rec: dict, dest: Path, with_edges: bool) -> Path:
    verts, faces = rec["verts"], rec["faces"]
    center, scale = fit_frame(verts)
    tag = f"{rec['source']}  {rec['sample_id']}"
    fig, axes = plt.subplots(1, len(ANGLES), figsize=(18.4, 2.55), dpi=130)
    for ax, az in zip(axes, ANGLES):
        eye = eye_from_azim(az)
        if with_edges:
            draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.22)
            draw_edges(ax, rec["xyz0"], rec["xyz1"], rec["dih"], center, scale, eye)
        else:
            draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.97)
        ax.set_title(f"{az}°", fontsize=8, pad=2)
    kind = "mesh + Dora edges" if with_edges else "mesh"
    fig.suptitle(f"{tag}  turntable  {kind}  elev={ELEV_DEG:.0f}°", fontsize=11, y=0.98)
    fig.subplots_adjust(left=0.01, right=0.995, top=0.78, bottom=0.02, wspace=0.04)
    name = "orbit_edges.png" if with_edges else "orbit_mesh.png"
    path = dest / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, facecolor="white")
    plt.close(fig)
    return path


def stack_gallery(paths: list[Path], labels: list[str], out: Path, title: str):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in imgs)
    h = max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    left = 220
    top = 48
    canvas = Image.new("RGB", (left + w, top + h * len(imgs)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((left + 8, 10), title, fill=(20, 20, 20), font=font(20))
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        draw.text((8, top + i * h + h // 2 - 8), lab, fill=(30, 30, 30), font=font(13))
        canvas.paste(im, (left, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    out_fig = OUT / "figures"
    rows_mesh = []
    rows_edge = []
    labels = []
    for source, sample_id in SAMPLES:
        print(f"orbit {source} {sample_id}", flush=True)
        rec = load_sample(source, sample_id)
        dest = OUT / "samples" / f"{source}__{sample_id}" / "panorama"
        rows_mesh.append(render_orbit(rec, dest, with_edges=False))
        rows_edge.append(render_orbit(rec, dest, with_edges=True))
        labels.append(f"{source[:3]} {sample_id}")
    stack_gallery(
        rows_mesh,
        labels,
        out_fig / "panorama_mesh_gallery.png",
        "cad_spatial Dora  |  8-view turntable  |  Z-up  |  mesh",
    )
    stack_gallery(
        rows_edge,
        labels,
        out_fig / "panorama_edges_gallery.png",
        "cad_spatial Dora  |  8-view turntable  |  Z-up  |  mesh + salient edges",
    )
    manifest = {
        "angles_deg": ANGLES,
        "elev_deg": ELEV_DEG,
        "samples": [f"{s}__{i}" for s, i in SAMPLES],
        "mesh_gallery": str(out_fig / "panorama_mesh_gallery.png"),
        "edges_gallery": str(out_fig / "panorama_edges_gallery.png"),
    }
    (OUT / "panorama_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
