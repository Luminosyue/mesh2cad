#!/usr/bin/env python3
"""How DeepCAD uses Dora: mesh in → SES / edge_score; V3 does not consume it.

Reads existing train/ + geometry_pack_v1 artifacts only.
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
    apply_canonical,
    font,
    load_mesh,
    load_sample,
    subsample,
)

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OUT = ROOT / "ours3/deepcad_dora_usage_viz_v1"
SAMPLES = [
    "0001_00017084",
    "0000_00001503",
    "0003_00032761",
    "0065_00652765",
    "0002_00022191",
    "0001_00017562",
]
FRAME = 0.80
WORLD_LIGHT = np.array([0.35, -0.55, 0.76], dtype=float)
WORLD_LIGHT = WORLD_LIGHT / float(np.linalg.norm(WORLD_LIGHT))
EYE = np.array([1.15, -1.35, 0.95], dtype=float)
EYE = EYE / float(np.linalg.norm(EYE))


def camera_basis(eye):
    f = eye / float(np.linalg.norm(eye))
    up0 = np.array([0.0, 0.0, 1.0])
    if abs(float(f @ up0)) > 0.97:
        up0 = np.array([0.0, 1.0, 0.0])
    right = np.cross(up0, f)
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
    for s in ax.spines.values():
        s.set_visible(False)


def project_pts(pts, center, scale, eye):
    right, up, _ = camera_basis(eye)
    x = (pts - center) / scale
    return np.stack([x @ right, x @ up], axis=-1)


def fit_frame(verts):
    c = verts.mean(0)
    return c, (float(np.abs(verts - c).max()) or 1.0) * 1.05


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
    order = np.argsort(x.mean(1) @ fwd)
    p2 = np.stack([x @ right, x @ up], axis=-1)[order]
    ax.add_collection(
        PolyCollection(
            p2,
            facecolors=np.c_[fc[order], np.full(len(order), alpha)],
            edgecolors=(0.18, 0.20, 0.22, 0.12),
            linewidths=0.05,
        )
    )


def draw_segs(ax, xyz0, xyz1, colors, center, scale, eye, lw=0.85):
    if len(xyz0) == 0:
        return
    idx = subsample(len(xyz0), MAX_EDGES, 3)
    segs = np.stack(
        [project_pts(xyz0[idx], center, scale, eye), project_pts(xyz1[idx], center, scale, eye)],
        1,
    )
    ax.add_collection(LineCollection(segs, colors=colors[idx], linewidths=lw, alpha=0.95))


def render_one(sid: str) -> dict:
    rec = load_sample("deepcad", sid)
    pack = DATA / "DeepCAD" / "geometry_pack_v1" / sid
    tf = json.loads((pack / "coordinate_transform.json").read_text())
    s, t = float(tf["scale"]), np.asarray(tf["translation"], dtype=float)
    mesh_p = load_mesh(pack / "mesh.obj")
    verts_p = apply_canonical(np.asarray(mesh_p.vertices, dtype=float), s, t)
    faces_p = np.asarray(mesh_p.faces, dtype=int)
    sharp = np.load(pack / "mesh_sharp_edges.npz")
    v0 = apply_canonical(sharp["v0"], s, t)
    v1 = apply_canonical(sharp["v1"], s, t)
    dih_m = np.asarray(sharp["dihedral_deg"], dtype=float)
    surf = np.load(pack / "surface_points.npy")[:, :3]
    dest = OUT / "samples" / sid
    dest.mkdir(parents=True, exist_ok=True)
    center, scale = fit_frame(rec["verts"])
    eye = EYE
    fig, axes = plt.subplots(1, 5, figsize=(20.5, 4.2), dpi=125)

    draw_mesh(axes[0], rec["verts"], rec["faces"], center, scale, eye, 0.97)
    axes[0].set_title("1. Dora INPUT\nSTEP -> mesh.obj", fontsize=9)

    draw_mesh(axes[1], rec["verts"], rec["faces"], center, scale, eye, 0.18)
    tcol = plt.cm.plasma(np.clip((rec["dih"] - 15) / 60, 0, 1))
    draw_segs(axes[1], rec["xyz0"], rec["xyz1"], tcol, center, scale, eye)
    axes[1].set_title(f"2. Dora SES on that mesh\nth=45 deg  n={rec['n_salient_edges']}", fontsize=9)

    draw_mesh(axes[2], rec["verts"], rec["faces"], center, scale, eye, 0.16)
    idx = subsample(len(rec["feat_xyz"]), MAX_POINTS, 11)
    q = project_pts(rec["feat_xyz"][idx], center, scale, eye)
    axes[2].scatter(q[:, 0], q[:, 1], s=2.0, c=rec["score"][idx], cmap=CMAP, vmin=0, vmax=1, linewidths=0, alpha=0.8)
    axes[2].set_title(
        f"3. DeepCAD ours uses this\n7ch edge_score  >0.5={rec['frac_gt_0_5']:.1%}",
        fontsize=9,
    )

    draw_mesh(axes[3], verts_p, faces_p, center, scale, eye, 0.16)
    idx = subsample(len(surf), MAX_POINTS, 9)
    q = project_pts(surf[idx], center, scale, eye)
    axes[3].scatter(q[:, 0], q[:, 1], s=1.6, c="#64748b", linewidths=0, alpha=0.7)
    axes[3].set_title("4. Current V3 surface\n6ch xyz+normal  NO Dora ch", fontsize=9)

    draw_mesh(axes[4], verts_p, faces_p, center, scale, eye, 0.16)
    tcol2 = plt.cm.plasma(np.clip((dih_m - 15) / 60, 0, 1)) if len(dih_m) else np.zeros((0, 4))
    draw_segs(axes[4], v0, v1, tcol2, center, scale, eye, lw=0.7)
    axes[4].set_title(f"5. pack mesh-sharp (30 deg)\ndetected ablation n={len(v0)}\nV3 default unused", fontsize=9)

    fig.suptitle(
        f"DeepCAD {sid}  |  Dora runs on mesh  |  ours=col3  V3=col4 (no Dora)",
        fontsize=12,
        y=1.03,
    )
    fig.tight_layout()
    path = dest / "usage_board.png"
    fig.savefig(path, dpi=125, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return {
        "sample_id": sid,
        "n_dora_edges": rec["n_salient_edges"],
        "frac_edge_score": rec["frac_gt_0_5"],
        "n_pack_mesh_sharp": int(len(v0)),
        "board": str(path),
    }


def stack(paths, out, title):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w, h = max(i.width for i in imgs), max(i.height for i in imgs)
    imgs = [i.resize((w, h), Image.Resampling.LANCZOS) if i.size != (w, h) else i for i in imgs]
    top = 44
    canvas = Image.new("RGB", (w, top + h * len(imgs)), "white")
    d = ImageDraw.Draw(canvas)
    d.text((12, 10), title, fill=(20, 20, 20), font=font(18))
    for i, im in enumerate(imgs):
        canvas.paste(im, (0, top + i * h))
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "samples").mkdir(exist_ok=True)
    rows = []
    for sid in SAMPLES:
        print(sid, flush=True)
        rows.append(render_one(sid))
    stack(
        [Path(r["board"]) for r in rows],
        OUT / "gallery.png",
        "DeepCAD Dora usage  |  1 mesh input  2 Dora SES  3 ours 7ch  4 V3 6ch  5 pack mesh-sharp",
    )
    (OUT / "manifest.json").write_text(
        json.dumps(
            {
                "note": "Dora runs on STEP tessellated mesh. DeepCAD ours consumes 7ch edge_score. Current V3 does not.",
                "samples": rows,
                "gallery": str(OUT / "gallery.png"),
            },
            indent=2,
        )
        + "\n"
    )
    print(json.dumps({"n": len(rows), "out": str(OUT)}, indent=2))


if __name__ == "__main__":
    main()
