#!/usr/bin/env python3
"""Longer EOS canary for frozen four-arm step-100 smoke checkpoints."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from transformers import AutoTokenizer

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path[:0] = [
    str(ROOT / "scripts/m2_c2_spatial_anchor_q_ablation_v1"),
    str(ROOT / "scripts/spatiallm_geometry_prefix_v3"),
    str(ROOT / "scripts/spatiallm_m2_spatial_anchor_v1"),
    str(ROOT / "scripts"),
    str(ROOT / "SpatialLM"),
    str(ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code"),
]

from run_four_arm_100step_impl import (
    ARMS,
    BASE,
    build_model,
    encode,
    install_geometry,
    load_anchor,
    load_raw,
    v3,
)

DEV = ROOT / "ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_decode_dev_50.json"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--checkpoint", required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-new-tokens", type=int, default=512)
    parser.add_argument("--num-samples", type=int, default=4)
    args = parser.parse_args()
    use_anchor, q = ARMS[args.arm]
    device = torch.device(args.device)
    checkpoint = Path(args.checkpoint)
    records = json.loads(DEV.read_text())["records"]
    v3.heldout_geometry.install()
    plugin = v3.get_cad_mm_plugin(point_token="<|point_pad|>", num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tokenizer = AutoTokenizer.from_pretrained(checkpoint, local_files_only=True, use_fast=False)
    model = v3.module.SpatialLMLlamaForCausalLM.from_pretrained(
        checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    )
    # Build the exact frozen arm branch, then attach the independently saved weights.
    from geometry_prefix_adapter import GeometryPrefixAdapter
    from spatiallm_m2_spatial_anchor_v1.m2_c2_spatial_anchor_v1 import M2C2SpatialAnchorV1
    adapter = GeometryPrefixAdapter(256, model.config.hidden_size, num_queries=q, target_norm=1.9414).to(device=device, dtype=torch.bfloat16)
    branch = M2C2SpatialAnchorV1(adapter).to(device=device, dtype=torch.bfloat16) if use_anchor else adapter
    branch.load_state_dict(torch.load(checkpoint / "geometry_branch.pt", map_location=device))
    model.edge_proj = branch
    model.config.separate_edge_tokens = True
    model.separate_edge_tokens = True
    model.config.use_cache = True
    model.eval()
    runtime = {}
    original_splice = install_geometry(model, branch, use_anchor, runtime)
    try:
        eos = tokenizer.eos_token_id
        per_sample = []
        for row in records[: args.num_samples]:
            ids, labels, prompt_len = encode(tokenizer, row, q)
            prompt = ids[:, :prompt_len].to(device)
            surface, _ = plugin._load_cad_separate_edge(row["surface_input"])
            surface = torch.tensor(surface, device=device).unsqueeze(0)
            raw, mask = load_raw(row)
            runtime["raw_mask"] = mask
            runtime["anchors"] = load_anchor(row)
            edge = raw.to(device).unsqueeze(0)
            with torch.no_grad():
                generated = model.generate(
                    input_ids=prompt,
                    attention_mask=torch.ones_like(prompt),
                    point_clouds=surface,
                    edge_clouds=edge,
                    max_new_tokens=args.max_new_tokens,
                    do_sample=False,
                )
            tokens = generated[0, prompt_len:].cpu().tolist()
            per_sample.append({
                "cad_id": row["cad_id"],
                "target_token_count": int(ids.shape[1] - prompt_len),
                "generated_token_count": len(tokens),
                "eos_emitted": eos in tokens if eos is not None else False,
                "hit_max_new_tokens": len(tokens) == args.max_new_tokens,
                "non_empty": bool(tokens),
                "immediate_catastrophic_loop": len(tokens) >= 16 and len(set(tokens[:16])) <= 1,
            })
        eos_count = sum(item["eos_emitted"] for item in per_sample)
        runaway_count = sum(item["hit_max_new_tokens"] and item["target_token_count"] <= args.max_new_tokens for item in per_sample)
        report = {
            "ARM": args.arm,
            "DECODE_DEV_RECORDS_LOADED": len(per_sample),
            "ANCHOR_EVAL_100_MODEL_READ": False,
            "PILOT150_MODEL_READ": False,
            "OFFICIAL_TEST_READ": False,
            "MAX_NEW_TOKENS": args.max_new_tokens,
            "EOS_COUNT": eos_count,
            "UNEXPECTED_RUNAWAY_COUNT": runaway_count,
            "PER_SAMPLE": per_sample,
            "PASS": eos_count > 0 and runaway_count < len(per_sample) and all(item["non_empty"] and not item["immediate_catastrophic_loop"] for item in per_sample),
        }
        Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
        print(json.dumps(report, indent=2))
        if not report["PASS"]:
            raise SystemExit(2)
    finally:
        v3.module._splice_geometry = original_splice


if __name__ == "__main__":
    main()
