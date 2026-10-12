#!/usr/bin/env python3
"""Exploded assembly + per-part renders for tank Route A (45 parts)."""
from __future__ import annotations

import colorsys
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/cadfit_xpart45_routea_v1"
CADFIT_RAW = CASE / "cadfit_raw"
ASSEMBLY_DIR = CASE / "assembly"
RENDER_DIR = CASE / "renders"
EXPLODED_DIR = RENDER_DIR / "exploded"


def load_font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def part_color(i: int, n: int) -> str:
    hue = (i / max(n, 1)) % 1.0
    r, g, b = colorsys.hsv_to_rgb(hue, 0.62, 0.88)
    return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"


def mesh_for_vis(mesh: trimesh.Trimesh, max_faces: int) -> trimesh.Trimesh:
    if len(mesh.faces) <= max_faces:
        return mesh
    idx = np.random.default_rng(42).choice(len(mesh.faces), size=max_faces, replace=False)
    return mesh.submesh([idx], append=True, repair=False)


def load_placed_parts() -> list[dict]:
    manifest = json.loads((ASSEMBLY_DIR / "assembly_manifest.json").read_text())
    rows = []
    n = len(manifest["parts"])
    for i, entry in enumerate(manifest["parts"]):
        mesh = trimesh.load(entry["recon_mesh"], force="mesh", process=False)
        mesh.apply_transform(np.asarray(entry["T_cadfit_local_to_source_global"], float))
        iou_path = CADFIT_RAW / entry["part_id"] / "final_iou.json"
        iou = float(json.loads(iou_path.read_text())["final_iou"]) if iou_path.is_file() else 0.0
        rows.append({"part_id": entry["part_id"], "mesh": mesh, "color": part_color(i, n), "iou": iou})
    return rows


def explode(meshes: list[trimesh.Trimesh], factor: float = 0.42) -> list[trimesh.Trimesh]:
    cents = np.vstack([np.asarray(m.centroid, float) for m in meshes])
    origin = cents.mean(axis=0)
    out = []
    for mesh, c in zip(meshes, cents):
        moved = mesh.copy()
        moved.apply_translation((c - origin) * factor)
        out.append(moved)
    return out


def draw_meshes(
    meshes: list[tuple[trimesh.Trimesh, str]],
    out_path: Path,
    title: str,
    elev: float = 22,
    azim: float = 42,
    max_faces: int = 2800,
    figsize: tuple[float, float] = (10, 10),
) -> None:
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection="3d")
    all_verts = []
    for mesh, color in meshes:
        mv = mesh_for_vis(mesh, max_faces)
        tris = mv.vertices[mv.faces]
        coll = Poly3DCollection(tris, linewidths=0.012, alpha=0.93)
        coll.set_facecolor(color)
        coll.set_edgecolor((0, 0, 0, 0.03))
        ax.add_collection3d(coll)
        all_verts.append(mv.vertices)
    verts = np.vstack(all_verts)
    bmin, bmax = verts.min(0), verts.max(0)
    ctr = 0.5 * (bmin + bmax)
    ext = np.max(bmax - bmin) * 0.55 + 1e-6
    ax.set_xlim(ctr[0] - ext, ctr[0] + ext)
    ax.set_ylim(ctr[1] - ext, ctr[1] + ext)
    ax.set_zlim(ctr[2] - ext, ctr[2] + ext)
    ax.set_box_aspect([1, 1, 1])
    ax.view_init(elev=elev, azim=azim)
    ax.set_title(title, fontsize=11)
    ax.axis("off")
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=180, bbox_inches="tight")
    plt.close(fig)
    print(f"WROTE {out_path}")


def render_single_part(mesh: trimesh.Trimesh, color: str, part_id: str, iou: float, out_path: Path) -> None:
    draw_meshes([(mesh, color)], out_path, f"{part_id}  IoU={iou:.3f}", max_faces=10000, figsize=(4.5, 4.5))


def render_parts_grid(rows: list[dict], out_path: Path, cols: int = 9) -> None:
    n = len(rows)
    rows_n = (n + cols - 1) // cols
    tile = 280
    header = 40
    canvas = Image.new("RGB", (cols * tile, rows_n * (tile + header) + 32), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(18)
    cap_font = load_font(12)
    draw.text((12, 6), "Tank — exploded CAD parts (45 solids)", fill=(30, 30, 30), font=title_font)
    for idx, row in enumerate(rows):
        img_path = EXPLODED_DIR / f"{row['part_id']}.png"
        if not img_path.is_file():
            continue
        im = Image.open(img_path).convert("RGB")
        r, c = divmod(idx, cols)
        x, y = c * tile + 6, 32 + r * (tile + header) + header
        thumb = im.copy()
        thumb.thumbnail((tile - 12, tile - 12))
        canvas.paste(thumb, (x + (tile - 12 - thumb.width) // 2, y + (tile - 12 - thumb.height) // 2))
        draw.text((c * tile + 8, 32 + r * (tile + header) + 6), f"{row['part_id']} {row['iou']:.2f}", fill=(40, 40, 40), font=cap_font)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out_path, dpi=(180, 180))
    print(f"WROTE {out_path}")


def main() -> int:
    rows = load_placed_parts()
    if not rows:
        raise SystemExit("no parts in assembly manifest")

    base_meshes = [r["mesh"] for r in rows]
    base_colored = [(m, r["color"]) for m, r in zip(base_meshes, rows)]
    exploded = explode(base_meshes, factor=0.42)
    exploded_colored = [(m, r["color"]) for m, r in zip(exploded, rows)]

    draw_meshes(base_colored, RENDER_DIR / "assembly_cadfit_isometric.png", f"Tank Route A CAD Assembly ({len(rows)} parts)")
    draw_meshes(
        base_colored,
        RENDER_DIR / "assembly_cadfit_top.png",
        "Tank Route A CAD Assembly — Top View",
        elev=90,
        azim=-90,
    )
    draw_meshes(
        exploded_colored,
        RENDER_DIR / "assembly_cadfit_exploded.png",
        f"Tank Route A CAD Assembly — Exploded ({len(rows)} parts)",
    )
    draw_meshes(
        exploded_colored,
        RENDER_DIR / "assembly_cadfit_exploded_side.png",
        "Tank Route A CAD Assembly — Exploded (side)",
        elev=18,
        azim=120,
    )

    for row, mesh in zip(rows, exploded):
        render_single_part(mesh, row["color"], row["part_id"], row["iou"], EXPLODED_DIR / f"{row['part_id']}.png")

    render_parts_grid(rows, RENDER_DIR / "exploded_parts_grid.png", cols=9)

    src_scene = trimesh.util.concatenate([mesh_for_vis(m, 6000) for m in base_meshes])
    cad_scene = trimesh.util.concatenate(base_meshes)
    draw_meshes(
        [(src_scene, "#4C78A8")],
        RENDER_DIR / "assembly_source_xpart_isometric.png",
        "Tank X-Part Source Assembly (reference)",
        max_faces=80000,
    )
    draw_meshes(
        [(src_scene, "#4C78A8"), (cad_scene, "#E45756")],
        RENDER_DIR / "assembly_source_vs_cad_overlay.png",
        "Source (blue) vs CADFit Assembly (red)",
        max_faces=50000,
    )

    summary = {
        "count": len(rows),
        "mean_iou": float(np.mean([r["iou"] for r in rows])),
        "parts": [{"part_id": r["part_id"], "iou": r["iou"]} for r in rows],
    }
    (RENDER_DIR / "exploded_manifest.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"DONE {len(rows)} parts mean_iou={summary['mean_iou']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
