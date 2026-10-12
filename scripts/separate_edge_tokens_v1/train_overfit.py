#!/usr/bin/env python3
"""Matched-budget overfit trainer for the three CAD geometry conditioners.

Variants
--------
E0  surface_only    6ch surface                      (existing baseline path)
E1  edge_score      7ch surface, widened Sonata stem (existing experiment)
E2  separate_edge   6ch surface + 6ch edge tokens    (this experiment)

All three share sample ids, target DSL, optimizer, schedule, epoch count and
seed, so the only difference is how sharp-edge information reaches the model.

Sonata stays frozen in every variant; the LLM, the surface projector and (for
E2) the edge projector are trained.
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from separate_edge_tokens_v1.common import (  # noqa: E402
    CACHE_DIR,
    DEFAULT_MODEL_PATH,
    OUT_ROOT,
    TRAIN_DIR,
    build_batch,
    json_dump,
    load_geometry,
    make_plugin,
    read_dsl,
    set_deterministic_serialization,
)

VARIANTS = ("surface_only", "edge_score", "separate_edge")


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_variant_model(variant: str, model_path: Path, device: str, dtype):
    """Load the checkpoint and apply exactly the patching that variant needs."""
    from separate_edge_tokens_v1.common import ensure_spatiallm_importable

    ensure_spatiallm_importable()
    import spatiallm  # noqa: F401
    from transformers import AutoModelForCausalLM, AutoTokenizer

    from spatiallm.tuner.framework.patcher import (
        _attach_edge_projector,
        _widen_point_stem_for_edge,
    )

    model = AutoModelForCausalLM.from_pretrained(str(model_path), torch_dtype=dtype)
    if variant == "edge_score":
        _widen_point_stem_for_edge(model)
    elif variant == "separate_edge":
        _attach_edge_projector(model)

    model.to(device)
    model.set_point_backbone_dtype(torch.float32)
    set_deterministic_serialization(model.point_backbone)
    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    return model, tokenizer


def build_sample_inputs(variant: str, sample_id: str, plugins: dict):
    """Return (surface_tensor, edge_tensor_or_None, separate_edge_flag)."""
    if variant == "separate_edge":
        surface, edge = load_geometry(sample_id, plugins["sepedge"])
        return surface, edge, True

    if variant == "surface_only":
        npy = TRAIN_DIR / sample_id / "features_canonical_xyz_normal.npy"
        feats = plugins["baseline"]._load_cad_npy(str(npy))
    else:  # edge_score
        npy = TRAIN_DIR / sample_id / "features_canonical.npy"
        feats = plugins["edge_score"]._load_cad_npy(str(npy))
    return torch.as_tensor(feats[None, ...], dtype=torch.float32), None, False


def autocast_ctx(enabled: bool):
    return torch.autocast("cuda", dtype=torch.bfloat16, enabled=enabled)


@torch.no_grad()
def evaluate(model, tokenizer, samples, variant, plugins, device, bf16=True) -> dict:
    model.eval()
    losses, correct, total = [], 0, 0
    for sid, dsl in samples:
        surface, edge, sep = build_sample_inputs(variant, sid, plugins)
        batch = build_batch(tokenizer, surface, edge, dsl, device, separate_edge=sep)
        with autocast_ctx(bf16):
            out = model(**batch)
        losses.append(float(out.loss.item()))

        # Teacher-forced next-token accuracy over the CAD target only.
        # Geometry splicing lengthens the sequence in the prompt region, but the
        # target always occupies the final `target_len` positions, so indexing
        # from the end stays valid for every variant. Batch size is 1, so no
        # right padding is appended.
        target_len = int((batch["labels"] != -100).sum().item())
        pred = out.logits[0, -target_len - 1 : -1].argmax(-1)
        gold = batch["labels"][0, -target_len:]
        correct += int((pred == gold).sum().item())
        total += int(gold.numel())
        del out
    torch.cuda.empty_cache()

    model.train()
    return {
        "mean_loss": float(np.mean(losses)),
        "token_accuracy": float(correct / max(total, 1)),
        "num_samples": len(samples),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", choices=VARIANTS, required=True)
    ap.add_argument("--ids-file", type=Path, required=True)
    ap.add_argument(
        "--val-ids-file",
        type=Path,
        default=None,
        help="held-out ids scored alongside train; never optimized on",
    )
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--model-path", type=Path, default=DEFAULT_MODEL_PATH)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--epochs", type=int, default=60)
    ap.add_argument("--lr", type=float, default=2e-5)
    ap.add_argument("--grad-accum", type=int, default=4)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--device", type=str, default="cuda")
    ap.add_argument("--save-checkpoint", action="store_true")
    ap.add_argument("--eval-every", type=int, default=10)
    # Memory controls. The DSL targets are heavily skewed (median 278 tokens,
    # max 5276), and a 5k-token sequence makes the fp32 logits alone ~3 GB.
    # Applied identically to every variant so the comparison stays matched.
    ap.add_argument("--no-bf16", action="store_true")
    ap.add_argument("--no-grad-checkpointing", action="store_true")
    args = ap.parse_args()

    set_seed(args.seed)
    ids = [
        ln.strip()
        for ln in args.ids_file.read_text(encoding="utf-8").splitlines()
        if ln.strip()
    ]
    if args.limit is not None:
        ids = ids[: args.limit]
    if args.variant == "separate_edge":
        ids = [i for i in ids if (CACHE_DIR / i / "edge_points.npy").is_file()]

    val_ids = []
    if args.val_ids_file and args.val_ids_file.is_file():
        val_ids = [
            ln.strip()
            for ln in args.val_ids_file.read_text(encoding="utf-8").splitlines()
            if ln.strip()
        ]
        if args.variant == "separate_edge":
            val_ids = [i for i in val_ids if (CACHE_DIR / i / "edge_points.npy").is_file()]

    samples = [(sid, read_dsl(sid)) for sid in ids]
    val_samples = [(sid, read_dsl(sid)) for sid in val_ids]
    plugins = {
        "baseline": make_plugin(separate_edge=False),
        "sepedge": make_plugin(separate_edge=True),
    }
    from separate_edge_tokens_v1.common import ensure_spatiallm_importable

    ensure_spatiallm_importable()
    from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin

    plugins["edge_score"] = get_cad_mm_plugin(use_edge_score=True)

    model, tokenizer = load_variant_model(
        args.variant, args.model_path, args.device, torch.float32
    )
    bf16 = not args.no_bf16
    if not args.no_grad_checkpointing:
        model.gradient_checkpointing_enable(
            gradient_checkpointing_kwargs={"use_reentrant": False}
        )
        model.config.use_cache = False
    trainable = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=args.lr, weight_decay=0.0)
    total_steps = max(1, math.ceil(len(samples) * args.epochs / args.grad_accum))
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=total_steps)

    args.out.mkdir(parents=True, exist_ok=True)
    initial = evaluate(model, tokenizer, samples, args.variant, plugins, args.device, bf16)
    initial_val = (
        evaluate(model, tokenizer, val_samples, args.variant, plugins, args.device, bf16)
        if val_samples
        else None
    )

    history = [{"epoch": 0, "step": 0, **initial, "val": initial_val}]
    print(
        f"[{args.variant}] n={len(samples)} epochs={args.epochs} steps={total_steps} "
        f"initial_loss={initial['mean_loss']:.4f} acc={initial['token_accuracy']:.4f}",
        flush=True,
    )

    model.train()
    rng = random.Random(args.seed)
    step = 0
    t0 = time.time()
    for epoch in range(1, args.epochs + 1):
        order = list(range(len(samples)))
        rng.shuffle(order)
        optimizer.zero_grad(set_to_none=True)
        epoch_losses = []
        for k, idx in enumerate(order):
            sid, dsl = samples[idx]
            surface, edge, sep = build_sample_inputs(args.variant, sid, plugins)
            batch = build_batch(
                tokenizer, surface, edge, dsl, args.device, separate_edge=sep
            )
            with autocast_ctx(bf16):
                loss = model(**batch).loss / args.grad_accum
            loss.backward()
            epoch_losses.append(float(loss.item()) * args.grad_accum)
            del loss, batch
            if (k + 1) % args.grad_accum == 0 or k == len(order) - 1:
                torch.nn.utils.clip_grad_norm_(trainable, 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                step += 1

        if epoch % args.eval_every == 0 or epoch == args.epochs:
            ev = evaluate(model, tokenizer, samples, args.variant, plugins, args.device, bf16)
            val = (
                evaluate(
                    model, tokenizer, val_samples, args.variant, plugins, args.device, bf16
                )
                if val_samples
                else None
            )
            history.append({"epoch": epoch, "step": step, **ev, "val": val})
            val_txt = (
                f" val_loss={val['mean_loss']:.4f} val_acc={val['token_accuracy']:.4f}"
                if val
                else ""
            )
            print(
                f"[{args.variant}] epoch={epoch} step={step} "
                f"train_loss={np.mean(epoch_losses):.4f} "
                f"eval_loss={ev['mean_loss']:.4f} acc={ev['token_accuracy']:.4f}"
                f"{val_txt} ({time.time() - t0:.0f}s)",
                flush=True,
            )

    final = history[-1]
    result = {
        "experiment": "separate_edge_tokens_v1",
        "variant": args.variant,
        "num_samples": len(samples),
        "sample_ids": ids,
        "epochs": args.epochs,
        "lr": args.lr,
        "grad_accum": args.grad_accum,
        "seed": args.seed,
        "optimizer": "AdamW(weight_decay=0.0)",
        "scheduler": "CosineAnnealingLR",
        "sonata_frozen": True,
        "bf16_autocast": bf16,
        "gradient_checkpointing": not args.no_grad_checkpointing,
        "INITIAL_TRAIN_LOSS": initial["mean_loss"],
        "FINAL_TRAIN_LOSS": final["mean_loss"],
        "LOSS_REDUCTION": initial["mean_loss"] - final["mean_loss"],
        "INITIAL_TOKEN_ACCURACY": initial["token_accuracy"],
        "TOKEN_ACCURACY": final["token_accuracy"],
        "TRAIN_LOSS_DECREASES": bool(final["mean_loss"] < initial["mean_loss"]),
        "num_val_samples": len(val_samples),
        "val_ids": val_ids,
        "INITIAL_VAL_LOSS": initial_val["mean_loss"] if initial_val else None,
        "FINAL_VAL_LOSS": final["val"]["mean_loss"] if final.get("val") else None,
        "FINAL_VAL_TOKEN_ACCURACY": (
            final["val"]["token_accuracy"] if final.get("val") else None
        ),
        "wall_time_sec": time.time() - t0,
        "history": history,
    }
    json_dump(args.out / "train_result.json", result)

    if args.save_checkpoint:
        ckpt = args.out / "checkpoint"
        model.save_pretrained(str(ckpt), safe_serialization=True)
        tokenizer.save_pretrained(str(ckpt))
        result["checkpoint"] = str(ckpt)
        json_dump(args.out / "train_result.json", result)

    print(json.dumps({k: v for k, v in result.items() if k not in ("history", "sample_ids")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
