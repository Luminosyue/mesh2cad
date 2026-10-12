#!/usr/bin/env python3
from pathlib import Path
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
sys.path.insert(0, str(ROOT))
from case09_edge_audit import FRESH, OUT, mesh_from_shape, read_step


def render(mesh, output, size=(1400, 1000), supersample=2):
    width, height = size[0] * supersample, size[1] * supersample
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=int)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    rel = vertices - center
    view = np.asarray([1.35, -1.55, 1.05], float); view /= np.linalg.norm(view)
    right = np.cross(view, [0.0, 0.0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, view); up /= np.linalg.norm(up)
    depth = rel @ view
    diagonal = max(float(np.linalg.norm(vertices.max(axis=0) - vertices.min(axis=0))), 1e-9)
    camera_distance = diagonal * 2.8
    focal = camera_distance * 1.15
    projected = np.column_stack(((rel @ right) * focal / (camera_distance - depth), (rel @ up) * focal / (camera_distance - depth)))
    low, high = projected.min(axis=0), projected.max(axis=0)
    span = max(float(np.max(high - low)), 1e-9) * 1.16
    mid = (low + high) * 0.5
    xy = (projected - mid) / span
    xy = np.column_stack(((xy[:, 0] + .5) * width, (.5 - xy[:, 1]) * height)
    )

    # Soft neutral studio background.
    image = Image.new('RGB', (width, height), (235, 240, 244))
    draw = ImageDraw.Draw(image, 'RGB')
    for y in range(height):
        value = int(244 - 20 * y / max(height - 1, 1))
        draw.line((0, y, width, y), fill=(value, value + 3, value + 6))

    # Ground shadow gives the otherwise untextured CAD surfaces depth.
    shadow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow, 'RGBA')
    bbox = [int(width * .20), int(height * .78), int(width * .80), int(height * .91)]
    shadow_draw.ellipse(bbox, fill=(25, 39, 51, 38))
    shadow = shadow.filter(ImageFilter.GaussianBlur(28 * supersample))
    image = Image.alpha_composite(image.convert('RGBA'), shadow)
    draw = ImageDraw.Draw(image, 'RGBA')

    light = np.asarray([-0.45, -0.55, 0.95], float); light /= np.linalg.norm(light)
    material = np.asarray([116, 163, 194], float)
    face_rows = []
    for face in faces:
        p = vertices[face]
        normal = np.cross(p[1] - p[0], p[2] - p[0])
        norm = np.linalg.norm(normal)
        normal = normal / norm if norm > 1e-12 else np.asarray([0.0, 0.0, 1.0])
        diffuse = max(0.0, abs(float(normal @ light)))
        # A small specular term keeps curved/freeform areas readable.
        specular = max(0.0, float(normal @ light)) ** 18
        color = np.clip(material * (0.30 + 0.70 * diffuse) + 35.0 * specular, 0, 255).astype(int)
        face_rows.append((float(depth[face].mean()), face, tuple(map(int, color))))
    for _, face, color in sorted(face_rows, key=lambda item: item[0]):
        polygon = [tuple(map(int, xy[index])) for index in face]
        draw.polygon(polygon, fill=(*color, 255))

    image = image.convert('RGB').resize(size, Image.Resampling.LANCZOS)
    image.save(output, dpi=(180, 180))


step = FRESH / 'final/CASE09_full_e2e_assembly.step'
shape, _ = read_step(step)
mesh = mesh_from_shape(shape)
output = OUT / 'artifacts/case09_fresh_e2e_3d_shaded_render.png'
output.parent.mkdir(parents=True, exist_ok=True)
render(mesh, output)
print(output)
