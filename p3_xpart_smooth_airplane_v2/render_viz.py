#!/usr/bin/env python3
"""Overall + per-part CAD visualization for smooth airplane v2."""
from __future__ import annotations

import json
import os
import shutil
from multiprocessing import Process, Queue
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

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2")
SRC = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/airplane/xpart_parts")
OUT = ROOT / "visualizations"
TMP = OUT / "_tmp"
OUT.mkdir(parents=True, exist_ok=True)
TMP.mkdir(exist_ok=True)

KEPT = {"PART_000", "PART_002", "PART_003", "PART_005", "PART_008"}
PAL = np.array(
    [
        (0.12, 0.47, 0.71),
        (1.00, 0.50, 0.05),
        (0.17, 0.63, 0.17),
        (0.84, 0.15, 0.16),
        (0.58, 0.40, 0.74),
        (0.55, 0.34, 0.29),
        (0.89, 0.47, 0.76),
        (0.50, 0.50, 0.50),
        (0.74, 0.74, 0.13),
    ],
    dtype=np.float64,
)
BG = [0.93, 0.94, 0.96, 1.0]


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


def explode(meshes, factor=1.25):
    cents = np.vstack([np.asarray(m.vertices).mean(0) for m in meshes])
    origin = cents.mean(0)
    out = []
    for mesh, c in zip(meshes, cents):
        mm = clone(mesh)
        mm.translate((c - origin) * factor)
        out.append(mm)
    return out


def cap_tris(mesh, nmax=160000):
    n = len(mesh.triangles)
    if n <= nmax:
        return mesh
    try:
        simplified = mesh.simplify_quadric_decimation(target_number_of_triangles=int(nmax))
        simplified.compute_vertex_normals()
        return simplified
    except Exception:
        return mesh


def bbox_mesh(bbox) -> o3d.geometry.TriangleMesh:
    lo = np.asarray(bbox[:3], dtype=np.float64)
    hi = np.asarray(bbox[3:], dtype=np.float64)
    size = np.maximum(hi - lo, 1e-6)
    mesh = o3d.geometry.TriangleMesh.create_box(float(size[0]), float(size[1]), float(size[2]))
    mesh.translate(lo)
    mesh.compute_vertex_normals()
    return mesh


def _tess_worker(path: str, tol: float, q: Queue):
    import cadquery as cq  # local import keeps spawn/fork workers independent
    wp = cq.importers.importStep(path)
    shape = wp.val()
    verts, faces = shape.tessellate(tol)
    v = np.array([[float(p.x), float(p.y), float(p.z)] for p in verts], dtype=np.float64)
    f = np.array([[int(a), int(b), int(c)] for a, b, c in faces], dtype=np.int32)
    q.put((v, f))


def tessellate_step(path: Path, extent: float, bbox) -> tuple:
    if float(extent) > 8.0:
        print("    skip STEP tessellate (scale fail) → bbox proxy", flush=True)
        return bbox_mesh(bbox), True
    tol = max(0.0018, float(extent) * 0.006)
    print(f"    tessellate in-process tol={tol:.5g}", flush=True)
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
    print(f"    raw_tris={len(mesh.triangles)}", flush=True)
    return cap_tris(mesh, 160000), False


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
    return cap_tris(mesh, 120000)


def caption(path: Path, text: str):
    im = Image.open(path).convert("RGB")
    f = font(26)
    draw = ImageDraw.Draw(im)
    bbox = draw.textbbox((0, 0), text, font=f)
    bar = (bbox[3] - bbox[1]) + 26
    out = Image.new("RGB", (im.width, im.height + bar), (237, 239, 244))
    out.paste(im, (0, bar))
    ImageDraw.Draw(out).text((16, 10), text, fill=(28, 32, 40), font=f)
    out.save(path, quality=92)


def panel4(paths, labels, title, out):
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w, h = imgs[0].size
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    gap, header, footer = 16, 52, 34
    canvas = Image.new("RGB", (w * 2 + gap * 3, h * 2 + gap * 3 + header), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 10), title, fill=(24, 28, 36), font=font(28))
    lf = font(18)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        r, c = divmod(i, 2)
        x = gap + c * (w + gap)
        y = header + gap + r * (h + gap)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + h - footer, x + w, y + h], fill=(255, 255, 255))
        draw.text((x + 10, y + h - footer + 6), lab, fill=(50, 55, 64), font=lf)
    canvas.save(out, quality=92)
    print("WROTE", out, flush=True)


class Renderer:
    def __init__(self, w=1400, h=1050):
        self.r = rendering.OffscreenRenderer(w, h)
        self.r.scene.set_background(BG)
        self.r.scene.scene.set_sun_light([-0.45, -0.55, -0.85], [1, 1, 1], 90000)
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

    def camera(self, meshes, eye_dir, dist=2.25, fov=50.0):
        lo, hi = aabb(meshes)
        center = 0.5 * (lo + hi)
        extent = float(np.max(hi - lo) + 1e-9)
        d = np.asarray(eye_dir, float)
        d = d / (np.linalg.norm(d) + 1e-12)
        self.r.setup_camera(float(fov), center, center + d * extent * dist, np.array([0.0, 0.0, 1.0]))

    def save(self, path):
        o3d.io.write_image(str(path), self.r.render_to_image(), 9)
        print("WROTE", path, flush=True)


def collect():
    rows = []
    for i, d in enumerate(sorted((ROOT / "parts").glob("PART_*"), key=lambda p: int(p.name.split("_")[1]))):
        pid = f"PART_{i:03d}"
        g = json.loads((d / "geometry.json").read_text()) if (d / "geometry.json").exists() else {}
        bbox = g.get("bbox") or [0, 0, 0, 1, 1, 1]
        extent = float(max(bbox[3] - bbox[0], bbox[4] - bbox[1], bbox[5] - bbox[2]))
        met = json.loads((d / "original_metrics.json").read_text()) if (d / "original_metrics.json").exists() else {}
        src = SRC / pid / f"complete_part_{i:03d}.obj"
        rows.append(
            {
                "i": i,
                "pid": pid,
                "dir": d,
                "step": d / "reconstructed.step",
                "src": src,
                "keep": pid in KEPT,
                "extent": extent,
                "bbox": bbox,
                "faces": g.get("faces"),
                "iou": float(met.get("iou128") or 0.0),
                "color": PAL[i % len(PAL)],
            }
        )
    return rows


def shot(rnd, meshes, colors, path, eye, dist=2.25, fov=50.0):
    rnd.clear()
    for j, (m, c) in enumerate(zip(meshes, colors)):
        rnd.add(f"g{j}", m, c)
    rnd.camera(meshes, eye, dist, fov)
    rnd.save(path)
    return path


def main():
    rows = collect()
    hero = [1.55, -1.85, 1.15]
    side = [2.4, 0.15, 0.55]

    for row in rows:
        print(f"load {row['pid']} keep={row['keep']} extent={row['extent']:.3g} iou={row['iou']:.3f}", flush=True)
        row["cad"], row["bbox_proxy"] = tessellate_step(row["step"], row["extent"], row["bbox"])
        row["src_mesh"] = load_source(row["src"])
        print(
            f"  cad_tris={len(row['cad'].triangles)} src_tris={len(row['src_mesh'].triangles)} proxy={row['bbox_proxy']}",
            flush=True,
        )

    rnd = Renderer()

    kept = [r for r in rows if r["keep"]]
    kcad = [r["cad"] for r in kept]
    ksrc = [r["src_mesh"] for r in kept]
    kcol = [r["color"] for r in kept]

    p_hero = shot(rnd, kcad, kcol, TMP / "cad_hero.png", hero, 1.72, 48.0)
    p_side = shot(rnd, kcad, kcol, TMP / "cad_side.png", side, 1.78, 48.0)
    p_src_h = shot(rnd, ksrc, kcol, TMP / "src_hero.png", hero, 1.72, 48.0)
    p_src_s = shot(rnd, ksrc, kcol, TMP / "src_side.png", side, 1.78, 48.0)
    exp = explode(kcad, 1.15)
    sexp = explode(ksrc, 1.15)
    p_exp = shot(rnd, exp, kcol, TMP / "cad_exp.png", hero, 1.62, 46.0)
    p_sexp = shot(rnd, sexp, kcol, TMP / "src_exp.png", hero, 1.62, 46.0)
    p_exp_s = shot(rnd, exp, kcol, TMP / "cad_exp_side.png", side, 1.68, 46.0)
    p_sexp_s = shot(rnd, sexp, kcol, TMP / "src_exp_side.png", side, 1.68, 46.0)

    hero_out = OUT / "airplane_cad_assembly.png"
    Image.open(p_hero).save(hero_out, quality=92)
    caption(hero_out, f"smooth airplane v2 · CAD assembly · kept {len(kept)}/9")
    exp_out = OUT / "airplane_cad_exploded.png"
    Image.open(p_exp).save(exp_out, quality=92)
    caption(exp_out, f"smooth airplane v2 · exploded CAD · kept {len(kept)}/9")

    panel4(
        [p_src_h, p_hero, p_src_s, p_side],
        ["Source", "CAD", "Source side", "CAD side"],
        f"smooth airplane v2 · overall assembly · kept {len(kept)}/9",
        OUT / "airplane_source_vs_cad.png",
    )
    panel4(
        [p_sexp, p_exp, p_sexp_s, p_exp_s],
        ["Source exploded", "CAD exploded", "Source exploded side", "CAD exploded side"],
        f"smooth airplane v2 · exploded parts · kept {len(kept)}/9",
        OUT / "airplane_exploded_source_vs_cad.png",
    )

    tiles = []
    for row in rows:
        rnd.clear()
        rnd.add("p", row["cad"], row["color"])
        rnd.camera([row["cad"]], [1.4, -1.7, 1.2], 1.62, 46.0)
        tp = TMP / f"{row['pid']}_cad.png"
        rnd.save(tp)
        captioned = OUT / f"{row['pid']}_cad.png"
        Image.open(tp).save(captioned, quality=92)
        tag = "kept" if row["keep"] else "scale-drop"
        if row["bbox_proxy"]:
            tag += " · bbox-proxy"
        caption(captioned, f"{row['pid']}  CAD  IoU {row['iou']:.3f}  {row['faces']} faces  {tag}")
        tiles.append((tp, f"{row['pid']}  {row['iou']:.2f}  {'OK' if row['keep'] else 'DROP'}"))

        rnd.clear()
        rnd.add("s", row["src_mesh"], row["color"])
        rnd.camera([row["src_mesh"]], [1.4, -1.7, 1.2], 1.62, 46.0)
        sp = TMP / f"{row['pid']}_src.png"
        rnd.save(sp)
        rnd.clear()
        rnd.add("c", row["cad"], row["color"])
        rnd.camera([row["cad"]], [1.4, -1.7, 1.2], 1.62, 46.0)
        pair = Image.new("RGB", (1400 * 2 + 24, 1050 + 48), (244, 246, 249))
        pair.paste(Image.open(sp).convert("RGB").resize((1400, 1050)), (12, 40))
        pair.paste(Image.open(tp).convert("RGB").resize((1400, 1050)), (1412, 40))
        d = ImageDraw.Draw(pair)
        d.text((20, 8), f"{row['pid']}  source vs CAD  IoU={row['iou']:.3f}", fill=(24, 28, 36), font=font(24))
        pair.save(OUT / f"{row['pid']}_source_vs_cad.png", quality=90)

    cols, tile, header, cap_h = 3, 420, 48, 36
    rows_n = (len(tiles) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tile + 16, header + rows_n * (tile + cap_h) + 16), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), "smooth airplane v2 · each CAD part", fill=(24, 28, 36), font=font(26))
    cf = font(14)
    for i, (p, lab) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = 8 + c * tile, header + r * (tile + cap_h)
        im = Image.open(p).convert("RGB")
        im.thumbnail((tile - 12, tile - 12))
        canvas.paste(im, (x + (tile - im.width) // 2, y + (tile - 12 - im.height) // 2))
        draw.text((x + 8, y + tile - 10), lab, fill=(40, 45, 54), font=cf)
    sheet = OUT / "airplane_parts_sheet.png"
    canvas.save(sheet, quality=90)
    print("WROTE", sheet, flush=True)

    shutil.rmtree(TMP, ignore_errors=True)
    os._exit(0)


if __name__ == "__main__":
    main()
