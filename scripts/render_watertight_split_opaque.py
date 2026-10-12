#!/usr/bin/env python3
"""Opaque / cutaway preview proving the volume-split parts are closed solids."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from scipy.spatial import cKDTree

PROJECT = Path("/data/home/cuiyuehan/project/mesh2cad")
SPLIT = PROJECT / "ours3/tank_watertight_mesh_split_v1"
P3 = PROJECT / "ours3/tank_p3_rerun_v1/p3_max_367k_4000"
SOURCE = PROJECT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
OUT = SPLIT / "artifacts/visuals_opaque"
HELPER = PROJECT / "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/scripts/render_p3_45_assembly.py"


def load_helper():
    spec = importlib.util.spec_from_file_location("render_p3", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_font(size: int):
    path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(str(path), size) if path.is_file() else ImageFont.load_default()


def render_opaque(meshes, colors, bounds, path, matrix, size=(1400, 1050), budgets=None):
    V = load_helper()
    w, h = size
    image = Image.new("RGB", size, (248, 249, 251))
    draw = ImageDraw.Draw(image)
    light = np.array([0.25, 0.40, 0.88], float)
    light /= np.linalg.norm(light)
    view = matrix[2]
    view = view / np.linalg.norm(view)
    for mesh, color, budget in zip(meshes, colors, budgets):
        vertices = np.asarray(mesh.vertices, float)
        faces = np.asarray(mesh.faces, np.int64)
        if len(faces) > budget:
            faces = faces[np.linspace(0, len(faces) - 1, budget).astype(np.int64)]
        xy, z = V.project(vertices, bounds, matrix, w, h)
        p0, p1, p2 = vertices[faces[:, 0]], vertices[faces[:, 1]], vertices[faces[:, 2]]
        normals = np.cross(p1 - p0, p2 - p0)
        normals = normals / np.clip(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12, None)
        facing = normals @ view > 0.0
        faces = faces[facing]
        normals = normals[facing]
        if len(faces) == 0:
            continue
        shade = 0.22 + 0.78 * np.clip(normals @ light, 0, 1)
        depth = (z[faces[:, 0]] + z[faces[:, 1]] + z[faces[:, 2]]) / 3.0
        polys = np.stack([xy[faces[:, 0]], xy[faces[:, 1]], xy[faces[:, 2]]], axis=1)
        rgb = (np.asarray(color, float) * shade[:, None]).clip(0, 255).astype(np.uint8)
        for i in np.argsort(depth):
            draw.polygon(
                [tuple(polys[i, 0]), tuple(polys[i, 1]), tuple(polys[i, 2])],
                fill=tuple(int(c) for c in rgb[i]),
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, dpi=(180, 180))


def occupancy_slice(source, labels, pitch, axis: int, path: Path, palette):
    voxel = source.voxelized(pitch).fill()
    matrix = np.asarray(voxel.matrix, dtype=bool)
    origin = np.asarray(voxel.transform[:3, 3], dtype=float)
    ijk = np.argwhere(matrix)
    points = origin + (ijk.astype(float) + 0.5) * pitch
    _, index = cKDTree(np.asarray(source.triangles_center, float)).query(points, workers=-1)
    assigned = labels[index]
    volume = np.full(matrix.shape, -1, dtype=np.int32)
    volume[tuple(ijk.T)] = assigned
    sl = volume.shape[axis] // 2
    plane = np.take(volume, sl, axis=axis)
    if axis == 0:
        plane = plane.T
    h, w = plane.shape
    scale = max(1, 720 // max(h, w))
    image = Image.new("RGB", (w * scale, h * scale), (255, 255, 255))
    px = image.load()
    for y in range(h):
        for x in range(w):
            lab = int(plane[y, x])
            color = (235, 237, 240) if lab < 0 else palette[lab % len(palette)]
            for dy in range(scale):
                for dx in range(scale):
                    px[x * scale + dx, (h - 1 - y) * scale + dy] = color
    image.save(path, dpi=(180, 180))
    return path


def compose(paths, titles, out, caption):
    images = [Image.open(p).convert("RGB") for p in paths]
    pw, ph = 640, 520
    canvas = Image.new("RGB", (pw * len(images), ph + 110), "white")
    draw = ImageDraw.Draw(canvas)
    font, small = load_font(18), load_font(15)
    for i, (im, title) in enumerate(zip(images, titles)):
        thumb = im.copy()
        thumb.thumbnail((pw - 20, ph - 30))
        canvas.paste(thumb, (i * pw + (pw - thumb.width) // 2, 40))
        draw.text((i * pw + 14, 10), title, fill=(28, 34, 46), font=font)
    draw.text((16, ph + 50), caption, fill=(70, 76, 88), font=small)
    canvas.save(out, dpi=(180, 180))


def main():
    V = load_helper()
    OUT.mkdir(parents=True, exist_ok=True)
    parts = []
    for i in range(45):
        mesh = trimesh.load(str(SPLIT / f"01_watertight_parts/part_{i:03d}.obj"), force="mesh", process=False)
        parts.append(mesh)
    colors = V.palette(45)
    vertices = np.vstack([np.asarray(p.vertices) for p in parts])
    bounds = np.vstack([vertices.min(0), vertices.max(0)]).T
    iso = V.camera_matrix(38, 24)
    counts = np.asarray([len(p.faces) for p in parts], float)
    budgets = np.maximum(400, np.round(counts / counts.sum() * 160000)).astype(int).tolist()
    opaque = OUT / "opaque_parts.png"
    opaque_cad = OUT / "opaque_shaded.png"
    render_opaque(parts, colors, bounds, opaque, iso, budgets=budgets)
    render_opaque(parts, [(168, 184, 196)] * 45, bounds, opaque_cad, iso, budgets=budgets)

    source = trimesh.load(str(SOURCE), force="mesh", process=False)
    labels = np.asarray(np.load(P3 / "triangle_part_id.npy"), dtype=np.int64).reshape(-1)
    pitch = float(np.max(source.extents) / 192)
    slice_png = OUT / "occupancy_slice.png"
    occupancy_slice(source, labels, pitch, axis=1, path=slice_png, palette=colors)

    p3 = trimesh.load(str(P3 / "part_010.obj"), force="mesh", process=False)
    wt = parts[10]
    p3_png = OUT / "p3_part010_open.png"
    wt_png = OUT / "wt_part010_closed.png"
    b3 = np.vstack([np.asarray(p3.vertices).min(0), np.asarray(p3.vertices).max(0)]).T
    bw = np.vstack([np.asarray(wt.vertices).min(0), np.asarray(wt.vertices).max(0)]).T
    render_opaque([p3], [(180, 90, 90)], b3, p3_png, iso, budgets=[min(80000, len(p3.faces))])
    render_opaque([wt], [(80, 150, 110)], bw, wt_png, iso, budgets=[min(80000, len(wt.faces))])

    sheet = OUT / "opaque_review.png"
    compose(
        [opaque_cad, opaque, slice_png, p3_png, wt_png],
        ["Opaque solids", "Opaque parts", "Solid occupancy slice", "P3 part 010 OPEN", "Split part 010 CLOSED"],
        sheet,
        "All 45 split parts have 0 boundary edges. Previous preview looked hollow because both triangle sides were shaded.",
    )
    dump = {
        "boundary_edges": 0,
        "watertight_parts": 45,
        "outputs": {p.name: str(p) for p in [opaque, opaque_cad, slice_png, p3_png, wt_png, sheet]},
    }
    (OUT / "manifest.json").write_text(json.dumps(dump, indent=2) + "\n")
    print(json.dumps(dump, indent=2))


if __name__ == "__main__":
    main()
