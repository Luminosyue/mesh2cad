#!/usr/bin/env python3
"""Visualize V3 curve-token INPUT vs Dora SES for gallery B samples.

M2 / C2 encodes B-Rep sharp curves (curve_samples.npz), not Dora mesh SES.
This figure puts both on the same canonical frame so the difference is visible.

Reads frozen assets only. Does not retrain, redecode, or modify jsonl/SUMMARY.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl_v3_curve_input")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import LineCollection, PolyCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
EVAL = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "pilot_eval_150_frozen_v1"
)
VIZ = EVAL / "visualization_v1"
OUT = VIZ / "curve_token_input_B_v1"
SELECTED = VIZ / "selected_cases.json"
SPLIT = (
    ROOT
    / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k"
    / "data/v3_pilot_eval_150.json"
)
DATA = ROOT / "cad_spatial_dataset"
CURVE_ROOT = ROOT / "ours3/curve_token_data_v1"

MESH_COLOR = np.array([0.62, 0.66, 0.70])
LIGHT = np.array([0.42, -0.58, 0.70], dtype=float)
LIGHT = LIGHT / float(np.linalg.norm(LIGHT))
EYE = np.array([1.15, -1.35, 0.95], dtype=float)
FRAME = 0.78
MAX_FACES = 12000
MAX_EDGES = 9000
MAX_POINTS = 4500
MAX_CURVES = 400
TYPE_COLOR = {
    0: np.array([0.15, 0.45, 0.90]),  # LINE
    1: np.array([0.86, 0.15, 0.15]),  # CIRCLE
    2: np.array([0.49, 0.23, 0.93]),  # ELLIPSE
    3: np.array([0.02, 0.59, 0.41]),  # BSPLINE
}
TYPE_NAME = {0: "LINE", 1: "CIRCLE", 2: "ELLIPSE", 3: "BSPLINE"}
ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
ELEV_DEG = 26.0
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def sample_dir(cad_id: str) -> Path:
    src, sid = cad_id.split("__", 1)
    folder = "DeepCAD" if src == "deepcad" else "Fusion360"
    return DATA / folder / "train" / sid


def pack_dir(cad_id: str) -> Path:
    src, sid = cad_id.split("__", 1)
    folder = "DeepCAD" if src == "deepcad" else "Fusion360"
    return DATA / folder / "geometry_pack_v1" / sid


def curve_dir(cad_id: str) -> Path:
    src, sid = cad_id.split("__", 1)
    split = "deepcad_train" if src == "deepcad" else "fusion360_train"
    return CURVE_ROOT / split / sid


def load_mesh(path: Path) -> trimesh.Trimesh:
    mesh = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.dump(concatenate=True)
    return mesh


def apply_canonical(pts: np.ndarray, scale: float, translation: np.ndarray) -> np.ndarray:
    return scale * np.asarray(pts, dtype=float) + translation


def camera_basis(eye: np.ndarray):
    f = eye / float(np.linalg.norm(eye))
    world_up = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ world_up)) > 0.97:
        world_up = np.array([0.0, 1.0, 0.0])
    right = np.cross(world_up, f)
    right = right / float(np.linalg.norm(right))
    up = np.cross(f, right)
    return right, up, f


def eye_from_azim(azim_deg: float, elev_deg: float = ELEV_DEG) -> np.ndarray:
    az = np.deg2rad(azim_deg)
    el = np.deg2rad(elev_deg)
    return np.array(
        [np.cos(el) * np.sin(az), -np.cos(el) * np.cos(az), np.sin(el)],
        dtype=float,
    )


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


def project_pts(pts: np.ndarray, center: np.ndarray, scale: float, eye: np.ndarray) -> np.ndarray:
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


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


def draw_segments(ax, xyz0, xyz1, colors, center, scale, eye, lw=0.7, alpha=0.92):
    n = len(xyz0)
    if n == 0:
        return
    idx = subsample(n, MAX_EDGES, 3)
    segs = np.stack(
        [project_pts(xyz0[idx], center, scale, eye), project_pts(xyz1[idx], center, scale, eye)],
        axis=1,
    )
    ax.add_collection(LineCollection(segs, colors=colors[idx], linewidths=lw, alpha=alpha))


def draw_polylines(ax, curves, types, keep, center, scale, eye):
    segs = []
    cols = []
    lws = []
    order = np.arange(len(curves))
    if len(order) > MAX_CURVES:
        kept = np.where(keep)[0]
        rest = np.where(~keep)[0]
        rest = rest[subsample(len(rest), max(0, MAX_CURVES - len(kept)), 5)]
        order = np.concatenate([kept, rest]) if len(rest) else kept
    for i in order:
        xyz = curves[i]
        for a, b in zip(xyz[:-1], xyz[1:]):
            if np.linalg.norm(b - a) < 1e-12:
                continue
            segs.append(np.stack([project_pts(a[None], center, scale, eye)[0], project_pts(b[None], center, scale, eye)[0]]))
            base = TYPE_COLOR.get(int(types[i]), np.array([0.8, 0.6, 0.1]))
            if keep[i]:
                cols.append((*base, 0.95))
                lws.append(1.15)
            else:
                cols.append((0.55, 0.55, 0.55, 0.35))
                lws.append(0.45)
    if segs:
        ax.add_collection(LineCollection(np.asarray(segs), colors=cols, linewidths=lws))


def save_fig(fig, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=130, bbox_inches="tight", facecolor="white", pad_inches=0.06)
    plt.close(fig)


def load_bundle(cad_id: str, rec: dict) -> dict:
    train = sample_dir(cad_id)
    pack = pack_dir(cad_id)
    tf = json.loads((pack / "coordinate_transform.json").read_text())
    s = float(tf["scale"])
    t = np.asarray(tf["translation"], dtype=float)
    mesh = load_mesh(pack / "mesh.obj")
    verts = apply_canonical(np.asarray(mesh.vertices, dtype=float), s, t)
    faces = np.asarray(mesh.faces, dtype=int)
    dora = np.load(train / "dora" / "salient_edges.npz")
    xyz0 = apply_canonical(dora["edge_xyz0"], s, t)
    xyz1 = apply_canonical(dora["edge_xyz1"], s, t)
    dih = np.asarray(dora["dihedral_deg"], dtype=float)
    dora_pts = apply_canonical(np.load(train / "dora" / "edge_points.npy"), s, t)
    sharp = np.load(pack / "edge_points_gt_sharp.npy").astype(float)[:, :3]
    detected = np.load(pack / "edge_points_detected.npy").astype(float)[:, :3]
    z = np.load(curve_dir(cad_id) / "curve_samples.npz", allow_pickle=True)
    curves = np.asarray(z["curve_xyz_normalized"], dtype=float)
    ctypes = np.asarray(z["curve_type_id"], dtype=int)
    selected = np.asarray(rec["selected_m2_indices"], dtype=int)
    keep = np.zeros(len(curves), dtype=bool)
    keep[selected] = True
    return {
        "cad_id": cad_id,
        "verts": verts,
        "faces": faces,
        "xyz0": xyz0,
        "xyz1": xyz1,
        "dih": dih,
        "dora_pts": dora_pts,
        "sharp": sharp,
        "detected": detected,
        "curves": curves,
        "ctypes": ctypes,
        "keep": keep,
        "k_valid": int(rec["k_valid"]),
        "n_dora": int(len(xyz0)),
        "n_curve": int(len(curves)),
        "n_selected": int(keep.sum()),
        "type_counts": {TYPE_NAME.get(int(k), str(k)): int((ctypes == k).sum()) for k in np.unique(ctypes)},
    }


def fit_frame(verts: np.ndarray):
    center = verts.mean(axis=0)
    scale = float(np.abs(verts - center).max()) or 1.0
    return center, scale


def dora_colors(dih: np.ndarray) -> np.ndarray:
    t = np.clip((dih - 15.0) / 60.0, 0.0, 1.0)
    return plt.cm.plasma(t)


def render_iso_board(bundle: dict, dest: Path) -> Path:
    center, scale = fit_frame(bundle["verts"])
    eye = EYE
    cid = bundle["cad_id"]
    fig, axes = plt.subplots(1, 4, figsize=(16.4, 4.35), dpi=130)
    draw_mesh(axes[0], bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.97)
    axes[0].set_title("mesh", fontsize=10)

    draw_mesh(axes[1], bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.18)
    draw_segments(axes[1], bundle["xyz0"], bundle["xyz1"], dora_colors(bundle["dih"]), center, scale, eye, lw=0.85)
    axes[1].set_title(f"Dora SES  n={bundle['n_dora']}\n(mesh dihedral, NOT C2 input)", fontsize=9)

    draw_mesh(axes[2], bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.16)
    draw_polylines(axes[2], bundle["curves"], bundle["ctypes"], bundle["keep"], center, scale, eye)
    axes[2].set_title(
        f"M2 / C2 input  B-Rep curves\nselected {bundle['n_selected']}/{bundle['n_curve']}  {bundle['type_counts']}",
        fontsize=9,
    )

    draw_mesh(axes[3], bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.16)
    pts = bundle["sharp"][subsample(len(bundle["sharp"]), MAX_POINTS, 11)]
    q = project_pts(pts, center, scale, eye)
    axes[3].scatter(q[:, 0], q[:, 1], s=2.0, c="#2563eb", alpha=0.7, linewidths=0)
    axes[3].set_title(f"B1 input  gt_sharp n={len(bundle['sharp'])}", fontsize=10)

    fig.suptitle(
        f"{cid}  curve-token input vs Dora  |  bright = selected M2  gray = dropped  |  LINE blue / CIRCLE red",
        fontsize=11,
        y=1.02,
    )
    fig.tight_layout()
    path = dest / "iso_board.png"
    save_fig(fig, path)
    return path


def render_orbit(bundle: dict, dest: Path) -> Path:
    center, scale = fit_frame(bundle["verts"])
    fig, axes = plt.subplots(1, len(ANGLES), figsize=(18.4, 2.55), dpi=120)
    for ax, az in zip(axes, ANGLES):
        eye = eye_from_azim(az)
        draw_mesh(ax, bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.18)
        draw_polylines(ax, bundle["curves"], bundle["ctypes"], bundle["keep"], center, scale, eye)
        ax.set_title(f"{az}°", fontsize=8, pad=2)
    fig.suptitle(
        f"{bundle['cad_id']}  M2 curve-token INPUT  (B-Rep sharp curves → C2)  selected {bundle['n_selected']}/{bundle['n_curve']}",
        fontsize=11,
        y=0.98,
    )
    fig.subplots_adjust(left=0.01, right=0.995, top=0.78, bottom=0.02, wspace=0.04)
    path = dest / "orbit_m2_curves.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, facecolor="white")
    plt.close(fig)
    return path


def render_orbit_dora(bundle: dict, dest: Path) -> Path:
    center, scale = fit_frame(bundle["verts"])
    fig, axes = plt.subplots(1, len(ANGLES), figsize=(18.4, 2.55), dpi=120)
    cols = dora_colors(bundle["dih"])
    for ax, az in zip(axes, ANGLES):
        eye = eye_from_azim(az)
        draw_mesh(ax, bundle["verts"], bundle["faces"], center, scale, eye, alpha=0.18)
        draw_segments(ax, bundle["xyz0"], bundle["xyz1"], cols, center, scale, eye, lw=0.8)
        ax.set_title(f"{az}°", fontsize=8, pad=2)
    fig.suptitle(
        f"{bundle['cad_id']}  Dora SES (mesh sharp edges)  n={bundle['n_dora']}  — not fed to C2",
        fontsize=11,
        y=0.98,
    )
    fig.subplots_adjust(left=0.01, right=0.995, top=0.78, bottom=0.02, wspace=0.04)
    path = dest / "orbit_dora.png"
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120, facecolor="white")
    plt.close(fig)
    return path


def stack_gallery(paths: list[Path], out: Path, title: str):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w = max(im.width for im in imgs)
    h = max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    top = 48
    canvas = Image.new("RGB", (w, top + h * len(imgs)), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 10), title, fill=(20, 20, 20), font=font(18))
    for i, im in enumerate(imgs):
        canvas.paste(im, (0, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    selected = json.loads(SELECTED.read_text())
    cases = selected["categories"]["B_b0_best"] + selected["extended"]["B_b0_best_more"]
    split = {r["cad_id"]: r for r in json.loads(SPLIT.read_text())["records"]}
    OUT.mkdir(parents=True, exist_ok=True)
    iso_paths, m2_paths, dora_paths, rows = [], [], [], []
    for case in cases:
        cid = case["cad_id"]
        print(cid, flush=True)
        bundle = load_bundle(cid, split[cid])
        dest = OUT / "samples" / cid
        dest.mkdir(parents=True, exist_ok=True)
        iso_paths.append(render_iso_board(bundle, dest))
        m2_paths.append(render_orbit(bundle, dest))
        dora_paths.append(render_orbit_dora(bundle, dest))
        rows.append(
            {
                "cad_id": cid,
                "n_dora": bundle["n_dora"],
                "n_curve": bundle["n_curve"],
                "n_selected": bundle["n_selected"],
                "k_valid": bundle["k_valid"],
                "type_counts": bundle["type_counts"],
            }
        )
        slim = {k: bundle[k] for k in rows[-1]}
        (dest / "stats.json").write_text(json.dumps(slim, indent=2) + "\n")
    stack_gallery(
        iso_paths,
        OUT / "gallery_iso.png",
        "gallery B  |  mesh | Dora SES | M2 C2 input (B-Rep curves) | B1 gt_sharp  — C2 does not read Dora",
    )
    stack_gallery(
        m2_paths,
        OUT / "gallery_orbit_m2.png",
        "gallery B  |  M2 curve-token INPUT turntable  |  B-Rep sharp curves selected into C2",
    )
    stack_gallery(
        dora_paths,
        OUT / "gallery_orbit_dora.png",
        "gallery B  |  Dora SES turntable  |  mesh dihedral edges  |  not the C2 payload",
    )
    manifest = {
        "n": len(rows),
        "note": "M2 curve tokens encode B-Rep sharp curves (curve_samples.npz) via frozen C2. Dora SES is a separate mesh detector.",
        "samples": rows,
        "original_results_modified": False,
        "gallery_iso": str(OUT / "gallery_iso.png"),
        "gallery_orbit_m2": str(OUT / "gallery_orbit_m2.png"),
        "gallery_orbit_dora": str(OUT / "gallery_orbit_dora.png"),
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
