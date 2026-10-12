#!/usr/bin/env python3
"""Render unused P1-good Circle-extrude cases. Does not overwrite prior figures."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rerender_more_p1_good_v1 import A0, A1, A3, OUT, P1, gallery, render_case, rows

MORE = [
    "deepcad__0075_00753412",
    "deepcad__0035_00357667",
    "deepcad__0079_00798306",
    "deepcad__0050_00504143",
    "deepcad__0082_00821407",
    "deepcad__0007_00079699",
    "deepcad__0058_00581356",
    "fusion360__34782_b461066c_0016",
]


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
    with (OUT / "selection/MORE_CIRCLE8.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(fields)
        w.writerows(recs)
    dest = OUT / "renders/P1_GEOMETRY_SUCCESS_CIRCLE8.png"
    gallery(
        MORE,
        imgs,
        dest,
        "P1 EXACT9998 VAL1000 Circle-extrude geometry-success cases",
    )
    print("WROTE", dest)


if __name__ == "__main__":
    main()
