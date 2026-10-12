#!/usr/bin/env python3
"""Aggregate held-out decode reports: main table + pairwise win matrix."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEC = ROOT / "ours3" / "spatiallm_curve_token_v1" / "heldout_decode"
OUT = ROOT / "ours3" / "spatiallm_curve_token_v1" / "runs" / "heldout" / "TABLE_HELDOUT_S0.md"
ARMS = ("B0", "B1n", "B1b", "M2")


def _fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def main() -> int:
    reports = {}
    by_id = {}
    for arm in ARMS:
        p = DEC / f"{arm.lower()}_s0" / "report.json"
        if not p.is_file():
            continue
        r = json.loads(p.read_text())
        reports[arm] = r
        by_id[arm] = {s["id"]: s for s in r.get("samples", [])}

    lines = [
        "# Held-out test (seed=0) — B0 / B1-native / B1-budget / M2",
        "",
        "split 2236/280/280, surface_points=4096, max_new_tokens=4096, freeze_point_tower=true.",
        "",
        "## Main (n=280 test)",
        "",
        "| arm | exact↑ | op F1↑ | STEP↑ | under-gen↓ | Chamfer↓ | MAX_LEN |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        r = reports.get(arm)
        if not r:
            lines.append(f"| {arm} | — | — | — | — | — | — |")
            continue
        lines.append(
            f"| {arm} | {_fmt(r.get('exact_match_rate'))} | {_fmt(r.get('mean_op_f1'))} | "
            f"{_fmt(r.get('step_valid_rate'))} | {_fmt(r.get('under_generation_rate'))} | "
            f"{_fmt(r.get('mean_chamfer_norm'), 4)} | {_fmt(r.get('max_length_rate'), 2)} |"
        )

    # strata from first available arm that has by_* keys
    for key, title in (
        ("by_gt_len_bucket", "By GT length"),
        ("by_K_bucket", "By curve-token count K"),
    ):
        lines += ["", f"## {title}", ""]
        # union buckets
        buckets = []
        for arm in ARMS:
            buckets.extend((reports.get(arm) or {}).get(key, {}).keys())
        buckets = sorted(set(buckets))
        if not buckets:
            lines.append("_pending decode_")
            continue
        header = "| bucket | " + " | ".join(f"{a} exact" for a in ARMS) + " |"
        sep = "|---|" + "|".join(["---:"] * len(ARMS)) + "|"
        lines += [header, sep]
        for b in buckets:
            cells = []
            for arm in ARMS:
                cell = (reports.get(arm) or {}).get(key, {}).get(b)
                cells.append(_fmt(cell["exact"]) if cell else "—")
            lines.append(f"| {b} | " + " | ".join(cells) + " |")

    # pairwise exact wins
    if len(by_id) >= 2:
        lines += [
            "",
            "## Pairwise exact wins (row beats column)",
            "",
            "| | " + " | ".join(ARMS) + " |",
            "|---|" + "|".join(["---:"] * len(ARMS)) + "|",
        ]
        ids = set.intersection(*[set(by_id[a]) for a in by_id])
        for a in ARMS:
            if a not in by_id:
                continue
            row = [a]
            for b in ARMS:
                if b not in by_id:
                    row.append("—")
                    continue
                if a == b:
                    row.append("—")
                    continue
                win = sum(
                    1
                    for i in ids
                    if by_id[a][i].get("exact_match") and not by_id[b][i].get("exact_match")
                )
                lose = sum(
                    1
                    for i in ids
                    if by_id[b][i].get("exact_match") and not by_id[a][i].get("exact_match")
                )
                row.append(f"{win}/{lose}")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")
        lines.append(f"cells = wins/losses on exact_match over n={len(ids)} paired ids.")

    lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
