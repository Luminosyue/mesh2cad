"""Baseline B1: PointNet Curve Encoder."""

from __future__ import annotations

import torch
import torch.nn as nn

from ..config import TOKEN_DIM
from .heads import CurveHeads


class PointNetCurveEncoder(nn.Module):
    """32 x C → MLP → max-pool → 256D token → heads."""

    def __init__(self, in_dim: int = 6, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, token_dim),
            nn.ReLU(inplace=True),
        )
        self.heads = CurveHeads(token_dim=token_dim)

    def encode(self, feat: torch.Tensor, point_mask: torch.Tensor | None = None) -> torch.Tensor:
        # feat: [B, N, C]
        h = self.mlp(feat)
        if point_mask is not None:
            # Masked max-pool: unobserved points → -inf
            neg = torch.finfo(h.dtype).min
            m = point_mask.unsqueeze(-1)
            h = h.masked_fill(m < 0.5, neg)
        token = h.max(dim=1).values
        # If an entire curve was masked (shouldn't happen), fall back to zeros.
        bad = ~torch.isfinite(token).all(dim=-1)
        if bad.any():
            token = torch.where(bad.unsqueeze(-1), torch.zeros_like(token), token)
        return token

    def forward(self, feat: torch.Tensor, point_mask: torch.Tensor | None = None) -> dict:
        return self.heads(self.encode(feat, point_mask))
