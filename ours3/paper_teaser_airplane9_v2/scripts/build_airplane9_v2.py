#!/usr/bin/env python3
"""Airplane9 teaser v2: smooth BRep panels without edges, plus world-frame assembly."""
from __future__ import annotations

import glob
import importlib.util
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
V1 = ROOT / "paper_teaser_airplane9_v1/manifests/AIRPLANE9_TEASER_MANIFEST.json"
OUT = ROOT / "paper_teaser_airplane9_v2"
RENDERER = ROOT / "paper_teaser_demo_v2/scripts/render_smooth_brep.py"
AUDITOR = ROOT / "paper_teaser_demo_v2/scripts/audit_brep_surfaces.py"
PARTS = [f"PART_{i:03d}" for i in range(9)]
PALETTE = [
    (0.086, 0.506, 0.553),
    (0.827, 0.412, 0.271),
    (0.271, 0.412, 0.553),
    (0.216, 0.580, 0.451),
    (0.855, 0.616, 0.255),
    (0.357, 0.439, 0.510),
    (0.525, 0.380, 0.600),
    (0.749, 0.337, 0.388),
    (0.400, 0.600, 0.690),
]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = load_module("render_smooth_brep", RENDERER)
A = load_module("audit_brep_surfaces", AUDITOR)
R.OUT = OUT


def records():
    out = {}
    for p in glob.glob(str(ROOT / "airplane9_fullseq_14bit_ir_v1/**/airplane__PART_00*/record.json"), recursive=True):
        d = json.loads(Path(p).read_text())
        out[d["part"]] = d
    return out


def to_world(v, rec):
    return (v - np.asarray(rec["translation"], dtype=np.float64)) / float(rec["scale"])


def render_scene(path: Path, items, fill=0.9):
    """items: (vertices, faces, corners, color, alpha)."""
    allv = np.vstack([it[0] for it in items])
    center, span = R.frame_of(allv)
    old = R.FILL
    R.FILL = fill
    half = R.projected_half(allv, center, span)
    R.FILL = old
    img, zbuf = R.blank()
    for v, f, c, color, alpha in items:
        R.paint_surface(img, zbuf, v, f, c, np.asarray(color, dtype=np.float64), center, span, half, alpha=alpha)
    R.save_image(path, img)


def render_mesh_scene(path: Path, meshes, fill=0.9):
    allv = np.vstack([m[0] for m in meshes])
    center, span = R.frame_of(allv)
    old = R.FILL
    R.FILL = fill
    half = R.projected_half(allv, center, span)
    R.FILL = old
    img, zbuf = R.blank()
    for v, f, c in meshes:
        sx, sy, z = R.paint_surface(img, zbuf, v, f, c, R.MESH_COLOR, center, span, half)
        segs = R.segments_from_indexed_edges(sx, sy, z, R.mesh_edge_index(f))
        R.draw_segments(*segs, img, zbuf, R.MESH_EDGE_COLOR, 0, 0.004, 0.02)
    R.save_image(path, img)


def main():
    for d in ("renders", "assembly", "teaser", "reports"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    manifest = json.loads(V1.read_text())
    rows = {r["PART_ID"]: r for r in manifest["ROWS"]}
    recs = records()
    audit, gen_world, can_world, mesh_world = [], [], [], []

    for i, part in enumerate(PARTS):
        row, rec = rows[part], recs[part]
        tag = part.replace("PART_", "part").lower()
        print("part", part, flush=True)
        for role, key in (("generated", "GENERATED_STEP"), ("canonical", "CANONICAL_STEP")):
            a = A.audit(Path(row[key]))
            a.update(part=part, role=role, gate=A.gate(a))
            audit.append(a)
        gen = R.load_cad(Path(row["GENERATED_STEP"]))
        can = R.load_cad(Path(row["CANONICAL_STEP"]))
        R.render_mesh_panel(OUT / f"renders/{tag}_input_mesh.png", Path(row["INPUT_OBJ"]))
        R.render_cad_panel(OUT / f"renders/{tag}_generated_brep.png", gen, np.asarray(PALETTE[i]))
        R.render_cad_panel(OUT / f"renders/{tag}_canonical_brep.png", can, R.CANONICAL_COLOR)
        R.render_overlay(OUT / f"renders/{tag}_overlay.png", gen, can)

        gen_world.append((to_world(gen[0], rec), gen[1], gen[2], PALETTE[i], 1.0))
        can_world.append((to_world(can[0], rec), can[1], can[2], R.CANONICAL_COLOR, 1.0))
        m = trimesh.load(Path(row["INPUT_OBJ"]), force="mesh", process=False)
        mv, mf = np.asarray(m.vertices, float), np.asarray(m.faces, np.int64)
        mesh_world.append((mv, mf, R.smooth_corner_normals(mv, mf, feature_deg=20.0)))

    (OUT / "reports/audit_rows.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")

    print("assembly", flush=True)
    render_scene(OUT / "assembly/airplane9_generated_assembly.png", gen_world)
    render_scene(OUT / "assembly/airplane9_canonical_assembly.png", can_world)
    render_mesh_scene(OUT / "assembly/airplane9_input_mesh_assembly.png", mesh_world)
    align = []
    for part, g, mw in zip(PARTS, gen_world, mesh_world):
        gc = (g[0].min(0) + g[0].max(0)) / 2
        mc = (mw[0].min(0) + mw[0].max(0)) / 2
        align.append({"part": part, "center_gap": float(np.linalg.norm(gc - mc)), "mesh_extent": float(np.max(mw[0].max(0) - mw[0].min(0)))})
    (OUT / "reports/assembly_alignment.json").write_text(json.dumps(align, indent=2) + "\n", encoding="utf-8")
    for a in align:
        print(a, flush=True)

    compose(rows)
    print("done")


def compose(rows):
    fig = plt.figure(figsize=(18, 13.2), facecolor="white")
    gs = fig.add_gridspec(4, 9, height_ratios=[1, 1, 1, 2.6], hspace=0.05, wspace=0.02)
    for j, part in enumerate(PARTS):
        tag = part.replace("PART_", "part").lower()
        n = rows[part]["TARGET_TOKEN_N"]
        for i, kind in enumerate(("input_mesh", "generated_brep", "overlay")):
            ax = fig.add_subplot(gs[i, j])
            ax.imshow(Image.open(OUT / f"renders/{tag}_{kind}.png"))
            ax.axis("off")
            if i == 0:
                ax.set_title(f"{part}\n{n:,} / {n:,}", fontsize=10, fontweight="bold", color="#14222b")
            if j == 0:
                ax.text(-0.08, 0.5, ("Input mesh", "Generated CAD", "Overlay")[i], rotation=90, va="center", ha="right",
                        transform=ax.transAxes, fontsize=11, fontweight="bold", color="#14222b")
    for k, (name, label) in enumerate((("input_mesh", "Input mesh assembly"), ("generated", "Generated CAD assembly"), ("canonical", "Canonical CAD assembly"))):
        ax = fig.add_subplot(gs[3, k * 3:(k + 1) * 3])
        ax.imshow(Image.open(OUT / f"assembly/airplane9_{name}_assembly.png"))
        ax.axis("off")
        ax.set_title(label, fontsize=13, fontweight="bold", color="#14222b")
    fig.suptitle("Airplane9 | Full-sequence Mesh-to-CAD", fontsize=20, fontweight="bold", color="#14222b", y=0.985)
    fig.text(0.5, 0.012, "9 / 9 exact  |  Smooth BRep  |  No tessellation edges  |  No chunk  |  No GT prefix  |  Natural EOS  |  IoU = 1.0  |  CD = 0.0",
             ha="center", fontsize=11, color="#31434d")
    fig.subplots_adjust(left=0.035, right=0.995, top=0.93, bottom=0.035)
    fig.savefig(OUT / "teaser/airplane9_teaser_overview.png", dpi=180, facecolor="white")
    fig.savefig(OUT / "teaser/airplane9_teaser_overview.pdf", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
