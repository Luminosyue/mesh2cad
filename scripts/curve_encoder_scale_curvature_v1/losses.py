"""Losses = baseline + optional straightness (C3)."""

from __future__ import annotations

import torch
import torch.nn.functional as F

from curve_encoder_baseline_v1.losses import compute_losses as baseline_losses


def compute_losses(
    out: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    *,
    lambda_type: float,
    lambda_recon: float,
    lambda_param: float,
    lambda_straight: float = 0.0,
) -> dict[str, torch.Tensor]:
    # remap recon target into batch key expected by baseline
    batch_for_base = dict(batch)
    batch_for_base["xyz"] = batch["xyz_recon"]
    losses = baseline_losses(
        out,
        batch_for_base,
        lambda_type=lambda_type,
        lambda_recon=lambda_recon,
        lambda_param=lambda_param,
    )
    if lambda_straight > 0 and "straight" in out:
        # supervise chord_h + total_turn/360
        l_s = F.smooth_l1_loss(out["straight"], batch["straight_gt"])
        losses["loss_straight"] = l_s.detach()
        losses["loss"] = losses["loss"] + lambda_straight * l_s
    else:
        losses["loss_straight"] = torch.zeros((), device=losses["loss"].device)
    return losses
