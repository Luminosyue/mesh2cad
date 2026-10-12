#!/usr/bin/env python3
"""Aggregate D0/D1 seed replicates into mean ± std tables (test split)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_token_head_v1.config import EXPERIMENTS, RUNS_DIR, SPLIT_NAME  # noqa: E402

CLS_COLS = [
    ("macro_f1", "Macro F1", 4),
    ("balanced_accuracy", "Bal Acc", 4),
    ("LINE_f1", "LINE F1", 4),
    ("CIRCLE_f1", "CIRCLE F1", 4),
    ("ELLIPSE_f1", "ELLIPSE F1", 4),
    ("BSPLINE_f1", "BSPLINE F1", 4),
    ("line_to_circle_fp", "L→C FP", 1),
]
GEO_COLS = [
    ("recon_chamfer_median", "Chamfer (med)", 5),
    ("line_dir_deg", "LINE dir°", 2),
    ("circle_normal_deg", "CIRCLE n°", 2),
    ("circle_radius_rel", "CIRCLE r rel", 4),
    ("ellipse_major_axis_deg", "ELLIPSE maj°", 2),
    ("bspline_degree_correct", "BSPL deg acc", 3),
]


def cell(vals: list, nd: int) -> str:
    vals = [v for v in vals if v is not None]
    if not vals:
        return "—"
    a = np.asarray(vals, dtype=np.float64)
    if len(a) == 1:
        return f"{a[0]:.{nd}f}"
    return f"{a.mean():.{nd}f} ± {a.std(ddof=0):.{nd}f}"


def table(per_exp: dict, cols, title: str) -> list[str]:
    lines = [
        f"### {title}",
        "",
        "| Exp | n seeds | " + " | ".join(h for _, h, _ in cols) + " |",
        "|" + "---|" * (len(cols) + 2),
    ]
    for exp, runs in per_exp.items():
        cells = [cell([r["test"].get(k) for r in runs], nd) for k, _, nd in cols]
        lines.append(f"| {exp} | {len(runs)} | " + " | ".join(cells) + " |")
    return lines + [""]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--seeds", nargs="+", type=int, default=[0, 1, 2])
    args = ap.parse_args()

    per_exp: dict[str, list[dict]] = {}
    for exp in sorted(EXPERIMENTS):
        runs = []
        for s in args.seeds:
            p = RUNS_DIR / f"{exp}_{SPLIT_NAME}_seed{s}" / "metrics.json"
            if p.is_file():
                r = json.loads(p.read_text(encoding="utf-8"))
                r["seed"] = s
                runs.append(r)
        if runs:
            per_exp[exp] = runs
    if not per_exp:
        raise SystemExit(f"no seed runs under {RUNS_DIR}")

    lines = [
        "# CURVE_TOKEN_HEAD_V1 — Step 4 key experiment (frozen C2, frozen_v1 test)",
        "",
        f"Seeds: {args.seeds}. Values are mean ± std over seeds.",
        "",
    ]
    for exp, runs in per_exp.items():
        lines.append(f"- **{exp}**: {runs[0]['spec']['desc']}")
    lines.append("")
    lines += table(per_exp, CLS_COLS, "Classification")
    lines += table(per_exp, GEO_COLS, "Geometry / parameters (median)")

    lines += ["### Per-seed Macro F1", "", "| Exp | " + " | ".join(
        f"seed {s}" for s in args.seeds) + " |", "|" + "---|" * (len(args.seeds) + 1)]
    for exp, runs in per_exp.items():
        by_seed = {r["seed"]: r["test"]["macro_f1"] for r in runs}
        lines.append(
            f"| {exp} | "
            + " | ".join(
                f"{by_seed[s]:.4f}" if s in by_seed else "—" for s in args.seeds
            )
            + " |"
        )
    lines.append("")

    d0 = per_exp.get("D0", [])
    d1 = per_exp.get("D1", [])
    if d0 and d1:
        m0 = np.array([r["test"]["macro_f1"] for r in d0])
        m1 = np.array([r["test"]["macro_f1"] for r in d1])
        spread = max(m0.std(ddof=0), m1.std(ddof=0))
        delta = m1.mean() - m0.mean()
        verdict = (
            "within seed noise — adding geometry supervision does not measurably "
            "change classification"
            if abs(delta) <= spread
            else ("geometry supervision helps classification" if delta > 0
                  else "geometry supervision costs classification")
        )
        ch = [r["test"]["recon_chamfer_median"] for r in d1]
        lines += [
            "### Verdict",
            "",
            f"- Macro F1 delta (D1 − D0) = {delta:+.4f}; max per-arm seed std = {spread:.4f} "
            f"→ **{verdict}**.",
            f"- D1 adds geometry the token did not expose before: reconstruction Chamfer "
            f"median {np.mean(ch):.5f} in curve-local units.",
            "",
        ]

    out = RUNS_DIR / "TABLE_D0D1_SEEDS_TEST.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"[table] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
