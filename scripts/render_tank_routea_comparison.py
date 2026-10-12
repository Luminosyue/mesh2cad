#!/usr/bin/env python3
"""Tank Route A comparison sheet: source high-poly, X-Part explode, CAD assemble/explode."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/cadfit_xpart45_routea_v1"
SOURCE_OBJ = ROOT / "ours3/meshes/yC4xcavDg89GZgqjJtUs5KYbrgz.obj"
XPART_ROOT = ROOT / "ours3/p3_xpart_frozen45_v1/xpart"
STEP_ROOT = CASE / "step"
RAW_ROOT = CASE / "cadfit_raw"
OUT = CASE / "renders"
HELPER = ROOT / "ours3/tank_fullstack_mesh2cad_mac_multibackend_v1/scripts/render_p3_45_assembly.py"
CAD_BLUE = (113, 174, 205)
SOURCE_GRAY = (198, 201, 206)
MAX_TRIANGLES = 120_000


def load_helper():
    spec = importlib.util.spec_from_file_location("tank_render_helper", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_font(size: int) -> ImageFont.ImageFont:
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def similarity_matrix(source: trimesh.Trimesh, recon: trimesh.Trimesh) -> np.ndarray:
    src_c = np.asarray(source.centroid, float)
    rec_c = np.asarray(recon.centroid, float)
    src_ext = float(np.max(source.extents))
    rec_ext = float(np.max(recon.extents))
    scale = src_ext / rec_ext if rec_ext > 1e-12 else 1.0
    t = src_c - scale * rec_c
    m = np.eye(4)
    m[0, 0] = m[1, 1] = m[2, 2] = scale
    m[:3, 3] = t
    return m


def bounds_of(meshes: list[trimesh.Trimesh]) -> np.ndarray:
    verts = np.vstack([np.asarray(m.vertices, float) for m in meshes])
    return np.vstack([verts.min(0), verts.max(0)]).T


def explode(meshes: list[trimesh.Trimesh], centroids: list[np.ndarray], diag: float, factor: float) -> list[trimesh.Trimesh]:
    center = np.mean(np.stack(centroids, axis=0), axis=0)
    out = []
    for mesh, centroid in zip(meshes, centroids):
        copied = mesh.copy()
        direction = centroid - center
        norm = float(np.linalg.norm(direction))
        if norm > 1e-9:
            copied.vertices = copied.vertices + direction / norm * diag * factor
        out.append(copied)
    return out


def part_budgets(face_counts: list[int], total: int = MAX_TRIANGLES) -> list[int]:
    counts = np.asarray(face_counts, float)
    shares = counts / max(float(counts.sum()), 1.0)
    budgets = np.maximum(400, np.round(shares * total)).astype(int)
    extra = int(budgets.sum() - total)
    if extra > 0:
        for idx in np.argsort(-budgets):
            take = min(extra, max(0, int(budgets[idx]) - 400))
            budgets[idx] -= take
            extra -= take
            if extra <= 0:
                break
    return budgets.tolist()


def draw_table(stats: dict, path: Path, size=(1400, 1050)) -> None:
    image = Image.new("RGB", size, (248, 249, 251))
    draw = ImageDraw.Draw(image)
    title_font = load_font(28)
    head_font = load_font(22)
    body_font = load_font(20)
    draw.text((48, 36), "Face / part counts", fill=(28, 34, 46), font=title_font)

    rows = [
        ("Stage", "Parts", "Faces", "Verts", "Notes"),
        (
            "Original high-poly (Meshy)",
            "1",
            f"{stats['source_faces']:,}",
            f"{stats['source_verts']:,}",
            "yC4xcavDg89GZgqjJtUs5KYbrgz.obj",
        ),
        (
            "X-Part watertight",
            str(stats["xpart_parts"]),
            f"{stats['xpart_faces']:,}",
            f"{stats['xpart_verts']:,}",
            f"min {stats['xpart_faces_min']:,} / max {stats['xpart_faces_max']:,}",
        ),
        (
            "CADFit tessellation",
            str(stats["cad_parts"]),
            f"{stats['cad_faces']:,}",
            f"{stats['cad_verts']:,}",
            f"min {stats['cad_faces_min']:,} / max {stats['cad_faces_max']:,}",
        ),
    ]
    col_x = [48, 430, 620, 880, 1080]
    y = 120
    row_h = 72
    for r, row in enumerate(rows):
        bg = (232, 236, 242) if r == 0 else ((255, 255, 255) if r % 2 else (242, 244, 247))
        draw.rectangle([36, y, size[0] - 36, y + row_h], fill=bg)
        font = head_font if r == 0 else body_font
        fill = (28, 34, 46) if r == 0 else (50, 56, 68)
        for x, text in zip(col_x, row):
            draw.text((x, y + 22), text, fill=fill, font=font)
        y += row_h

    extras = [
        f"CADFit mean IoU: {stats['mean_iou']:.3f}",
        f"Face reduction vs original: {stats['cad_vs_source_pct']:.1f}% of source faces",
        f"Face reduction vs X-Part: {stats['cad_vs_xpart_pct']:.1f}% of X-Part faces",
        "CADFit max_iterations=1, fillet/chamfer OFF",
    ]
    y += 36
    for line in extras:
        draw.text((48, y), line, fill=(70, 76, 88), font=body_font)
        y += 36
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, dpi=(180, 180))


def compose_grid(cells: list[tuple[Path, str, str]], out: Path, caption: str) -> None:
    images = [(Image.open(p).convert("RGB"), title, sub) for p, title, sub in cells]
    pw, ph = 900, 700
    header, sub_h, footer = 46, 36, 78
    cols = 3
    rows = int(np.ceil(len(images) / cols))
    canvas = Image.new("RGB", (pw * cols, rows * (ph + header + sub_h) + footer), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(22)
    sub_font = load_font(16)
    cap_font = load_font(16)
    for i, (im, title, sub) in enumerate(images):
        r, c = divmod(i, cols)
        x0 = c * pw
        y0 = r * (ph + header + sub_h)
        draw.text((x0 + 18, y0 + 10), title, fill=(28, 34, 46), font=title_font)
        thumb = im.copy()
        thumb.thumbnail((pw - 28, ph - 16))
        canvas.paste(thumb, (x0 + (pw - thumb.width) // 2, y0 + header))
        draw.text((x0 + 18, y0 + header + ph - 4), sub, fill=(90, 96, 108), font=sub_font)
    draw.text((18, canvas.height - 52), caption, fill=(70, 76, 88), font=cap_font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(180, 180))


def main() -> int:
    mod = load_helper()
    part_ids = sorted(p.name for p in XPART_ROOT.glob("PART_*") if p.is_dir())
    source = trimesh.load(str(SOURCE_OBJ), force="mesh", process=False)

    xpart_meshes = []
    cad_meshes = []
    xpart_faces = []
    cad_faces = []
    xpart_verts = []
    cad_verts = []
    centroids = []

    for pid in part_ids:
        idx = int(pid.split("_")[1])
        xp = trimesh.load(str(XPART_ROOT / pid / f"complete_part_{idx:03d}.obj"), force="mesh", process=False)
        recon_path = STEP_ROOT / pid / f"{pid}_reconstructed.stl"
        if not recon_path.is_file():
            recon_path = RAW_ROOT / pid / "best_greedy_parallel_iterative.stl"
        rec = trimesh.load(str(recon_path), force="mesh", process=False)
        placed = rec.copy()
        placed.apply_transform(similarity_matrix(xp, rec))
        xpart_meshes.append(xp)
        cad_meshes.append(placed)
        xpart_faces.append(int(len(xp.faces)))
        cad_faces.append(int(len(placed.faces)))
        xpart_verts.append(int(len(xp.vertices)))
        cad_verts.append(int(len(placed.vertices)))
        centroids.append(np.asarray(xp.centroid, float))
        print(f"{pid} xpart_F={xpart_faces[-1]} cad_F={cad_faces[-1]}")

    gate = json.loads((CASE / "gate.json").read_text()) if (CASE / "gate.json").is_file() else {}
    stats = {
        "source_faces": int(len(source.faces)),
        "source_verts": int(len(source.vertices)),
        "xpart_parts": len(part_ids),
        "xpart_faces": int(sum(xpart_faces)),
        "xpart_verts": int(sum(xpart_verts)),
        "xpart_faces_min": int(min(xpart_faces)),
        "xpart_faces_max": int(max(xpart_faces)),
        "cad_parts": len(part_ids),
        "cad_faces": int(sum(cad_faces)),
        "cad_verts": int(sum(cad_verts)),
        "cad_faces_min": int(min(cad_faces)),
        "cad_faces_max": int(max(cad_faces)),
        "mean_iou": float(gate.get("MEAN_IOU") or 0.0),
        "per_part": [
            {"part_id": pid, "xpart_faces": xf, "cad_faces": cf}
            for pid, xf, cf in zip(part_ids, xpart_faces, cad_faces)
        ],
    }
    stats["cad_vs_source_pct"] = 100.0 * stats["cad_faces"] / max(stats["source_faces"], 1)
    stats["cad_vs_xpart_pct"] = 100.0 * stats["cad_faces"] / max(stats["xpart_faces"], 1)

    colors = mod.palette(len(part_ids))
    assembled_bounds = bounds_of(xpart_meshes)
    diag = float(np.linalg.norm(assembled_bounds[:, 1] - assembled_bounds[:, 0]))
    iso = mod.camera_matrix(38, 24)
    x_exploded = explode(xpart_meshes, centroids, diag, 0.28)
    c_exploded = explode(cad_meshes, centroids, diag, 0.28)
    x_exp_bounds = bounds_of(x_exploded)
    c_exp_bounds = bounds_of(c_exploded)
    budgets_x = part_budgets(xpart_faces)
    budgets_c = part_budgets(cad_faces, total=min(MAX_TRIANGLES, max(sum(cad_faces), 1000)))

    panels = OUT / "comparison_panels"
    panels.mkdir(parents=True, exist_ok=True)
    p_src = panels / "01_source_highpoly.png"
    p_xp = panels / "02_xpart_assembled.png"
    p_xpe = panels / "03_xpart_exploded.png"
    p_cad = panels / "04_cad_assembled.png"
    p_cade = panels / "05_cad_exploded.png"
    p_tbl = panels / "06_face_counts.png"

    print("rendering panels...")
    mod.render_scene(
        [source],
        [SOURCE_GRAY],
        assembled_bounds,
        p_src,
        iso,
        budgets=[min(MAX_TRIANGLES, stats["source_faces"])],
    )
    mod.render_scene(xpart_meshes, colors, assembled_bounds, p_xp, iso, budgets=budgets_x)
    mod.render_scene(x_exploded, colors, x_exp_bounds, p_xpe, iso, budgets=budgets_x)
    mod.render_scene(cad_meshes, [CAD_BLUE] * len(cad_meshes), assembled_bounds, p_cad, iso, budgets=budgets_c)
    mod.render_scene(c_exploded, colors, c_exp_bounds, p_cade, iso, budgets=budgets_c)
    draw_table(stats, p_tbl)

    caption = (
        f"Tank Route A  |  source {stats['source_faces']:,} faces  |  "
        f"X-Part {stats['xpart_parts']} parts / {stats['xpart_faces']:,} faces  |  "
        f"CADFit {stats['cad_parts']} solids / {stats['cad_faces']:,} tessellated faces  |  "
        f"mean IoU {stats['mean_iou']:.3f}"
    )
    sheet = OUT / "comparison_sheet.png"
    compose_grid(
        [
            (p_src, "1. Original high-poly (Meshy asset)", f"{stats['source_faces']:,} faces  /  {stats['source_verts']:,} verts"),
            (p_xp, "2. X-Part segmented assembly", f"{stats['xpart_parts']} parts  /  {stats['xpart_faces']:,} faces"),
            (p_xpe, "3. X-Part exploded parts", f"45 colored solids  |  max part {stats['xpart_faces_max']:,} faces"),
            (p_cad, "4. CADFit CAD assembly", f"{stats['cad_faces']:,} tessellated faces  |  mean IoU {stats['mean_iou']:.3f}"),
            (p_cade, "5. CADFit exploded parts", f"45 CAD solids  |  max part {stats['cad_faces_max']:,} faces"),
            (p_tbl, "6. Face counts", "source vs X-Part vs CADFit"),
        ],
        sheet,
        caption,
    )
    (OUT / "comparison_stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(f"WROTE {sheet}")
    print(json.dumps({k: stats[k] for k in stats if k != "per_part"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
