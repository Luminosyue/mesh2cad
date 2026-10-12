#!/usr/bin/env python3
"""Collect the three arms' loss curves into one comparison table.

Reads `trainer_state.json` from each arm's latest checkpoint rather than the
stdout logs: a checkpoint's `log_history` belongs to exactly one training
process, so it stays clean even when a log file was appended to by more than one
run.
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from spatiallm_curve_token_v1.config import (  # noqa: E402
    RUNS_DIR,
    SCHEMA_VERSION,
    SPATIALLM_ROOT,
)

ARMS = {
    "B0": ("curve100_b0_surface", "surface only"),
    "B1": ("curve100_b1_edgepoints", "surface + sharp edge POINT tokens"),
    "M2": ("curve100_m2_curvetoken", "surface + CURVE tokens (ours)"),
}
THRESHOLDS = (10.0, 5.0, 2.0, 1.0, 0.5, 0.1, 0.01)


def read_arm(save_name: str) -> dict:
    save_dir = SPATIALLM_ROOT / "saves" / save_name
    states = sorted(
        glob.glob(str(save_dir / "checkpoint-*" / "trainer_state.json")),
        key=lambda p: int(p.split("checkpoint-")[1].split("/")[0]),
    )
    if not states:
        return {}
    state = json.loads(Path(states[-1]).read_text(encoding="utf-8"))
    hist = [e for e in state["log_history"] if "loss" in e]
    evals = [e for e in state["log_history"] if "eval_loss" in e]
    curve = [(e["epoch"], e["loss"]) for e in hist]
    out = {
        "checkpoint": Path(states[-1]).parent.name,
        "global_step": state["global_step"],
        "max_steps": state.get("max_steps"),
        "finished": state["global_step"] == state.get("max_steps"),
        "curve": curve,
        "last_loss": curve[-1][1] if curve else None,
        "min_loss": min((l for _, l in curve), default=None),
        "last_epoch": curve[-1][0] if curve else None,
        "min_eval_loss": min((e["eval_loss"] for e in evals), default=None),
    }
    for thr in THRESHOLDS:
        out[f"epoch_to_{thr}"] = next((e for e, l in curve if l < thr), None)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=RUNS_DIR / "TABLE_CURVE100.md")
    args = ap.parse_args()

    results = {arm: {**read_arm(sv), "desc": desc} for arm, (sv, desc) in ARMS.items()}

    def f(v, nd=4):
        if v is None:
            return "—"
        return f"{v:,}" if isinstance(v, int) else f"{v:.{nd}f}"

    lines = [
        "# Curve Token overfit probe — 100 CADs (80 DeepCAD + 20 Fusion360)",
        "",
        "Same 100 CADs, same prompts, same budget; train == eval by design. The "
        "question is whether the LLM can exploit the Curve Token stream, not "
        "whether it generalizes.",
        "",
        "| arm | second stream | step | min train loss | last train loss | min eval loss |",
        "|---|---|---|---|---|---|",
    ]
    for arm, r in results.items():
        step = (
            f"{r.get('global_step', 0):,}/{r.get('max_steps') or 0:,}"
            if r.get("global_step")
            else "—"
        )
        lines.append(
            f"| {arm} | {r['desc']} | {step} | {f(r.get('min_loss'))} | "
            f"{f(r.get('last_loss'))} | {f(r.get('min_eval_loss'))} |"
        )

    lines += [
        "",
        "All arms memorize 100 CADs, so the final loss cannot separate them. "
        "Convergence speed can:",
        "",
        "## First epoch reaching a train loss below",
        "",
        "| arm | " + " | ".join(f"{t}" for t in THRESHOLDS) + " |",
        "|" + "---|" * (len(THRESHOLDS) + 1),
    ]
    for arm, r in results.items():
        lines.append(
            f"| {arm} | "
            + " | ".join(f(r.get(f"epoch_to_{t}"), 1) for t in THRESHOLDS)
            + " |"
        )

    lines += ["", "## Loss by epoch", "", "| epoch | " + " | ".join(ARMS) + " |",
              "|" + "---|" * (len(ARMS) + 1)]
    by_epoch: dict[int, dict[str, float]] = {}
    for arm, r in results.items():
        for ep, loss in r.get("curve", []):
            if abs(ep - round(ep)) < 1e-6 and round(ep) % 2 == 0:
                by_epoch.setdefault(int(round(ep)), {})[arm] = loss
    for ep in sorted(by_epoch):
        row = by_epoch[ep]
        lines.append(
            f"| {ep} | "
            + " | ".join(f"{row[a]:.4f}" if a in row else "—" for a in ARMS)
            + " |"
        )
    lines.append("")

    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (RUNS_DIR / "curve100_results.json").write_text(
        json.dumps({"schema_version": SCHEMA_VERSION, "arms": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    print("\n".join(lines))
    print(f"[collect] wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
