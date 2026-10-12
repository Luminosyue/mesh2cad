#!/usr/bin/env python3
"""Lightweight 10-sample CAD DSL overfit (pipeline sanity check).

Avoids SpatialLM's full Trainer footprint so a shared ~22GB GPU can finish.
Trains LLM+projector with frozen point backbone; logs loss; optional decode.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import numpy as np
import torch
from torch.optim import AdamW
from tqdm import tqdm

ROOT = Path(__file__).resolve().parents[2]
SPATIALLM_ROOT = ROOT / "SpatialLM"
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(SPATIALLM_ROOT))

CAD_INSTRUCTION = """Generate CAD construction program from the point cloud.

Allowed operations (CAD DSL v1):
Sketch, Circle, Rectangle, Extrude, Cut, Union

Output only valid DSL assignments ending with result = ...
"""


def load_records(train_json: Path, media_dir: Path, limit: int | None):
    rows = json.loads(train_json.read_text(encoding="utf-8"))
    if limit:
        rows = rows[:limit]
    out = []
    for r in rows:
        feats = np.load(media_dir / r["point_clouds"][0])
        dsl = r["conversations"][1]["value"]
        out.append({"id": r["id"], "features": feats, "dsl": dsl})
    return out


def build_batch(sample, tokenizer, preprocess_fn, use_edge: bool, device: str, max_new: int):
    feats = sample["features"]
    points, normals = feats[:, :3], feats[:, 3:6]
    edge = feats[:, 6] if feats.shape[1] >= 7 else np.zeros(len(feats))
    if not use_edge:
        edge = np.zeros_like(edge)
    part = preprocess_fn(points, normals, edge)
    point_cloud = part.tensor.to(device)
    if not use_edge:
        # Pretrained stem expects 6 feat channels: xyz + normal (no edge).
        point_cloud = point_cloud[..., :9]  # grid(3)+xyz(3)+normal(3)

    prompt = f"<|point_start|><|point_pad|><|point_end|>\n{CAD_INSTRUCTION.strip()}"
    conversation = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": sample["dsl"]},
    ]
    full_ids = tokenizer.apply_chat_template(
        conversation, tokenize=True, add_generation_prompt=False, return_tensors="pt"
    ).to(device)
    prompt_ids = tokenizer.apply_chat_template(
        conversation[:1], tokenize=True, add_generation_prompt=True, return_tensors="pt"
    ).to(device)
    labels = full_ids.clone()
    labels[:, : prompt_ids.shape[1]] = -100
    if full_ids.shape[1] > max_new:
        full_ids = full_ids[:, :max_new]
        labels = labels[:, :max_new]
    attention_mask = torch.ones_like(full_ids)
    return point_cloud, full_ids, labels, attention_mask


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("ours", "baseline"), default="ours")
    parser.add_argument(
        "--train-json",
        type=Path,
        default=ROOT / "cad_spatial_dataset/DeepCAD/deepcad_cad_ours_overfit10_train.json",
    )
    parser.add_argument("--media-dir", type=Path, default=ROOT / "cad_spatial_dataset/DeepCAD")
    parser.add_argument("--model", type=Path, default=SPATIALLM_ROOT / "models/SpatialLM1.1-Llama-1B")
    parser.add_argument("--epochs", type=int, default=200)
    parser.add_argument("--lr", type=float, default=2e-5)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--max-len", type=int, default=2048)
    parser.add_argument("--out", type=Path, default=ROOT / "ours3/deepcad_overfit10_lite")
    parser.add_argument("--log-every", type=int, default=10)
    parser.add_argument("--save-every", type=int, default=50)
    args = parser.parse_args()

    use_edge = args.variant == "ours"
    if use_edge:
        args.train_json = ROOT / "cad_spatial_dataset/DeepCAD/deepcad_cad_ours_overfit10_train.json"
    else:
        args.train_json = ROOT / "cad_spatial_dataset/DeepCAD/deepcad_cad_baseline_overfit10_train.json"

    from transformers import AutoModelForCausalLM, AutoTokenizer
    import spatiallm  # noqa: F401
    from spatiallm_cad_frontend import (
        load_spatiallm_with_edge_channel,
        preprocess_cad_point_cloud,
        widen_embedding_stem,
    )

    # Monkey-patch Sonata flash off (already patched in spatiallm_llama.py)
    samples = load_records(args.train_json, args.media_dir, limit=10)
    print(f"loaded {len(samples)} samples, variant={args.variant}, use_edge={use_edge}")

    tokenizer = AutoTokenizer.from_pretrained(str(args.model), trust_remote_code=True)
    if use_edge:
        model = load_spatiallm_with_edge_channel(args.model, device=args.device, dtype=torch.bfloat16)
    else:
        model = AutoModelForCausalLM.from_pretrained(str(args.model), torch_dtype=torch.bfloat16)
        model.to(args.device)
        model.set_point_backbone_dtype(torch.float32)

    # Freeze point backbone — overfit checks decoder/label wiring first.
    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    if hasattr(model, "gradient_checkpointing_enable"):
        model.gradient_checkpointing_enable()
    model.train()
    trainable = [p for p in model.parameters() if p.requires_grad]
    n_train = sum(p.numel() for p in trainable)
    print(f"trainable params: {n_train:,}")

    from torch.optim import AdamW

    opt = AdamW(trainable, lr=args.lr, fused=False)
    out_dir = args.out / args.variant
    out_dir.mkdir(parents=True, exist_ok=True)
    loss_log = []

    step = 0
    for epoch in range(args.epochs):
        epoch_losses = []
        for sample in samples:
            point_cloud, input_ids, labels, attention_mask = build_batch(
                sample, tokenizer, preprocess_cad_point_cloud, use_edge, args.device, args.max_len
            )
            opt.zero_grad(set_to_none=True)
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
                out = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    point_clouds=point_cloud,
                    labels=labels,
                )
                loss = out.loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            opt.step()
            epoch_losses.append(float(loss.detach().cpu()))
            step += 1
            if step % args.log_every == 0:
                print(f"step={step} epoch={epoch} loss={epoch_losses[-1]:.4f}")
        mean_loss = float(np.mean(epoch_losses))
        loss_log.append({"epoch": epoch, "mean_loss": mean_loss})
        print(f"=== epoch {epoch} mean_loss={mean_loss:.4f} ===")
        (out_dir / "loss.json").write_text(json.dumps(loss_log, indent=2) + "\n", encoding="utf-8")
        if (epoch + 1) % args.save_every == 0 or mean_loss < 0.05:
            ckpt = out_dir / f"epoch_{epoch:03d}"
            ckpt.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(ckpt)
            tokenizer.save_pretrained(ckpt)
            print(f"saved {ckpt}")
            if mean_loss < 0.05:
                print("loss near zero — overfit success")
                break

    (out_dir / "loss.json").write_text(json.dumps(loss_log, indent=2) + "\n", encoding="utf-8")
    print(f"done. final mean_loss={loss_log[-1]['mean_loss']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
