#!/usr/bin/env python3
"""More complete Dora viz on current V3 training packs.

PCA 'full-part' camera + 8-view Z-up turntable. Reads existing
cad_spatial_dataset Dora artifacts only.
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
    CMAP,
    DATA,
    MAX_EDGES,
    MAX_FACES,
    MAX_POINTS,
    MESH_COLOR,
    SAMPLES as SEED_SAMPLES,
    V3_TRAIN,
    font,
    load_sample,
    sample_dir,
    subsample,
)

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/cad_spatial_dora_train_viz_v2"
ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
ELEV_DEG = 28.0
FRAME = 0.82
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))
N_DEEP = 24
N_FUS = 8


def eye_from_azim(azim_deg: float, elev_deg: float = ELEV_DEG) -> np.ndarray:
    az = np.deg2rad(azim_deg)
    el = np.deg2rad(elev_deg)
    return np.array(
        [np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), np.sin(el)],
        dtype=float,
    )


def pca_eye(verts: np.ndarray) -> np.ndarray:
    x = verts - verts.mean(axis=0)
    _, _, vt = np.linalg.svd(x, full_matrices=False)
    longest, mid, shortest = vt[0], vt[1], vt[2]
    if shortest[2] < 0:
        shortest = -shortest
    eye = 0.45 * longest + 0.70 * mid + 1.05 * shortest
    n = float(np.linalg.norm(eye)) or 1.0
    return eye / n


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


def project_pts(pts, center, scale, eye):
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def fit_frame(verts: np.ndarray):
    center = verts.mean(axis=0)
    scale = float(np.abs(verts - center).max()) or 1.0
    return center, scale * 1.05


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
    order = np.argsort(x.mean(axis=1) @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.10),
            linewidths=0.05,
        )
    )


def draw_edges(ax, xyz0, xyz1, dih, center, scale, eye, lw=0.85):
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
    ax.add_collection(LineCollection(segs, colors=plt.cm.plasma(t), linewidths=lw, alpha=0.95))


def pick_samples() -> list[tuple[str, str]]:
    rows = json.loads(V3_TRAIN.read_text())["records"]
    stats = []
    for r in rows:
        cid = r["cad_id"]
        src = "deepcad" if cid.startswith("deepcad__") else "fusion360"
        sid = cid.split("__", 1)[1]
        z = np.load(sample_dir(src, sid) / "dora" / "salient_edges.npz")
        feat = np.load(sample_dir(src, sid) / "features_canonical.npy")
        stats.append(
            {
                "source": src,
                "sample_id": sid,
                "n_edges": int(len(z["edge_xyz0"])),
                "frac": float((feat[:, -1] > 0.5).mean()),
            }
        )
    chosen: list[tuple[str, str]] = []
    seen = set()

    def add(src: str, sid: str) -> None:
        key = (src, sid)
        if key not in seen:
            chosen.append(key)
            seen.add(key)

    for src, sid in SEED_SAMPLES:
        add(src, sid)

    def fill(pool: list[dict], target: int) -> None:
        have = sum(1 for s, _ in chosen if s == pool[0]["source"]) if pool else 0
        need = max(0, target - have)
        ordered = sorted(pool, key=lambda s: s["n_edges"])
        if not ordered or need == 0:
            return
        idx = np.linspace(0, len(ordered) - 1, min(len(ordered), need * 3)).round().astype(int)
        for i in idx:
            if sum(1 for s, _ in chosen if s == pool[0]["source"]) >= target:
                return
            add(ordered[int(i)]["source"], ordered[int(i)]["sample_id"])
        for s in ordered:
            if sum(1 for a, _ in chosen if a == pool[0]["source"]) >= target:
                return
            add(s["source"], s["sample_id"])

    deep = [s for s in stats if s["source"] == "deepcad"]
    fus = [s for s in stats if s["source"] == "fusion360"]
    fill(fus, N_FUS)
    fill(deep, N_DEEP)
    return chosen


def render_hero(rec: dict, dest: Path) -> Path:
    verts, faces = rec["verts"], rec["faces"]
    center, scale = fit_frame(verts)
    eye = pca_eye(verts)
    tag = f"{rec['source']}  {rec['sample_id']}"
    fig, axes = plt.subplots(1, 4, figsize=(16.8, 4.35), dpi=130)
    draw_mesh(axes[0], verts, faces, center, scale, eye, alpha=0.97)
    axes[0].set_title("complete mesh (PCA view)", fontsize=10)

    draw_mesh(axes[1], verts, faces, center, scale, eye, alpha=0.20)
    draw_edges(axes[1], rec["xyz0"], rec["xyz1"], rec["dih"], center, scale, eye)
    axes[1].set_title(f"Dora SES  n={rec['n_salient_edges']}", fontsize=10)

    draw_mesh(axes[2], verts, faces, center, scale, eye, alpha=0.16)
    idx = subsample(len(rec["feat_xyz"]), MAX_POINTS, 11)
    q = project_pts(rec["feat_xyz"][idx], center, scale, eye)
    axes[2].scatter(
        q[:, 0], q[:, 1], s=2.2, c=rec["score"][idx], cmap=CMAP, vmin=0, vmax=1, linewidths=0, alpha=0.8
    )
    axes[2].set_title(f"8192 pts  edge_score  >0.5={rec['frac_gt_0_5']:.1%}", fontsize=9)

    draw_mesh(axes[3], verts, faces, center, scale, eye, alpha=0.18)
    show = rec["edge_pts"][subsample(len(rec["edge_pts"]), MAX_POINTS, 13)]
    qe = project_pts(show, center, scale, eye)
    axes[3].scatter(qe[:, 0], qe[:, 1], s=1.8, c="#dc2626", alpha=0.55, linewidths=0)
    axes[3].set_title(f"Dora edge_points n={rec['n_edge_points']}", fontsize=10)

    fig.suptitle(f"{tag}  training Dora  |  full part  |  PCA camera", fontsize=11, y=1.02)
    fig.tight_layout()
    path = dest / "hero_board.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def render_orbit(rec: dict, dest: Path, with_edges: bool) -> Path:
    verts, faces = rec["verts"], rec["faces"]
    center, scale = fit_frame(verts)
    fig, axes = plt.subplots(1, len(ANGLES), figsize=(18.6, 2.6), dpi=120)
    for ax, az in zip(axes, ANGLES):
        eye = eye_from_azim(az)
        if with_edges:
            draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.20)
            draw_edges(ax, rec["xyz0"], rec["xyz1"], rec["dih"], center, scale, eye)
        else:
            draw_mesh(ax, verts, faces, center, scale, eye, alpha=0.97)
        ax.set_title(f"{az}°", fontsize=8, pad=2)
    kind = "mesh + Dora SES" if with_edges else "complete mesh"
    fig.suptitle(
        f"{rec['source']}  {rec['sample_id']}  turntable  {kind}  edges={rec['n_salient_edges']}",
        fontsize=11,
        y=0.98,
    )
    fig.subplots_adjust(left=0.01, right=0.995, top=0.78, bottom=0.02, wspace=0.03)
    name = "orbit_dora.png" if with_edges else "orbit_mesh.png"
    path = dest / name
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, facecolor="white")
    plt.close(fig)
    return path


def stack_gallery(paths: list[Path], out: Path, title: str, left_labels: list[str] | None = None):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in imgs)
    h = max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    left = 210 if left_labels else 8
    top = 48
    canvas = Image.new("RGB", (left + w, top + h * len(imgs)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((left + 8, 10), title, fill=(20, 20, 20), font=font(18))
    for i, im in enumerate(imgs):
        if left_labels:
            draw.text((8, top + i * h + h // 2 - 8), left_labels[i], fill=(30, 30, 30), font=font(12))
        canvas.paste(im, (left, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "samples").mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    keys = pick_samples()
    print(f"n_samples={len(keys)}", flush=True)
    heroes, orbits_m, orbits_d, rows, labels = [], [], [], [], []
    for source, sample_id in keys:
        print(f"{source} {sample_id}", flush=True)
        rec = load_sample(source, sample_id)
        dest = OUT / "samples" / f"{source}__{sample_id}"
        heroes.append(render_hero(rec, dest))
        orbits_m.append(render_orbit(rec, dest, with_edges=False))
        orbits_d.append(render_orbit(rec, dest, with_edges=True))
        slim = {
            k: rec[k]
            for k in rec
            if k not in {"verts", "faces", "feat_xyz", "score", "xyz0", "xyz1", "dih", "edge_pts"}
        }
        rows.append(slim)
        labels.append(f"{source[:3]} {sample_id}")
        (dest / "stats.json").write_text(json.dumps(slim, indent=2) + "\n")

    n = len(heroes)
    mid = (n + 1) // 2
    stack_gallery(heroes, OUT / "figures" / "hero_gallery.png", "V3-train Dora  |  PCA full-part  |  mesh | SES | edge_score | edge_points")
    stack_gallery(heroes[:mid], OUT / "figures" / "hero_gallery_1.png", "V3-train Dora  part 1  |  complete parts, PCA camera")
    stack_gallery(heroes[mid:], OUT / "figures" / "hero_gallery_2.png", "V3-train Dora  part 2  |  complete parts, PCA camera")
    stack_gallery(orbits_m[:mid], OUT / "figures" / "orbit_mesh_1.png", "complete mesh turntable  (Z-up, 8 views)")
    stack_gallery(orbits_m[mid:], OUT / "figures" / "orbit_mesh_2.png", "complete mesh turntable  (Z-up, 8 views)")
    stack_gallery(orbits_d[:mid], OUT / "figures" / "orbit_dora_1.png", "Dora SES turntable on complete parts")
    stack_gallery(orbits_d[mid:], OUT / "figures" / "orbit_dora_2.png", "Dora SES turntable on complete parts")
    stack_gallery(
        orbits_d,
        OUT / "figures" / "orbit_dora_all.png",
        "V3-train Dora SES  |  8-view turntable  |  complete parts",
        left_labels=labels,
    )
    manifest = {
        "output": str(OUT),
        "n": n,
        "note": "Current V3 training Dora packs. PCA camera shows full part; turntable is Z-up 8-view.",
        "samples": rows,
        "hero_gallery": str(OUT / "figures" / "hero_gallery.png"),
        "orbit_dora": str(OUT / "figures" / "orbit_dora_all.png"),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"n": n, "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
