"""Train Geometry-only Curve Encoder baselines (PointNet / Transformer)."""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

from .config import (
    CKPT_DIR,
    DEFAULT_BATCH,
    DEFAULT_EPOCHS,
    DEFAULT_LR,
    DEFAULT_NUM_WORKERS,
    DEFAULT_WEIGHT_DECAY,
    RUNS_DIR,
    TOKEN_DIM,
)
from .dataset import CurveCacheDataset, input_dim, make_loader
from .losses import compute_losses
from .models import PointNetCurveEncoder, TransformerCurveEncoder


def build_model(arch: str, in_dim: int, n_layers: int = 4) -> torch.nn.Module:
    if arch == "pointnet":
        return PointNetCurveEncoder(in_dim=in_dim, token_dim=TOKEN_DIM)
    if arch == "transformer":
        return TransformerCurveEncoder(in_dim=in_dim, token_dim=TOKEN_DIM, n_layers=n_layers)
    raise ValueError(arch)


@torch.no_grad()
def eval_epoch(model, loader, device) -> dict:
    model.eval()
    totals = {"loss": 0.0, "type_loss": 0.0, "recon_loss": 0.0, "param_loss": 0.0, "recon_l2": 0.0, "n": 0}
    correct, total = 0, 0
    for batch in loader:
        batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
        out = model(batch["feat"], batch["point_mask"])
        losses = compute_losses(out, batch)
        bs = batch["feat"].shape[0]
        for k in ("loss", "type_loss", "recon_loss", "param_loss", "recon_l2"):
            totals[k] += float(losses[k]) * bs
        totals["n"] += bs
        pred = out["type_logits"].argmax(-1)
        correct += int((pred == batch["type_id"]).sum())
        total += bs
    n = max(totals["n"], 1)
    return {
        "loss": totals["loss"] / n,
        "type_loss": totals["type_loss"] / n,
        "recon_loss": totals["recon_loss"] / n,
        "param_loss": totals["param_loss"] / n,
        "recon_l2": totals["recon_l2"] / n,
        "type_acc": correct / max(total, 1),
    }


def train_one(
    arch: str,
    ablation: str,
    epochs: int,
    batch_size: int,
    lr: float,
    device: str,
    run_name: str,
    max_train_curves: int | None = None,
    noise_rel: float = 0.0,
    partial_frac: float = 1.0,
    n_layers: int = 4,
    seed: int = 0,
) -> dict:
    torch.manual_seed(seed)
    np.random.seed(seed)

    in_dim = input_dim(ablation)
    train_ds = CurveCacheDataset(
        split="train",
        ablation=ablation,
        noise_rel=noise_rel,
        partial_frac=partial_frac,
        seed=seed,
        max_curves=max_train_curves,
    )
    val_ds = CurveCacheDataset(
        split="val",
        ablation=ablation,
        noise_rel=0.0,
        partial_frac=1.0,
        seed=seed + 1,
    )
    train_loader = make_loader(train_ds, batch_size, shuffle=True, num_workers=DEFAULT_NUM_WORKERS)
    val_loader = make_loader(val_ds, batch_size, shuffle=False, num_workers=DEFAULT_NUM_WORKERS)

    model = build_model(arch, in_dim, n_layers=n_layers).to(device)
    opt = AdamW(model.parameters(), lr=lr, weight_decay=DEFAULT_WEIGHT_DECAY)
    sched = CosineAnnealingLR(opt, T_max=max(epochs, 1))

    run_dir = RUNS_DIR / run_name
    ckpt_dir = CKPT_DIR / run_name
    run_dir.mkdir(parents=True, exist_ok=True)
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    history = []
    best_val = float("inf")
    best_path = ckpt_dir / "best.pt"
    t0 = time.time()

    for epoch in range(1, epochs + 1):
        model.train()
        running = 0.0
        n_seen = 0
        for batch in train_loader:
            batch = {k: v.to(device) if torch.is_tensor(v) else v for k, v in batch.items()}
            out = model(batch["feat"], batch["point_mask"])
            losses = compute_losses(out, batch)
            opt.zero_grad(set_to_none=True)
            losses["loss"].backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            bs = batch["feat"].shape[0]
            running += float(losses["loss"]) * bs
            n_seen += bs
        sched.step()
        train_loss = running / max(n_seen, 1)
        val_stats = eval_epoch(model, val_loader, device)
        row = {"epoch": epoch, "train_loss": train_loss, **{f"val_{k}": v for k, v in val_stats.items()}}
        history.append(row)
        print(
            f"[{run_name}] epoch {epoch}/{epochs}  train={train_loss:.4f}  "
            f"val_loss={val_stats['loss']:.4f}  type_acc={val_stats['type_acc']:.4f}  "
            f"recon_l2={val_stats['recon_l2']:.5f}",
            flush=True,
        )
        if val_stats["loss"] < best_val:
            best_val = val_stats["loss"]
            torch.save(
                {
                    "model": model.state_dict(),
                    "arch": arch,
                    "ablation": ablation,
                    "in_dim": in_dim,
                    "n_layers": n_layers,
                    "epoch": epoch,
                    "val": val_stats,
                    "noise_rel_train": noise_rel,
                    "partial_frac_train": partial_frac,
                },
                best_path,
            )

    # Final checkpoint
    last_path = ckpt_dir / "last.pt"
    torch.save({"model": model.state_dict(), "arch": arch, "ablation": ablation, "in_dim": in_dim}, last_path)

    summary = {
        "run_name": run_name,
        "arch": arch,
        "ablation": ablation,
        "epochs": epochs,
        "batch_size": batch_size,
        "lr": lr,
        "device": device,
        "n_train": len(train_ds),
        "n_val": len(val_ds),
        "best_val_loss": best_val,
        "best_ckpt": str(best_path),
        "history": history,
        "seconds": time.time() - t0,
        "noise_rel_train": noise_rel,
        "partial_frac_train": partial_frac,
    }
    (run_dir / "train_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--arch", choices=["pointnet", "transformer"], required=True)
    ap.add_argument("--ablation", default="B1_xyz_tangent")
    ap.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    ap.add_argument("--batch-size", type=int, default=DEFAULT_BATCH)
    ap.add_argument("--lr", type=float, default=DEFAULT_LR)
    ap.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    ap.add_argument("--run-name", default=None)
    ap.add_argument("--max-train-curves", type=int, default=None)
    ap.add_argument("--noise-rel", type=float, default=0.0)
    ap.add_argument("--partial-frac", type=float, default=1.0)
    ap.add_argument("--n-layers", type=int, default=4)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    run_name = args.run_name or f"{args.arch}_{args.ablation}"
    summary = train_one(
        arch=args.arch,
        ablation=args.ablation,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device=args.device,
        run_name=run_name,
        max_train_curves=args.max_train_curves,
        noise_rel=args.noise_rel,
        partial_frac=args.partial_frac,
        n_layers=args.n_layers,
        seed=args.seed,
    )
    print(json.dumps({k: summary[k] for k in summary if k != "history"}, indent=2))


if __name__ == "__main__":
    main()
