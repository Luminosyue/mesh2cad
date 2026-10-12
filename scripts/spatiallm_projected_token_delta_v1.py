#!/usr/bin/env python3
"""How much does edge_score change the embeddings the LLM actually sees?

An earlier ablation showed edge_score measurably changes the Sonata *encoder*
output. But the LLM does not read encoder output directly: it reads
`point_proj(encoder_output)`, and the projector is frozen too. This script
measures the variant-to-variant delta at that point, which is the quantity that
bounds how much a frozen LLM head could possibly respond to edge_score.

Reported per variant pair, over the token axis:

    relative_delta   ||a - b|| / ||a||, per token
    cosine           token-wise cosine similarity
    frac_cos_below   fraction of tokens moved past a cosine threshold

The comparison that matters is B_ours vs C_shuffled_edge (identical edge
histogram, scrambled placement) and B_ours vs B0_ours_zero_edge (identical
widened stem, no edge information). A_rgb_zeros vs A2_normal is included as a
reference scale for "a feature change the encoder was pretrained to handle".
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
sys.path.insert(0, str(ROOT / "scripts"))

from spatiallm_zeroshot_probe_v1 import (  # noqa: E402
    MODEL_PATHS,
    build_variants,
    load_model,
    set_in_channels,
)

DEFAULT_OUT = ROOT / "ours3/spatiallm_zeroshot_probe_v1"
KEY_PAIRS = [
    ("B_ours", "B0_ours_zero_edge"),
    ("B_ours", "C_shuffled_edge"),
    ("A_rgb_zeros", "A2_normal"),
]


def pair_stats(a: np.ndarray, b: np.ndarray) -> dict:
    delta = np.linalg.norm(a - b, axis=1)
    norm = np.linalg.norm(a, axis=1)
    rel = delta / np.maximum(norm, 1e-12)
    cos = np.sum(a * b, axis=1) / np.maximum(np.linalg.norm(a, axis=1) * np.linalg.norm(b, axis=1), 1e-12)
    return {
        "identical": bool(np.array_equal(a, b)),
        "num_tokens": int(a.shape[0]),
        "relative_delta_mean": float(rel.mean()),
        "relative_delta_median": float(np.median(rel)),
        "relative_delta_max": float(rel.max()),
        "cosine_mean": float(cos.mean()),
        "cosine_min": float(cos.min()),
        "frac_cos_below_0_999": float((cos < 0.999).mean()),
        "frac_cos_below_0_99": float((cos < 0.99).mean()),
    }


@torch.inference_mode()
def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--part-dir", type=Path, default=ROOT / "cad_spatial_dataset/PART_005")
    parser.add_argument("--model", default="qwen0.5b", choices=sorted(MODEL_PATHS))
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()

    part_dir = args.part_dir.resolve()
    out_dir = args.out / part_dir.name / args.model
    out_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(MODEL_PATHS[args.model], torch.float32, "cuda")
    num_bins = model.config.point_config["num_bins"]
    stem = model.point_backbone.embedding.stem.linear
    base_stem_state = {"weight": stem.weight.data.clone()}
    if stem.bias is not None:
        base_stem_state["bias"] = stem.bias.data.clone()

    encoded: dict[str, np.ndarray] = {}
    projected: dict[str, np.ndarray] = {}
    for variant in build_variants(part_dir, num_bins, None):
        set_in_channels(model, variant.feat_dim, base_stem_state)
        pc = variant.tensor[0].to(model.device)
        nan_mask = torch.isnan(pc).any(dim=1)
        pc = pc[~nan_mask]
        feats = pc[:, 3:].float()
        enc = model.point_backbone(
            {
                "coord": feats[:, :3],
                "grid_coord": pc[:, :3].int(),
                "feat": feats,
                "batch": torch.zeros(pc.shape[0], dtype=torch.long, device=model.device),
            }
        )
        encoded[variant.name] = enc.float().cpu().numpy()
        projected[variant.name] = model.point_proj(enc.unsqueeze(0).float())[0].float().cpu().numpy()

    names = list(projected)
    token_counts = {k: int(v.shape[0]) for k, v in projected.items()}
    report = {
        "part_id": part_dir.name,
        "model": args.model,
        "encoder_dim": int(next(iter(encoded.values())).shape[1]),
        "projected_dim": int(next(iter(projected.values())).shape[1]),
        "num_tokens": token_counts,
        "encoder": {},
        "projected": {},
    }
    for a, b in itertools.combinations(names, 2):
        if token_counts[a] != token_counts[b]:
            continue
        key = f"{a}__vs__{b}"
        report["encoder"][key] = pair_stats(encoded[a], encoded[b])
        report["projected"][key] = pair_stats(projected[a], projected[b])

    path = out_dir / "projected_token_delta.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"{args.part_dir.name} / {args.model}   encoder_dim={report['encoder_dim']} "
          f"projected_dim={report['projected_dim']} tokens={next(iter(token_counts.values()))}")
    head = f"{'pair':42s} {'enc rel_d':>10s} {'proj rel_d':>11s} {'proj cos':>10s} {'cos<.99':>9s}"
    print(head)
    print("-" * len(head))
    for a, b in KEY_PAIRS + [p for p in itertools.combinations(names, 2) if p not in KEY_PAIRS]:
        key = f"{a}__vs__{b}"
        if key not in report["projected"]:
            continue
        e, p = report["encoder"][key], report["projected"][key]
        print(f"{key:42s} {e['relative_delta_mean']:10.5f} {p['relative_delta_mean']:11.5f} "
              f"{p['cosine_mean']:10.6f} {p['frac_cos_below_0_99']:9.4f}")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
