#!/usr/bin/env python3
"""Render X-Part CAD overall assembly + exploded views for airplane and tank."""
from __future__ import annotations

import json
import os
import traceback
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

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1")
SRC = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases")
OUT = ROOT / "visualizations" / "assembly"
OUT.mkdir(parents=True, exist_ok=True)

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
        (0.09, 0.75, 0.81),
        (0.68, 0.78, 0.91),
        (1.00, 0.73, 0.47),
        (0.60, 0.87, 0.54),
        (1.00, 0.60, 0.59),
        (0.77, 0.69, 0.84),
        (0.77, 0.61, 0.58),
        (0.97, 0.71, 0.82),
        (0.78, 0.78, 0.78),
        (0.86, 0.86, 0.55),
        (0.62, 0.85, 0.90),
    ],
    dtype=np.float64,
)

BG = [0.93, 0.94, 0.96, 1.0]


def font(size: int) -> ImageFont.ImageFont:
    for p in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def load_source_mesh(path: Path) -> o3d.geometry.TriangleMesh:
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


def tessellate_step(path: Path, tol: float = 0.0008) -> o3d.geometry.TriangleMesh:
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
    return mesh


def clone(mesh: o3d.geometry.TriangleMesh) -> o3d.geometry.TriangleMesh:
    m = o3d.geometry.TriangleMesh()
    m.vertices = o3d.utility.Vector3dVector(np.asarray(mesh.vertices).copy())
    m.triangles = o3d.utility.Vector3iVector(np.asarray(mesh.triangles).copy())
    if mesh.has_vertex_normals():
        m.compute_vertex_normals()
    return m


def colorize(mesh: o3d.geometry.TriangleMesh, rgb) -> o3d.geometry.TriangleMesh:
    m = clone(mesh)
    m.paint_uniform_color(list(map(float, rgb)))
    m.compute_vertex_normals()
    return m


def aabb_of(meshes: list[o3d.geometry.TriangleMesh]):
    pts = [np.asarray(m.vertices) for m in meshes if len(m.vertices) > 0]
    lo = np.min([p.min(0) for p in pts], axis=0)
    hi = np.max([p.max(0) for p in pts], axis=0)
    return lo, hi


def centroid(mesh: o3d.geometry.TriangleMesh) -> np.ndarray:
    v = np.asarray(mesh.vertices)
    return v.mean(axis=0) if len(v) else np.zeros(3)


def explode(meshes: list[o3d.geometry.TriangleMesh], factor: float) -> list[o3d.geometry.TriangleMesh]:
    cents = np.vstack([centroid(m) for m in meshes])
    origin = cents.mean(axis=0)
    out = []
    for mesh, c in zip(meshes, cents):
        mm = clone(mesh)
        mm.translate((c - origin) * factor)
        out.append(mm)
    return out


class Renderer:
    def __init__(self, w=1600, h=1200):
        self.w, self.h = w, h
        self.r = rendering.OffscreenRenderer(w, h)
        self.r.scene.set_background(BG)
        self.r.scene.scene.set_sun_light([-0.45, -0.55, -0.85], [1, 1, 1], 90000)
        self.r.scene.scene.enable_sun_light(True)
        self.mat = rendering.MaterialRecord()
        self.mat.shader = "defaultLit"
        self.names: list[str] = []

    def clear(self):
        for n in self.names:
            try:
                self.r.scene.remove_geometry(n)
            except Exception:
                pass
        self.names = []

    def add(self, name: str, mesh: o3d.geometry.TriangleMesh, rgb=None):
        m = colorize(mesh, rgb) if rgb is not None else mesh
        self.r.scene.add_geometry(name, m, self.mat)
        self.names.append(name)

    def camera(self, meshes, eye_dir, dist_scale=2.35, fov=50.0):
        lo, hi = aabb_of(meshes)
        center = 0.5 * (lo + hi)
        extent = float(np.max(hi - lo) + 1e-9)
        d = np.asarray(eye_dir, dtype=np.float64)
        d = d / (np.linalg.norm(d) + 1e-12)
        eye = center + d * extent * dist_scale
        self.r.setup_camera(float(fov), center, eye, np.array([0.0, 0.0, 1.0]))

    def save(self, path: Path):
        img = self.r.render_to_image()
        o3d.io.write_image(str(path), img, 9)
        print("WROTE", path, flush=True)


def caption(path: Path, text: str) -> None:
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    f = font(28)
    pad = 14
    bbox = draw.textbbox((0, 0), text, font=f)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    bar_h = th + pad * 2
    overlay = Image.new("RGB", (im.width, im.height + bar_h), (237, 239, 244))
    overlay.paste(im, (0, bar_h))
    d = ImageDraw.Draw(overlay)
    d.text((18, pad - 2), text, fill=(28, 32, 40), font=f)
    overlay.save(path, quality=92)


def panel4(paths: list[Path], labels: list[str], title: str, out: Path) -> None:
    imgs = [Image.open(p).convert("RGB") for p in paths]
    w, h = imgs[0].size
    imgs = [im.resize((w, h), Image.Resampling.LANCZOS) if im.size != (w, h) else im for im in imgs]
    gap, header, footer = 18, 56, 36
    canvas = Image.new("RGB", (w * 2 + gap * 3, h * 2 + gap * 3 + header), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 12), title, fill=(24, 28, 36), font=font(32))
    lf = font(18)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        r, c = divmod(i, 2)
        x = gap + c * (w + gap)
        y = header + gap + r * (h + gap)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + h - footer, x + w, y + h], fill=(255, 255, 255))
        draw.text((x + 12, y + h - footer + 8), lab, fill=(50, 55, 64), font=lf)
    canvas.save(out, quality=92)
    print("WROTE", out, flush=True)


def parts_sheet(tiles: list[tuple[Path, str]], out: Path, cols: int, title: str) -> None:
    tile = 320
    header = 44
    cap = 28
    n = len(tiles)
    rows = (n + cols - 1) // cols
    canvas = Image.new("RGB", (cols * tile + 16, header + rows * (tile + cap) + 16), (244, 246, 249))
    draw = ImageDraw.Draw(canvas)
    draw.text((12, 8), title, fill=(24, 28, 36), font=font(26))
    cf = font(13)
    for i, (p, lab) in enumerate(tiles):
        r, c = divmod(i, cols)
        x, y = 8 + c * tile, header + r * (tile + cap)
        im = Image.open(p).convert("RGB")
        im.thumbnail((tile - 10, tile - 10))
        ox = x + (tile - im.width) // 2
        oy = y + (tile - 10 - im.height) // 2
        canvas.paste(im, (ox, oy))
        draw.text((x + 8, y + tile - 8), lab, fill=(40, 45, 54), font=cf)
    canvas.save(out, quality=90)
    print("WROTE", out, flush=True)


def collect_xpart(case: str) -> list[dict]:
    case_dir = ROOT / "cases" / case
    rows = []
    for met in sorted(case_dir.glob("*/metrics.json")):
        d = json.loads(met.read_text())
        src = d.get("source_path", "")
        if "/xpart_parts/" not in src and "xpart_parts" not in d.get("part_id", ""):
            continue
        if "p3_parts" in met.parent.name:
            continue
        step = met.parent / "reconstructed.step"
        if not step.exists():
            continue
        src_path = SRC / src
        if not src_path.exists():
            # tank STL vs airplane OBJ naming
            alt = list((SRC / case / "xpart_parts").glob(f"*{d['part_id'].split('_')[-1]}*"))
            src_path = alt[0] if alt else src_path
        rows.append(
            {
                "part_id": d["part_id"],
                "step": step,
                "source": src_path,
                "iou": float(d.get("iou128") or 0.0),
                "quality": d.get("quality_level", ""),
            }
        )
    rows.sort(key=lambda r: r["part_id"])
    return rows


def render_case(case: str, renderer: Renderer) -> dict:
    rows = collect_xpart(case)
    print(f"\n==== {case} {len(rows)} xpart parts ====", flush=True)
    cad_meshes = []
    src_meshes = []
    info = []
    for i, row in enumerate(rows):
        print(f"  tessellate {row['part_id']} iou={row['iou']:.3f} {row['quality']}", flush=True)
        cad = tessellate_step(row["step"])
        src = load_source_mesh(row["source"])
        cad_meshes.append(cad)
        src_meshes.append(src)
        info.append(row)
        print(f"    cad_tris={len(cad.triangles)} src_tris={len(src.triangles)}", flush=True)

    colors = [PAL[i % len(PAL)] for i in range(len(cad_meshes))]
    factor = 1.25 if case == "airplane" else 0.85
    cad_exp = explode(cad_meshes, factor)
    src_exp = explode(src_meshes, factor)

    views = {
        "hero": ([1.55, -1.85, 1.15], 2.25),
        "side": ([2.4, 0.15, 0.55], 2.35),
    }

    tmp_dir = OUT / f"_{case}_tmp"
    tmp_dir.mkdir(exist_ok=True)
    files = {}

    def shot(key, meshes, rgbs, eye, dist, fov=50.0):
        renderer.clear()
        for j, (m, c) in enumerate(zip(meshes, rgbs)):
            renderer.add(f"{key}_{j}", m, c)
        renderer.camera(meshes, eye, dist, fov)
        p = tmp_dir / f"{key}.png"
        renderer.save(p)
        return p

    src_gray = [(0.62, 0.66, 0.70)] * len(src_meshes)

    files["cad_hero"] = shot("cad_hero", cad_meshes, colors, views["hero"][0], views["hero"][1])
    files["cad_side"] = shot("cad_side", cad_meshes, colors, views["side"][0], views["side"][1])
    files["src_hero"] = shot("src_hero", src_meshes, colors, views["hero"][0], views["hero"][1])
    files["src_side"] = shot("src_side", src_meshes, colors, views["side"][0], views["side"][1])
    files["cad_exp"] = shot("cad_exp", cad_exp, colors, views["hero"][0], 2.15, 48.0)
    files["cad_exp_side"] = shot("cad_exp_side", cad_exp, colors, views["side"][0], 2.25, 48.0)
    files["src_exp"] = shot("src_exp", src_exp, colors, views["hero"][0], 2.15, 48.0)
    files["src_exp_side"] = shot("src_exp_side", src_exp, colors, views["side"][0], 2.25, 48.0)

    hero = OUT / f"{case}_cad_assembly.png"
    Image.open(files["cad_hero"]).save(hero, quality=92)
    caption(hero, f"{case} · X-Part CAD assembly · {len(cad_meshes)} parts")

    exp = OUT / f"{case}_cad_exploded.png"
    Image.open(files["cad_exp"]).save(exp, quality=92)
    caption(exp, f"{case} · exploded CAD parts · factor={factor}")

    panel4(
        [files["src_hero"], files["cad_hero"], files["src_side"], files["cad_side"]],
        ["Source", "CAD", "Source side", "CAD side"],
        f"{case} high-fidelity X-Part · overall assembly · {len(cad_meshes)} parts",
        OUT / f"{case}_source_vs_cad.png",
    )
    panel4(
        [files["src_exp"], files["cad_exp"], files["src_exp_side"], files["cad_exp_side"]],
        ["Source exploded", "CAD exploded", "Source exploded side", "CAD exploded side"],
        f"{case} high-fidelity X-Part · exploded parts · {len(cad_meshes)} parts",
        OUT / f"{case}_exploded_source_vs_cad.png",
    )

    tiles = []
    for i, (mesh, row, col) in enumerate(zip(cad_meshes, info, colors)):
        renderer.clear()
        renderer.add("p", mesh, col)
        renderer.camera([mesh], [1.4, -1.7, 1.2], 2.15, 48.0)
        tp = tmp_dir / f"part_{i:03d}.png"
        renderer.save(tp)
        short = row["part_id"].replace("xpart_parts__", "").replace("__complete_part", "")
        tiles.append((tp, f"{short}  IoU {row['iou']:.2f}"))
    cols = 3 if case == "airplane" else 9
    parts_sheet(
        tiles,
        OUT / f"{case}_parts_sheet.png",
        cols,
        f"{case} · each CAD part",
    )

    return {
        "n": len(cad_meshes),
        "mean_iou": float(np.mean([r["iou"] for r in info])),
        "qualities": {q: sum(1 for r in info if r["quality"] == q) for q in sorted({r["quality"] for r in info})},
        "outputs": [str(hero), str(exp), str(OUT / f"{case}_source_vs_cad.png"), str(OUT / f"{case}_exploded_source_vs_cad.png"), str(OUT / f"{case}_parts_sheet.png")],
    }


def main():
    renderer = Renderer(1400, 1050)
    summary = {}
    for case in ("airplane", "tank"):
        try:
            summary[case] = render_case(case, renderer)
        except Exception:
            traceback.print_exc()
            summary[case] = {"error": traceback.format_exc()[-800:]}
    (OUT / "render_summary.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "error"} for k, v in summary.items()}, indent=2))
    # Avoid Filament abort during interpreter teardown.
    os._exit(0)


if __name__ == "__main__":
    main()
