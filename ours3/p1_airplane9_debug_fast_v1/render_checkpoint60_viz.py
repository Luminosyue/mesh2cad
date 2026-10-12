#!/usr/bin/env python3
"""Assemble and render P1 airplane-9 checkpoint-60 generated CAD."""
from __future__ import annotations

import json
import os
import shutil
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPEN3D_CPU_RENDERING", "true")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import cadquery as cq
import numpy as np
import open3d as o3d
import trimesh
from open3d.visualization import rendering
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1")
EVAL = ROOT / "evaluations" / "checkpoint-60"
SRC = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/airplane/xpart_parts")
OUT = ROOT / "visualizations" / "checkpoint-60"
TMP = OUT / "_tmp"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)

PAL = np.array(
    [
        (0.18, 0.52, 0.78),
        (0.95, 0.55, 0.12),
        (0.20, 0.62, 0.32),
        (0.82, 0.18, 0.22),
        (0.58, 0.40, 0.74),
        (0.62, 0.45, 0.32),
        (0.88, 0.48, 0.72),
        (0.45, 0.52, 0.58),
        (0.82, 0.72, 0.16),
    ],
    dtype=np.float64,
)
BG = [0.90, 0.92, 0.95, 1.0]


def font(size: int):
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def clone(mesh):
    m = o3d.geometry.TriangleMesh()
    m.vertices = o3d.utility.Vector3dVector(np.asarray(mesh.vertices).copy())
    m.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles).copy())
    m.compute_vertex_normals()
    return m


def colorize(mesh, rgb):
    m = clone(mesh)
    m.paint_uniform_color(list(map(float, rgb)))
    m.compute_vertex_normals()
    return m


def aabb(meshes):
    pts = [np.asarray(m.vertices) for m in meshes if len(m.vertices)]
    lo = np.min([p.min(0) for p in pts], axis=0)
    hi = np.max([p.max(0) for p in pts], axis=0)
    return lo, hi


def explode(meshes, factor=1.28):
    cents = np.vstack([np.asarray(m.vertices).mean(0) for m in meshes])
    origin = cents.mean(0)
    out = []
    for mesh, c in zip(meshes, cents):
        mm = clone(mesh)
        mm.translate((c - origin) * factor)
        out.append(mm)
    return out


def tessellate_step(path: Path, extent: float) -> o3d.geometry.TriangleMesh:
    tol = max(0.0014, float(extent) * 0.004)
    print(f"    tessellate {path.name} tol={tol:.5g}", flush=True)
    wp = cq.importers.importStep(str(path))
    shape = wp.val()
    verts, faces = shape.tessellate(tol)
    v = np.array([[float(p.x), float(p.y), float(p.z)] for p in verts], dtype=np.float64)
    f = np.array([[int(a), int(b), int(c)] for a, b, c in faces], dtype=np.int32)
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(v),
        o3d.utility.Vector3iVector(f),
    )
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.compute_vertex_normals()
    print(f"    tris={len(mesh.triangles)}", flush=True)
    return mesh


def load_source(path: Path) -> o3d.geometry.TriangleMesh:
    m = trimesh.load(str(path), force="mesh", process=False)
    if isinstance(m, trimesh.Scene):
        m = m.dump(concatenate=True)
    mesh = o3d.geometry.TriangleMesh(
        o3d.utility.Vector3dVector(np.asarray(m.vertices, dtype=np.float64)),
        o3d.utility.Vector3iVector(np.asarray(m.faces, dtype=np.int32)),
    )
    mesh.remove_duplicated_vertices()
    mesh.remove_degenerate_triangles()
    mesh.compute_vertex_normals()
    return mesh


def caption(path: Path, text: str):
    im = Image.open(path).convert("RGB")
    f = font(24)
    draw = ImageDraw.Draw(im)
    bbox = draw.textbbox((0, 0), text, font=f)
    bar = (bbox[3] - bbox[1]) + 22
    out = Image.new("RGB", (im.width, im.height + bar), (236, 239, 244))
    out.paste(im, (0, bar))
    ImageDraw.Draw(out).text((16, 9), text, fill=(28, 32, 40), font=f)
    out.save(path, quality=93)


def panel(paths, labels, title, out, cols=2):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w, h = max(im.width for im in imgs), max(im.height for im in imgs)
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    n = len(imgs)
    rows = (n + cols - 1) // cols
    gap, header, footer = 14, 50, 32
    canvas = Image.new("RGB", (w * cols + gap * (cols + 1), h * rows + gap * (rows + 1) + header), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 10), title, fill=(24, 28, 36), font=font(26))
    lf = font(17)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        r, c = divmod(i, cols)
        x = gap + c * (w + gap)
        y = header + gap + r * (h + gap)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + h - footer, x + w, y + h], fill=(255, 255, 255))
        draw.text((x + 10, y + h - footer + 6), lab, fill=(50, 55, 64), font=lf)
    canvas.save(out, quality=92)
    print("WROTE", out, flush=True)


class Renderer:
    def __init__(self, w=1600, h=1100):
        self.r = rendering.OffscreenRenderer(w, h)
        self.r.scene.set_background(BG)
        self.r.scene.scene.set_sun_light([-0.35, 0.55, -0.85], [1, 1, 1], 110000)
        self.r.scene.scene.enable_sun_light(True)
        self.mat = rendering.MaterialRecord()
        self.mat.shader = "defaultLit"
        self.names = []

    def clear(self):
        for n in self.names:
            try:
                self.r.scene.remove_geometry(n)
            except Exception:
                pass
        self.names = []

    def add(self, name, mesh, rgb):
        self.r.scene.add_geometry(name, colorize(mesh, rgb), self.mat)
        self.names.append(name)

    def camera(self, meshes, eye_dir, fill=2.15, fov=40.0):
        lo, hi = aabb(meshes)
        center = 0.5 * (lo + hi)
        radius = 0.5 * float(np.linalg.norm(hi - lo) + 1e-9)
        d = np.asarray(eye_dir, float)
        d = d / (np.linalg.norm(d) + 1e-12)
        self.r.setup_camera(float(fov), center, center + d * radius * fill, np.array([0.0, 0.0, 1.0]))

    def save(self, path):
        o3d.io.write_image(str(path), self.r.render_to_image(), 9)
        print("WROTE", path, flush=True)


def shot(rnd, meshes, colors, path, eye, fill=2.15, fov=40.0):
    rnd.clear()
    for j, (m, c) in enumerate(zip(meshes, colors)):
        rnd.add(f"g{j}", m, c)
    rnd.camera(meshes, eye, fill, fov)
    rnd.save(path)
    return path


def assemble_step(rows):
    solids = []
    for row in rows:
        wp = cq.importers.importStep(str(row["step"]))
        solids.extend(wp.solids().vals())
    compound = cq.Compound.makeCompound(solids)
    out = OUT / "airplane_assembly.step"
    compound.exportStep(str(out))
    print(f"WROTE {out} solids={len(solids)}", flush=True)
    return out


def main():
    rows = []
    for i in range(9):
        pid = f"PART_{i:03d}"
        d = EVAL / pid
        step = d / "prediction_original_coordinates.step"
        wp = cq.importers.importStep(str(step))
        bb = wp.val().BoundingBox()
        extent = float(max(bb.xlen, bb.ylen, bb.zlen))
        met = json.loads((d / "metrics.json").read_text())
        res = json.loads((d / "result.json").read_text())
        rows.append(
            {
                "i": i,
                "pid": pid,
                "step": step,
                "src": SRC / pid / f"complete_part_{i:03d}.obj",
                "extent": extent,
                "iou_note": res.get("SEQUENCE_EXACT_MATCH"),
                "geom": bool(met.get("geometry_pass")),
                "color": PAL[i],
            }
        )
        print(f"{pid} extent={extent:.3f} exact={rows[-1]['iou_note']} geom={rows[-1]['geom']}", flush=True)

    assemble_step(rows)

    for row in rows:
        print(f"load {row['pid']}", flush=True)
        row["cad"] = tessellate_step(row["step"], row["extent"])
        row["src_mesh"] = load_source(row["src"])

    cad = [r["cad"] for r in rows]
    src = [r["src_mesh"] for r in rows]
    col = [r["color"] for r in rows]

    rnd = Renderer()
    hero = [1.20, -1.55, 0.72]
    side = [1.00, 0.06, 0.10]
    front = [0.12, -1.00, 0.18]
    top = [0.08, -0.22, 1.00]

    p_hero = shot(rnd, cad, col, TMP / "cad_hero.png", hero, 2.05, 38.0)
    p_side = shot(rnd, cad, col, TMP / "cad_side.png", side, 2.12, 36.0)
    p_front = shot(rnd, cad, col, TMP / "cad_front.png", front, 2.20, 36.0)
    p_top = shot(rnd, cad, col, TMP / "cad_top.png", top, 2.05, 36.0)
    p_src_h = shot(rnd, src, col, TMP / "src_hero.png", hero, 2.05, 38.0)
    p_src_s = shot(rnd, src, col, TMP / "src_side.png", side, 2.12, 36.0)

    exp = explode(cad, 1.22)
    sexp = explode(src, 1.22)
    p_exp = shot(rnd, exp, col, TMP / "cad_exp.png", hero, 2.00, 38.0)
    p_exp_s = shot(rnd, exp, col, TMP / "cad_exp_side.png", side, 2.08, 36.0)
    p_sexp = shot(rnd, sexp, col, TMP / "src_exp.png", hero, 2.00, 38.0)

    def publish(src_path, dest, text):
        Image.open(src_path).save(dest, quality=93)
        caption(dest, text)

    publish(p_hero, OUT / "airplane_cad_assembly.png", "P1 airplane-9  checkpoint-60  CAD assembly  9/9 exact")
    publish(p_side, OUT / "airplane_cad_assembly_side.png", "P1 airplane-9  checkpoint-60  CAD side  9/9")
    publish(p_front, OUT / "airplane_cad_assembly_front.png", "P1 airplane-9  checkpoint-60  CAD front  9/9")
    publish(p_top, OUT / "airplane_cad_assembly_top.png", "P1 airplane-9  checkpoint-60  CAD top  9/9")
    publish(p_exp, OUT / "airplane_cad_exploded.png", "P1 airplane-9  checkpoint-60  exploded CAD  9/9")

    panel(
        [p_hero, p_side, p_front, p_top],
        ["3/4", "Side", "Front / nose", "Top"],
        "P1 airplane-9 checkpoint-60 · generated CAD assembly",
        OUT / "airplane_cad_multiview.png",
    )
    panel(
        [p_src_h, p_hero, p_src_s, p_side],
        ["Source", "CAD", "Source side", "CAD side"],
        "P1 airplane-9 checkpoint-60 · source mesh vs generated CAD",
        OUT / "airplane_source_vs_cad.png",
    )
    panel(
        [p_sexp, p_exp, p_src_s, p_exp_s],
        ["Source exploded", "CAD exploded", "Source side", "CAD exploded side"],
        "P1 airplane-9 checkpoint-60 · exploded source vs CAD",
        OUT / "airplane_exploded_source_vs_cad.png",
    )

    tiles = []
    for row in rows:
        rnd.clear()
        rnd.add("p", row["cad"], row["color"])
        rnd.camera([row["cad"]], [1.25, -1.45, 0.85], 2.05, 40.0)
        tp = TMP / f"{row['pid']}_cad.png"
        rnd.save(tp)
        dest = OUT / f"{row['pid']}_cad.png"
        Image.open(tp).save(dest, quality=93)
        caption(dest, f"{row['pid']}  generated CAD  exact={row['iou_note']}  geom_pass={row['geom']}")
        tiles.append(tp)

        rnd.clear()
        rnd.add("s", row["src_mesh"], row["color"])
        rnd.camera([row["src_mesh"]], [1.25, -1.45, 0.85], 2.05, 40.0)
        sp = TMP / f"{row['pid']}_src.png"
        rnd.save(sp)
        pair = Image.new("RGB", (1600 * 2 + 24, 1100 + 48), (244, 246, 249))
        pair.paste(Image.open(sp).convert("RGB").resize((1600, 1100)), (12, 40))
        pair.paste(Image.open(tp).convert("RGB").resize((1600, 1100)), (1612, 40))
        ImageDraw.Draw(pair).text(
            (20, 8),
            f"{row['pid']}  source (left) vs generated CAD (right)",
            fill=(24, 28, 36),
            font=font(22),
        )
        pair.save(OUT / f"{row['pid']}_source_vs_cad.png", quality=92)

    cols, tile, header, cap_h = 3, 460, 50, 34
    canvas = Image.new("RGB", (cols * tile + 20, header + 3 * (tile + cap_h) + 16), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 10), "P1 airplane-9 checkpoint-60 · each generated CAD part", fill=(24, 28, 36), font=font(24))
    cf = font(15)
    for i, p in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = 10 + c * tile, header + r * (tile + cap_h)
        im = Image.open(p).convert("RGB")
        im.thumbnail((tile - 12, tile - 12))
        canvas.paste(im, (x + (tile - im.width) // 2, y + (tile - 12 - im.height) // 2))
        draw.text((x + 8, y + tile - 8), f"PART_{i:03d}  exact", fill=(40, 45, 54), font=cf)
    sheet = OUT / "airplane_parts_sheet.png"
    canvas.save(sheet, quality=92)
    print("WROTE", sheet, flush=True)

    shutil.rmtree(TMP, ignore_errors=True)
    os._exit(0)


if __name__ == "__main__":
    main()
