#!/usr/bin/env python3
"""Train / eval one CURVE_ENCODER_BASELINE_V1 experiment (P0–T2)."""

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
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from curve_encoder_baseline_v1.config import (  # noqa: E402
    EXPERIMENTS,
    RUNS_DIR,
    SCHEMA_VERSION,
    SPLIT_DIR,
    SPLIT_NAME,
    TOKEN_DIM,
    TRAIN,
)
from curve_encoder_baseline_v1.dataset import (  # noqa: E402
    CurveEncoderDataset,
    TypeAwareSampler,
    collate_curves,
)
from curve_encoder_baseline_v1.losses import compute_losses  # noqa: E402
from curve_encoder_baseline_v1.metrics import evaluate_model, primary_scorecard  # noqa: E402
from curve_encoder_baseline_v1.models import build_model  # noqa: E402


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def cosine_lr(optimizer, epoch: int, epochs: int, base_lr: float, warmup: int) -> float:
    if epoch < warmup:
        lr = base_lr * float(epoch + 1) / float(max(warmup, 1))
    else:
        t = (epoch - warmup) / float(max(epochs - warmup, 1))
        lr = base_lr * 0.5 * (1.0 + math.cos(math.pi * t))
    for g in optimizer.param_groups:
        g["lr"] = lr
    return lr


def train_one_epoch(model, loader, optimizer, device, cfg: dict) -> dict:
    model.train()
    totals = {k: 0.0 for k in ("loss", "loss_type", "loss_recon", "loss_param", "loss_chamfer")}
    n = 0
    for batch in loader:
        batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
        out = model(batch["feats"])
        losses = compute_losses(
            out,
            batch,
            lambda_type=cfg["lambda_type"],
            lambda_recon=cfg["lambda_recon"],
            lambda_param=cfg["lambda_param"],
        )
        optimizer.zero_grad(set_to_none=True)
        losses["loss"].backward()
        if cfg["grad_clip"] > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip"])
        optimizer.step()
        bs = batch["feats"].size(0)
        for k in totals:
            totals[k] += float(losses[k]) * bs
        n += bs
    return {k: totals[k] / max(n, 1) for k in totals}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exp", required=True, choices=sorted(EXPERIMENTS.keys()))
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--epochs", type=int, default=TRAIN["epochs"])
    ap.add_argument("--batch-size", type=int, default=TRAIN["batch_size"])
    ap.add_argument("--samples-per-epoch", type=int, default=TRAIN["samples_per_epoch"])
    ap.add_argument("--lr", type=float, default=TRAIN["lr"])
    ap.add_argument("--seed", type=int, default=TRAIN["seed"])
    ap.add_argument("--num-workers", type=int, default=TRAIN["num_workers"])
    ap.add_argument("--force-rebuild-cache", action="store_true")
    ap.add_argument("--smoke", action="store_true", help="2 epochs, tiny budget")
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()

    if not (SPLIT_DIR / "manifest.json").is_file():
        raise SystemExit(
            f"missing {SPLIT_DIR / 'manifest.json'}; run make_frozen_split_v1.py first"
        )

    cfg = dict(TRAIN)
    cfg.update(
        {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "samples_per_epoch": args.samples_per_epoch,
            "lr": args.lr,
            "seed": args.seed,
            "num_workers": args.num_workers,
        }
    )
    if args.smoke:
        cfg["epochs"] = min(2, cfg["epochs"])
        cfg["samples_per_epoch"] = min(2048, cfg["samples_per_epoch"])
        cfg["batch_size"] = min(64, cfg["batch_size"])

    spec = EXPERIMENTS[args.exp]
    set_seed(cfg["seed"])
    device = torch.device(args.device)

    out_dir = args.out_dir or (RUNS_DIR / f"{args.exp}_{SPLIT_NAME}")
    if args.smoke:
        out_dir = args.out_dir or (RUNS_DIR / f"{args.exp}_{SPLIT_NAME}_smoke")
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[exp={args.exp}] encoder={spec['encoder']} features={spec['features']} device={device}")
    train_ds = CurveEncoderDataset(
        "train", spec["features"], force_rebuild=args.force_rebuild_cache
    )
    val_ds = CurveEncoderDataset("val", spec["features"], force_rebuild=False)
    test_ds = CurveEncoderDataset("test", spec["features"], force_rebuild=False)

    train_sampler = TypeAwareSampler(
        train_ds.type_id, cfg["samples_per_epoch"], seed=cfg["seed"]
    )
    train_loader = DataLoader(
        train_ds,
        batch_size=cfg["batch_size"],
        sampler=train_sampler,
        num_workers=cfg["num_workers"],
        collate_fn=collate_curves,
        pin_memory=device.type == "cuda",
        drop_last=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=cfg["num_workers"],
        collate_fn=collate_curves,
        pin_memory=device.type == "cuda",
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=cfg["num_workers"],
        collate_fn=collate_curves,
        pin_memory=device.type == "cuda",
    )

    model = build_model(spec["encoder"], tuple(spec["features"])).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"]
    )

    history = []
    best = {"macro_f1": -1.0, "epoch": -1}
    t0 = time.time()
    for epoch in range(cfg["epochs"]):
        train_sampler.set_epoch(epoch)
        lr = cosine_lr(optimizer, epoch, cfg["epochs"], cfg["lr"], cfg["warmup_epochs"])
        tr = train_one_epoch(model, train_loader, optimizer, device, cfg)
        row = {"epoch": epoch + 1, "lr": lr, "train": tr}
        if (epoch + 1) % cfg["eval_every"] == 0 or epoch + 1 == cfg["epochs"]:
            val = evaluate_model(model, val_loader, device)
            row["val"] = primary_scorecard(val)
            row["val_full"] = val
            print(
                f"[{args.exp}] epoch={epoch+1}/{cfg['epochs']} "
                f"loss={tr['loss']:.4f} type={tr['loss_type']:.4f} "
                f"recon={tr['loss_recon']:.4f} param={tr['loss_param']:.4f} | "
                f"val macroF1={val['macro_f1']:.4f} balAcc={val['balanced_accuracy']:.4f} "
                f"chamfer={val['recon_chamfer']['mean']:.5f} "
                f"({time.time()-t0:.0f}s)",
                flush=True,
            )
            if val["macro_f1"] > best["macro_f1"]:
                best = {"macro_f1": val["macro_f1"], "epoch": epoch + 1}
                torch.save(
                    {
                        "model": model.state_dict(),
                        "exp": args.exp,
                        "spec": spec,
                        "epoch": epoch + 1,
                        "val": primary_scorecard(val),
                    },
                    out_dir / "best.pt",
                )
        else:
            print(
                f"[{args.exp}] epoch={epoch+1}/{cfg['epochs']} loss={tr['loss']:.4f}",
                flush=True,
            )
        # drop bulky confusion from history file size; keep scorecard
        slim = {k: v for k, v in row.items() if k != "val_full"}
        if "val_full" in row:
            slim["val_full_path_hint"] = "see final metrics"
        history.append(slim)

    # final test with best checkpoint
    ckpt = torch.load(out_dir / "best.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    test_metrics = evaluate_model(model, test_loader, device)
    val_metrics = evaluate_model(model, val_loader, device)

    result = {
        "schema_version": SCHEMA_VERSION,
        "experiment": "CURVE_ENCODER_BASELINE_V1",
        "exp_id": args.exp,
        "spec": spec,
        "split": SPLIT_NAME,
        "token_dim": TOKEN_DIM,
        "n_points": 32,
        "train_config": cfg,
        "train_type_counts": train_ds.type_counts,
        "val_type_counts": val_ds.type_counts,
        "test_type_counts": test_ds.type_counts,
        "best_epoch": best["epoch"],
        "val": primary_scorecard(val_metrics),
        "test": primary_scorecard(test_metrics),
        "val_full": val_metrics,
        "test_full": test_metrics,
        "history": history,
        "seconds": time.time() - t0,
        "smoke": bool(args.smoke),
    }
    (out_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (out_dir / "scorecard.json").write_text(
        json.dumps(
            {
                "exp": args.exp,
                "val": result["val"],
                "test": result["test"],
                "best_epoch": best["epoch"],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"exp": args.exp, "val": result["val"], "test": result["test"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
