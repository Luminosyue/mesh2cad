#!/usr/bin/env python3
"""Sequence-budget audit for curve100 B0 / B1 / M2.

Answers whether B1's exact-match drop is explained by edge tokens crowding
the context / generation budget.

Per sample we record:
  - surface input voxels (plugin) and Sonata→LLM surface token count
  - second-stream input size and LLM token count (edge points or curve tokens)
  - text prompt length, GT CAD target length
  - total geometry+prompt tokens into the LLM
  - decode stop_reason / exact / prediction_tokens (from existing decode rows)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch

REPO_ROOT = Path(__file__).resolve().parents[2]
for p in (
    str(REPO_ROOT / "SpatialLM"),
    str(REPO_ROOT / "scripts"),
    str(REPO_ROOT / "scripts" / "deepcad"),
    str(REPO_ROOT / "scripts" / "geometry_pack_v1"),
    str(REPO_ROOT / "scripts" / "separate_edge_tokens_v1"),
):
    if p not in sys.path:
        sys.path.insert(0, p)

from decode_joint_j0_j2 import _load_sepedge, _load_surface_only  # noqa: E402
from separate_edge_tokens_v1.common import (  # noqa: E402
    build_prompt,
    load_model,
    make_plugin,
    set_deterministic_serialization,
)

from spatiallm_curve_token_v1.config import OUTPUT_ROOT, SUBSET_DIR  # noqa: E402
from spatiallm_curve_token_v1.decode_curve100 import (  # noqa: E402
    ARM_CKPT,
    MEDIA_DEFAULT,
    _configure_env,
    _load_m2_checkpoint,
)

DECODE_ROOT = OUTPUT_ROOT / "decode"


@torch.inference_mode()
def _count_geometry_tokens(model, surface, edge, separate_edge: bool) -> dict:
    # loaders return (1, N, C); forward_geometry expects a single-sample (N, C).
    surf = surface[0] if surface.dim() == 3 else surface
    edge_in = None
    if separate_edge and edge is not None:
        edge_in = edge[0] if edge.dim() == 3 else edge
    surf_t, edge_t = model.forward_geometry(
        surf.to(model.device),
        edge_in.to(model.device) if edge_in is not None else None,
        device=model.device,
        dtype=next(model.parameters()).dtype,
    )
    return {
        "surface_llm_tokens": int(surf_t.shape[1]),
        "second_llm_tokens": 0 if edge_t is None else int(edge_t.shape[1]),
    }


def _prompt_len(tokenizer, separate_edge: bool) -> int:
    prompt = build_prompt(separate_edge=separate_edge)
    ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}],
        add_generation_prompt=True,
        return_tensors="pt",
    )
    return int(ids.shape[1])


def audit_arm(arm: str, records: list[dict], media: Path, device: str, dtype: torch.dtype) -> dict:
    _configure_env(arm)
    separate_edge = arm in ("B1", "M2")
    if arm == "M2":
        from spatiallm_curve_token_v1 import curve_token_injector

        curve_token_injector.install()
        model, tokenizer = _load_m2_checkpoint(ARM_CKPT[arm], device, dtype)
    else:
        model, tokenizer = load_model(
            ARM_CKPT[arm],
            separate_edge=separate_edge,
            device=device,
            dtype=dtype,
            freeze_sonata=True,
        )
    set_deterministic_serialization(model.point_backbone)
    model.eval()
    plugin = make_plugin(separate_edge=separate_edge)
    prompt_tokens = _prompt_len(tokenizer, separate_edge=separate_edge)

    decode_report = json.loads((DECODE_ROOT / arm.lower() / "report.json").read_text())
    decode_by_id = {r["id"]: r for r in decode_report["samples"]}

    rows = []
    for rec in records:
        sid = rec["id"]
        npy = media / rec["point_clouds"][0]
        if separate_edge:
            surface, edge = _load_sepedge(plugin, npy)
            second_in = int(edge.shape[1])
        else:
            surface = _load_surface_only(plugin, npy)
            edge = None
            second_in = 0
        surface_in = int(surface.shape[1])
        geom = _count_geometry_tokens(model, surface, edge, separate_edge)
        gt = rec["conversations"][1]["value"]
        gt_tok = len(tokenizer(gt, add_special_tokens=False)["input_ids"])
        dec = decode_by_id.get(sid, {})
        total_in = prompt_tokens + geom["surface_llm_tokens"] + geom["second_llm_tokens"]
        # Remaining room before max_new_tokens budget is independent of context
        # (model max_pos is 131k); the relevant squeeze is generation length vs GT.
        rows.append(
            {
                "id": sid,
                "dataset": rec.get("dataset"),
                "arm": arm,
                "surface_input_voxels": surface_in,
                "second_input_points_or_K": second_in,
                **geom,
                "prompt_tokens": prompt_tokens,
                "total_input_tokens": total_in,
                "gt_cad_tokens": gt_tok,
                "max_new_tokens": 2048,
                "gt_fits_in_max_new": gt_tok <= 2048,
                "headroom_vs_gt": 2048 - gt_tok,
                "exact_match": dec.get("exact_match"),
                "step_ok": dec.get("step_ok"),
                "stop_reason": dec.get("stop_reason"),
                "prediction_tokens": dec.get("prediction_tokens"),
                "op_f1": dec.get("op_f1"),
            }
        )
        print(
            f"[{arm}] {sid}: surf={geom['surface_llm_tokens']} "
            f"2nd={geom['second_llm_tokens']} total_in={total_in} "
            f"gt={gt_tok} stop={dec.get('stop_reason')} exact={dec.get('exact_match')}",
            flush=True,
        )

    def _mean(xs):
        xs = [x for x in xs if x is not None]
        return float(np.mean(xs)) if xs else None

    summary = {
        "arm": arm,
        "n": len(rows),
        "prompt_tokens": prompt_tokens,
        "surface_llm_tokens_mean": _mean([r["surface_llm_tokens"] for r in rows]),
        "surface_llm_tokens_p50": float(np.median([r["surface_llm_tokens"] for r in rows])),
        "surface_llm_tokens_p90": float(np.percentile([r["surface_llm_tokens"] for r in rows], 90)),
        "second_llm_tokens_mean": _mean([r["second_llm_tokens"] for r in rows]),
        "second_llm_tokens_p50": float(np.median([r["second_llm_tokens"] for r in rows])),
        "second_llm_tokens_p90": float(np.percentile([r["second_llm_tokens"] for r in rows], 90)),
        "second_input_mean": _mean([r["second_input_points_or_K"] for r in rows]),
        "total_input_tokens_mean": _mean([r["total_input_tokens"] for r in rows]),
        "gt_cad_tokens_mean": _mean([r["gt_cad_tokens"] for r in rows]),
        "gt_cad_tokens_p90": float(np.percentile([r["gt_cad_tokens"] for r in rows], 90)),
        "gt_cad_tokens_max": int(max(r["gt_cad_tokens"] for r in rows)),
        "gt_exceeds_2048_n": sum(1 for r in rows if not r["gt_fits_in_max_new"]),
        "decode_exact_rate": _mean([float(r["exact_match"]) for r in rows if r["exact_match"] is not None]),
        "decode_max_length_n": sum(1 for r in rows if r.get("stop_reason") == "MAX_LENGTH"),
        "decode_max_length_and_inexact_n": sum(
            1
            for r in rows
            if r.get("stop_reason") == "MAX_LENGTH" and r.get("exact_match") is False
        ),
        # Among inexact: how often MAX_LENGTH?
        "inexact_n": sum(1 for r in rows if r.get("exact_match") is False),
        "inexact_max_length_n": sum(
            1
            for r in rows
            if r.get("exact_match") is False and r.get("stop_reason") == "MAX_LENGTH"
        ),
        # Correlation proxies
        "mean_second_tokens_when_exact": _mean(
            [r["second_llm_tokens"] for r in rows if r.get("exact_match") is True]
        ),
        "mean_second_tokens_when_inexact": _mean(
            [r["second_llm_tokens"] for r in rows if r.get("exact_match") is False]
        ),
        "mean_gt_tokens_when_exact": _mean(
            [r["gt_cad_tokens"] for r in rows if r.get("exact_match") is True]
        ),
        "mean_gt_tokens_when_inexact": _mean(
            [r["gt_cad_tokens"] for r in rows if r.get("exact_match") is False]
        ),
        "mean_surface_tokens_when_exact": _mean(
            [r["surface_llm_tokens"] for r in rows if r.get("exact_match") is True]
        ),
        "mean_surface_tokens_when_inexact": _mean(
            [r["surface_llm_tokens"] for r in rows if r.get("exact_match") is False]
        ),
        "samples": rows,
    }
    return summary


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--arms", nargs="+", default=["B0", "B1", "M2"])
    ap.add_argument("--split-json", type=Path, default=SUBSET_DIR / "curve100_train.json")
    ap.add_argument("--media-dir", type=Path, default=MEDIA_DEFAULT)
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--out", type=Path, default=OUTPUT_ROOT / "runs" / "seq_budget_audit.json")
    args = ap.parse_args()

    records = json.loads(args.split_json.read_text(encoding="utf-8"))
    dtype = getattr(torch, args.dtype)
    all_reports = {}
    for arm in args.arms:
        print(f"=== audit {arm} ===", flush=True)
        all_reports[arm] = audit_arm(arm, records, args.media_dir, args.device, dtype)
        # free GPU between arms
        torch.cuda.empty_cache()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(all_reports, indent=2) + "\n", encoding="utf-8")

    # Markdown table
    md = [
        "# Curve100 sequence-budget audit (B0 / B1 / M2)",
        "",
        "Do edge tokens crowd out CAD generation? `max_new_tokens=2048` for all arms;",
        "geometry is spliced into the prompt (context max_pos=131k — not the bottleneck).",
        "",
        "| arm | surf tokens p50/p90 | 2nd tokens p50/p90 | total_in mean | GT tok p90/max | GT>2048 | MAX_LEN | inexact | inexact∩MAX_LEN | 2nd tok exact→inexact | GT tok exact→inexact |",
        "|---|---|---|---:|---|---:|---:|---:|---:|---|---|",
    ]
    for arm in args.arms:
        r = all_reports[arm]
        md.append(
            f"| {arm} | {r['surface_llm_tokens_p50']:.0f}/{r['surface_llm_tokens_p90']:.0f} | "
            f"{r['second_llm_tokens_p50']:.0f}/{r['second_llm_tokens_p90']:.0f} | "
            f"{r['total_input_tokens_mean']:.0f} | "
            f"{r['gt_cad_tokens_p90']:.0f}/{r['gt_cad_tokens_max']} | "
            f"{r['gt_exceeds_2048_n']} | {r['decode_max_length_n']} | "
            f"{r['inexact_n']} | {r['inexact_max_length_n']} | "
            f"{r['mean_second_tokens_when_exact']:.0f}→{r['mean_second_tokens_when_inexact'] or 0:.0f} | "
            f"{r['mean_gt_tokens_when_exact']:.0f}→{r['mean_gt_tokens_when_inexact'] or 0:.0f} |"
        )
    md_path = args.out.with_suffix(".md")
    # actually out is .json; write sibling
    md_path = args.out.parent / "TABLE_SEQ_BUDGET.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"[wrote] {args.out}")
    print(f"[wrote] {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
