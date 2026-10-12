#!/usr/bin/env python3
"""Visualize tank_xpart_assembly.step: overall + exploded, colored by solid."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPEN3D_CPU_RENDERING", "true")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mplconfig")

import cadquery as cq
import numpy as np
import open3d as o3d
from open3d.visualization import rendering
from PIL import Image, ImageDraw, ImageFont

STEP = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1/assemblies/tank_xpart_assembly.step")
OUT = Path("/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1/assemblies/viz")
OUT.mkdir(parents=True, exist_ok=True)

PAL = np.array(
    [
        (0.12, 0.47, 0.71), (1.00, 0.50, 0.05), (0.17, 0.63, 0.17), (0.84, 0.15, 0.16),
        (0.58, 0.40, 0.74), (0.55, 0.34, 0.29), (0.89, 0.47, 0.76), (0.50, 0.50, 0.50),
        (0.74, 0.74, 0.13), (0.09, 0.75, 0.81), (0.68, 0.78, 0.91), (1.00, 0.73, 0.47),
        (0.60, 0.87, 0.54), (1.00, 0.60, 0.59), (0.77, 0.69, 0.84), (0.77, 0.61, 0.58),
        (0.97, 0.71, 0.82), (0.78, 0.78, 0.78), (0.86, 0.86, 0.55), (0.62, 0.85, 0.90),
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


def tessellate_shape(shape, tol=0.0008) -> o3d.geometry.TriangleMesh:
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


def explode(meshes, factor=0.85):
    cents = np.vstack([np.asarray(m.vertices).mean(0) for m in meshes])
    origin = cents.mean(0)
    out = []
    for mesh, c in zip(meshes, cents):
        mm = clone(mesh)
        mm.translate((c - origin) * factor)
        out.append(mm)
    return out


def caption(path: Path, text: str):
    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)
    f = font(28)
    bbox = draw.textbbox((0, 0), text, font=f)
    th = bbox[3] - bbox[1]
    bar = th + 28
    out = Image.new("RGB", (im.width, im.height + bar), (237, 239, 244))
    out.paste(im, (0, bar))
    ImageDraw.Draw(out).text((18, 12), text, fill=(28, 32, 40), font=f)
    out.save(path, quality=92)


def main():
    print("loading", STEP, flush=True)
    wp = cq.importers.importStep(str(STEP))
    solids = wp.solids().vals()
    print("solids", len(solids), flush=True)
    meshes = []
    for i, s in enumerate(solids):
        m = tessellate_shape(s)
        print(f"  solid {i:02d} tris={len(m.triangles)} verts={len(m.vertices)}", flush=True)
        meshes.append(m)
    colors = [PAL[i % len(PAL)] for i in range(len(meshes))]

    r = rendering.OffscreenRenderer(1600, 1200)
    r.scene.set_background(BG)
    r.scene.scene.set_sun_light([-0.45, -0.55, -0.85], [1, 1, 1], 90000)
    r.scene.scene.enable_sun_light(True)
    mat = rendering.MaterialRecord()
    mat.shader = "defaultLit"
    names = []

    def clear():
        nonlocal names
        for n in names:
            try:
                r.scene.remove_geometry(n)
            except Exception:
                pass
        names = []

    def add_all(ms, cols):
        clear()
        for i, (m, c) in enumerate(zip(ms, cols)):
            name = f"s{i}"
            r.scene.add_geometry(name, colorize(m, c), mat)
            names.append(name)

    def camera(ms, eye_dir, dist=2.25, fov=50.0):
        lo, hi = aabb(ms)
        center = 0.5 * (lo + hi)
        extent = float(np.max(hi - lo) + 1e-9)
        d = np.asarray(eye_dir, float)
        d = d / (np.linalg.norm(d) + 1e-12)
        eye = center + d * extent * dist
        r.setup_camera(float(fov), center, eye, np.array([0.0, 0.0, 1.0]))

    def save_raw(path):
        img = r.render_to_image()
        o3d.io.write_image(str(path), img, 9)
        print("WROTE", path, flush=True)

    def save(path, title):
        save_raw(path)
        caption(path, title)

    views = [
        ("iso_a", [1.55, -1.85, 1.15], 2.25, 50.0, "3/4 A"),
        ("iso_b", [-1.60, -1.70, 1.20], 2.25, 50.0, "3/4 B"),
        ("iso_c", [1.50, 1.80, 1.10], 2.25, 50.0, "3/4 C"),
        ("iso_d", [-1.50, 1.70, 1.15], 2.25, 50.0, "3/4 D"),
        ("front", [0.05, 1.00, 0.18], 2.40, 48.0, "Front"),
        ("rear", [0.05, -1.00, 0.18], 2.40, 48.0, "Rear"),
        ("side_l", [1.00, 0.05, 0.18], 2.40, 48.0, "Side L"),
        ("side_r", [-1.00, 0.05, 0.18], 2.40, 48.0, "Side R"),
        ("top", [0.12, -0.20, 1.00], 2.55, 42.0, "Top"),
    ]

    add_all(meshes, colors)
    tiles = []
    for name, eye, dist, fov, label in views:
        camera(meshes, eye, dist, fov)
        raw = OUT / f"tank_xpart_assembly_{name}.png"
        save(raw, f"tank_xpart_assembly.step · {label} · {len(meshes)} solids")
        tiles.append((raw, label))

    # contact sheet from uncaptioned frames: re-render raw without bars
    raw_dir = OUT / "_mv_raw"
    raw_dir.mkdir(exist_ok=True)
    raw_tiles = []
    for name, eye, dist, fov, label in views:
        camera(meshes, eye, dist, fov)
        rp = raw_dir / f"{name}.png"
        save_raw(rp)
        raw_tiles.append((rp, label))

    cols, rows_n = 3, 3
    w, h = 640, 480
    gap, header, footer = 14, 52, 32
    canvas = Image.new(
        "RGB",
        (cols * w + (cols + 1) * gap, header + rows_n * (h + footer) + (rows_n + 1) * gap),
        (244, 246, 249),
    )
    draw = ImageDraw.Draw(canvas)
    draw.text((gap, 10), f"tank_xpart_assembly.step · 9 views · {len(meshes)} solids", fill=(24, 28, 36), font=font(30))
    lf = font(18)
    for i, (p, lab) in enumerate(raw_tiles):
        rr, cc = divmod(i, cols)
        x = gap + cc * (w + gap)
        y = header + gap + rr * (h + footer + gap)
        im = Image.open(p).convert("RGB").resize((w, h), Image.Resampling.LANCZOS)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + h, x + w, y + h + footer], fill=(255, 255, 255))
        draw.text((x + 10, y + h + 6), lab, fill=(50, 55, 64), font=lf)
    sheet = OUT / "tank_xpart_assembly_multiview.png"
    canvas.save(sheet, quality=92)
    print("WROTE", sheet, flush=True)

    bronze = [(0.72, 0.58, 0.38)] * len(meshes)
    add_all(meshes, bronze)
    camera(meshes, [1.55, -1.85, 1.15], 2.25)
    save(OUT / "tank_xpart_assembly_shaded.png", f"tank_xpart_assembly.step · shaded · {len(meshes)} solids")
    camera(meshes, [0.12, -0.20, 1.00], 2.55, 42.0)
    save(OUT / "tank_xpart_assembly_shaded_top.png", f"tank_xpart_assembly.step · shaded top · {len(meshes)} solids")
    camera(meshes, [0.05, 1.00, 0.18], 2.40, 48.0)
    save(OUT / "tank_xpart_assembly_shaded_front.png", f"tank_xpart_assembly.step · shaded front · {len(meshes)} solids")

    exp = explode(meshes, 0.85)
    add_all(exp, colors)
    camera(exp, [1.55, -1.85, 1.15], 2.15, 48.0)
    save(OUT / "tank_xpart_assembly_exploded.png", f"tank_xpart_assembly.step · exploded · {len(meshes)} solids")

    import shutil
    shutil.rmtree(raw_dir, ignore_errors=True)
    os._exit(0)


if __name__ == "__main__":
    main()
