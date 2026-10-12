#!/usr/bin/env python3
"""Forced-choice likelihood probe for a frozen SpatialLM on mechanical parts.

The pretrained checkpoint is fine-tuned so hard onto the indoor-layout grammar
that free generation emits `Wall(...)`/`Bbox(...)` no matter what the prompt
asks. That makes generated text useless for comparing feature variants, so this
probe scores candidate statements instead: for each contrastive pair the model
is asked, implicitly, which continuation it finds more likely given the point
tokens.

For every (variant, pair) the probe reports

    margin = NLL(wrong statement) - NLL(correct statement)      [nats/token]

A positive margin means the point-conditioned model prefers the statement that
is true of the part. The same pairs are also scored with the point cloud removed
(`no_point`), which gives the pure language prior; the informative quantity is

    delta = margin(variant) - margin(no_point)

i.e. how much the point cloud moved the model toward the correct statement.
`A2_normal` vs `B_ours` isolates edge_score from normals.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

import sys

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from spatiallm_zeroshot_probe_v1 import (  # noqa: E402
    MODEL_PATHS,
    build_variants,
    load_model,
    set_in_channels,
)

DEFAULT_OUT = ROOT / "ours3/spatiallm_zeroshot_probe_v1"
QUESTION = "Describe the mechanical part."
POINT_HEAD = "<|point_start|><|point_pad|><|point_end|>"

# Every "correct" statement below is true of PART_005 / PART_019 per the Dora
# geometry summary: rotational road-wheel-like components, cylindrical ratio
# ~0.5, 5 fitted circular rings, concentric radius groups, an inner circular
# feature, sharp circular boundaries.
# Three paraphrases per concept: a single sentence pair is dominated by
# tokenizer-level luck, and the quantity of interest (variant-to-variant margin
# difference) is far smaller than the spread across phrasings.
PAIRS = [
    {
        "name": "domain/1",
        "correct": "The object is a rotational mechanical component. It contains a cylindrical body and concentric circular edges.",
        "wrong": "The object is a room with walls, doors and windows.",
    },
    {
        "name": "domain/2",
        "correct": "This is a machined mechanical part.",
        "wrong": "This is an indoor room scene.",
    },
    {
        "name": "domain/3",
        "correct": "The point cloud shows a single manufactured component.",
        "wrong": "The point cloud shows a furnished interior space.",
    },
    {
        "name": "circular_feature/1",
        "correct": "The object contains circular features and a circular rim.",
        "wrong": "The object contains no circular features and no curved surfaces.",
    },
    {
        "name": "circular_feature/2",
        "correct": "Several concentric circles lie on the surface.",
        "wrong": "Only straight rectangular outlines lie on the surface.",
    },
    {
        "name": "circular_feature/3",
        "correct": "The outer boundary is a circle.",
        "wrong": "The outer boundary is a square.",
    },
    {
        "name": "hole/1",
        "correct": "The part has a concentric inner circular feature along its axis.",
        "wrong": "The part is a plain solid block with no inner feature.",
    },
    {
        "name": "hole/2",
        "correct": "There is a hole through the middle of the part.",
        "wrong": "There is no hole anywhere in the part.",
    },
    {
        "name": "symmetry/1",
        "correct": "The part is rotationally symmetric about a single axis.",
        "wrong": "The part has no symmetry and an irregular free-form shape.",
    },
    {
        "name": "symmetry/2",
        "correct": "The shape repeats under rotation about its axis.",
        "wrong": "The shape changes completely under rotation about its axis.",
    },
    {
        "name": "sharp_boundary/1",
        "correct": "The surface is bounded by sharp circular edges.",
        "wrong": "The surface is smooth everywhere with no sharp edges.",
    },
    {
        "name": "sharp_boundary/2",
        "correct": "Sharp creases separate the flat faces from the curved faces.",
        "wrong": "No creases separate any of the faces.",
    },
    {
        "name": "primitive/1",
        "correct": "The dominant primitive shape is a cylinder.",
        "wrong": "The dominant primitive shape is a rectangular box.",
    },
    {
        "name": "primitive/2",
        "correct": "The part is best described as a disc.",
        "wrong": "The part is best described as a flat wall panel.",
    },
    {
        "name": "cad_op/1",
        "correct": "The part can be built by revolving a profile about an axis.",
        "wrong": "The part can be built by stacking axis-aligned boxes.",
    },
]


def build_inputs(tokenizer, model, statement: str, with_point: bool):
    """Return (input_ids, first_answer_token_index)."""
    user = (POINT_HEAD if with_point else "") + QUESTION
    if model.config.model_type == "spatiallm_qwen":
        conversation = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user},
        ]
    else:
        conversation = [{"role": "user", "content": user}]

    prefix = tokenizer.apply_chat_template(
        conversation, add_generation_prompt=True, return_tensors="pt"
    )
    answer = tokenizer(statement, add_special_tokens=False, return_tensors="pt")["input_ids"]
    input_ids = torch.cat([prefix, answer], dim=1)
    return input_ids, prefix.shape[1]


@torch.inference_mode()
def statement_nll(model, tokenizer, statement: str, point_cloud, ) -> dict:
    """Mean and total NLL of `statement` as the assistant turn."""
    with_point = point_cloud is not None
    input_ids, answer_start = build_inputs(tokenizer, model, statement, with_point)
    input_ids = input_ids.to(model.device)
    attention_mask = torch.ones_like(input_ids)

    kwargs = dict(input_ids=input_ids, attention_mask=attention_mask, use_cache=False)
    if with_point:
        kwargs["point_clouds"] = point_cloud.to(model.device)
    logits = model(**kwargs).logits.float()

    # The model splices `num_patches` point embeddings in after <|point_start|>
    # and drops <|point_pad|>, so every original position j >= point_end lands at
    # j + offset in the logits.
    offset = logits.shape[1] - input_ids.shape[1]
    targets = input_ids[0, answer_start:]
    pred_positions = torch.arange(answer_start - 1, input_ids.shape[1] - 1, device=logits.device) + offset
    token_logits = logits[0, pred_positions, :]
    nll = torch.nn.functional.cross_entropy(token_logits, targets, reduction="none")
    return {
        "num_tokens": int(targets.numel()),
        "nll_mean": float(nll.mean()),
        "nll_total": float(nll.sum()),
        "point_tokens": int(offset + 1) if with_point else 0,
    }


def run_condition(model, tokenizer, point_cloud, label: str) -> dict:
    pairs = []
    point_tokens = 0
    for pair in PAIRS:
        good = statement_nll(model, tokenizer, pair["correct"], point_cloud)
        bad = statement_nll(model, tokenizer, pair["wrong"], point_cloud)
        point_tokens = good["point_tokens"]
        pairs.append(
            {
                "pair": pair["name"],
                "nll_correct": good["nll_mean"],
                "nll_wrong": bad["nll_mean"],
                "margin": bad["nll_mean"] - good["nll_mean"],
                "prefers_correct": bad["nll_mean"] > good["nll_mean"],
                "tokens_correct": good["num_tokens"],
                "tokens_wrong": bad["num_tokens"],
            }
        )
    n_correct = sum(p["prefers_correct"] for p in pairs)
    by_concept: dict[str, list[float]] = {}
    for p in pairs:
        by_concept.setdefault(p["pair"].split("/")[0], []).append(p["margin"])
    return {
        "condition": label,
        "point_tokens": point_tokens,
        "pairs": pairs,
        "num_pairs": len(pairs),
        "num_prefers_correct": n_correct,
        "accuracy": n_correct / len(pairs),
        "mean_margin": sum(p["margin"] for p in pairs) / len(pairs),
        "concept_margin": {k: sum(v) / len(v) for k, v in by_concept.items()},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part-dir", type=Path, default=ROOT / "cad_spatial_dataset/PART_005")
    parser.add_argument("--model", default="qwen0.5b", choices=sorted(MODEL_PATHS))
    parser.add_argument("--variants", nargs="+", default=None)
    parser.add_argument("--dtype", default="float32", choices=["bfloat16", "float32"],
                        help="float32 by default: NLL margins are small and bf16 is too coarse")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    part_dir = args.part_dir.resolve()
    out_dir = args.out / part_dir.name / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(MODEL_PATHS[args.model], getattr(torch, args.dtype), "cuda")
    num_bins = model.config.point_config["num_bins"]
    stem = model.point_backbone.embedding.stem.linear
    base_stem_state = {"weight": stem.weight.data.clone()}
    if stem.bias is not None:
        base_stem_state["bias"] = stem.bias.data.clone()

    conditions = [run_condition(model, tokenizer, None, "no_point")]
    for variant in build_variants(part_dir, num_bins, args.variants):
        set_in_channels(model, variant.feat_dim, base_stem_state)
        cond = run_condition(model, tokenizer, variant.tensor, variant.name)
        cond["in_channels"] = variant.feat_dim
        cond["note"] = variant.note
        conditions.append(cond)

    prior = conditions[0]
    prior_margin = {p["pair"]: p["margin"] for p in prior["pairs"]}
    for cond in conditions[1:]:
        for p in cond["pairs"]:
            p["delta_vs_no_point"] = p["margin"] - prior_margin[p["pair"]]
        cond["mean_delta_vs_no_point"] = cond["mean_margin"] - prior["mean_margin"]

    report = {
        "part_id": part_dir.name,
        "model": args.model,
        "model_path": str(MODEL_PATHS[args.model]),
        "dtype": args.dtype,
        "question": QUESTION,
        "pairs": PAIRS,
        "conditions": conditions,
    }
    path = out_dir / "forced_choice.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    head = f"{'condition':22s} {'in_ch':>5s} {'acc':>6s} {'margin':>9s} {'delta':>9s}"
    print(head)
    print("-" * len(head))
    for cond in conditions:
        delta = cond.get("mean_delta_vs_no_point")
        print(
            f"{cond['condition']:22s} {cond.get('in_channels', 0):5d} "
            f"{cond['num_prefers_correct']}/{cond['num_pairs']:<4d} {cond['mean_margin']:+9.4f} "
            f"{'' if delta is None else f'{delta:+9.4f}'}"
        )
    print()
    print(f"{'concept':18s} " + " ".join(f"{c['condition'][:13]:>13s}" for c in conditions))
    for concept in conditions[0]["concept_margin"]:
        row = " ".join(f"{c['concept_margin'][concept]:+13.4f}" for c in conditions)
        print(f"{concept:18s} {row}")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
