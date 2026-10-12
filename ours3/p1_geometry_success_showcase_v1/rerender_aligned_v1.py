#!/usr/bin/env python3
"""Re-render the 4-case showcase with P1/GT in the same CAD frame.

Predictions were exported in source/model.obj coordinates. GT DSL STEP is in
canonical CAD coordinates. Map pred vertices by the frozen
geometry_pack coordinate_transform.json: v_can = v_src * scale + translation.
Input uses pack surface_points.npy (already canonical). Shared GT bbox,
orthographic camera. Does not modify predictions or metrics.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from collections import defaultdict

from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
BASE = ROOT / "ours3"
OUT = BASE / "p1_geometry_success_showcase_v1"
P1 = BASE / "p1_exact9998_val1000_eval_v2"
A0 = BASE / "m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0"
A1 = BASE / "m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1"
A3 = BASE / "m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3"
MAIN = [
    "deepcad__0062_00623202",
    "deepcad__0008_00080235",
    "deepcad__0002_00024054",
    "fusion360__41970_24ba0c1b_0009",
]
AZIM, ELEV = -42.0, 24.0
LIGHT = np.array([0.32, 0.48, 0.81], dtype=np.float64)
LIGHT /= np.linalg.norm(LIGHT)
_az, _el = np.deg2rad(AZIM), np.deg2rad(ELEV)
CAM = np.array([np.cos(_el) * np.cos(_az), np.cos(_el) * np.sin(_az), np.sin(_el)], dtype=np.float64)
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def pack_dir(cid: str) -> Path:
    ds, sid = cid.split("__", 1)
    folder = "DeepCAD" if ds == "deepcad" else "Fusion360"
    return ROOT / "cad_spatial_dataset" / folder / "geometry_pack_v1" / sid


def load_T(cid: str) -> tuple[float, np.ndarray]:
    t = json.loads((pack_dir(cid) / "coordinate_transform.json").read_text())
    return float(t["scale"]), np.asarray(t["translation"], dtype=np.float64)


def tessellate(step: Path, linear: float, angular: float = 0.12):
    import cadquery as cq

    v, f = cq.importers.importStep(str(step)).val().tessellate(linear, angular)
    verts = np.array([[q.x, q.y, q.z] for q in v], dtype=np.float64)
    faces = np.asarray(f, dtype=np.int64)
    return verts, faces


def weld(verts: np.ndarray, faces: np.ndarray, dec: int = 6):
    key = np.round(verts, dec)
    uniq, inv = np.unique(key, axis=0, return_inverse=True)
    return uniq.astype(np.float64), inv[faces]


def shade_faces(tris: np.ndarray, color: str) -> np.ndarray:
    n = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    n /= np.clip(np.linalg.norm(n, axis=1, keepdims=True), 1e-12, None)
    val = 0.40 + 0.60 * np.abs(n @ LIGHT)
    rgb = np.asarray(to_rgb(color), dtype=np.float64)
    return np.clip(rgb * val[:, None], 0, 1)


def sharp_edge_idx(verts: np.ndarray, faces: np.ndarray, deg: float = 48.0) -> np.ndarray:
    e2f = defaultdict(list)
    for i, f in enumerate(faces):
        for a, b in ((f[0], f[1]), (f[1], f[2]), (f[2], f[0])):
            e2f[tuple(sorted((int(a), int(b))))].append(i)
    n = np.cross(verts[faces[:, 1]] - verts[faces[:, 0]], verts[faces[:, 2]] - verts[faces[:, 0]])
    n /= np.clip(np.linalg.norm(n, axis=1, keepdims=True), 1e-12, None)
    front = (n @ CAM) > 0.0
    segs = []
    thr = np.cos(np.deg2rad(deg))
    for (a, b), fs in e2f.items():
        if len(fs) == 2:
            f0, f1 = fs
            if not (front[f0] or front[f1]):
                continue
            sil = bool(front[f0]) != bool(front[f1])
            sharp = float(n[f0] @ n[f1]) <= thr
            if sil or sharp:
                segs.append((a, b))
    return np.asarray(segs, dtype=np.int64) if segs else np.zeros((0, 2), dtype=np.int64)


def align_points_to_gt(pts: np.ndarray, center: np.ndarray, diag: float) -> np.ndarray:
    pmin, pmax = pts.min(0), pts.max(0)
    pdiag = float(np.linalg.norm(pmax - pmin))
    if pdiag < 1e-8:
        return pts
    if pdiag > 1.35 * diag:
        pc = (pmin + pmax) / 2
        pts = (pts - pc) * (diag / pdiag) + center
    return pts


def panel(title: str, color: str, verts=None, faces=None, points=None, tr=None):
    fig = plt.figure(figsize=(3.15, 3.15), dpi=170)
    ax = fig.add_subplot(111, projection="3d")
    ax.set_proj_type("ortho")
    ax.set_axis_off()
    ax.set_facecolor("white")
    fig.patch.set_facecolor("white")
    center, diag = tr
    try:
        if points is not None:
            p = (np.asarray(points, dtype=np.float64) - center) / diag
            if len(p) > 3500:
                p = p[np.linspace(0, len(p) - 1, 3500).astype(int)]
            ax.scatter(p[:, 0], p[:, 1], p[:, 2], s=1.4, c="#4d5f70", alpha=0.9, linewidths=0)
        elif verts is not None and faces is not None and len(faces):
            verts, faces = weld(np.asarray(verts, dtype=np.float64), np.asarray(faces, dtype=np.int64))
            v = (verts - center) / diag
            tris = v[faces]
            fc = shade_faces(tris, color)
            coll = Poly3DCollection(tris, facecolors=fc, edgecolors="none", linewidths=0, shade=False)
            ax.add_collection3d(coll)
            eidx = sharp_edge_idx(verts, faces)
            if len(eidx):
                ax.add_collection3d(Line3DCollection(v[eidx], colors="#2b3946", linewidths=0.9))
        else:
            raise RuntimeError("empty")
    except Exception as exc:
        ax.text2D(
            0.5,
            0.5,
            "UNAVAILABLE",
            transform=ax.transAxes,
            ha="center",
            va="center",
            fontsize=11,
            color="crimson",
        )
    ax.set_xlim(-0.72, 0.72)
    ax.set_ylim(-0.72, 0.72)
    ax.set_zlim(-0.72, 0.72)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(ELEV, AZIM)
    ax.set_title(title, fontsize=8, pad=2)
    fig.subplots_adjust(0, 0, 1, 0.90)
    return fig


def rows(d: Path) -> dict:
    out = {}
    for p in d.glob("*/row.json"):
        try:
            out[p.parent.name] = json.loads(p.read_text())
        except Exception:
            pass
    return out


def main() -> None:
    R = {k: rows(v) for k, v in {"P1": P1, "A0": A0, "A1": A1, "A3": A3}.items()}
    pred_root = {"A0": A0, "A1": A1, "A3": A3, "P1": P1}
    imgs = {}
    for cid in MAIN:
        gt_step = OUT / "renders" / f"{cid}__GT.step"
        vg0, _ = tessellate(gt_step, 1e-3, 0.2)
        mn, mx = vg0.min(0), vg0.max(0)
        center = (mn + mx) / 2
        diag = float(max(np.linalg.norm(mx - mn), 1e-8))
        linear = max(diag * 2.5e-4, 5e-5)
        vg, fg = tessellate(gt_step, linear, 0.07)
        tr = (center, diag)
        scale, trans = load_T(cid)
        pts = align_points_to_gt(np.load(pack_dir(cid) / "surface_points.npy")[:, :3], center, diag)
        imgs[cid] = []
        specs = [
            ("Input", "#4d5f70", None, False),
            ("GT", "#8eabc0", gt_step, False),
            ("A0", "#d98b72", pred_root["A0"] / cid / "pred.step", True),
            ("A1", "#d98b72", pred_root["A1"] / cid / "pred.step", True),
            ("A3", "#68b58a", pred_root["A3"] / cid / "pred.step", True),
            ("P1", "#68a0c4", pred_root["P1"] / cid / "pred.step", True),
        ]
        for lab, col, path, apply_T in specs:
            title = lab
            if lab not in ("Input", "GT"):
                r = R[lab].get(cid, {})
                g = r.get("geometry") or {}
                cd = g.get("chamfer_norm")
                step_ok = bool(r.get("step_ok")) or (path is not None and path.exists())
                if cd is not None:
                    title = f"{lab}  Op-F1 {float(r.get('op_f1') or 0):.2f}\nSTEP {'PASS' if step_ok else 'FAIL'}  CD {float(cd):.3f}"
            verts = faces = points = None
            if lab == "Input":
                points = pts
            elif path is not None and path.exists():
                pred_lin = linear if not apply_T else max(np.linalg.norm(np.ptp(tessellate(path, 1e-3, 0.2)[0], axis=0)) * 2.5e-4, 4e-5)
                verts, faces = tessellate(path, pred_lin, 0.07)
                if apply_T:
                    verts = verts * scale + trans
            q = OUT / "renders" / f"{cid}__{lab}.png"
            fig = panel(title, col, verts, faces, points, tr)
            fig.savefig(q, bbox_inches="tight", pad_inches=0.03)
            plt.close(fig)
            imgs[cid].append(q)

    cols = ["Input", "GT", "A0", "A1", "A3", "P1"]
    cw, ch, m = 420, 410, 108
    im = Image.new("RGB", (m + cw * 6, ch * len(MAIN) + 88), "white")
    d = ImageDraw.Draw(im)
    d.text(
        (16, 14),
        "P1 EXACT9998 VAL1000 geometry success showcase",
        fill="#17202a",
        font=ImageFont.truetype(FONT_B, 24),
    )
    d.text(
        (16, 44),
        "Predictions mapped to GT CAD frame by frozen coordinate_transform.json  ·  shared GT bbox  ·  ortho -42°/24°",
        fill="#5a6a78",
        font=ImageFont.truetype(FONT_R, 12),
    )
    for j, cid in enumerate(MAIN):
        d.text((8, 92 + j * ch), cid, fill="#263746", font=ImageFont.truetype(FONT_R, 12))
        for i, p in enumerate(imgs[cid]):
            q = Image.open(p).convert("RGB")
            q.thumbnail((cw - 10, ch - 24))
            im.paste(q, (m + i * cw + (cw - q.width) // 2, 86 + j * ch + 16))
        if j == 0:
            for i, x in enumerate(cols):
                d.text((m + i * cw + 10, 68), x, fill="#111", font=ImageFont.truetype(FONT_B, 14))
    dest = OUT / "renders/P1_GEOMETRY_SUCCESS_4CASE.png"
    im.save(dest, dpi=(300, 300))
    im.save(OUT / "renders/P1_GEOMETRY_SUCCESS_MENTOR.png", dpi=(300, 300))
    policy = {
        "source": "frozen formal STEP and GT DSL",
        "shared_GT_transform": True,
        "prediction_frame": "source STEP vertices mapped by frozen geometry_pack coordinate_transform.json (v*scale+translation) into GT CAD/canonical frame",
        "camera": "orthographic azimuth -42 elevation 24",
        "gt_bbox_scale": "diagonal; axis limits +/-0.72",
        "per_method_autofit": False,
        "per_method_recenter": False,
        "per_method_rescale": False,
        "input": "geometry_pack_v1 surface_points.npy (canonical)",
        "tessellation": "OCC linear ~0.0004*diag, angular 0.10 rad, Lambert shading",
    }
    (OUT / "protocol/RENDER_POLICY.json").write_text(json.dumps(policy, indent=2) + "\n")
    print("WROTE", dest)


if __name__ == "__main__":
    main()
