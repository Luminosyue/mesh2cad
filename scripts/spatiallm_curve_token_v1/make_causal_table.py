#!/usr/bin/env python3
"""Build TABLE_CAUSAL_M2.md from causal_m2/*/report.json (+ reuse decode/m2 as correct).

Prefer max_new_tokens=4096 for correct / shuffle. drop / zero may remain at 2048
(gap already decisive); annotate budget per row.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAUSAL = ROOT / "ours3" / "spatiallm_curve_token_v1" / "causal_m2"
CAUSAL_2048 = ROOT / "ours3" / "spatiallm_curve_token_v1" / "causal_m2_max2048"
DECODE_M2 = ROOT / "ours3" / "spatiallm_curve_token_v1" / "decode" / "m2"
OUT = ROOT / "ours3" / "spatiallm_curve_token_v1" / "runs" / "TABLE_CAUSAL_M2.md"


def _fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def _load_variant(v: str) -> dict | None:
    p = CAUSAL / v / "report.json"
    if p.is_file():
        return json.loads(p.read_text())
    # Fallback: seed correct from fresh M2 decode
    if v == "correct" and (DECODE_M2 / "report.json").is_file():
        src = json.loads((DECODE_M2 / "report.json").read_text())
        src["causal_variant"] = "correct"
        src["arm"] = "M2"
        CAUSAL.joinpath("correct").mkdir(parents=True, exist_ok=True)
        (CAUSAL / "correct" / "report.json").write_text(json.dumps(src, indent=2) + "\n")
        return src
    # Legacy 2048 archive for drop/zero
    p2048 = CAUSAL_2048 / v / "report.json"
    if p2048.is_file():
        r = json.loads(p2048.read_text())
        r["_from_archive_2048"] = True
        return r
    return None


def main() -> int:
    lines = [
        "# M2 free causal test (frozen checkpoint, no retrain)",
        "",
        "Question: on the overfit 100 CADs, does the model actually read curve tokens?",
        "",
        "Budgets: **correct / shuffle re-run at max_new_tokens=4096**; drop / zero",
        "kept from the 2048 archive when not re-run (gap already large).",
        "",
        "| variant | budget | n | exact↑ | op F1↑ | STEP↑ | under-gen↓ | Chamfer↓ | MAX_LEN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for v in ("correct", "drop", "zero", "shuffle"):
        r = _load_variant(v)
        if r is None:
            lines.append(f"| M2-{v} | — | — | — | — | — | — | — | — |")
            continue
        budget = r.get("max_new_tokens", "—")
        if r.get("_from_archive_2048"):
            budget = f"{budget}†"
        filt = r.get("subset")
        n = r.get("n_samples")
        lines.append(
            f"| M2-{v} | {budget} | {n} | {_fmt(r.get('exact_match_rate'))} | "
            f"{_fmt(r.get('mean_op_f1'))} | {_fmt(r.get('step_valid_rate'))} | "
            f"{_fmt(r.get('under_generation_rate'))} | {_fmt(r.get('mean_chamfer_norm'), 4)} | "
            f"{_fmt(r.get('max_length_rate'), 2)} |"
        )
        # Optional filtered companion if present
        p_le = CAUSAL / v / "report_gt_le2048.json"
        if p_le.is_file():
            rf = json.loads(p_le.read_text())
            lines.append(
                f"| M2-{v} (GT≤2048) | {rf.get('max_new_tokens', budget)} | "
                f"{rf.get('n_samples')} | {_fmt(rf.get('exact_match_rate'))} | "
                f"{_fmt(rf.get('mean_op_f1'))} | {_fmt(rf.get('step_valid_rate'))} | "
                f"{_fmt(rf.get('under_generation_rate'))} | "
                f"{_fmt(rf.get('mean_chamfer_norm'), 4)} | "
                f"{_fmt(rf.get('max_length_rate'), 2)} |"
            )

    lines += [
        "",
        "† from `causal_m2_max2048/` (not re-decoded at 4096).",
        "",
        "## Reading",
        "",
        "- If **drop / zero / shuffle ≈ correct**: surface stream carries the memorization;",
        "  curve tokens are not causally used (Gate can still pass; do not claim curve prior is learned).",
        "- If **shuffle / zero / drop collapse**: model depends on the curve stream content.",
        "",
        "Full 2048 causal table: `TABLE_CAUSAL_M2_max2048.md`.",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
