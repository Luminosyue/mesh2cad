#!/usr/bin/env python3
"""IoU bar chart and overlay contact sheet for tank Route A."""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/cadfit_xpart45_routea_v1"
CADFIT_RAW = CASE / "cadfit_raw"
RENDER_DIR = CASE / "renders"


def load_font(size: int):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def collect_rows() -> list[dict]:
    rows = []
    for part_dir in sorted(CADFIT_RAW.glob("PART_*")):
        iou_path = part_dir / "final_iou.json"
        if not iou_path.is_file():
            continue
        rows.append(
            {
                "part_id": part_dir.name,
                "iou": float(json.loads(iou_path.read_text())["final_iou"]),
                "overlay": RENDER_DIR / part_dir.name / "03_overlay_projection.png",
            }
        )
    return rows


def render_bar(rows: list[dict], out: Path) -> None:
    parts = [r["part_id"] for r in rows]
    ious = [r["iou"] for r in rows]
    colors = ["#E45756" if x < 0.5 else "#F58518" if x < 0.7 else "#4C78A8" if x < 0.85 else "#54A24B" for x in ious]
    fig, ax = plt.subplots(figsize=(16, 4.5))
    ax.bar(parts, ious, color=colors, edgecolor="white", linewidth=0.5)
    ax.axhline(np.mean(ious), color="#333333", ls="--", lw=1.2, label=f"mean={np.mean(ious):.3f}")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("CADFit IoU")
    ax.set_title("Tank — per-part CADFit IoU (45 parts)")
    ax.tick_params(axis="x", rotation=90, labelsize=7)
    ax.legend(loc="upper right")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)
    print(f"WROTE {out}")


def render_contact_sheet(rows: list[dict], out: Path, cols: int = 9) -> None:
    imgs = []
    for row in rows:
        if row["overlay"].is_file():
            imgs.append((Image.open(row["overlay"]).convert("RGB"), row))
    if not imgs:
        return
    n = len(imgs)
    rows_n = (n + cols - 1) // cols
    tile = 280
    header = 40
    canvas = Image.new("RGB", (cols * tile, rows_n * (tile + header) + 32), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(18)
    cap_font = load_font(11)
    draw.text((12, 6), "Tank — Source vs CADFit overlay (blue=source, red=recon)", fill=(30, 30, 30), font=title_font)
    for idx, (im, row) in enumerate(imgs):
        r, c = divmod(idx, cols)
        x, y = c * tile + 6, 32 + r * (tile + header) + header
        thumb = im.copy()
        thumb.thumbnail((tile - 12, tile - 12))
        canvas.paste(thumb, (x + (tile - 12 - thumb.width) // 2, y + (tile - 12 - thumb.height) // 2))
        draw.text((c * tile + 8, 32 + r * (tile + header) + 6), f"{row['part_id']} {row['iou']:.2f}", fill=(50, 50, 50), font=cap_font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(180, 180))
    print(f"WROTE {out}")


def main() -> int:
    rows = collect_rows()
    if not rows:
        print("no IoU rows")
        return 1
    render_bar(rows, RENDER_DIR / "iou_by_part.png")
    render_contact_sheet(rows, RENDER_DIR / "overlay_contact_sheet.png", cols=9)
    summary = {
        "count": len(rows),
        "mean_iou": float(np.mean([r["iou"] for r in rows])),
        "min_iou": float(min(r["iou"] for r in rows)),
        "max_iou": float(max(r["iou"] for r in rows)),
    }
    (RENDER_DIR / "iou_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
