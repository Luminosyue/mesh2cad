#!/usr/bin/env python3
"""Visualize Dora-sampled training packs in cad_spatial_dataset.

Reads existing DeepCAD / Fusion360 train artifacts only.
Does not re-run Dora, rebuild samples, or touch frozen Llama/Qwen eval.
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
from matplotlib.colors import Normalize
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
DATA = ROOT / "cad_spatial_dataset"
OUT = ROOT / "ours3/cad_spatial_dora_train_viz_v1"
V3_TRAIN = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json"
)

# Stratified V3-train IDs: simple / typical / dense / high-score / low-score / Fusion360.
SAMPLES = [
    ("deepcad", "0000_00001503"),
    ("deepcad", "0001_00017084"),
    ("deepcad", "0002_00022191"),
    ("deepcad", "0002_00028955"),
    ("deepcad", "0003_00032761"),
    ("deepcad", "0065_00652765"),
    ("deepcad", "0068_00680688"),
    ("deepcad", "0069_00691329"),
    ("fusion360", "109232_04340d62_0014"),
    ("fusion360", "111501_1e74ed05_0000"),
    ("fusion360", "143244_f1429885_0002"),
    ("fusion360", "41501_b627682a_0026"),
]

MESH_COLOR = np.array([0.62, 0.66, 0.70])
LIGHT = np.array([0.42, -0.58, 0.70], dtype=float)
LIGHT = LIGHT / float(np.linalg.norm(LIGHT))
EYE = np.array([1.15, -1.35, 0.95], dtype=float)
FRAME = 0.72
MAX_FACES = 12000
MAX_EDGES = 9000
MAX_POINTS = 4500
CMAP = plt.cm.turbo


def sample_dir(source: str, sample_id: str) -> Path:
    folder = "DeepCAD" if source == "deepcad" else "Fusion360"
    return DATA / folder / "train" / sample_id


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


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
    if n == 0:
        return
    idx = subsample(n, MAX_EDGES, 3)
    segs = np.stack(
        [project_pts(xyz0[idx], center, scale), project_pts(xyz1[idx], center, scale)],
        axis=1,
    )
    t = np.clip((dih[idx] - 15.0) / 60.0, 0.0, 1.0)
    colors = plt.cm.plasma(t)
    ax.add_collection(LineCollection(segs, colors=colors, linewidths=0.7, alpha=0.92))


def save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white", pad_inches=0.08)
    plt.close(fig)


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
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
    draw.text((16, 10), title, fill=(20, 20, 20), font=font(20))
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        canvas.paste(im, (i * w, header))
        draw.text((i * w + 12, header + h + 4), lab, fill=(40, 40, 40), font=font(15))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def stitch_grid(cells: list[list[Path]], row_labels: list[str], col_labels: list[str], out: Path, title: str):
    imgs = [[Image.open(p).convert("RGB") for p in row] for row in cells]
    w = max(im.width for row in imgs for im in row)
    h = max(im.height for row in imgs for im in row)
    left = 210
    top = 56
    canvas = Image.new("RGB", (left + w * len(col_labels), top + h * len(row_labels)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((left + 8, 8), title, fill=(20, 20, 20), font=font(22))
    for j, lab in enumerate(col_labels):
        draw.text((left + j * w + 10, 32), lab, fill=(50, 50, 50), font=font(14))
    for i, row in enumerate(imgs):
        draw.text((8, top + i * h + h // 2 - 8), row_labels[i], fill=(30, 30, 30), font=font(13))
        for j, im in enumerate(row):
            if im.size != (w, h):
                im = im.resize((w, h), Image.Resampling.LANCZOS)
            canvas.paste(im, (left + j * w, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def apply_canonical(pts: np.ndarray, scale: float, translation: np.ndarray) -> np.ndarray:
    return scale * np.asarray(pts, dtype=float) + translation


def load_sample(source: str, sample_id: str) -> dict:
    d = sample_dir(source, sample_id)
    tf = json.loads((d / "coordinate_transform.json").read_text())
    s = float(tf["scale"])
    t = np.asarray(tf["translation"], dtype=float)
    mesh = load_mesh(d / "model.obj")
    verts = apply_canonical(np.asarray(mesh.vertices, dtype=float), s, t)
    faces = np.asarray(mesh.faces, dtype=int)
    feat = np.load(d / "features_canonical.npy").astype(float)
    z = np.load(d / "dora" / "salient_edges.npz")
    edge_pts = apply_canonical(np.load(d / "dora" / "edge_points.npy"), s, t)
    xyz0 = apply_canonical(z["edge_xyz0"], s, t)
    xyz1 = apply_canonical(z["edge_xyz1"], s, t)
    dih = np.asarray(z["dihedral_deg"], dtype=float)
    score = feat[:, 6]
    return {
        "source": source,
        "sample_id": sample_id,
        "dir": str(d),
        "verts": verts,
        "faces": faces,
        "feat_xyz": feat[:, :3],
        "score": score,
        "xyz0": xyz0,
        "xyz1": xyz1,
        "dih": dih,
        "edge_pts": edge_pts,
        "n_faces": int(len(faces)),
        "n_verts": int(len(verts)),
        "n_points": int(len(feat)),
        "n_salient_edges": int(len(xyz0)),
        "n_edge_points": int(len(edge_pts)),
        "score_min": float(score.min()),
        "score_med": float(np.median(score)),
        "score_max": float(score.max()),
        "frac_gt_0_5": float((score > 0.5).mean()),
        "dihedral_p50": float(np.median(dih)) if len(dih) else None,
        "dihedral_p95": float(np.percentile(dih, 95)) if len(dih) else None,
        "canonical_scale": s,
    }


def render_sample(rec: dict) -> dict:
    source = rec["source"]
    sample_id = rec["sample_id"]
    dest = OUT / "samples" / f"{source}__{sample_id}"
    dest.mkdir(parents=True, exist_ok=True)
    verts, faces = rec["verts"], rec["faces"]
    _, center, scale = normalize_verts(verts)
    tag = f"{source}  {sample_id}"

    fig, ax = plt.subplots(figsize=(5.0, 4.6), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.96)
    ax.set_title(f"{tag}  mesh", fontsize=10)
    save_fig(fig, dest / "00_mesh.png")

    fig, ax = plt.subplots(figsize=(5.0, 4.6), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.16)
    idx = subsample(len(rec["feat_xyz"]), MAX_POINTS, 11)
    q = project_pts(rec["feat_xyz"][idx], center, scale)
    sc = rec["score"][idx]
    ax.scatter(q[:, 0], q[:, 1], s=2.4, c=sc, cmap=CMAP, vmin=0.0, vmax=1.0, alpha=0.78, linewidths=0)
    ax.set_title(f"{tag}  8192 pts  edge_score  frac>0.5={rec['frac_gt_0_5']:.3f}", fontsize=9)
    save_fig(fig, dest / "01_edge_score.png")

    fig, ax = plt.subplots(figsize=(5.0, 4.6), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.20)
    draw_edges(ax, rec["xyz0"], rec["xyz1"], rec["dih"], center, scale)
    ax.set_title(f"{tag}  Dora salient edges n={rec['n_salient_edges']}", fontsize=10)
    save_fig(fig, dest / "02_salient_edges.png")

    fig, ax = plt.subplots(figsize=(5.0, 4.6), dpi=130)
    draw_mesh(ax, verts, faces, center, scale, alpha=0.18)
    show = rec["edge_pts"][subsample(len(rec["edge_pts"]), MAX_POINTS, 13)]
    qe = project_pts(show, center, scale)
    ax.scatter(qe[:, 0], qe[:, 1], s=1.8, c="#dc2626", alpha=0.55, linewidths=0)
    ax.set_title(f"{tag}  Dora edge_points n={rec['n_edge_points']}", fontsize=10)
    save_fig(fig, dest / "03_edge_points.png")

    stitch_row(
        [
            dest / "00_mesh.png",
            dest / "01_edge_score.png",
            dest / "02_salient_edges.png",
            dest / "03_edge_points.png",
        ],
        [
            "canonical mesh",
            f"edge_score  >0.5={rec['frac_gt_0_5']:.1%}",
            f"salient edges n={rec['n_salient_edges']}",
            f"edge_points n={rec['n_edge_points']}",
        ],
        dest / "board.png",
        f"{tag}  cad_spatial Dora pack  (canonical frame, turbo=edge_score)",
    )
    slim = {k: rec[k] for k in rec if k not in {"verts", "faces", "feat_xyz", "score", "xyz0", "xyz1", "dih", "edge_pts"}}
    (dest / "stats.json").write_text(json.dumps(slim, indent=2) + "\n")
    return slim


def render_colorbar(path: Path):
    fig, ax = plt.subplots(figsize=(5.2, 0.55), dpi=140)
    fig.subplots_adjust(bottom=0.55, top=0.85, left=0.08, right=0.98)
    cb = plt.colorbar(
        plt.cm.ScalarMappable(norm=Normalize(0, 1), cmap=CMAP),
        cax=ax,
        orientation="horizontal",
    )
    cb.set_label("Dora edge_score  (0=surface, 1=near sharp edge)", fontsize=9)
    fig.savefig(path, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def pool_stats() -> dict:
    rows = json.loads(V3_TRAIN.read_text())["records"]
    n_edges = []
    n_epts = []
    fracs = []
    by_src = {"deepcad": 0, "fusion360": 0}
    missing = 0
    for r in rows:
        cid = r["cad_id"]
        src = "deepcad" if cid.startswith("deepcad__") else "fusion360"
        sid = cid.split("__", 1)[1]
        d = sample_dir(src, sid)
        feat_p = d / "features_canonical.npy"
        z_p = d / "dora" / "salient_edges.npz"
        ep_p = d / "dora" / "edge_points.npy"
        if not (feat_p.exists() and z_p.exists() and ep_p.exists()):
            missing += 1
            continue
        by_src[src] += 1
        feat = np.load(feat_p)
        n_edges.append(int(len(np.load(z_p)["edge_xyz0"])))
        n_epts.append(int(np.load(ep_p).shape[0]))
        fracs.append(float((feat[:, -1] > 0.5).mean()))
    arr_e = np.asarray(n_edges)
    arr_p = np.asarray(n_epts)
    arr_f = np.asarray(fracs)

    fig, axes = plt.subplots(1, 3, figsize=(11.4, 3.2), dpi=130)
    axes[0].hist(arr_e, bins=40, color="#2563eb", alpha=0.85)
    axes[0].set_title("V3-train 800  salient-edge count")
    axes[0].set_xlabel("n Dora salient edges")
    axes[1].hist(np.log10(np.clip(arr_p, 1, None)), bins=40, color="#dc2626", alpha=0.85)
    axes[1].set_title("V3-train 800  log10(edge_points)")
    axes[1].set_xlabel("log10 n")
    axes[2].hist(arr_f, bins=40, color="#ca8a04", alpha=0.85)
    axes[2].set_title("V3-train 800  frac(edge_score>0.5)")
    axes[2].set_xlabel("fraction of 8192 pts")
    for ax in axes:
        ax.set_ylabel("samples")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    fig.tight_layout()
    save_fig(fig, OUT / "figures" / "v3_train_dora_histograms.png")

    return {
        "v3_train_n": len(rows),
        "with_dora_pack": int(len(arr_e)),
        "missing": missing,
        "by_source": by_src,
        "n_salient_edges": {
            "p10": float(np.percentile(arr_e, 10)),
            "p50": float(np.percentile(arr_e, 50)),
            "p90": float(np.percentile(arr_e, 90)),
            "max": int(arr_e.max()),
        },
        "n_edge_points": {
            "p10": float(np.percentile(arr_p, 10)),
            "p50": float(np.percentile(arr_p, 50)),
            "p90": float(np.percentile(arr_p, 90)),
            "max": int(arr_p.max()),
        },
        "frac_edge_score_gt_0_5": {
            "p10": float(np.percentile(arr_f, 10)),
            "p50": float(np.percentile(arr_f, 50)),
            "p90": float(np.percentile(arr_f, 90)),
            "mean": float(arr_f.mean()),
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "samples").mkdir(exist_ok=True)
    (OUT / "figures").mkdir(exist_ok=True)
    render_colorbar(OUT / "figures" / "edge_score_colorbar.png")

    rows = []
    for source, sample_id in SAMPLES:
        print(f"{source} {sample_id}", flush=True)
        rec = load_sample(source, sample_id)
        rows.append(render_sample(rec))

    keys = [f"{s}__{i}" for s, i in SAMPLES]
    stitch_grid(
        [
            [
                OUT / "samples" / k / "00_mesh.png",
                OUT / "samples" / k / "01_edge_score.png",
                OUT / "samples" / k / "02_salient_edges.png",
                OUT / "samples" / k / "03_edge_points.png",
            ]
            for k in keys
        ],
        [f"{s[:3]} {i}" for s, i in SAMPLES],
        ["mesh", "8192 pts × edge_score", "Dora salient edges", "Dora edge_points"],
        OUT / "figures" / "overview_grid.png",
        "cad_spatial_dataset  Dora training pack  |  canonical frame  |  V3-train subset",
    )
    stitch_grid(
        [[OUT / "samples" / k / "01_edge_score.png"] for k in keys],
        [f"{s[:3]} {i}" for s, i in SAMPLES],
        ["edge_score on 8192 surface samples"],
        OUT / "figures" / "edge_score_gallery.png",
        "Dora edge_score on cad_spatial 8192-pt samples  (turbo: blue=surface, red=sharp)",
    )
    stitch_row(
        [OUT / "samples" / k / "board.png" for k in keys[:6]],
        [f"{s}_{i[-6:]}" for s, i in SAMPLES[:6]],
        OUT / "figures" / "boards_row1.png",
        "cad_spatial Dora boards  (DeepCAD)",
    )
    stitch_row(
        [OUT / "samples" / k / "board.png" for k in keys[6:]],
        [f"{s}_{i[-6:]}" for s, i in SAMPLES[6:]],
        OUT / "figures" / "boards_row2.png",
        "cad_spatial Dora boards  (DeepCAD high/low score + Fusion360)",
    )
    stats = pool_stats()
    manifest = {
        "output": str(OUT),
        "data_root": str(DATA),
        "note": "Visualizes existing Dora packs in cad_spatial_dataset. Coordinates shown in CAD canonical frame (s*p+t).",
        "samples": rows,
        "v3_train_pool": stats,
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"n_samples": len(rows), "out": str(OUT), "pool": stats}, indent=2))


if __name__ == "__main__":
    main()
