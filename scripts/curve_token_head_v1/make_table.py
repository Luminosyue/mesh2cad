#!/usr/bin/env python3
"""Render the Step-4 D0 vs D1 comparison table (test split)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_token_head_v1.config import EXPERIMENTS, RUNS_DIR, SPLIT_NAME  # noqa: E402

CLS_COLS = [
    ("macro_f1", "Macro F1", "{:.4f}"),
    ("balanced_accuracy", "Bal Acc", "{:.4f}"),
    ("LINE_f1", "LINE F1", "{:.4f}"),
    ("CIRCLE_f1", "CIRCLE F1", "{:.4f}"),
    ("ELLIPSE_f1", "ELLIPSE F1", "{:.4f}"),
    ("BSPLINE_f1", "BSPLINE F1", "{:.4f}"),
    ("line_to_circle_fp", "L→C FP", "{}"),
]
GEO_COLS = [
    ("recon_chamfer_median", "Chamfer (med)", "{:.5f}"),
    ("line_dir_deg", "LINE dir°", "{:.2f}"),
    ("circle_normal_deg", "CIRCLE n°", "{:.2f}"),
    ("circle_radius_rel", "CIRCLE r rel", "{:.4f}"),
    ("ellipse_major_axis_deg", "ELLIPSE maj°", "{:.2f}"),
    ("bspline_degree_correct", "BSPL deg acc", "{:.3f}"),
]


def fmt(v, f):
    return "—" if v is None else f.format(v)


def row(name: str, sc: dict, cols) -> str:
    return "| " + " | ".join([name] + [fmt(sc.get(k), f) for k, _, f in cols]) + " |"


def table(results: dict, cols, title: str) -> list[str]:
    head = "| Exp | " + " | ".join(h for _, h, _ in cols) + " |"
    sep = "|" + "---|" * (len(cols) + 1)
    lines = [f"### {title}", "", head, sep]
    for exp, r in results.items():
        lines.append(row(exp, r["test"], cols))
    return lines + [""]


def main() -> int:
    results = {}
    for exp in sorted(EXPERIMENTS):
        p = RUNS_DIR / f"{exp}_{SPLIT_NAME}" / "metrics.json"
        if p.is_file():
            results[exp] = json.loads(p.read_text(encoding="utf-8"))
    if not results:
        raise SystemExit(f"no metrics.json under {RUNS_DIR}")

    lines = [
        "# CURVE_TOKEN_HEAD_V1 — D0 vs D1 (frozen C2 backbone, frozen_v1 test)",
        "",
        "Backbone frozen as C2: curve-local xyz+tangent+s → PointNet, "
        "log(length) scale branch, fusion → 256-D Curve Token.",
        "",
    ]
    for exp, r in results.items():
        lines.append(f"- **{exp}**: {r['spec']['desc']} (best epoch {r['best_epoch']})")
    lines.append("")
    lines += table(results, CLS_COLS, "Classification")
    lines += table(results, GEO_COLS, "Geometry / parameters (median)")

    detail = ["### Full parameter error stats (test)", ""]
    for exp, r in results.items():
        params = r["test_full"].get("params") or {}
        if not params:
            continue
        detail += [f"**{exp}**", "", "| metric | n | mean | median | p90 |", "|---|---|---|---|---|"]
        for k, st in sorted(params.items()):
            if st is None:
                continue
            detail.append(
                f"| {k} | {st['n']} | {st['mean']:.4f} | {st['median']:.4f} | {st['p90']:.4f} |"
            )
        detail.append("")
    lines += detail

    out = RUNS_DIR / "TABLE_D0D1_TEST.md"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"[table] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
