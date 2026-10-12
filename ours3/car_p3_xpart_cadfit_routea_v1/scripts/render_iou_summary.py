#!/usr/bin/env python3
"""Per-part IoU bar chart and contact sheet for toy car CADFit."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from paths import CADFIT_RAW, CASE  # noqa: E402

OUT = CASE / "cadfit_routea/renders"


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
        data = json.loads(iou_path.read_text())
        rows.append(
            {
                "part_id": part_dir.name,
                "iou": float(data["final_iou"]),
                "overlay": str(part_dir.parent.parent / "renders" / part_dir.name / "03_overlay_projection.png"),
            }
        )
    return rows


def render_bar(rows: list[dict], out: Path) -> None:
    parts = [r["part_id"] for r in rows]
    ious = [r["iou"] for r in rows]
    colors = ["#E45756" if x < 0.5 else "#F58518" if x < 0.7 else "#4C78A8" if x < 0.85 else "#54A24B" for x in ious]
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.bar(parts, ious, color=colors, edgecolor="white", linewidth=0.6)
    ax.axhline(np.mean(ious), color="#333333", ls="--", lw=1.2, label=f"mean={np.mean(ious):.3f}")
    ax.set_ylim(0, 1.0)
    ax.set_ylabel("CADFit IoU")
    ax.set_title("Toy Car — per-part CADFit IoU (13 parts)")
    ax.tick_params(axis="x", rotation=45)
    ax.legend(loc="upper right")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=180)
    plt.close(fig)
    print(f"WROTE {out}")


def render_contact_sheet(rows: list[dict], out: Path, cols: int = 4) -> None:
    imgs = []
    for row in rows:
        p = row["overlay"]
        if p.is_file():
            imgs.append((Image.open(p).convert("RGB"), row))
    if not imgs:
        return
    n = len(imgs)
    rows_n = (n + cols - 1) // cols
    tile = 420
    header = 52
    canvas = Image.new("RGB", (cols * tile, rows_n * (tile + header) + 40), "white")
    draw = ImageDraw.Draw(canvas)
    title_font = load_font(18)
    cap_font = load_font(14)
    draw.text((12, 8), "Toy Car — Source vs CADFit overlay (blue=source, red=recon)", fill=(30, 30, 30), font=title_font)
    for idx, (im, row) in enumerate(imgs):
        r, c = divmod(idx, cols)
        x, y = c * tile + 8, 40 + r * (tile + header) + header
        thumb = im.copy()
        thumb.thumbnail((tile - 16, tile - 16))
        canvas.paste(thumb, (x + (tile - 16 - thumb.width) // 2, y + (tile - 16 - thumb.height) // 2))
        draw.text((c * tile + 12, 40 + r * (tile + header) + 8), f"{row['part_id']}  IoU={row['iou']:.3f}", fill=(50, 50, 50), font=cap_font)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(out, dpi=(180, 180))
    print(f"WROTE {out}")


def main() -> int:
    rows = collect_rows()
    if not rows:
        print("no IoU rows")
        return 1
    render_bar(rows, OUT / "iou_by_part.png")
    render_contact_sheet(rows, OUT / "overlay_contact_sheet.png")
    summary = {
        "count": len(rows),
        "mean_iou": float(np.mean([r["iou"] for r in rows])),
        "min_iou": float(min(r["iou"] for r in rows)),
        "max_iou": float(max(r["iou"] for r in rows)),
        "parts": rows,
    }
    (OUT / "iou_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
