#!/usr/bin/env python3
"""Render additional P1-good VAL1000 cases with the aligned CAD-frame renderer.

Does not modify predictions or metrics. Does not overwrite the original 4-case figure.
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rerender_aligned_v1 import (
    A0,
    A1,
    A3,
    BASE,
    FONT_B,
    FONT_R,
    OUT,
    P1,
    ROOT,
    align_points_to_gt,
    load_T,
    pack_dir,
    panel,
    rows,
    tessellate,
)

import numpy as np

PY = "/data/miniconda3/envs/cadfit-env/bin/python"
DSL = ROOT / "scripts/deepcad/dsl_to_occ.py"
MORE = [
    "deepcad__0087_00875000",
    "deepcad__0024_00241946",
    "deepcad__0079_00798021",
    "deepcad__0029_00297473",
    "deepcad__0098_00984147",
    "deepcad__0068_00689117",
    "deepcad__0066_00668316",
    "fusion360__128996_2777de76_0000",
]
PRED_ROOT = {"A0": A0, "A1": A1, "A3": A3, "P1": P1}


def ensure_gt_step(cid: str) -> Path:
    gt = OUT / "renders" / f"{cid}__GT.step"
    if gt.exists():
        return gt
    dsl = P1 / cid / "gt.dsl"
    stl = gt.with_suffix(".stl")
    r = subprocess.run(
        [PY, str(DSL), "--dsl", str(dsl), "--step", str(gt), "--stl", str(stl)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if r.returncode != 0 or not gt.exists():
        raise RuntimeError(f"GT STEP failed for {cid}: {r.stderr[-800:]}")
    return gt


def render_case(cid: str, R: dict) -> list[Path]:
    gt_step = ensure_gt_step(cid)
    vg0, _ = tessellate(gt_step, 1e-3, 0.2)
    mn, mx = vg0.min(0), vg0.max(0)
    center = (mn + mx) / 2
    diag = float(max(np.linalg.norm(mx - mn), 1e-8))
    linear = max(diag * 2.5e-4, 5e-5)
    tr = (center, diag)
    scale, trans = load_T(cid)
    pts = align_points_to_gt(np.load(pack_dir(cid) / "surface_points.npy")[:, :3], center, diag)
    out_paths = []
    specs = [
        ("Input", "#4d5f70", None, False),
        ("GT", "#8eabc0", gt_step, False),
        ("A0", "#d98b72", PRED_ROOT["A0"] / cid / "pred.step", True),
        ("A1", "#d98b72", PRED_ROOT["A1"] / cid / "pred.step", True),
        ("A3", "#68b58a", PRED_ROOT["A3"] / cid / "pred.step", True),
        ("P1", "#68a0c4", PRED_ROOT["P1"] / cid / "pred.step", True),
    ]
    for lab, col, path, apply_T in specs:
        title = lab
        if lab not in ("Input", "GT"):
            r = R[lab].get(cid, {})
            g = r.get("geometry") or {}
            cd = g.get("chamfer_norm")
            step_ok = bool(r.get("step_ok")) or (path is not None and path.exists())
            if cd is not None:
                title = (
                    f"{lab}  Op-F1 {float(r.get('op_f1') or 0):.2f}\n"
                    f"STEP {'PASS' if step_ok else 'FAIL'}  CD {float(cd):.3f}"
                )
        verts = faces = points = None
        if lab == "Input":
            points = pts
        elif path is not None and path.exists():
            pred_lin = linear if not apply_T else max(
                np.linalg.norm(np.ptp(tessellate(path, 1e-3, 0.2)[0], axis=0)) * 2.5e-4, 4e-5
            )
            verts, faces = tessellate(path, pred_lin, 0.07)
            if apply_T:
                verts = verts * scale + trans
        q = OUT / "renders" / f"{cid}__{lab}.png"
        fig = panel(title, col, verts, faces, points, tr)
        fig.savefig(q, bbox_inches="tight", pad_inches=0.03)
        plt.close(fig)
        out_paths.append(q)
    return out_paths


def gallery(ids, imgs, dest: Path, title: str) -> None:
    cols = ["Input", "GT", "A0", "A1", "A3", "P1"]
    cw, ch, m = 420, 410, 118
    im = Image.new("RGB", (m + cw * 6, ch * len(ids) + 88), "white")
    d = ImageDraw.Draw(im)
    d.text((16, 14), title, fill="#17202a", font=ImageFont.truetype(FONT_B, 22))
    d.text(
        (16, 44),
        "Additional P1-good VAL1000 cases  ·  same aligned CAD-frame protocol as the 4-case figure",
        fill="#5a6a78",
        font=ImageFont.truetype(FONT_R, 12),
    )
    for j, cid in enumerate(ids):
        d.text((6, 92 + j * ch), cid, fill="#263746", font=ImageFont.truetype(FONT_R, 11))
        for i, p in enumerate(imgs[cid]):
            q = Image.open(p).convert("RGB")
            q.thumbnail((cw - 10, ch - 24))
            im.paste(q, (m + i * cw + (cw - q.width) // 2, 86 + j * ch + 16))
        if j == 0:
            for i, x in enumerate(cols):
                d.text((m + i * cw + 10, 68), x, fill="#111", font=ImageFont.truetype(FONT_B, 14))
    im.save(dest, dpi=(300, 300))


def main() -> None:
    (OUT / "renders").mkdir(parents=True, exist_ok=True)
    (OUT / "selection").mkdir(parents=True, exist_ok=True)
    R = {k: rows(v) for k, v in {"P1": P1, "A0": A0, "A1": A1, "A3": A3}.items()}
    recs = []
    imgs = {}
    for cid in MORE:
        print("RENDER", cid, flush=True)
        imgs[cid] = render_case(cid, R)
        p = R["P1"][cid]
        g = p.get("geometry") or {}
        recs.append(
            [
                cid,
                p.get("dataset"),
                ">".join(p.get("gt_ops") or []),
                p.get("op_f1"),
                g.get("chamfer_norm"),
                g.get("hausdorff_95_norm"),
                g.get("volume_error"),
                p.get("exact_match"),
            ]
        )
    fields = ["case_id", "source", "gt_ops", "P1_OpF1", "P1_Chamfer", "P1_H95", "P1_Volume_Error", "exact_match"]
    with (OUT / "selection/MORE_8CASE.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        w.writerows(recs)
    dest = OUT / "renders/P1_GEOMETRY_SUCCESS_MORE8.png"
    gallery(MORE, imgs, dest, "P1 EXACT9998 VAL1000 additional geometry-success cases")
    print("WROTE", dest)


if __name__ == "__main__":
    main()
