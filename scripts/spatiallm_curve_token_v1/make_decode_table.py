#!/usr/bin/env python3
"""Summarize curve100 decode reports into TABLE_DECODE_CURVE100.md.

Main table uses max_new_tokens=4096. Reports both:
  - all 100 samples
  - 96 samples with GT CAD tokens <= 2048
2048-budget results live under decode_max2048 / TABLE_DECODE_CURVE100_max2048.md.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DECODE = ROOT / "ours3" / "spatiallm_curve_token_v1" / "decode"
DECODE_2048 = ROOT / "ours3" / "spatiallm_curve_token_v1" / "decode_max2048"
OUT = ROOT / "ours3" / "spatiallm_curve_token_v1" / "runs" / "TABLE_DECODE_CURVE100.md"


def _fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def _row(r: dict) -> str:
    return (
        f"| {r.get('arm')} | {r.get('n_samples')} | "
        f"{_fmt(r.get('exact_match_rate'), 3)} | {_fmt(r.get('mean_op_f1'), 3)} | "
        f"{_fmt(r.get('mean_op_recall'), 3)} | "
        f"{_fmt(r.get('mean_predicted_op_count_over_gt_op_count'), 2)} | "
        f"{_fmt(r.get('under_generation_rate'), 3)} | "
        f"{_fmt(r.get('step_valid_rate'), 3)} | "
        f"{_fmt(r.get('mean_chamfer_norm'), 4)} | "
        f"{_fmt(r.get('mean_hausdorff_95_norm'), 4)} | "
        f"{_fmt(r.get('eos_rate'), 2)} | {_fmt(r.get('max_length_rate'), 2)} |"
    )


def _load_arm(base: Path, arm: str, filtered: bool) -> dict | None:
    name = "report_gt_le2048.json" if filtered else "report.json"
    p = base / arm.lower() / name
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> int:
    header = (
        "| arm | n | exact | op F1 | op recall | pred/gt ops | under-gen | "
        "STEP valid | Chamfer↓ | H95↓ | EOS | MAX_LEN |"
    )
    sep = "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"

    lines = [
        "# Curve100 overfit decode — B0 / B1 / M2 (max_new_tokens=4096)",
        "",
        "Same 100 CADs the arms memorized. **Main eval budget is 4096**",
        "(separates output-length hard caps from content failures).",
        "Appendix: `TABLE_DECODE_CURVE100_max2048.md` / `decode_max2048/`.",
        "",
        "## All 100",
        "",
        header,
        sep,
    ]
    for arm in ("B0", "B1", "M2"):
        r = _load_arm(DECODE, arm, filtered=False)
        if r:
            lines.append(_row(r))

    lines += [
        "",
        "## Exclude GT length > 2048 (n=96)",
        "",
        "Drops the 4 CADs whose GT DSL exceeds the old 2048 generation budget",
        "(`deepcad__0029_00298546`, `fusion360__23658_*`, `fusion360__36066_*`,",
        "`fusion360__38288_*`). Remaining failures are content, not length-cap.",
        "",
        header,
        sep,
    ]
    for arm in ("B0", "B1", "M2"):
        r = _load_arm(DECODE, arm, filtered=True)
        if r:
            lines.append(_row(r))

    # Optional appendix block if 2048 archive still present
    if (DECODE_2048 / "b0" / "report.json").is_file():
        lines += [
            "",
            "## Appendix — previous max_new_tokens=2048 (all 100)",
            "",
            header,
            sep,
        ]
        for arm in ("B0", "B1", "M2"):
            r = _load_arm(DECODE_2048, arm, filtered=False)
            if r:
                lines.append(_row(r))

    lines.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text(encoding="utf-8"))
    print(f"[wrote] {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
