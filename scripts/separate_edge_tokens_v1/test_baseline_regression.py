#!/usr/bin/env python3
"""Prove the separate_edge_tokens_v1 changes did not disturb existing paths.

Three things are checked:

1. The generalised splice helpers reproduce the original single-region
   arithmetic exactly, for embeddings, attention mask and labels.
2. The 6-channel baseline still loads with `edge_proj is None`, forwards, and
   produces a finite loss with no `edge_clouds` kwarg anywhere.
3. The 7-channel edge_score experiment still widens the Sonata stem to
   `Linear(7, 48)` and still forwards.

Also asserts that enabling both experiment flags raises.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import (  # noqa: E402
    DEFAULT_MODEL_PATH,
    OUT_ROOT,
    TRAIN_DIR,
    ensure_spatiallm_importable,
    json_dump,
)

IGNORE_INDEX = -100


def check_splice_equivalence() -> dict:
    """Single-region splice must equal the original inline implementation."""
    ensure_spatiallm_importable()
    from spatiallm.model.spatiallm_llama import _splice_geometry, _splice_labels

    torch.manual_seed(0)
    seq_len, hidden, num_patches = 40, 8, 13
    embeds = torch.randn(seq_len, hidden)
    attn = torch.ones(seq_len)
    labels = torch.arange(seq_len)
    feats = torch.randn(num_patches, hidden)
    start, end = torch.tensor(3), torch.tensor(5)

    # Original arithmetic, copied verbatim from the pre-change implementation.
    ref_embeds = torch.cat((embeds[: start + 1], feats, embeds[end:]), dim=0)
    ref_attn = torch.cat(
        (attn[: start + 1], torch.ones(num_patches, device=attn.device), attn[end:]),
        dim=0,
    )
    ref_labels = torch.cat(
        (
            labels[: start + 1],
            torch.full((num_patches,), IGNORE_INDEX, device=labels.device),
            labels[end:],
        ),
        dim=0,
    )
    target_len = ref_labels.shape[0] + 7
    ref_labels = torch.nn.functional.pad(
        ref_labels, (0, target_len - ref_labels.shape[0]), value=IGNORE_INDEX
    )

    got_embeds, got_attn = _splice_geometry(embeds, attn, [(start, feats, end)])
    got_labels = _splice_labels(labels, [(start, num_patches, end)], target_len)

    return {
        "embeds_identical": bool(torch.equal(ref_embeds, got_embeds)),
        "attention_identical": bool(torch.equal(ref_attn, got_attn)),
        "labels_identical": bool(torch.equal(ref_labels, got_labels)),
        "shapes": {
            "embeds": list(got_embeds.shape),
            "attention": list(got_attn.shape),
            "labels": list(got_labels.shape),
        },
    }


def check_two_region_splice() -> dict:
    """Two regions must mask both geometry blocks and keep lengths consistent."""
    ensure_spatiallm_importable()
    from spatiallm.model.spatiallm_llama import _splice_geometry, _splice_labels

    torch.manual_seed(1)
    seq_len, hidden = 30, 4
    embeds = torch.randn(seq_len, hidden)
    attn = torch.ones(seq_len)
    labels = torch.arange(seq_len)
    surf = torch.randn(6, hidden)
    edge = torch.randn(3, hidden)
    regions_e = [(torch.tensor(2), surf, torch.tensor(4)), (torch.tensor(5), edge, torch.tensor(7))]
    regions_l = [(torch.tensor(2), 6, torch.tensor(4)), (torch.tensor(5), 3, torch.tensor(7))]

    got_e, got_a = _splice_geometry(embeds, attn, regions_e)
    got_l = _splice_labels(labels, regions_l, got_e.shape[0])

    # layout: keep[0:3] surface[3:9] keep[9:11] edge[11:14] keep[14:]
    masked = (got_l == IGNORE_INDEX).sum().item()
    return {
        "embeds_len": int(got_e.shape[0]),
        "attention_len": int(got_a.shape[0]),
        "labels_len": int(got_l.shape[0]),
        "lengths_agree": bool(got_e.shape[0] == got_a.shape[0] == got_l.shape[0]),
        "num_masked_labels": int(masked),
        "expected_masked": 9,
        "geometry_fully_masked": bool(masked == 9),
        "surface_block_matches": bool(torch.equal(got_e[3:9], surf)),
        "edge_block_matches": bool(torch.equal(got_e[11:14], edge)),
        "masked_positions_are_geometry": bool(
            torch.equal(
                torch.where(got_l == IGNORE_INDEX)[0],
                torch.tensor([3, 4, 5, 6, 7, 8, 11, 12, 13]),
            )
        ),
    }


def check_flag_conflict() -> dict:
    ensure_spatiallm_importable()
    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin

    raised_plugin = False
    try:
        get_cad_mm_plugin(use_edge_score=True, separate_edge_tokens=True)
    except ValueError as exc:
        raised_plugin = "cannot be enabled simultaneously" in str(exc)
    return {"plugin_rejects_both_flags": raised_plugin}


@torch.no_grad()
def check_baseline_forward(model_path: Path, sample_id: str, device: str) -> dict:
    """6-channel baseline: no edge projector, no edge kwarg, finite loss."""
    ensure_spatiallm_importable()
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin

    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=torch.float32)
    has_edge_proj = getattr(model, "edge_proj", None) is not None
    stem_in = model.point_backbone.embedding.stem.linear.in_features
    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))

    plugin = get_cad_mm_plugin(use_edge_score=False, separate_edge_tokens=False)
    feats_path = TRAIN_DIR / sample_id / "features_canonical_xyz_normal.npy"
    tensor = plugin._load_cad_npy(str(feats_path))
    point_clouds = torch.as_tensor(tensor[None, ...], dtype=torch.float32).to(device)

    prompt = "<|point_start|><|point_pad|><|point_end|>\nGenerate CAD construction program."
    ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}], add_generation_prompt=True, return_tensors="pt"
    ).to(device)
    labels = torch.full_like(ids, IGNORE_INDEX)
    labels[0, -3:] = ids[0, -3:]

    out = model(
        input_ids=ids,
        attention_mask=torch.ones_like(ids),
        labels=labels,
        point_clouds=point_clouds,
    )
    result = {
        "edge_proj_is_none": not has_edge_proj,
        "stem_in_features": int(stem_in),
        "surface_input_channels": int(tensor.shape[1]) - 3,
        "logits_shape": list(out.logits.shape),
        "loss": float(out.loss.item()),
        "loss_finite": bool(np.isfinite(out.loss.item())),
    }
    del model
    torch.cuda.empty_cache()
    return result


@torch.no_grad()
def check_edge_score_forward(model_path: Path, sample_id: str, device: str) -> dict:
    """7-channel edge_score experiment must still widen and forward."""
    ensure_spatiallm_importable()
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
    from spatiallm.tuner.framework.patcher import _widen_point_stem_for_edge

    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=torch.float32)
    stem_before = model.point_backbone.embedding.stem.linear.in_features
    _widen_point_stem_for_edge(model)
    stem_after = model.point_backbone.embedding.stem.linear.in_features
    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    model.eval()
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))

    plugin = get_cad_mm_plugin(use_edge_score=True, separate_edge_tokens=False)
    feats_path = TRAIN_DIR / sample_id / "features_canonical.npy"
    tensor = plugin._load_cad_npy(str(feats_path))
    point_clouds = torch.as_tensor(tensor[None, ...], dtype=torch.float32).to(device)

    prompt = "<|point_start|><|point_pad|><|point_end|>\nGenerate CAD construction program."
    ids = tokenizer.apply_chat_template(
        [{"role": "user", "content": prompt}], add_generation_prompt=True, return_tensors="pt"
    ).to(device)
    labels = torch.full_like(ids, IGNORE_INDEX)
    labels[0, -3:] = ids[0, -3:]

    out = model(
        input_ids=ids,
        attention_mask=torch.ones_like(ids),
        labels=labels,
        point_clouds=point_clouds,
    )
    result = {
        "stem_in_features_before": int(stem_before),
        "stem_in_features_after": int(stem_after),
        "widened_to_7": bool(stem_after == 7),
        "surface_input_channels": int(tensor.shape[1]) - 3,
        "loss": float(out.loss.item()),
        "loss_finite": bool(np.isfinite(out.loss.item())),
    }
    del model
    torch.cuda.empty_cache()
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    ap.add_argument("--sample-id", type=str, default="0000_00000525")
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--out", type=Path, default=OUT_ROOT / "audit/baseline_regression.json")
    ap.add_argument("--skip-gpu", action="store_true")
    args = ap.parse_args()

    report = {
        "splice_single_region": check_splice_equivalence(),
        "splice_two_regions": check_two_region_splice(),
        "flag_conflict": check_flag_conflict(),
    }
    if not args.skip_gpu:
        report["baseline_6ch"] = check_baseline_forward(
            args.model_path, args.sample_id, args.device
        )
        report["edge_score_7ch"] = check_edge_score_forward(
            args.model_path, args.sample_id, args.device
        )

    checks = [
        report["splice_single_region"]["embeds_identical"],
        report["splice_single_region"]["attention_identical"],
        report["splice_single_region"]["labels_identical"],
        report["splice_two_regions"]["lengths_agree"],
        report["splice_two_regions"]["geometry_fully_masked"],
        report["splice_two_regions"]["surface_block_matches"],
        report["splice_two_regions"]["edge_block_matches"],
        report["splice_two_regions"]["masked_positions_are_geometry"],
        report["flag_conflict"]["plugin_rejects_both_flags"],
    ]
    if not args.skip_gpu:
        checks += [
            report["baseline_6ch"]["edge_proj_is_none"],
            report["baseline_6ch"]["stem_in_features"] == 6,
            report["baseline_6ch"]["loss_finite"],
            report["edge_score_7ch"]["widened_to_7"],
            report["edge_score_7ch"]["loss_finite"],
        ]

    report["OLD_BASELINE_REGRESSION"] = "PASS" if all(checks) else "FAIL"
    report["EDGE_SCORE_REGRESSION"] = (
        "NOT_RUN"
        if args.skip_gpu
        else ("PASS" if report["edge_score_7ch"]["widened_to_7"] and report["edge_score_7ch"]["loss_finite"] else "FAIL")
    )
    json_dump(args.out, report)
    import json as _json

    print(_json.dumps(report, indent=2))
    return 0 if report["OLD_BASELINE_REGRESSION"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
