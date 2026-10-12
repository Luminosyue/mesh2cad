"""Debug renders: per-part stages, contact sheets, failure heatmap overlay."""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def _font(size=16):
    for candidate in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _project(points: np.ndarray, bounds) -> np.ndarray:
    pts = np.asarray(points, float).reshape(-1, 3)
    lo, hi = bounds
    span = np.maximum(hi - lo, 1e-9)
    scale = span.max()
    centered = (pts - (lo + hi) * 0.5) / scale
    x = centered[:, 0] - centered[:, 2] * 0.35
    y = centered[:, 1] + centered[:, 2] * 0.22
    return np.stack([x, y], axis=1)


def _to_pix(uv, size, pad=24):
    if len(uv) == 0:
        return np.zeros((0, 2), int)
    lo = uv.min(axis=0)
    hi = uv.max(axis=0)
    span = np.maximum(hi - lo, 1e-9)
    s = (size - 2 * pad) / span.max()
    pix = (uv - lo) * s
    pix[:, 1] = (hi[1] - lo[1]) * s - pix[:, 1]
    return (pix + pad).astype(int)


def render_overlay(path: Path, clouds: list[dict], bounds, title: str, size=640, status: str | None = None):
    path.parent.mkdir(parents=True, exist_ok=True)
    img = Image.new("RGB", (size, size + 36), (248, 249, 252))
    draw = ImageDraw.Draw(img)
    all_pts = []
    projected = []
    for cloud in clouds:
        raw = cloud.get("points")
        pts = np.asarray([] if raw is None else raw, float).reshape(-1, 3)
        projected.append(pts)
        if len(pts):
            all_pts.append(pts)
    if all_pts:
        uv_all = _project(np.vstack(all_pts), bounds)
        # include source bbox corners
        lo, hi = bounds
        corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        uv_all = np.vstack([uv_all, _project(corners, bounds)])
        pix_all = _to_pix(uv_all, size)
    else:
        pix_all = np.zeros((0, 2), int)
    # source bbox
    lo, hi = np.asarray(bounds[0], float), np.asarray(bounds[1], float)
    corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
    box_uv = _project(corners, bounds)
    box_pix = _to_pix(np.vstack([box_uv, pix_all]) if len(pix_all) else box_uv, size)[:8]
    edges = [(0, 1), (0, 2), (0, 4), (1, 3), (1, 5), (2, 3), (2, 6), (3, 7), (4, 5), (4, 6), (5, 7), (6, 7)]
    for a, b in edges:
        if a < len(box_pix) and b < len(box_pix):
            draw.line([tuple(box_pix[a]), tuple(box_pix[b])], fill=(180, 80, 80), width=2)
    offset = 8 if len(pix_all) else 0
    cursor = 0
    for cloud, pts in zip(clouds, projected):
        if len(pts) == 0:
            continue
        uv = _project(pts, bounds)
        base = np.vstack([uv, box_uv])
        pix = _to_pix(base, size)[: len(uv)]
        color = tuple(cloud.get("color") or (40, 90, 160))
        if cloud.get("lines"):
            for i in range(0, len(pix) - 1, 2):
                draw.line([tuple(pix[i]), tuple(pix[i + 1])], fill=color, width=1)
        else:
            for x, y in pix[:: max(1, len(pix) // 4000)]:
                draw.point((int(x), int(y)), fill=color)
        cursor += len(pts)
    badge = {"PASS": (46, 125, 50), "WARNING": (230, 160, 40), "REJECT": (198, 40, 40), "EXPLODED": (198, 40, 40)}.get(status or "", (70, 80, 95))
    draw.rectangle([0, size, size, size + 36], fill=badge)
    draw.text((12, size + 8), f"{title}  [{status or ''}]", fill="white", font=_font(15))
    img.save(path)


def contact_sheet(paths: list[Path], titles: list[str], out: Path, panel=(420, 360)):
    out.parent.mkdir(parents=True, exist_ok=True)
    images = []
    for p in paths:
        if p and Path(p).is_file():
            images.append(Image.open(p).convert("RGB"))
        else:
            images.append(Image.new("RGB", panel, (230, 230, 235)))
    cols = min(4, max(1, len(images)))
    rows = int(np.ceil(len(images) / cols))
    pw, ph = panel
    canvas = Image.new("RGB", (pw * cols, (ph + 36) * rows), "white")
    draw = ImageDraw.Draw(canvas)
    fnt = _font(14)
    for i, (im, title) in enumerate(zip(images, titles)):
        r, c = divmod(i, cols)
        thumb = im.copy()
        thumb.thumbnail((pw - 16, ph - 28))
        x = c * pw + (pw - thumb.size[0]) // 2
        y = r * (ph + 36) + 32 + (ph - 28 - thumb.size[1]) // 2
        canvas.paste(thumb, (x, y))
        draw.text((c * pw + 10, r * (ph + 36) + 8), title, fill=(20, 30, 45), font=fnt)
    canvas.save(out, dpi=(160, 160))


def heatmap_assembly(path: Path, parts: list[dict], bounds, size=720):
    clouds = []
    colors = {"PASS": (46, 125, 50), "WARNING": (230, 160, 40), "REJECT": (198, 40, 40), "EXPLODED": (198, 40, 40)}
    for part in parts:
        raw = part.get("points")
        pts = np.asarray([] if raw is None else raw, float).reshape(-1, 3)
        if len(pts) == 0:
            lo = np.asarray(part.get("bbox_min") or bounds[0], float)
            hi = np.asarray(part.get("bbox_max") or bounds[1], float)
            pts = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        clouds.append({"points": pts[:: max(1, len(pts) // 2500)], "color": colors.get(part.get("status"), (80, 80, 90))})
    render_overlay(path, clouds, bounds, "assembly status heatmap (geometry unchanged)", status="PASS")
