"""Encoders + multi-head Curve Token model."""

from __future__ import annotations

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .config import MAX_PARAM_DIM, N_POINTS, N_TYPES, TOKEN_DIM


class PointNetCurveEncoder(nn.Module):
    def __init__(self, in_dim: int, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, 128),
            nn.ReLU(inplace=True),
            nn.Linear(128, token_dim),
            nn.ReLU(inplace=True),
        )
        self.proj = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, token_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, N, C]
        h = self.mlp(x).max(dim=1).values
        return self.proj(h)


class TransformerCurveEncoder(nn.Module):
    def __init__(
        self,
        in_dim: int,
        token_dim: int = TOKEN_DIM,
        n_layers: int = 4,
        n_heads: int = 4,
        ff_mult: int = 2,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.embed = nn.Linear(in_dim, token_dim)
        self.pos = nn.Parameter(torch.zeros(1, N_POINTS, token_dim))
        nn.init.normal_(self.pos, std=0.02)
        layer = nn.TransformerEncoderLayer(
            d_model=token_dim,
            nhead=n_heads,
            dim_feedforward=token_dim * ff_mult,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True,
        )
        self.encoder = nn.TransformerEncoder(layer, num_layers=n_layers)
        self.norm = nn.LayerNorm(token_dim)
        self.pool = nn.Linear(token_dim, token_dim)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        h = self.embed(x) + self.pos[:, : x.size(1), :]
        h = self.encoder(h)
        h = self.norm(h)
        return self.pool(h.mean(dim=1))


class TypeHead(nn.Module):
    def __init__(self, token_dim: int = TOKEN_DIM, n_types: int = N_TYPES):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(token_dim, token_dim // 2),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim // 2, n_types),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.fc(z)


class ReconstructionHead(nn.Module):
    """Decode Curve Token → ordered [N,3] xyz in normalized frame."""

    def __init__(self, token_dim: int = TOKEN_DIM, n_points: int = N_POINTS):
        super().__init__()
        self.n_points = n_points
        self.fc = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, n_points * 3),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.fc(z).view(-1, self.n_points, 3)


class ParameterHead(nn.Module):
    """Shared MLP → MAX_PARAM_DIM; type-specific slices supervised via mask.

    BSPLINE has zero mask → no param regression (by design).
    """

    def __init__(self, token_dim: int = TOKEN_DIM, param_dim: int = MAX_PARAM_DIM):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, token_dim // 2),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim // 2, param_dim),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.fc(z)


class CurveTokenModel(nn.Module):
    def __init__(self, encoder_name: str, in_dim: int, token_dim: int = TOKEN_DIM):
        super().__init__()
        if encoder_name == "pointnet":
            self.encoder = PointNetCurveEncoder(in_dim, token_dim)
        elif encoder_name == "transformer":
            self.encoder = TransformerCurveEncoder(in_dim, token_dim)
        else:
            raise ValueError(encoder_name)
        self.type_head = TypeHead(token_dim)
        self.recon_head = ReconstructionHead(token_dim)
        self.param_head = ParameterHead(token_dim)
        self.token_dim = token_dim

    def forward(self, feats: torch.Tensor) -> dict[str, torch.Tensor]:
        z = self.encoder(feats)
        return {
            "token": z,
            "type_logits": self.type_head(z),
            "recon_xyz": self.recon_head(z),
            "param": self.param_head(z),
        }


def build_model(encoder_name: str, features: tuple[str, ...]) -> CurveTokenModel:
    from .dataset import feature_channels

    return CurveTokenModel(encoder_name, feature_channels(features))
