#!/usr/bin/env python3
"""Render the Step 6.1A / 6.2 report from domain_gap_*.json."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from mesh_edge_to_curve_v1.config import RUNS_DIR  # noqa: E402

ARM_LABEL = {
    "brep": "B-Rep exact (train dist.)",
    "brep_fd": "B-Rep xyz + FD tangent",
    "mesh": "Mesh sharp edge (oracle group)",
}
CLS_ROWS = [
    ("macro_f1", "Macro F1", 4),
    ("balanced_accuracy", "Bal Acc", 4),
    ("LINE_f1", "LINE F1", 4),
    ("CIRCLE_f1", "CIRCLE F1", 4),
    ("ELLIPSE_f1", "ELLIPSE F1", 4),
    ("BSPLINE_f1", "BSPLINE F1", 4),
]
GEO_ROWS = [
    ("recon_chamfer/median", "Chamfer (med)", 5),
    ("params/line_dir_deg/median", "LINE dir°", 3),
    ("params/line_len_rel/median", "LINE len rel", 4),
    ("params/circle_normal_deg/median", "CIRCLE n°", 3),
    ("params/circle_radius_rel/median", "CIRCLE r rel", 4),
    ("params/ellipse_major_axis_deg/median", "ELLIPSE maj°", 2),
    ("params/bspline_degree_correct/mean", "BSPL deg acc", 3),
    ("params/bspline_ncp_rel/median", "BSPL ncp rel", 3),
]


def cell(v: dict | None, nd: int) -> str:
    if not v:
        return "—"
    return f"{v['mean']:.{nd}f} ± {v['std']:.{nd}f}"


def block(section: dict, rows, arms: list[str], title: str) -> list[str]:
    out = [
        f"### {title}",
        "",
        "| metric | " + " | ".join(ARM_LABEL[a] for a in arms) + " |",
        "|" + "---|" * (len(arms) + 1),
    ]
    for key, label, nd in rows:
        vals = section.get(key, {})
        out.append(f"| {label} | " + " | ".join(cell(vals.get(a), nd) for a in arms) + " |")
    return out + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exp", default="D1")
    ap.add_argument("--split", default="test")
    args = ap.parse_args()

    src = RUNS_DIR / f"domain_gap_{args.exp}_{args.split}.json"
    d = json.loads(src.read_text(encoding="utf-8"))
    arms = list(d["arms"])
    bm = d["build_meta"]

    lines = [
        f"# Step 6.1A — mesh sharp edge → Curve Token (oracle grouping, {args.split})",
        "",
        f"Frozen C2 backbone with {args.exp} heads, seeds {d['seeds']} (mean ± std over seeds). "
        f"All arms evaluate the **same {d['n_curves_evaluated']} curves** with the same "
        "checkpoints; only the 32 input points differ.",
        "",
        f"- Oracle (to be replaced in 6.1B): {'; '.join(bm['oracle'])}",
        f"- Purely mesh-derived: {'; '.join(bm['mesh_derived'])}",
        "",
        "## Coverage: which B-Rep curves survive the mesh path",
        "",
        "A B-Rep edge whose dihedral is below the 30° sharp threshold cannot appear in the "
        "mesh sharp-edge set at all, so it is not a detection failure — it is out of scope "
        "for an edge-based pipeline.",
        "",
        "| type | GT curves | B-Rep sharp | recovered | recall of all | recall of B-Rep sharp |",
        "|---|---|---|---|---|---|",
    ]
    for t, c in bm["coverage_by_type"].items():
        lines.append(
            f"| {t} | {c['gt']} | {c['gt_brep_sharp']} | {c['recovered']} | "
            f"{c['rate_of_all']:.1%} | {c['rate_of_brep_sharp']:.1%} |"
        )
    tot = bm["totals"]
    lines += [
        f"| **all** | {bm['n_curves_total']} | — | {bm['n_curves_recovered']} | "
        f"{bm['n_curves_recovered'] / max(bm['n_curves_total'], 1):.1%} | — |",
        "",
        f"Mesh sharp segments: {tot['n_segments']} total, "
        f"{tot['n_segments_assigned']} assigned to a B-Rep curve "
        f"({tot['n_segments_assigned'] / max(tot['n_segments'], 1):.2%}).",
        "",
        "## Step 6.2 — how the mesh input differs from the exact input",
        "",
        "Canonical frame (bbox diagonal = 6.0).",
        "",
        "| type | n | max position dev (med / p90) | tangent angle° (med / p90) | "
        "spacing CV B-Rep / mesh | mesh points per curve (med) |",
        "|---|---|---|---|---|---|",
    ]
    for t, s in d["input_difference"].items():
        pos, ang = s["position_dev_canonical"], s["tangent_angle_deg"]
        cg, cm = s["spacing_cv_gt"], s["spacing_cv_mesh"]
        lines.append(
            f"| {t} | {s['n']} | {pos['median']:.5f} / {pos['p90']:.5f} | "
            f"{ang['median']:.3f} / {ang['p90']:.3f} | "
            f"{cg['median']:.4f} / {cm['median']:.4f} | {s['n_mesh_points']['median']:.0f} |"
        )
    lines += [
        "",
        "## Model behaviour on the recovered subset",
        "",
    ]
    lines += block(d["classification"], CLS_ROWS, arms, "Classification")
    lines += block(d["geometry"], GEO_ROWS, arms, "Geometry / parameters")

    out = RUNS_DIR / f"REPORT_STEP61A_{args.exp}_{args.split}.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"[report] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
