#!/usr/bin/env python3
"""Aggregate 4-way Dora edge ablation decode reports."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUT = ROOT / "ours3/deepcad_train100_edge_ablation_val_decode"

VARIANTS = ["baseline", "edge_zero", "edge_shuffle", "ours"]
LABELS = {
    "baseline": "6ch Base",
    "edge_zero": "7ch Zero",
    "edge_shuffle": "7ch Shuffle",
    "ours": "7ch Real",
}
KEYS = [
    "exact_match_rate",
    "mean_op_recall",
    "mean_op_f1",
    "dsl_parse_valid_rate",
    "step_valid_rate",
    "mean_chamfer_norm",
    "mean_hausdorff_95_norm",
    "mean_volume_error",
    "n_samples",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--decode-root", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()
    out = args.decode_root

    summary = {}
    maps = {}
    for v in VARIANTS:
        rep = json.loads((out / v / "report.json").read_text())
        summary[v] = {k: rep.get(k) for k in KEYS}
        maps[v] = {s["sample_id"]: s for s in rep["samples"]}

    cmp = {"summary": summary, "per_sample": []}
    for sid in sorted(set().union(*(m.keys() for m in maps.values()))):
        row: dict = {"sample_id": sid}
        for v in VARIANTS:
            s = maps[v].get(sid, {})
            g = s.get("geometry") or {}
            row[v] = {
                "exact": s.get("exact_match"),
                "op_recall": s.get("op_recall"),
                "chamfer": g.get("chamfer_norm"),
                "step_ok": s.get("step_ok"),
            }
        cmp["per_sample"].append(row)

    (out / "comparison.json").write_text(json.dumps(cmp, indent=2) + "\n")

    def fmt(x):
        if x is None:
            return "—"
        if isinstance(x, float):
            return f"{x:.4f}"
        return str(x)

    lines = [
        "# Dora Edge Ablation — Canonical Train100 Val (n=19)",
        "",
        "## Summary",
        "",
        "| Method | exact | op_recall | op_f1 | parse | STEP | Chamfer | H95 | vol_err |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in VARIANTS:
        s = summary[v]
        lines.append(
            f"| {LABELS[v]} | {fmt(s['exact_match_rate'])} | {fmt(s['mean_op_recall'])} | "
            f"{fmt(s['mean_op_f1'])} | {fmt(s['dsl_parse_valid_rate'])} | {fmt(s['step_valid_rate'])} | "
            f"{fmt(s['mean_chamfer_norm'])} | {fmt(s['mean_hausdorff_95_norm'])} | "
            f"{fmt(s['mean_volume_error'])} |"
        )
    lines += ["", "## Key comparison: Zero vs Shuffle vs Real", ""]
    z, sh, r = summary["edge_zero"], summary["edge_shuffle"], summary["ours"]
    for k in ["mean_op_recall", "mean_chamfer_norm", "step_valid_rate"]:
        lines.append(f"- **{k}**: Zero={z.get(k)} Shuffle={sh.get(k)} Real={r.get(k)}")
    text = "\n".join(lines) + "\n"
    (out / "comparison.md").write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
