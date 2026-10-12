#!/usr/bin/env python3
"""Paper main table for heldout_best_v2 (best-val decode only).

Metrics: best step / best val CE, exact, op F1, STEP valid, under/over-gen,
Chamfer mean/median/P90, common STEP-valid Chamfer, token counts, paired
bootstrap 95% CIs. Never reads last-ckpt decode dirs.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "ours3" / "spatiallm_curve_token_v1" / "runs" / "heldout_best_v2"
DEC = RUN / "decode"
OUT = RUN / "TABLE.md"
ARMS = ("B0", "B1n", "B1b", "M2")
ARM_DIR = {
    "B0": RUN / "b0",
    "B1n": RUN / "b1_native",
    "B1b": RUN / "b1_budget_match",
    "M2": RUN / "m2",
}
N_BOOT = 10000
BOOT_SEED = 42


def _fmt(x, nd=3):
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{x:.{nd}f}"
    return str(x)


def _ci_fmt(point, lo, hi, nd=3):
    if point is None:
        return "—"
    return f"{point:.{nd}f} [{lo:.{nd}f}, {hi:.{nd}f}]"


def _load_selection(arm: str) -> dict | None:
    p = ARM_DIR[arm] / "best_model" / "selection.json"
    if not p.is_file():
        p = ARM_DIR[arm] / "selection.json"
    if not p.is_file():
        return None
    return json.loads(p.read_text())


def _chamfers(samples: list[dict]) -> np.ndarray:
    vals = [
        s["geometry"]["chamfer_norm"]
        for s in samples
        if "chamfer_norm" in s.get("geometry", {})
    ]
    return np.asarray(vals, dtype=np.float64)


def _metric_from_rows(rows: list[dict], name: str):
    n = len(rows)
    if n == 0:
        return None
    if name == "exact":
        return float(np.mean([bool(r.get("exact_match")) for r in rows]))
    if name == "op_f1":
        return float(np.mean([r.get("op_f1", 0.0) for r in rows]))
    if name == "step":
        return float(np.mean([bool(r.get("step_ok")) for r in rows]))
    if name == "under":
        return float(np.mean([bool(r.get("under_generation")) for r in rows]))
    if name == "over":
        return float(
            np.mean(
                [
                    r.get("over_generation", False)
                    or (
                        r.get("predicted_op_count", 0) > r.get("gt_op_count", 0)
                        and r.get("gt_op_count", 0) > 0
                    )
                    for r in rows
                ]
            )
        )
    if name == "cd_mean":
        c = _chamfers(rows)
        return None if c.size == 0 else float(c.mean())
    if name == "cd_median":
        c = _chamfers(rows)
        return None if c.size == 0 else float(np.median(c))
    if name == "cd_p90":
        c = _chamfers(rows)
        return None if c.size == 0 else float(np.percentile(c, 90))
    raise KeyError(name)


def _paired_bootstrap(by_arm: dict[str, dict], metric: str) -> dict:
    """Paired over the intersection of ids; 95% percentile CI."""
    ids = set.intersection(*[set(by_arm[a]) for a in by_arm]) if by_arm else set()
    ids = sorted(ids)
    n = len(ids)
    rng = np.random.default_rng(BOOT_SEED)
    out = {a: {} for a in by_arm}
    if n == 0:
        return out
    rows = {a: [by_arm[a][i] for i in ids] for a in by_arm}
    point = {a: _metric_from_rows(rows[a], metric) for a in by_arm}
    draws = {a: [] for a in by_arm}
    idx = np.arange(n)
    for _ in range(N_BOOT):
        take = rng.choice(idx, size=n, replace=True)
        for a in by_arm:
            boot_rows = [rows[a][j] for j in take]
            draws[a].append(_metric_from_rows(boot_rows, metric))
    for a in by_arm:
        arr = np.asarray(draws[a], dtype=np.float64)
        arr = arr[np.isfinite(arr)]
        if arr.size == 0 or point[a] is None:
            out[a] = {"point": point[a], "lo": None, "hi": None}
            continue
        out[a] = {
            "point": point[a],
            "lo": float(np.percentile(arr, 2.5)),
            "hi": float(np.percentile(arr, 97.5)),
        }
    return out


def main() -> int:
    reports = {}
    by_id = {}
    selections = {}
    for arm in ARMS:
        sel = _load_selection(arm)
        if sel:
            selections[arm] = sel
        p = DEC / arm.lower() / "report.json"
        if not p.is_file():
            continue
        r = json.loads(p.read_text())
        reports[arm] = r
        by_id[arm] = {s["id"]: s for s in r.get("samples", [])}

    lines = [
        "# Held-out best_v2 — paper Gate (best-val only)",
        "",
        "Init: original SpatialLM1.1-Llama-1B. Checkpoint = min val eval_loss. "
        "Decode: do_sample=false, num_beams=1, max_new_tokens=4096, test n=280. "
        "Test was **not** used for checkpoint selection. Old `runs/heldout/` last-ckpt "
        "runs are diagnostic only and are not in this table.",
        "",
        "## Selection (val CE)",
        "",
        "| arm | best step | best val CE | checkpoint | test used? |",
        "|---|---:|---:|---|---|",
    ]
    for arm in ARMS:
        sel = selections.get(arm)
        if not sel:
            lines.append(f"| {arm} | — | — | — | — |")
            continue
        lines.append(
            f"| {arm} | {_fmt(sel.get('best_step'), 0)} | {_fmt(sel.get('best_metric'), 4)} | "
            f"`{Path(sel.get('best_checkpoint') or '').name}` | "
            f"{sel.get('test_used_for_selection')} |"
        )

    metrics = (
        ("exact", "exact↑", 3),
        ("op_f1", "op F1↑", 3),
        ("step", "STEP valid↑", 3),
        ("under", "under-gen↓", 3),
        ("over", "over-gen↓", 3),
        ("cd_mean", "CD mean↓", 4),
        ("cd_median", "CD median↓", 4),
        ("cd_p90", "CD P90↓", 4),
    )
    boot = {name: _paired_bootstrap(by_id, name) for name, *_ in metrics} if by_id else {}

    lines += [
        "",
        "## Main (n=280 test, paired bootstrap 95% CI)",
        "",
        "| arm | " + " | ".join(label for _, label, _ in metrics) + " |",
        "|---|" + "|".join(["---:"] * len(metrics)) + "|",
    ]
    for arm in ARMS:
        if arm not in reports:
            lines.append("| " + arm + " | " + " | ".join("—" for _ in metrics) + " |")
            continue
        cells = []
        for name, _, nd in metrics:
            b = boot[name].get(arm, {})
            cells.append(_ci_fmt(b.get("point"), b.get("lo"), b.get("hi"), nd=nd))
        lines.append(f"| {arm} | " + " | ".join(cells) + " |")

    # common STEP-valid Chamfer
    lines += [
        "",
        "## Chamfer on common STEP-valid subset",
        "",
        "| arm | n | CD mean | CD median | CD P90 |",
        "|---|---:|---:|---:|---:|",
    ]
    if len(by_id) >= 2:
        ids = set.intersection(*[set(by_id[a]) for a in by_id])
        common_ok = [
            i
            for i in ids
            if all(bool(by_id[a][i].get("step_ok")) for a in by_id)
        ]
        for arm in ARMS:
            if arm not in by_id:
                lines.append(f"| {arm} | — | — | — | — |")
                continue
            rows = [by_id[arm][i] for i in common_ok]
            c = _chamfers(rows)
            if c.size == 0:
                lines.append(f"| {arm} | {len(common_ok)} | — | — | — |")
            else:
                lines.append(
                    f"| {arm} | {len(common_ok)} | {_fmt(float(c.mean()), 4)} | "
                    f"{_fmt(float(np.median(c)), 4)} | {_fmt(float(np.percentile(c, 90)), 4)} |"
                )
        lines.append("")
        lines.append(
            f"Intersection of ids where **every** decoded arm is STEP-valid (n={len(common_ok) if len(by_id) >= 2 else 0})."
        )
    else:
        lines.append("| — | — | — | — | — |")

    lines += [
        "",
        "## Token budget",
        "",
        "| arm | mean surface voxels | mean 2nd-stream tokens | mean pred tokens | mean GT CAD tokens | mean K |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for arm in ARMS:
        r = reports.get(arm)
        if not r:
            lines.append(f"| {arm} | — | — | — | — | — |")
            continue
        samples = r.get("samples") or []
        gt_tok = [s.get("gt_cad_tokens") for s in samples if s.get("gt_cad_tokens") is not None]
        k = [s.get("curve_token_K") for s in samples if s.get("curve_token_K") is not None]
        lines.append(
            f"| {arm} | {_fmt(r.get('mean_surface_voxels'), 1)} | "
            f"{_fmt(r.get('mean_second_stream_tokens'), 1)} | "
            f"{_fmt(r.get('mean_pred_tokens'), 1)} | "
            f"{_fmt(float(np.mean(gt_tok)) if gt_tok else None, 1)} | "
            f"{_fmt(float(np.mean(k)) if k else None, 1)} |"
        )

    lines.append("")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(OUT.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
