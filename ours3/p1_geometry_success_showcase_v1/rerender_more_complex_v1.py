#!/usr/bin/env python3
"""Render unused P1-good cases with longer / nested boolean programs.

Does not overwrite prior showcase figures. Does not modify predictions or metrics.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rerender_aligned_v1 import FONT_B, FONT_R
from rerender_more_p1_good_v1 import A0, A1, A3, OUT, P1, render_case, rows

MORE = [
    "deepcad__0019_00199177",  # nested Cut/Union, 2 holes, exact
    "deepcad__0050_00506931",  # 64-gon outline + 48-gon hole, exact
    "deepcad__0072_00722866",  # 3 holes
    "deepcad__0029_00295360",  # 4 holes
    "deepcad__0064_00648240",  # 5-circle Cut/Union
    "deepcad__0004_00041577",  # Cut + Union, 3 ops
    "fusion360__54958_9a4ff7d7_0000",  # Cut two circles
    "deepcad__0051_00516650",  # 8 bodies / 3 holes; hardest GT (Op-F1 0.74)
]


def gallery(ids, imgs, dest: Path, title: str) -> None:
    cols = ["Input", "GT", "A0", "A1", "A3", "P1"]
    cw, ch, m = 420, 410, 118
    im = Image.new("RGB", (m + cw * 6, ch * len(ids) + 88), "white")
    d = ImageDraw.Draw(im)
    d.text((16, 14), title, fill="#17202a", font=ImageFont.truetype(FONT_B, 22))
    d.text(
        (16, 44),
        "Nested Cut/Union, multi-hole, multi-body  ·  same aligned CAD-frame protocol  ·  VAL1000 GT programs are at most 4 ops",
        fill="#5a6a78",
        font=ImageFont.truetype(FONT_R, 12),
    )
    for j, cid in enumerate(ids):
        d.text((6, 92 + j * ch), cid, fill="#263746", font=ImageFont.truetype(FONT_R, 11))
        for i, p in enumerate(imgs[cid]):
            q = Image.open(p).convert("RGB")
            q.thumbnail((cw - 10, ch - 24))
            im.paste(q, (m + i * cw + (cw - q.width) // 2, 86 + j * ch + 16))
        if j == 0:
            for i, x in enumerate(cols):
                d.text((m + i * cw + 10, 68), x, fill="#111", font=ImageFont.truetype(FONT_B, 14))
    im.save(dest, dpi=(300, 300))


def main() -> None:
    (OUT / "renders").mkdir(parents=True, exist_ok=True)
    (OUT / "selection").mkdir(parents=True, exist_ok=True)
    R = {k: rows(v) for k, v in {"P1": P1, "A0": A0, "A1": A1, "A3": A3}.items()}
    recs = []
    imgs = {}
    for cid in MORE:
        print("RENDER", cid, flush=True)
        imgs[cid] = render_case(cid, R)
        p = R["P1"][cid]
        g = p.get("geometry") or {}
        recs.append(
            [
                cid,
                p.get("dataset"),
                ">".join(p.get("gt_ops") or []),
                p.get("op_f1"),
                g.get("chamfer_norm"),
                g.get("hausdorff_95_norm"),
                g.get("volume_error"),
                p.get("exact_match"),
            ]
        )
    fields = ["case_id", "source", "gt_ops", "P1_OpF1", "P1_Chamfer", "P1_H95", "P1_Volume_Error", "exact_match"]
    with (OUT / "selection/MORE_COMPLEX8.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        w.writerows(recs)
    dest = OUT / "renders/P1_GEOMETRY_SUCCESS_COMPLEX8.png"
    gallery(
        MORE,
        imgs,
        dest,
        "P1 EXACT9998 VAL1000 more-complex geometry cases",
    )
    print("WROTE", dest)


if __name__ == "__main__":
    main()
