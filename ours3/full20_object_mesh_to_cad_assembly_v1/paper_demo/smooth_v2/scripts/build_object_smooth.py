#!/usr/bin/env python3
"""Model-generated objects: BRep audit, smooth edge-free part renders, object-space assembly."""
from __future__ import annotations

import colorsys
import importlib.util
import json
import re
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
FULL20 = ROOT / "full20_object_mesh_to_cad_assembly_v1"
OUT = FULL20 / "paper_demo/smooth_v2"
RENDERER = ROOT / "paper_teaser_demo_v2/scripts/render_smooth_brep.py"
AUDITOR = ROOT / "paper_teaser_demo_v2/scripts/audit_brep_surfaces.py"
OBJECTS = {
    "pottery_large": ("Pottery Large", "free_320"),
    "aroma_stainless_steel_milk_frother_2_cup": ("Milk Frother", "free_320"),
    "cube": ("Cube", "completion_side_final_v1"),
    "baby_car": ("Baby Car", "completion_side_final_v1"),
    "android_figure_orange": ("Android Figure", "completion_side_final_v1"),
    "speaker_big": ("Speaker Big", "completion_side_final_v2"),
    "fire_truck": ("Fire Truck", "completion_side_final_v1"),
    "robot": ("Robot", "completion_side_final_v1"),
    "pressure_cooker": ("Pressure Cooker", "completion_side_final_v1"),
    "dvd_player": ("DVD Player", "completion_side_final_v1"),
    "2_of_jenga_classic_game": ("Jenga Classic", "completion_side_final_v1"),
    "toaster": ("Toaster", "completion_side_final_v1"),
    "mini_excavator": ("Mini Excavator", "completion_side_final_v1"),
    "3d_dollhouse_sofa": ("Dollhouse Sofa", "completion_side_final_v1"),
    "assorted_vegetable_set": ("Vegetable Set", "completion_side_final_v1"),
    "mini_fire_engine": ("Mini Fire Engine", "completion_side_final_v1"),
    "birdhouse": ("Birdhouse", "completion_side_final_v1"),
    "winerack": ("Winerack", "completion_side_final_v1"),
    "paintmaker": ("Paintmaker", "completion_side_final_v1"),
}
NEW_BATCH = ["dvd_player", "2_of_jenga_classic_game", "toaster", "mini_excavator", "3d_dollhouse_sofa",
             "assorted_vegetable_set", "mini_fire_engine", "birdhouse", "winerack", "paintmaker"]


def part_tokens(gen_dir: Path, pid: str):
    gate = json.loads((gen_dir / f"parts/{pid}/GATE.json").read_text())
    ir = Path(gate.get("generated_ir", ""))
    for cand in (ir.parent / "SUMMARY.json",):
        try:
            rows = json.loads(cand.read_text())["rows"]
            for r in rows:
                if r["part"] == pid:
                    return int(r["GENERATED_TOKEN_N"])
        except Exception:
            pass
    try:
        tok = json.loads((ir.parent / f"{pid}_tokens.json").read_text())
        seq = tok if isinstance(tok, list) else tok.get("tokens") or tok.get("generated_tokens")
        return int(len(seq)) if seq is not None else int(tok["GENERATED_TOKEN_N"])
    except Exception:
        return None
MESH_OVERLAY = np.array([0.70, 0.73, 0.76])


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


R = load_module("render_smooth_brep", RENDERER)
A = load_module("audit_brep_surfaces", AUDITOR)
R.W = R.H = 1200


def palette(n):
    return [np.asarray(colorsys.hsv_to_rgb((0.52 + i * 0.618034) % 1.0, 0.50, 0.68)) for i in range(n)]


CAD_NORMAL_SMOOTH_ITERS = {"android_figure_orange": 160, "pressure_cooker": 160}
_cad_smooth_iters = 0


def diffuse_normals(v, f, iters):
    """Display-only: Laplacian diffusion of vertex normals; vertices are never moved."""
    import scipy.sparse as sp

    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    unit_fn = fn / np.clip(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12, None)
    tol = max(float(np.ptp(v, axis=0).max()) * 1e-5, 1e-9)
    _, weld = np.unique(np.round(v / tol).astype(np.int64), axis=0, return_inverse=True)
    weld = weld.ravel()
    f_orig, f = f, weld[f]
    v = np.zeros((weld.max() + 1, 3))
    vn = np.zeros_like(v)
    for k in range(3):
        np.add.at(vn, f[:, k], fn)
    vn /= np.clip(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12, None)
    i = np.concatenate([f[:, 0], f[:, 1], f[:, 2], f[:, 1], f[:, 2], f[:, 0]])
    j = np.concatenate([f[:, 1], f[:, 2], f[:, 0], f[:, 0], f[:, 1], f[:, 2]])
    adj = sp.coo_matrix((np.ones(len(i)), (i, j)), shape=(len(v), len(v))).tocsr()
    adj.data[:] = 1.0
    adj = adj + sp.identity(len(v), format="csr")
    adj = sp.diags(1.0 / np.asarray(adj.sum(axis=1)).ravel()) @ adj
    for _ in range(iters):
        vn = adj @ vn
        vn /= np.clip(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12, None)
    corners = vn[f]
    crease = np.einsum("fkc,fc->fk", corners, unit_fn) < np.cos(np.deg2rad(50.0))
    corners[crease] = np.repeat(unit_fn[:, None, :], 3, axis=1)[crease]
    return corners


def load_cad(path: Path):
    shape = R.read_step(path)
    from OCP.Bnd import Bnd_Box
    from OCP.BRepBndLib import BRepBndLib

    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box)
    x0, y0, z0, x1, y1, z1 = box.Get()
    diag = max(((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5, 1e-9)
    v, f = R.mesh_shape(shape, max(diag * 0.0008, 1e-5), 0.08)
    if _cad_smooth_iters:
        return v, f, diffuse_normals(v, f, _cad_smooth_iters)
    return v, f, R.smooth_corner_normals(v, f, feature_deg=18.0)


def load_mesh(path: Path):
    m = trimesh.load(path, force="mesh", process=False)
    v, f = np.asarray(m.vertices, float), np.asarray(m.faces, np.int64)
    return v, f, R.smooth_corner_normals(v, f, feature_deg=20.0)


def framed(items, fill=0.88):
    allv = np.vstack([it[0] for it in items])
    center, span = R.frame_of(allv)
    old = R.FILL
    R.FILL = fill
    half = R.projected_half(allv, center, span)
    R.FILL = old
    return center, span, half


MESH_WIRE = np.array([0.44, 0.50, 0.55])


def paint(items, frame, mesh_edges=False):
    """items: (v, f, corners, color)."""
    center, span, half = frame
    img, zbuf = R.blank()
    for v, f, c, color in items:
        sx, sy, z = R.paint_surface(img, zbuf, v, f, c, np.asarray(color, float), center, span, half)
        if mesh_edges:
            segs = R.segments_from_indexed_edges(sx, sy, z, R.mesh_edge_index(f))
            R.draw_segments(*segs, img, zbuf, MESH_WIRE, 0, 0.004, 0.02)
    return img, zbuf


def render_items(path: Path, items, frame, mesh_edges=False):
    img, _ = paint(items, frame, mesh_edges)
    R.save_image(path, img)


def render_overlay(path: Path, mesh_items, cad_items, frame, cad_weight=0.5):
    mesh_img, mesh_z = paint(mesh_items, frame)
    cad_img, cad_z = paint(cad_items, frame)
    out = np.empty_like(mesh_img)
    out[:] = R.BG
    both = (mesh_z > -1e29) & (cad_z > -1e29)
    only_m = (mesh_z > -1e29) & ~both
    only_c = (cad_z > -1e29) & ~both
    out[both] = (1 - cad_weight) * mesh_img[both] + cad_weight * cad_img[both]
    out[only_m] = 0.55 * mesh_img[only_m] + 0.45 * R.BG
    out[only_c] = 0.55 * cad_img[only_c] + 0.45 * R.BG
    R.save_image(path, out)


def build(obj: str, label: str, run: str):
    global _cad_smooth_iters
    _cad_smooth_iters = CAD_NORMAL_SMOOTH_ITERS.get(obj, 160 if obj in NEW_BATCH else 0)
    out = OUT / obj
    for d in ("renders", "assembly", "reports"):
        (out / d).mkdir(parents=True, exist_ok=True)
    gen_dir = FULL20 / f"model_v1/generated/{obj}/{run}"
    gate = json.loads((gen_dir / "OBJECT_GATE.json").read_text())
    parts = sorted(p.name for p in (gen_dir / "parts").iterdir() if p.is_dir())
    tokens = {pid: part_tokens(gen_dir, pid) for pid in parts}
    colors = palette(len(parts))

    audit, cad_all, mesh_all = [], [], []
    for i, pid in enumerate(parts):
        step = gen_dir / f"parts/{pid}/part.step"
        hit = re.search(r'"input_mesh": "([^"]+)"', (gen_dir / f"parts/{pid}/GATE.json").read_text())
        mesh_path = Path(hit.group(1)) if hit else FULL20 / f"objects/{obj}/parts/{pid}.obj"
        a = A.audit(step)
        a.update(object=obj, part=pid, role="generated", gate=A.gate(a))
        audit.append(a)
        print(obj, pid, a["BREP_FACE_N"], a["solid_count"], a["surface_types"], a["plane_triangular_face_n"],
              a["DISPLAY_TESSELLATION_TRIANGLE_N"], a["gate"], flush=True)
        cv, cf, cc = load_cad(step)
        mv, mf, mc = load_mesh(mesh_path)
        frame = framed([(cv,), (mv,)])
        render_items(out / f"renders/{pid}_input_mesh.png", [(mv, mf, mc, R.MESH_COLOR)], frame, mesh_edges=True)
        render_items(out / f"renders/{pid}_generated_cad.png", [(cv, cf, cc, colors[i])], frame)
        render_overlay(out / f"renders/{pid}_overlay.png", [(mv, mf, mc, MESH_OVERLAY)], [(cv, cf, cc, colors[i])], frame)
        cad_all.append((cv, cf, cc, colors[i]))
        mesh_all.append((mv, mf, mc, R.MESH_COLOR))

    (out / "reports/audit_rows.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    frame = framed(cad_all + mesh_all)
    render_items(out / "assembly/input_mesh_assembly.png", mesh_all, frame, mesh_edges=False)
    render_items(out / "assembly/generated_cad_assembly.png", cad_all, frame)
    render_overlay(out / "assembly/overlay_assembly.png", [(v, f, c, MESH_OVERLAY) for v, f, c, _ in mesh_all], cad_all, frame)
    compose(out, obj, label, parts, tokens, gate)
    return audit


def compose(out: Path, obj: str, label: str, parts, tokens, gate):
    n = len(parts)
    cols = min(n, 10)
    bands = -(-n // cols)
    fig = plt.figure(figsize=(max(3.1 * cols + 1.2, 13), 4.2 * bands + 7.5), facecolor="white")
    outer = fig.add_gridspec(2, 1, height_ratios=[3 * bands, 2.2 * 1.35], hspace=0.06)
    top = outer[0].subgridspec(3 * bands, cols, hspace=0.12, wspace=0.03)
    bottom = outer[1].subgridspec(1, 3, wspace=0.03)
    for idx, pid in enumerate(parts):
        b, j = divmod(idx, cols)
        for i, (kind, lab) in enumerate((("input_mesh", "Input mesh"), ("generated_cad", "Generated CAD"), ("overlay", "Mesh / CAD overlay"))):
            ax = fig.add_subplot(top[3 * b + i, j])
            ax.imshow(Image.open(out / f"renders/{pid}_{kind}.png"))
            ax.axis("off")
            if i == 0:
                sub = f"\n{tokens[pid]:,} tokens" if tokens[pid] else ""
                ax.set_title(f"{pid}{sub}", fontsize=11 if n <= 8 else 8, fontweight="bold", color="#14222b")
            if j == 0:
                ax.text(-0.05, 0.5, lab, rotation=90, va="center", ha="right", transform=ax.transAxes,
                        fontsize=11, fontweight="bold", color="#14222b")
    for k, (name, lab) in enumerate((("input_mesh", "Input mesh assembly"), ("generated_cad", "Generated CAD assembly"), ("overlay", "Mesh / CAD overlay"))):
        ax = fig.add_subplot(bottom[0, k])
        ax.imshow(Image.open(out / f"assembly/{name}_assembly.png"))
        ax.axis("off")
        ax.set_title(lab, fontsize=13, fontweight="bold", color="#14222b")
    m = gate["metrics"]
    fig.suptitle(f"{label} | Model-generated Mesh-to-CAD ({n}/{n} parts)", fontsize=19, fontweight="bold", color="#14222b", y=0.99)
    fig.text(0.5, 0.012,
             f"q14 + Compact IR V3  |  empty-target greedy  |  no GT prefix  |  natural EOS {gate['natural_eos_n']}/{n}  |  "
             f"CD {m['CD']:.4f}  |  Surface IoU64 {m['IOU']:.3f}  |  Volume error {m['VOLUME_ERROR'] * 100:.2f}%  |  Smooth BRep, no edges",
             ha="center", fontsize=10.5, color="#31434d")
    fig.subplots_adjust(left=0.03, right=0.995, top=0.92, bottom=0.04)
    fig.savefig(out / f"{obj}_part_level_demo.png", dpi=170, facecolor="white")
    fig.savefig(out / f"{obj}_part_level_demo.pdf", facecolor="white")
    plt.close(fig)


def main():
    targets = sys.argv[1:] or list(OBJECTS)
    for obj in targets:
        label, run = OBJECTS[obj]
        build(obj, label, run)
    print("done")


if __name__ == "__main__":
    main()
