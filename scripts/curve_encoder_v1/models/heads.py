"""Shared prediction heads for Curve Encoder V1."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from ..config import N_SAMPLE, N_TYPES, PARAM_DIM, TOKEN_DIM


class CurveHeads(nn.Module):
    def __init__(self, token_dim: int = TOKEN_DIM, n_sample: int = N_SAMPLE):
        super().__init__()
        self.n_sample = n_sample
        self.type_head = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, N_TYPES),
        )
        self.recon_head = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, n_sample * 3),
        )
        self.param_head = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, PARAM_DIM),
        )

    def forward(self, token: torch.Tensor) -> dict[str, torch.Tensor]:
        b = token.shape[0]
        return {
            "token": token,
            "type_logits": self.type_head(token),
            "xyz_recon": self.recon_head(token).view(b, self.n_sample, 3),
            "params": self.param_head(token),
        }
