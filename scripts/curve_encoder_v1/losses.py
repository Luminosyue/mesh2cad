"""Losses for Geometry-only Curve Encoder V1."""

from __future__ import annotations

import torch
import torch.nn.functional as F

from .config import W_PARAM, W_RECON, W_TYPE


def _unit(v: torch.Tensor, eps: float = 1e-8) -> torch.Tensor:
    return v / v.norm(dim=-1, keepdim=True).clamp_min(eps)


def param_loss(pred: torch.Tensor, gt: torch.Tensor, mask: torch.Tensor, type_id: torch.Tensor) -> torch.Tensor:
    """Type-aware parameter loss with angular terms for directions/normals/axes."""
    # Base masked L1 on all active slots.
    base = (pred - gt).abs() * mask
    loss = base.sum() / mask.sum().clamp_min(1.0)

    # Directional extras (cosine) where applicable.
    extras = []
    is_line = type_id == 0
    is_circ = type_id == 1
    is_ell = type_id == 2
    if is_line.any():
        d_p, d_g = _unit(pred[is_line, 3:6]), _unit(gt[is_line, 3:6])
        # Direction is sign-ambiguous.
        cos = (d_p * d_g).sum(-1).abs().clamp(-1, 1)
        extras.append(1.0 - cos)
    if is_circ.any():
        n_p, n_g = _unit(pred[is_circ, 3:6]), _unit(gt[is_circ, 3:6])
        cos = (n_p * n_g).sum(-1).abs().clamp(-1, 1)
        extras.append(1.0 - cos)
    if is_ell.any():
        n_p, n_g = _unit(pred[is_ell, 3:6]), _unit(gt[is_ell, 3:6])
        a_p, a_g = _unit(pred[is_ell, 6:9]), _unit(gt[is_ell, 6:9])
        extras.append(1.0 - (n_p * n_g).sum(-1).abs().clamp(-1, 1))
        extras.append(1.0 - (a_p * a_g).sum(-1).abs().clamp(-1, 1))
    if extras:
        loss = loss + torch.cat(extras).mean()
    return loss


# Approximate inverse-frequency weights from the full dataset distribution
# (LINE 95.3%, CIRCLE 3.5%, ELLIPSE 0.21%, BSPLINE 0.91%). Renormalized to mean 1.
TYPE_CLASS_WEIGHTS = (0.15, 4.0, 25.0, 8.0)


def compute_losses(out: dict, batch: dict, class_weights: torch.Tensor | None = None) -> dict[str, torch.Tensor]:
    if class_weights is None:
        class_weights = torch.tensor(
            TYPE_CLASS_WEIGHTS, device=out["type_logits"].device, dtype=out["type_logits"].dtype
        )
    type_loss = F.cross_entropy(out["type_logits"], batch["type_id"], weight=class_weights)
    # Ordered MSE on the shared arc-length sample grid (+ Chamfer reported at eval).
    recon = ((out["xyz_recon"] - batch["xyz_gt"]) ** 2).sum(-1).mean()
    recon_l2 = (out["xyz_recon"] - batch["xyz_gt"]).norm(dim=-1).mean()
    p_loss = param_loss(out["params"], batch["params"], batch["param_mask"], batch["type_id"])
    total = W_TYPE * type_loss + W_RECON * recon + W_PARAM * p_loss
    return {
        "loss": total,
        "type_loss": type_loss.detach(),
        "recon_loss": recon.detach(),
        "recon_l2": recon_l2.detach(),
        "param_loss": p_loss.detach(),
    }
