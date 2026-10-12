#!/usr/bin/env python3
"""Reload a trained separate_edge_tokens_v1 checkpoint and prove determinism.

Confirms the saved config recreates `edge_proj`, that its weights survive the
round trip, and that the same input yields the same logits and loss.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import (  # noqa: E402
    OUT_ROOT,
    build_batch,
    json_dump,
    load_geometry,
    load_model,
    make_plugin,
    read_dsl,
    set_deterministic_serialization,
)


@torch.no_grad()
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--checkpoint", type=Path, required=True)
    ap.add_argument("--sample-id", type=str, required=True)
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--out", type=Path, default=OUT_ROOT / "overfit1/reload_check.json")
    args = ap.parse_args()

    cfg = json.loads((args.checkpoint / "config.json").read_text(encoding="utf-8"))
    plugin = make_plugin(separate_edge=True)
    surface, edge = load_geometry(args.sample_id, plugin)
    dsl = read_dsl(args.sample_id)

    runs = []
    for _ in range(2):
        model, tokenizer = load_model(
            args.checkpoint, separate_edge=True, device=args.device, dtype=torch.float32
        )
        set_deterministic_serialization(model.point_backbone)
        model.eval()
        batch = build_batch(tokenizer, surface, edge, dsl, args.device, separate_edge=True)
        out = model(**batch)
        runs.append(
            {
                "loss": float(out.loss.item()),
                "logits": out.logits.float().cpu().numpy(),
                "edge_w": next(model.edge_proj.parameters()).detach().float().cpu().numpy(),
            }
        )
        del model
        torch.cuda.empty_cache()

    report = {
        "checkpoint": str(args.checkpoint),
        "sample_id": args.sample_id,
        "config_separate_edge_tokens": cfg.get("separate_edge_tokens"),
        "config_edge_start_token_id": cfg.get("edge_start_token_id"),
        "config_point_in_channels": cfg.get("point_config", {}).get("in_channels"),
        "loss_run1": runs[0]["loss"],
        "loss_run2": runs[1]["loss"],
        "loss_abs_diff": abs(runs[0]["loss"] - runs[1]["loss"]),
        "logits_max_abs_diff": float(
            np.abs(runs[0]["logits"] - runs[1]["logits"]).max()
        ),
        "edge_projector_weights_identical": bool(
            np.array_equal(runs[0]["edge_w"], runs[1]["edge_w"])
        ),
    }
    report["CHECKPOINT_RELOAD_OK"] = bool(
        report["config_separate_edge_tokens"] is True
        and report["config_point_in_channels"] == 6
        and report["edge_projector_weights_identical"]
        and report["logits_max_abs_diff"] == 0.0
    )
    json_dump(args.out, report)
    print(json.dumps(report, indent=2))
    return 0 if report["CHECKPOINT_RELOAD_OK"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
