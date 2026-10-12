from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import trimesh
from PIL import Image, ImageDraw


def render_mesh(mesh: trimesh.Trimesh, path: Path, title: str, color=(185, 205, 225)) -> None:
    size = (720, 540)
    image = Image.new("RGB", size, "white")
    draw = ImageDraw.Draw(image)
    if len(mesh.vertices) == 0 or len(mesh.faces) == 0:
        draw.text((20, 20), title, fill=(20, 30, 40))
        image.save(path)
        return
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    center = (vertices.min(axis=0) + vertices.max(axis=0)) * 0.5
    direction = np.asarray([1.2, -1.35, 0.85], dtype=float)
    direction /= np.linalg.norm(direction)
    right = np.cross(direction, [0.0, 0.0, 1.0])
    right /= max(np.linalg.norm(right), 1e-12)
    up = np.cross(right, direction)
    projected = np.column_stack(((vertices - center) @ right, (vertices - center) @ up))
    scale = max(float(np.max(np.abs(projected))), 1e-9)
    xy = np.column_stack((360 + projected[:, 0] * 300 / scale, 300 - projected[:, 1] * 300 / scale))
    depth = (vertices - center) @ direction
    normals = np.asarray(mesh.face_normals, dtype=float)
    light = np.asarray([0.35, -0.45, 0.82], dtype=float)
    light /= np.linalg.norm(light)
    for index in np.argsort(depth[faces].mean(axis=1)):
        shade = 0.42 + 0.58 * max(float(np.dot(normals[int(index)], light)), 0.0)
        fill = tuple(int(channel * shade) for channel in color)
        draw.polygon([tuple(np.rint(xy[int(i)]).astype(int)) for i in faces[int(index)]], fill=fill)
    draw.rectangle((0, 0, size[0], 42), fill="white")
    draw.text((16, 14), title, fill=(20, 30, 40))
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)


def contact_sheet(images: Iterable[tuple[Path, str]], output: Path, title: str) -> None:
    items = list(images)
    tile = (360, 290)
    canvas = Image.new("RGB", (tile[0] * 2, tile[1] * max(1, (len(items) + 1) // 2)), "white")
    draw = ImageDraw.Draw(canvas)
    for index, (path, label) in enumerate(items):
        x = (index % 2) * tile[0]
        y = (index // 2) * tile[1]
        if path.is_file():
            image = Image.open(path).convert("RGB")
            image.thumbnail((tile[0] - 10, tile[1] - 42))
            canvas.paste(image, (x + 5, y + 30))
        draw.text((x + 8, y + 8), label, fill=(20, 30, 40))
    canvas.save(output)
