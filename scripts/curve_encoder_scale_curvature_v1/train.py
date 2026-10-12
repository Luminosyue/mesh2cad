#!/usr/bin/env python3
"""Train one C0–C3 run. Primary selection: minimize val LINE→CIRCLE FP."""

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

from curve_encoder_baseline_v1.dataset import TypeAwareSampler  # noqa: E402
from curve_encoder_scale_curvature_v1.config import (  # noqa: E402
    EXPERIMENTS,
    REF_P2,
    RUNS_DIR,
    SCHEMA_VERSION,
    SPLIT_DIR,
    SPLIT_NAME,
    TOKEN_DIM,
    TRAIN,
)
from curve_encoder_scale_curvature_v1.dataset import (  # noqa: E402
    ScaleCurvatureDataset,
    collate,
)
from curve_encoder_scale_curvature_v1.losses import compute_losses  # noqa: E402
from curve_encoder_scale_curvature_v1.metrics import evaluate_model, scorecard  # noqa: E402
from curve_encoder_scale_curvature_v1.models import build_model  # noqa: E402


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def cosine_lr(optimizer, epoch, epochs, base_lr, warmup) -> float:
    if epoch < warmup:
        lr = base_lr * float(epoch + 1) / float(max(warmup, 1))
    else:
        t = (epoch - warmup) / float(max(epochs - warmup, 1))
        lr = base_lr * 0.5 * (1.0 + math.cos(math.pi * t))
    for g in optimizer.param_groups:
        g["lr"] = lr
    return lr


def prepare_batch(batch, spec, device):
    batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
    frame = spec["frame"]
    shape = batch["feats_object"] if frame == "object" else batch["feats_local"]
    xyz_recon = batch["xyz_object"] if frame == "object" else batch["xyz_local"]
    batch["xyz_recon"] = xyz_recon
    out = {
        "shape": shape,
        "scale": batch["scale_feat"] if spec["use_scale_branch"] else None,
        "curv": batch["curv_feat"] if spec["use_curvature"] else None,
        "batch": batch,
    }
    return out


def train_one_epoch(model, loader, optimizer, device, spec, cfg):
    model.train()
    totals = {
        k: 0.0
        for k in ("loss", "loss_type", "loss_recon", "loss_param", "loss_straight")
    }
    n = 0
    for batch in loader:
        prep = prepare_batch(batch, spec, device)
        out = model(prep["shape"], scale_feat=prep["scale"], curv_feat=prep["curv"])
        losses = compute_losses(
            out,
            prep["batch"],
            lambda_type=cfg["lambda_type"],
            lambda_recon=cfg["lambda_recon"],
            lambda_param=cfg["lambda_param"],
            lambda_straight=cfg["lambda_straight"] if spec["use_straightness_head"] else 0.0,
        )
        optimizer.zero_grad(set_to_none=True)
        losses["loss"].backward()
        if cfg["grad_clip"] > 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip"])
        optimizer.step()
        bs = prep["shape"].size(0)
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
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args()

    if not (SPLIT_DIR / "manifest.json").is_file():
        raise SystemExit(f"missing frozen_v1 split at {SPLIT_DIR}")

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

    print(f"[{args.exp}] {spec['desc']} device={device}", flush=True)
    train_ds = ScaleCurvatureDataset("train")
    val_ds = ScaleCurvatureDataset("val")
    test_ds = ScaleCurvatureDataset("test")

    sampler = TypeAwareSampler(train_ds.type_id, cfg["samples_per_epoch"], seed=cfg["seed"])
    train_loader = DataLoader(
        train_ds,
        batch_size=cfg["batch_size"],
        sampler=sampler,
        num_workers=cfg["num_workers"],
        collate_fn=collate,
        pin_memory=device.type == "cuda",
        drop_last=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=cfg["num_workers"],
        collate_fn=collate,
        pin_memory=device.type == "cuda",
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=cfg["batch_size"],
        shuffle=False,
        num_workers=cfg["num_workers"],
        collate_fn=collate,
        pin_memory=device.type == "cuda",
    )

    model = build_model(spec).to(device)
    optimizer = torch.optim.AdamW(
        model.parameters(), lr=cfg["lr"], weight_decay=cfg["weight_decay"]
    )

    history = []
    best = {"line_to_circle_fp": 10**9, "circle_recall": -1.0, "epoch": -1}
    t0 = time.time()
    for epoch in range(cfg["epochs"]):
        sampler.set_epoch(epoch)
        lr = cosine_lr(optimizer, epoch, cfg["epochs"], cfg["lr"], cfg["warmup_epochs"])
        tr = train_one_epoch(model, train_loader, optimizer, device, spec, cfg)
        row = {"epoch": epoch + 1, "lr": lr, "train": tr}
        if (epoch + 1) % cfg["eval_every"] == 0 or epoch + 1 == cfg["epochs"]:
            val = evaluate_model(model, val_loader, device, spec, val_ds.line_length_p90)
            sc = scorecard(val)
            row["val"] = sc
            print(
                f"[{args.exp}] epoch={epoch+1}/{cfg['epochs']} "
                f"loss={tr['loss']:.4f} | val L→C={sc['line_to_circle_fp']} "
                f"({sc['line_to_circle_rate']:.1%}) top90={sc['top_decile_line_to_circle_fp_rate']:.1%} "
                f"C_rec={sc['circle_recall']:.3f} macroF1={sc['macro_f1']:.3f} "
                f"({time.time()-t0:.0f}s)",
                flush=True,
            )
            better = sc["line_to_circle_fp"] < best["line_to_circle_fp"] or (
                sc["line_to_circle_fp"] == best["line_to_circle_fp"]
                and sc["circle_recall"] > best["circle_recall"]
            )
            if better:
                best = {
                    "line_to_circle_fp": sc["line_to_circle_fp"],
                    "circle_recall": sc["circle_recall"],
                    "epoch": epoch + 1,
                }
                torch.save(
                    {
                        "model": model.state_dict(),
                        "exp": args.exp,
                        "spec": spec,
                        "epoch": epoch + 1,
                        "val": sc,
                    },
                    out_dir / "best.pt",
                )
        history.append(row)

    ckpt = torch.load(out_dir / "best.pt", map_location=device, weights_only=True)
    model.load_state_dict(ckpt["model"])
    val_m = evaluate_model(model, val_loader, device, spec, val_ds.line_length_p90)
    test_m = evaluate_model(model, test_loader, device, spec, test_ds.line_length_p90)
    result = {
        "schema_version": SCHEMA_VERSION,
        "experiment": "CURVE_ENCODER_SCALE_CURVATURE_V1",
        "exp_id": args.exp,
        "spec": spec,
        "split": SPLIT_NAME,
        "token_dim": TOKEN_DIM,
        "train_config": cfg,
        "ref_p2_test": REF_P2,
        "best_epoch": best["epoch"],
        "val": scorecard(val_m),
        "test": scorecard(test_m),
        "val_full": val_m,
        "test_full": test_m,
        "history": [
            {k: v for k, v in h.items() if k != "val_full"} for h in history
        ],
        "seconds": time.time() - t0,
        "smoke": bool(args.smoke),
    }
    (out_dir / "metrics.json").write_text(json.dumps(result, indent=2) + "\n")
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
        + "\n"
    )
    print(json.dumps({"exp": args.exp, "test": result["test"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
