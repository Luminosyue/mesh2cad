"""Baseline B2: 1D Transformer Curve Encoder."""

from __future__ import annotations

import math

import torch
import torch.nn as nn

from ..config import N_SAMPLE, TOKEN_DIM
from .heads import CurveHeads


class TransformerCurveEncoder(nn.Module):
    """32 x C → Linear + arc-position embedding → Transformer → CLS pool → 256D."""

    def __init__(
        self,
        in_dim: int = 6,
        token_dim: int = TOKEN_DIM,
        n_layers: int = 4,
        n_heads: int = 4,
        n_sample: int = N_SAMPLE,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.token_dim = token_dim
        self.input_proj = nn.Linear(in_dim, token_dim)
        # Learnable arc-length position embedding (index 0..N-1 ≈ uniform abscissa).
        self.pos_embed = nn.Parameter(torch.zeros(1, n_sample, token_dim))
        nn.init.normal_(self.pos_embed, std=0.02)
        self.cls_token = nn.Parameter(torch.zeros(1, 1, token_dim))
        nn.init.normal_(self.cls_token, std=0.02)
        enc_layer = nn.TransformerEncoderLayer(
            d_model=token_dim,
            nhead=n_heads,
            dim_feedforward=token_dim * 2,
            dropout=dropout,
            batch_first=True,
            activation="gelu",
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(enc_layer, num_layers=n_layers)
        self.heads = CurveHeads(token_dim=token_dim, n_sample=n_sample)

    def encode(self, feat: torch.Tensor, point_mask: torch.Tensor | None = None) -> torch.Tensor:
        b, n, _ = feat.shape
        x = self.input_proj(feat) + self.pos_embed[:, :n, :]
        cls = self.cls_token.expand(b, -1, -1)
        x = torch.cat([cls, x], dim=1)  # [B, 1+N, D]
        key_padding = None
        if point_mask is not None:
            # True = ignore. CLS is never ignored.
            pad = point_mask < 0.5  # [B, N]
            key_padding = torch.cat(
                [torch.zeros(b, 1, device=feat.device, dtype=torch.bool), pad], dim=1
            )
        x = self.encoder(x, src_key_padding_mask=key_padding)
        return x[:, 0]  # CLS

    def forward(self, feat: torch.Tensor, point_mask: torch.Tensor | None = None) -> dict:
        return self.heads(self.encode(feat, point_mask))
