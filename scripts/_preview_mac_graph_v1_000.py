#!/usr/bin/env python3
"""PIL iso preview for BUILD_A_ROBOT MAC graph v1 part 000."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3/build_a_robot_mac_graph_v1")
COMP = ROOT / "03_components" / "P3_COMPONENT_000"
OUT = ROOT / "artifacts"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def load_mesh(path: Path) -> trimesh.Trimesh | None:
    if not path.is_file():
        return None
    mesh = trimesh.load(path, force="mesh", process=False)
    if isinstance(mesh, trimesh.Scene):
        mesh = mesh.to_mesh()
    if mesh is None or len(getattr(mesh, "faces", [])) == 0:
        return None
    return mesh


def project(points: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    iso = points[:, 0] - 0.42 * points[:, 1]
    elev = points[:, 2] + 0.28 * points[:, 1]
    depth = points[:, 0] * 0.35 + points[:, 1] * 0.85 + points[:, 2] * 0.15
    return np.column_stack((iso, elev)), depth


def render_mesh(mesh: trimesh.Trimesh, rgb: tuple[int, int, int], bounds_xy: np.ndarray, size: int = 720, face_limit: int = 22000, alpha: int = 255) -> Image.Image:
    vertices = np.asarray(mesh.vertices, dtype=float)
    faces = np.asarray(mesh.faces, dtype=np.int64)
    if len(faces) > face_limit:
        faces = faces[np.linspace(0, len(faces) - 1, face_limit, dtype=np.int64)]
    xy, depth = project(vertices)
    low, high = bounds_xy
    scale = max(float(np.max(high - low)), 1e-9)
    mapped = (xy - (low + high) * 0.5) / scale * (size * 0.82) + size * 0.5
    tris = vertices[faces]
    normals = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    normals = normals / (np.linalg.norm(normals, axis=1, keepdims=True) + 1e-9)
    light = np.array([-0.4, -0.75, 0.55])
    light = light / np.linalg.norm(light)
    shade = np.clip(normals @ light, 0.22, 1.0)
    order = np.argsort(depth[faces].mean(axis=1))
    image = Image.new("RGBA", (size, size + 56), (244, 246, 248, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    for idx in order:
        pts = [(int(mapped[i, 0]), int(size - 8 - mapped[i, 1])) for i in faces[idx]]
        color = tuple(int(c * (0.32 + 0.68 * shade[idx])) for c in rgb) + (alpha,)
        draw.polygon(pts, fill=color)
    return image


def label(image: Image.Image, text: str) -> Image.Image:
    font = ImageFont.truetype(FONT, 26) if Path(FONT).is_file() else ImageFont.load_default()
    draw = ImageDraw.Draw(image)
    draw.text((16, image.height - 42), text, fill=(31, 42, 51), font=font)
    return image


def main() -> None:
    qa = json.loads((COMP / "08_qa/MAC_CANDIDATE_01/qa.json").read_text())
    jobs = [
        (COMP / "01_prepare/source_part.obj", (170, 180, 190), "source mesh"),
        (COMP / "08_qa/MAC_CANDIDATE_01/MAC_CANDIDATE_01.stl", (217, 95, 2), "MAC generated CAD"),
        (COMP / "08_qa/CURRENT_V6_PROFILE_LOFT/CURRENT_V6_PROFILE_LOFT.stl", (44, 127, 184), "CURRENT_V6 loft"),
        (COMP / "08_qa/FACETED_FALLBACK/P3_COMPONENT_000__FACETED_FALLBACK.stl", (139, 152, 168), "selected faceted"),
    ]
    meshes = []
    for path, color, title in jobs:
        mesh = load_mesh(path)
        if mesh is not None:
            meshes.append((mesh, color, title))
    xy_all = np.vstack([project(np.asarray(m.vertices))[0] for m, _, _ in meshes])
    bounds_xy = np.vstack((xy_all.min(axis=0), xy_all.max(axis=0)))
    OUT.mkdir(parents=True, exist_ok=True)
    panels = [label(render_mesh(mesh, color, bounds_xy), title) for mesh, color, title in meshes]
    overlay = render_mesh(meshes[0][0], (154, 163, 173), bounds_xy, alpha=90)
    mac_layer = render_mesh(meshes[1][0], (217, 95, 2), bounds_xy, alpha=200)
    overlay = Image.alpha_composite(overlay, mac_layer)
    overlay = label(overlay, "overlay: source + MAC")
    overlay.convert("RGB").save(OUT / "preview_P3_COMPONENT_000_mac_overlay.png")
    width = sum(p.width for p in panels)
    height = max(p.height for p in panels)
    sheet = Image.new("RGB", (width, height + 44), (244, 246, 248))
    x = 0
    for panel in panels:
        sheet.paste(panel.convert("RGB"), (x, 44))
        x += panel.width
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype(FONT, 22) if Path(FONT).is_file() else ImageFont.load_default()
    draw.text(
        (16, 10),
        f"P3_COMPONENT_000  QA pass={qa.get('qa_pass')} coverage={qa.get('coverage')} hausdorff={qa.get('hausdorff')}  selected=FACETED_FALLBACK",
        fill=(51, 65, 85),
        font=font,
    )
    out_sheet = OUT / "preview_P3_COMPONENT_000_mac_vs_source.png"
    sheet.save(out_sheet)
    print(out_sheet)
    print(OUT / "preview_P3_COMPONENT_000_mac_overlay.png")


if __name__ == "__main__":
    main()
