"""L = CE(type) + λ1 * Chamfer(recon) + λ2 * per-type parameter loss."""

from __future__ import annotations

import torch
import torch.nn.functional as F

from curve_encoder_baseline_v1.losses import chamfer_l2, direction_loss, ordered_mse

from .config import TYPE_TO_ID

LINE_ID = TYPE_TO_ID["LINE"]
CIRCLE_ID = TYPE_TO_ID["CIRCLE"]
ELLIPSE_ID = TYPE_TO_ID["ELLIPSE"]
BSPLINE_ID = TYPE_TO_ID["BSPLINE"]


def _rel_err(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    return (pred - gt).abs() / gt.abs().clamp_min(1e-3)


def _angle_pair_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    """(cos,sin) pairs; L2 after unit-normalizing the prediction. [B,2] → [B]."""
    return ((F.normalize(pred, dim=-1, eps=1e-6) - gt) ** 2).sum(-1)


def line_param_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    origin = F.smooth_l1_loss(pred[:, 0:3], gt[:, 0:3], reduction="none").mean(-1)
    direction = direction_loss(pred[:, 3:6], gt[:, 3:6])
    length = _rel_err(pred[:, 6], gt[:, 6])
    return origin + direction + length


def circle_param_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    center = F.smooth_l1_loss(pred[:, 0:3], gt[:, 0:3], reduction="none").mean(-1)
    normal = direction_loss(pred[:, 3:6], gt[:, 3:6])
    radius = _rel_err(pred[:, 6], gt[:, 6])
    a0 = _angle_pair_loss(pred[:, 7:9], gt[:, 7:9])
    a1 = _angle_pair_loss(pred[:, 9:11], gt[:, 9:11])
    span = (pred[:, 11] - gt[:, 11]).abs()
    return center + normal + radius + 0.5 * (a0 + a1) + span


def ellipse_param_loss(pred: torch.Tensor, gt: torch.Tensor) -> torch.Tensor:
    center = F.smooth_l1_loss(pred[:, 0:3], gt[:, 0:3], reduction="none").mean(-1)
    maj = direction_loss(pred[:, 3:6], gt[:, 3:6])
    mn = direction_loss(pred[:, 6:9], gt[:, 6:9])
    nrm = direction_loss(pred[:, 9:12], gt[:, 9:12])
    r_maj = _rel_err(pred[:, 12], gt[:, 12])
    r_min = _rel_err(pred[:, 13], gt[:, 13])
    a0 = _angle_pair_loss(pred[:, 14:16], gt[:, 14:16])
    span = (pred[:, 16] - gt[:, 16]).abs()
    return center + maj + mn + nrm + r_maj + r_min + a0 + span


def compute_losses(
    out: dict[str, torch.Tensor],
    batch: dict[str, torch.Tensor],
    *,
    lambda_type: float,
    lambda_recon: float,
    lambda_param: float,
    use_recon: bool,
    use_param: bool,
) -> dict[str, torch.Tensor]:
    type_id = batch["type_id"]
    device = type_id.device
    zero = torch.zeros((), device=device)

    l_type = F.cross_entropy(out["type_logits"], type_id)

    l_chamfer = zero
    l_recon = zero
    if use_recon:
        recon = out["recon_xyz"]
        tgt = batch["xyz_target"]
        l_chamfer = chamfer_l2(recon, tgt).mean()
        # Chamfer is the reported objective; ordered MSE keeps arc-length order.
        l_recon = 0.5 * l_chamfer + 0.5 * ordered_mse(recon, tgt).mean()

    l_param = zero
    parts: dict[str, torch.Tensor] = {}
    if use_param:
        terms = []
        m = type_id == LINE_ID
        if m.any():
            v = line_param_loss(out["line_param"][m], batch["line_param"][m]).mean()
            parts["param_line"] = v.detach()
            terms.append(v)
        m = type_id == CIRCLE_ID
        if m.any():
            v = circle_param_loss(out["circle_param"][m], batch["circle_param"][m]).mean()
            parts["param_circle"] = v.detach()
            terms.append(v)
        m = type_id == ELLIPSE_ID
        if m.any():
            v = ellipse_param_loss(out["ellipse_param"][m], batch["ellipse_param"][m]).mean()
            parts["param_ellipse"] = v.detach()
            terms.append(v)
        m = (type_id == BSPLINE_ID) & (batch["bspline_degree"] >= 0)
        if m.any():
            deg = F.cross_entropy(
                out["bspline_degree_logits"][m], batch["bspline_degree"][m]
            )
            ncp = F.smooth_l1_loss(
                out["bspline_logncp"][m], batch["bspline_logncp"][m]
            )
            v = deg + ncp
            parts["param_bspline"] = v.detach()
            terms.append(v)
        if terms:
            # type-balanced: rare types are not drowned out by LINE
            l_param = torch.stack(terms).mean()

    total = lambda_type * l_type + lambda_recon * l_recon + lambda_param * l_param
    return {
        "loss": total,
        "loss_type": l_type.detach(),
        "loss_recon": l_recon.detach() if use_recon else zero,
        "loss_chamfer": l_chamfer.detach() if use_recon else zero,
        "loss_param": l_param.detach() if use_param else zero,
        **parts,
    }
