#!/usr/bin/env python3
"""Shaded 3D original-mesh vs CAD comparison for the coffee canister."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CASE, SOURCE, STEP_DIR, XPART_DIR  # noqa: E402

HELPER = Path(
    "/data/home/cuiyuehan/project/mesh2cad/ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/scripts/render_p3_45_assembly.py"
)
OUT = CASE / "cadfit_routea/renders"
CAD_BLUE = (113, 174, 205)
SOURCE_GRAY = (186, 190, 196)
PALETTE = [(76, 120, 168), (228, 87, 86), (84, 162, 75)]
MAX_SRC = 160_000


def load_helper():
    spec = importlib.util.spec_from_file_location("tank_render_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def bounds_of(meshes: list[trimesh.Trimesh]) -> np.ndarray:
    verts = np.vstack([np.asarray(m.vertices, float) for m in meshes])
    return np.vstack([verts.min(0), verts.max(0)]).T


def compose_row(panels: list[tuple[Path, str, str]], out: Path, caption: str) -> None:
    images = [Image.open(p).convert("RGB") for p, _, _ in panels]
    pw, ph = 900, 720
    header, sub, footer = 44, 28, 56
    canvas = Image.new("RGB", (pw * len(images), ph + header + sub + footer), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(22)
    sub_font = load_font(16)
    cap_font = load_font(16)
    for i, (im, (path, title, subtext)) in enumerate(zip(images, panels)):
        thumb = im.copy()
        thumb.thumbnail((pw - 20, ph - 16))
        x = i * pw + (pw - thumb.width) // 2
        canvas.paste(thumb, (x, header + 6))
        draw.text((i * pw + 18, 10), title, fill=(28, 34, 46), font=title_font)
        draw.text((i * pw + 18, header + ph - 2), subtext, fill=(90, 96, 108), font=sub_font)
    draw.text((18, header + ph + sub + 12), caption, fill=(70, 76, 88), font=cap_font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(180, 180))
    print(f"WROTE {out}")


def main() -> int:
    mod = load_helper()
    manifest = json.loads((CASE / "assembly/assembly_manifest.json").read_text())
    source = trimesh.load(str(SOURCE), force="mesh", process=False)
    cad_parts = []
    ious = []
    for i, entry in enumerate(manifest["parts"]):
        recon = trimesh.load(entry["recon_mesh"], force="mesh", process=False)
        recon.apply_transform(np.asarray(entry["T_cadfit_local_to_source_global"], float))
        cad_parts.append(recon)
        iou_path = CASE / "cadfit_routea/cadfit_raw" / entry["part_id"] / "final_iou.json"
        if iou_path.is_file():
            ious.append(float(json.loads(iou_path.read_text())["final_iou"]))
    cad = trimesh.util.concatenate(cad_parts)
    bounds = bounds_of([source, cad])
    iso = mod.camera_matrix(42, 26)
    iso2 = mod.camera_matrix(128, 18)
    mean_iou = float(np.mean(ious)) if ious else 0.0

    panels = OUT / "comparison_3d"
    panels.mkdir(parents=True, exist_ok=True)
    p_src = panels / "01_source_iso.png"
    p_cad = panels / "02_cad_iso.png"
    p_over = panels / "03_overlay_iso.png"
    p_src2 = panels / "04_source_iso2.png"
    p_cad2 = panels / "05_cad_iso2.png"
    p_over2 = panels / "06_overlay_iso2.png"

    src_budget = min(MAX_SRC, int(len(source.faces)))
    cad_budgets = [max(800, int(len(m.faces))) for m in cad_parts]

    print("rendering shaded views...")
    mod.render_scene([source], [SOURCE_GRAY], bounds, p_src, iso, size=(1400, 1100), budgets=[src_budget])
    mod.render_scene(cad_parts, PALETTE, bounds, p_cad, iso, size=(1400, 1100), budgets=cad_budgets)
    mod.render_scene(
        [source, *cad_parts],
        [SOURCE_GRAY, *PALETTE],
        bounds,
        p_over,
        iso,
        size=(1400, 1100),
        budgets=[src_budget, *cad_budgets],
    )
    mod.render_scene([source], [SOURCE_GRAY], bounds, p_src2, iso2, size=(1400, 1100), budgets=[src_budget])
    mod.render_scene(cad_parts, PALETTE, bounds, p_cad2, iso2, size=(1400, 1100), budgets=cad_budgets)
    mod.render_scene(
        [source, *cad_parts],
        [SOURCE_GRAY, *PALETTE],
        bounds,
        p_over2,
        iso2,
        size=(1400, 1100),
        budgets=[src_budget, *cad_budgets],
    )

    caption = (
        f"Coffee canister  |  source {len(source.faces):,} faces  |  "
        f"CADFit 3 solids / {sum(len(m.faces) for m in cad_parts):,} tess faces  |  mean IoU {mean_iou:.3f}"
    )
    compose_row(
        [
            (p_src, "1. Original high-poly mesh", f"{len(source.faces):,} faces  /  {len(source.vertices):,} verts"),
            (p_cad, "2. CADFit assembly", f"3 solids  |  mean IoU {mean_iou:.3f}"),
            (p_over, "3. Overlay (gray mesh + CAD)", "same camera, depth-sorted"),
        ],
        OUT / "source_vs_cad_3d.png",
        caption,
    )
    compose_row(
        [
            (p_src2, "1. Original mesh (side)", f"{len(source.faces):,} faces"),
            (p_cad2, "2. CADFit assembly (side)", "3 solids"),
            (p_over2, "3. Overlay (side)", "same camera, depth-sorted"),
        ],
        OUT / "source_vs_cad_3d_side.png",
        caption,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
