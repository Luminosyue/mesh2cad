#!/usr/bin/env python3
"""Tank: BRep audit, smooth edge-free part renders, world-frame assembly."""
from __future__ import annotations

import colorsys
import importlib.util
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
SRC = ROOT / "tank_full_object_q14_v3_assembly_v1"
OUT = SRC / "smooth_render_v2"
RENDERER = ROOT / "paper_teaser_demo_v2/scripts/render_smooth_brep.py"
AUDITOR = ROOT / "paper_teaser_demo_v2/scripts/audit_brep_surfaces.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


R = load_module("render_smooth_brep", RENDERER)
A = load_module("audit_brep_surfaces", AUDITOR)
R.W = R.H = 1000


def load_cad(path: Path):
    shape = R.read_step(path)
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    x0, y0, z0, x1, y1, z1 = box.Get()
    diag = max(((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5, 1e-9)
    vertices, faces = R.mesh_shape(shape, max(diag * 0.0015, 1e-4), 0.1)
    corners = R.smooth_corner_normals(vertices, faces, feature_deg=18.0)
    return vertices, faces, corners, [], int(len(faces))


def palette(n):
    return [np.asarray(colorsys.hsv_to_rgb((0.53 + i * 0.618034) % 1.0, 0.48, 0.70)) for i in range(n)]


def load_mesh(path: Path):
    m = trimesh.load(path, force="mesh", process=False)
    v, f = np.asarray(m.vertices, float), np.asarray(m.faces, np.int64)
    return v, f, R.smooth_corner_normals(v, f, feature_deg=20.0)


def scene(path: Path, items, mesh_edges=False, fill=0.92):
    allv = np.vstack([it[0] for it in items])
    center, span = R.frame_of(allv)
    old = R.FILL
    R.FILL = fill
    half = R.projected_half(allv, center, span)
    R.FILL = old
    img, zbuf = R.blank()
    for v, f, c, color in items:
        sx, sy, z = R.paint_surface(img, zbuf, v, f, c, np.asarray(color, float), center, span, half)
        if mesh_edges:
            segs = R.segments_from_indexed_edges(sx, sy, z, R.mesh_edge_index(f))
            R.draw_segments(*segs, img, zbuf, R.MESH_EDGE_COLOR, 0, 0.004, 0.02)
    R.save_image(path, img)


def main():
    for d in ("renders", "assembly", "teaser", "reports"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    parts = json.loads((SRC / "assembly/tank_assembly_manifest.json").read_text())["parts"]
    mesh_paths = {}
    for line in (SRC / "manifests/TANK_FULL_PART_MANIFEST.csv").read_text().splitlines()[1:]:
        cols = line.split(",")
        mesh_paths[cols[0]] = Path(cols[1])
    colors = palette(len(parts))
    only_audit = "--audit-only" in sys.argv

    audit_path = OUT / "reports/audit_rows.json"
    if audit_path.exists() and not only_audit:
        parts_audit_done = True
    else:
        parts_audit_done = False
    audit = [] if not parts_audit_done else json.loads(audit_path.read_text())
    for p in ([] if parts_audit_done else parts):
        a = A.audit(Path(p["CAD_SOURCE"]))
        a.update(part=p["PART_ID"], role=p["GENERATED_OR_CANONICAL"], gate=A.gate(a))
        audit.append(a)
        print(p["PART_ID"], a["BREP_FACE_N"], a["surface_types"]["BSplineSurface"], a["surface_types"]["Plane"],
              a["plane_triangular_face_n"], a["DISPLAY_TESSELLATION_TRIANGLE_N"], a["gate"], flush=True)
    audit_path.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    faceted = [a["part"] for a in audit if a["gate"] == "FACETED_BREP"]
    print("FACETED_PARTS", faceted, flush=True)
    if only_audit:
        return

    cad_world, mesh_world = [], []
    for i, p in enumerate(parts):
        pid = p["PART_ID"]
        print("render", pid, flush=True)
        cad = load_cad(Path(p["CAD_SOURCE"]))
        R.render_cad_panel(OUT / f"renders/{pid}_cad.png", cad, colors[i])
        R.render_mesh_panel(OUT / f"renders/{pid}_input_mesh.png", mesh_paths[pid])
        cad_world.append((cad[0], cad[1], cad[2], colors[i]))
        mv, mf, mc = load_mesh(mesh_paths[pid])
        mesh_world.append((mv, mf, mc, R.MESH_COLOR))

    R.W = R.H = 2000
    print("assembly", flush=True)
    scene(OUT / "assembly/tank_cad_assembly.png", cad_world)
    scene(OUT / "assembly/tank_cad_assembly_mono.png", [(v, f, c, R.CANONICAL_COLOR) for v, f, c, _ in cad_world])
    scene(OUT / "assembly/tank_input_mesh_assembly.png", mesh_world, mesh_edges=True)
    compose(parts)
    print("done")


def compose(parts):
    n = len(parts)
    cols = 9
    rows = (n + cols - 1) // cols
    fig = plt.figure(figsize=(20, 5.2 + rows * 2.3), facecolor="white")
    gs = fig.add_gridspec(rows + 1, cols, height_ratios=[2.6] * 1 + [1] * rows, hspace=0.12, wspace=0.02)
    for k, (name, label) in enumerate((("input_mesh", "Input mesh assembly"), ("cad", "CAD assembly (smooth BRep)"), ("cad_mono", "CAD assembly (single color)"))):
        ax = fig.add_subplot(gs[0, k * 3:(k + 1) * 3])
        ax.imshow(Image.open(OUT / f"assembly/tank_{name}_assembly.png" if name != "cad_mono" else OUT / "assembly/tank_cad_assembly_mono.png"))
        ax.axis("off")
        ax.set_title(label, fontsize=14, fontweight="bold", color="#14222b")
    for idx, p in enumerate(parts):
        ax = fig.add_subplot(gs[1 + idx // cols, idx % cols])
        ax.imshow(Image.open(OUT / f"renders/{p['PART_ID']}_cad.png"))
        ax.axis("off")
        tag = " (generated)" if p["GENERATED_OR_CANONICAL"] == "GENERATED_STRICT" else ""
        ax.set_title(f"{p['PART_ID']}{tag}", fontsize=9, fontweight="bold", color="#14222b")
    fig.suptitle("Tank | 45-part Mesh-to-CAD", fontsize=22, fontweight="bold", color="#14222b", y=0.99)
    fig.text(0.5, 0.008, "45 / 45 parts  |  Smooth BRep  |  No tessellation edges  |  Object-space assembly",
             ha="center", fontsize=12, color="#31434d")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.95, bottom=0.025)
    fig.savefig(OUT / "teaser/tank_teaser_overview.png", dpi=160, facecolor="white")
    fig.savefig(OUT / "teaser/tank_teaser_overview.pdf", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
