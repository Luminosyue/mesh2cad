#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
OUT = HERE.parent

spec = importlib.util.spec_from_file_location("bos_meta", HERE / "build_object_smooth.py")


def load_meta():
    src = (HERE / "build_object_smooth.py").read_text()
    ns: dict = {}
    start = src.index("OBJECTS = {")
    end = src.index("\n}\n", start) + 3
    exec(src[start:end], ns)
    return ns["OBJECTS"]


def crop(img: np.ndarray, pad=12):
    mask = (np.abs(img[..., :3].astype(int) - img[0, 0, :3].astype(int)).sum(-1) > 6)
    ys, xs = np.where(mask)
    if len(xs) == 0:
        return img
    h, w = img.shape[:2]
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, h)
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, w)
    side = max(y1 - y0, x1 - x0)
    cy, cx = (y0 + y1) // 2, (x0 + x1) // 2
    canvas = np.full((side, side, img.shape[2]), img[0, 0], dtype=img.dtype)
    sy0, sx0 = max(cy - side // 2, 0), max(cx - side // 2, 0)
    sub = img[sy0:sy0 + side, sx0:sx0 + side]
    canvas[:sub.shape[0], :sub.shape[1]] = sub
    return canvas


def compose(obj: str, label: str):
    d = OUT / obj
    parts = sorted(p.name.replace("_generated_cad.png", "") for p in (d / "renders").glob("*_generated_cad.png"))
    n = len(parts)
    cols = min(n, 8 if n > 12 else max(n, 4))
    rows = -(-n // cols)
    cell = 2.3
    fig = plt.figure(figsize=(cols * cell + cols * cell * 0.9, max(rows * cell + 1.0, 6.5)), facecolor="white")
    outer = fig.add_gridspec(1, 2, width_ratios=[cols, cols * 0.9], wspace=0.04)
    grid = outer[0].subgridspec(rows, cols, hspace=0.18, wspace=0.04)
    for k, pid in enumerate(parts):
        ax = fig.add_subplot(grid[k // cols, k % cols])
        ax.imshow(crop(np.asarray(Image.open(d / f"renders/{pid}_generated_cad.png"))))
        ax.axis("off")
        ax.set_title(pid, fontsize=9, fontweight="bold", color="#14222b")
    ax = fig.add_subplot(outer[1])
    ax.imshow(crop(np.asarray(Image.open(d / "assembly/generated_cad_assembly.png"))))
    ax.axis("off")
    ax.set_title("Generated CAD assembly", fontsize=13, fontweight="bold", color="#14222b")
    fig.suptitle(f"{label} | all {n} generated CAD parts", fontsize=16, fontweight="bold", color="#14222b")
    fig.subplots_adjust(left=0.01, right=0.99, top=0.9, bottom=0.02)
    fig.savefig(d / f"{obj}_cad_parts_gallery.png", dpi=170, facecolor="white")
    fig.savefig(d / f"{obj}_cad_parts_gallery.pdf", facecolor="white")
    plt.close(fig)
    print(d / f"{obj}_cad_parts_gallery.png")


def main():
    objects = load_meta()
    for obj in sys.argv[1:] or list(objects):
        compose(obj, objects[obj][0])


if __name__ == "__main__":
    main()
