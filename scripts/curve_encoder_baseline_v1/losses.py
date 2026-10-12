"""Shared losses for all P0–T2 runs."""

from __future__ import annotations

import torch
import torch.nn.functional as F


def chamfer_l2(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Bidirectional mean NN L2. a,b: [B,N,3] → [B]."""
    d = torch.cdist(a, b, p=2)
    return 0.5 * (d.min(dim=-1).values.mean(dim=-1) + d.min(dim=-2).values.mean(dim=-1))


def ordered_mse(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """Pointwise MSE on arc-length-aligned samples. [B,N,3] → [B]."""
    return ((a - b) ** 2).mean(dim=(1, 2))


def direction_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    """Unit-direction L2 with sign ambiguity (min of d, -d). pred/gt [B,3]."""
    pred = F.normalize(pred, dim=-1, eps=1e-6)
    gt = F.normalize(gt, dim=-1, eps=1e-6)
    d1 = ((pred - gt) ** 2).sum(-1)
    d2 = ((pred + gt) ** 2).sum(-1)
    return torch.minimum(d1, d2)


def normal_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    return direction_loss(pred, gt)


def compute_losses(
    out: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    *,
    lambda_type: float,
    lambda_recon: float,
    lambda_param: float,
) -> dict[str, torch.Tensor]:
    type_logits = out["type_logits"]
    type_id = batch["type_id"]
    l_type = F.cross_entropy(type_logits, type_id)

    recon = out["recon_xyz"]
    xyz = batch["xyz"]
    # Primary recon objective = Chamfer (matches reported metric).
    # Ordered MSE is an auxiliary regularizer for arc-length alignment.
    l_chamfer = chamfer_l2(recon, xyz).mean()
    l_ordered = ordered_mse(recon, xyz).mean()
    l_recon = 0.5 * l_chamfer + 0.5 * l_ordered

    pred_p = out["param"]
    gt_p = batch["param"]
    mask = batch["param_mask"]
    has = batch["has_param"]  # [B]

    # Per-type structured param loss on masked dims
    # LINE direction: dims 0:3 with sign-aware loss
    # CIRCLE/ELLIPSE: masked MSE on remaining dims; normals/axes sign-aware
    B = pred_p.size(0)
    device = pred_p.device
    per = torch.zeros(B, device=device)

    is_line = type_id == 0
    is_circle = type_id == 1
    is_ellipse = type_id == 2

    def _center_err(pred_c: torch.Tensor, gt_c: torch.Tensor, scale: torch.Tensor) -> torch.Tensor:
        # scale-invariant L1 center error (scale ≈ |radius| or 1)
        return (pred_c - gt_c).abs().mean(-1) / scale.clamp_min(1e-3)

    if is_line.any():
        per[is_line] = direction_loss(pred_p[is_line, 0:3], gt_p[is_line, 0:3])

    if is_circle.any():
        c_idx = is_circle
        scale = gt_p[c_idx, 6].abs()
        center = _center_err(pred_p[c_idx, 0:3], gt_p[c_idx, 0:3], scale)
        normal = normal_loss(pred_p[c_idx, 3:6], gt_p[c_idx, 3:6])
        radius = (pred_p[c_idx, 6] - gt_p[c_idx, 6]).abs() / scale.clamp_min(1e-3)
        per[c_idx] = center + normal + radius

    if is_ellipse.any():
        e_idx = is_ellipse
        scale = gt_p[e_idx, 9].abs()
        center = _center_err(pred_p[e_idx, 0:3], gt_p[e_idx, 0:3], scale)
        maj = direction_loss(pred_p[e_idx, 3:6], gt_p[e_idx, 3:6])
        mn = direction_loss(pred_p[e_idx, 6:9], gt_p[e_idx, 6:9])
        rmaj = (pred_p[e_idx, 9] - gt_p[e_idx, 9]).abs() / scale.clamp_min(1e-3)
        rmin = (pred_p[e_idx, 10] - gt_p[e_idx, 10]).abs() / (
            gt_p[e_idx, 10].abs().clamp_min(1e-3)
        )
        per[e_idx] = center + maj + mn + rmaj + rmin

    # BSPLINE: has_param=0 → ignored
    denom = has.sum().clamp_min(1.0)
    l_param = (per * has).sum() / denom

    # Light masked L1 on active dims (keeps unused dims near 0 without exploding)
    l1_mask = ((pred_p - gt_p).abs() * mask).sum() / mask.sum().clamp_min(1.0)
    l_param = l_param + 0.05 * l1_mask

    total = lambda_type * l_type + lambda_recon * l_recon + lambda_param * l_param
    return {
        "loss": total,
        "loss_type": l_type.detach(),
        "loss_recon": l_recon.detach(),
        "loss_chamfer": l_chamfer.detach(),
        "loss_ordered": l_ordered.detach(),
        "loss_param": l_param.detach(),
    }
