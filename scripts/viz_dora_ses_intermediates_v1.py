#!/usr/bin/env python3
"""Visualize Dora SES intermediate products on the frozen X-Part canary set.

Reads existing SES artifacts only. Does not re-run Dora, X-Part, or Route B.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
XPART = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
DORA = ROOT / "ours3/dora_ses_xpart45_v1"
OUT = DORA / "visualization_v1"
PARTS = ["PART_003", "PART_012", "PART_019", "PART_041", "PART_042"]
THRESHOLDS = [15, 25, 35, 45]
MESH_COLOR = np.array([0.62, 0.66, 0.70])
LIGHT = np.array([0.42, -0.58, 0.70], dtype=float)
LIGHT = LIGHT / float(np.linalg.norm(LIGHT))
EYE = np.array([1.15, -1.35, 0.95], dtype=float)
FRAME = 0.72
MAX_FACES = 12000
MAX_EDGES = 9000
MAX_POINTS = 4500


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def source_path(part: str) -> Path:
    idx = int(part.split("_")[1])
    return XPART / part / f"complete_part_{idx:03d}.obj"


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right = right / float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def normalize_verts(verts: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    c = verts.mean(axis=0)
    x = verts - c
    scale = float(np.abs(x).max()) or 1.0
    return x / scale, c, scale


def project_pts(pts: np.ndarray, center: np.ndarray, scale: float) -> np.ndarray:
    right, up, _ = camera_basis(EYE)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def subsample(n: int, cap: int, seed: int) -> np.ndarray:
    if n <= cap:
        return np.arange(n)
    return np.random.default_rng(seed).choice(n, cap, replace=False)


def blank_ax(ax):
    ax.set_facecolor("white")
    ax.set_xlim(-FRAME, FRAME)
    ax.set_ylim(-FRAME, FRAME)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)


def draw_mesh(ax, verts: np.ndarray, faces: np.ndarray, center: np.ndarray, scale: float, alpha: float = 0.92):
    blank_ax(ax)
    faces = faces[subsample(len(faces), MAX_FACES, 7)]
    tris = verts[faces]
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    nn = np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    n = n / nn
    shade = 0.28 + 0.72 * np.clip(n @ LIGHT, 0.0, 1.0)
    fc = np.clip(MESH_COLOR.reshape(1, 3) * shade.reshape(-1, 1), 0, 1)
    right, up, fwd = camera_basis(EYE)
    x = (tris - center) / scale
    cents = x.mean(axis=1)
    order = np.argsort(cents @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.12),
            linewidths=0.06,
        )
    )


def draw_edges(ax, xyz0: np.ndarray, xyz1: np.ndarray, dih: np.ndarray, center: np.ndarray, scale: float):
    n = len(xyz0)
    idx = subsample(n, MAX_EDGES, 3)
    segs = np.stack(
        [project_pts(xyz0[idx], center, scale), project_pts(xyz1[idx], center, scale)],
        axis=1,
    )
    t = np.clip((dih[idx] - 15.0) / 60.0, 0.0, 1.0)
    colors = plt.cm.plasma(t)
    ax.add_collection(LineCollection(segs, colors=colors, linewidths=0.55, alpha=0.88))


def save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(fig)


def load_edges(part: str, th: int):
    path = DORA / f"threshold_{th}" / part / "salient_edges_source_space.npz"
    if not path.is_file():
        return None
    z = np.load(path)
    return {
        "n": int(len(z["edge_xyz0"])),
        "xyz0": np.asarray(z["edge_xyz0"], dtype=float),
        "xyz1": np.asarray(z["edge_xyz1"], dtype=float),
        "dih": np.asarray(z["dihedral_deg"], dtype=float),
        "p95": float(np.percentile(z["dihedral_deg"], 95)) if len(z["dihedral_deg"]) else 0.0,
    }


def load_sharp_points(part: str) -> np.ndarray | None:
    path = DORA / "threshold_15" / part / "dora_samples_source_space.npz"
    if not path.is_file():
        return None
    z = np.load(path, allow_pickle=True)
    pts = np.asarray(z["fps_sharp_surface"], dtype=float)
    if pts.ndim == 3:
        pts = pts.reshape(pts.shape[0], -1)[:, :3]
    return pts[:, :3]


def font(size: int):
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def stitch_row(paths: list[Path], labels: list[str], out: Path, title: str):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in imgs)
    h = max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    header = 46
    footer = 28
    canvas = Image.new("RGB", (w * len(imgs), h + header + footer), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 10), title, fill=(20, 20, 20), font=font(22))
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        canvas.paste(im, (i * w, header))
        draw.text((i * w + 12, header + h + 4), lab, fill=(40, 40, 40), font=font(16))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def render_part(part: str) -> dict:
    dest = OUT / "parts" / part
    dest.mkdir(parents=True, exist_ok=True)
    mesh = load_mesh(source_path(part))
    verts = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    _, center, scale = normalize_verts(verts)
    rec = {"part": part, "n_verts": int(len(verts)), "n_faces": int(len(faces)), "thresholds": {}}

    fig, ax = plt.subplots(figsize=(5.4, 5.0), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.96)
    ax.set_title(f"{part}  X-Part watertight", fontsize=10)
    save_fig(fig, dest / "00_source_mesh.png")

    pts = load_sharp_points(part)
    fig, ax = plt.subplots(figsize=(5.4, 5.0), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.18)
    if pts is not None and len(pts):
        show = pts[subsample(len(pts), MAX_POINTS, 11)]
        q = project_pts(show, center, scale)
        ax.scatter(q[:, 0], q[:, 1], s=1.6, c="#dc2626", alpha=0.55, linewidths=0)
        rec["n_sharp_samples"] = int(len(pts))
        ax.set_title(f"{part}  Dora fps_sharp_surface n={len(pts)}", fontsize=10)
    else:
        rec["n_sharp_samples"] = 0
        ax.set_title(f"{part}  Dora samples missing", fontsize=10)
    save_fig(fig, dest / "01_sharp_samples.png")

    edge_paths = []
    edge_labels = []
    for th in THRESHOLDS:
        ed = load_edges(part, th)
        fig, ax = plt.subplots(figsize=(5.4, 5.0), dpi=130)
        draw_mesh(ax, verts, faces, center, scale, alpha=0.22)
        if ed is not None:
            draw_edges(ax, ed["xyz0"], ed["xyz1"], ed["dih"], center, scale)
            rec["thresholds"][str(th)] = {"n_edges": ed["n"], "dihedral_p95": ed["p95"]}
            ax.set_title(f"{part}  SES threshold={th}°  edges={ed['n']}", fontsize=10)
        else:
            rec["thresholds"][str(th)] = {"n_edges": 0, "dihedral_p95": None}
            ax.set_title(f"{part}  SES threshold={th}°  missing", fontsize=10)
        p = dest / f"th{th:02d}_salient_edges.png"
        save_fig(fig, p)
        edge_paths.append(p)
        n = rec["thresholds"][str(th)]["n_edges"]
        edge_labels.append(f"th={th}°  n={n}")

    stitch_row(
        [dest / "00_source_mesh.png", dest / "01_sharp_samples.png"] + edge_paths,
        ["source mesh", f"sharp samples n={rec['n_sharp_samples']}"] + edge_labels,
        dest / "board.png",
        f"{part}  Dora SES intermediates  (edge color = dihedral, plasma)",
    )
    return rec


def stitch_grid(cells: list[list[Path]], row_labels: list[str], col_labels: list[str], out: Path, title: str):
    imgs = [[Image.open(p).convert("RGB") for p in row] for row in cells]
    w = max(im.width for row in imgs for im in row)
    h = max(im.height for row in imgs for im in row)
    left = 90
    top = 52
    canvas = Image.new("RGB", (left + w * len(col_labels), top + h * len(row_labels)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((left + 8, 10), title, fill=(20, 20, 20), font=font(22))
    for j, lab in enumerate(col_labels):
        draw.text((left + j * w + 10, 30), lab, fill=(50, 50, 50), font=font(14))
    for i, row in enumerate(imgs):
        draw.text((8, top + i * h + h // 2 - 8), row_labels[i], fill=(30, 30, 30), font=font(14))
        for j, im in enumerate(row):
            if im.size != (w, h):
                im = im.resize((w, h), Image.Resampling.LANCZOS)
            canvas.paste(im, (left + j * w, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "parts").mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    rows = []
    for part in PARTS:
        print(part, flush=True)
        rows.append(render_part(part))

    stitch_row(
        [OUT / "parts" / p / "board.png" for p in PARTS],
        PARTS,
        OUT / "figures" / "all_part_boards.png",
        "Dora SES canary parts  |  mesh → sharp samples → threshold 15/25/35/45",
    )
    stitch_grid(
        [[OUT / "parts" / p / f"th{th:02d}_salient_edges.png" for th in THRESHOLDS] for p in PARTS],
        PARTS,
        [f"th={th}°" for th in THRESHOLDS],
        OUT / "figures" / "threshold_grid.png",
        "Dora SES salient edges by dihedral threshold  (source-space, color=dihedral)",
    )
    stitch_grid(
        [[OUT / "parts" / p / "00_source_mesh.png", OUT / "parts" / p / "01_sharp_samples.png"] for p in PARTS],
        PARTS,
        ["X-Part mesh", "Dora fps_sharp_surface"],
        OUT / "figures" / "mesh_vs_samples.png",
        "Dora intermediate: watertight mesh vs sharp-surface FPS samples",
    )
    (OUT / "manifest.json").write_text(json.dumps({"parts": rows, "output": str(OUT), "dora_root": str(DORA)}, indent=2) + "\n")
    print(json.dumps({"n_parts": len(rows), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
