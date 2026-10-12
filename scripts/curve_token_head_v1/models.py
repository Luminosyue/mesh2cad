"""Frozen C2 backbone + type / reconstruction / per-type parameter heads."""

from __future__ import annotations

import torch
import torch.nn as nn

from curve_encoder_baseline_v1.models import (
    PointNetCurveEncoder,
    ReconstructionHead,
    TypeHead,
)
from curve_encoder_scale_curvature_v1.models import ScaleMLP

from .config import (
    BSPLINE_DEGREE_CLASSES,
    CIRCLE_DIM,
    ELLIPSE_DIM,
    LINE_DIM,
    N_POINTS,
    N_TYPES,
    TOKEN_DIM,
)


class C2Backbone(nn.Module):
    """FROZEN architecture: PointNet(curve-local shape) ⊕ MLP(log length) → 256-D."""

    def __init__(self, shape_dim: int = 7, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.shape_enc = PointNetCurveEncoder(shape_dim, token_dim)
        self.scale_mlp = ScaleMLP(1, 64)
        self.fuse = nn.Sequential(
            nn.Linear(token_dim + 64, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, token_dim),
        )

    def forward(self, shape_feats: torch.Tensor, scale_feat: torch.Tensor) -> torch.Tensor:
        h = self.shape_enc(shape_feats)
        s = self.scale_mlp(scale_feat)
        return self.fuse(torch.cat([h, s], dim=-1))


class _MLPHead(nn.Module):
    def __init__(self, token_dim: int, out_dim: int, hidden: int | None = None):
        super().__init__()
        hidden = hidden or token_dim // 2
        self.net = nn.Sequential(
            nn.Linear(token_dim, token_dim),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim, hidden),
            nn.ReLU(inplace=True),
            nn.Linear(hidden, out_dim),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


class CurveTokenModel(nn.Module):
    def __init__(self, *, use_recon: bool, use_param: bool, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.backbone = C2Backbone(token_dim=token_dim)
        # identical to C2's classification path, so D0 == C2 architecture
        self.type_head = TypeHead(token_dim, N_TYPES)
        self.use_recon = use_recon
        self.use_param = use_param
        self.recon_head = ReconstructionHead(token_dim, N_POINTS) if use_recon else None
        if use_param:
            self.line_head = _MLPHead(token_dim, LINE_DIM)
            self.circle_head = _MLPHead(token_dim, CIRCLE_DIM)
            self.ellipse_head = _MLPHead(token_dim, ELLIPSE_DIM)
            self.bspline_degree_head = _MLPHead(token_dim, BSPLINE_DEGREE_CLASSES)
            self.bspline_ncp_head = _MLPHead(token_dim, 1)

    def forward(self, shape_feats: torch.Tensor, scale_feat: torch.Tensor) -> dict:
        z = self.backbone(shape_feats, scale_feat)
        out = {"token": z, "type_logits": self.type_head(z)}
        if self.recon_head is not None:
            out["recon_xyz"] = self.recon_head(z)
        if self.use_param:
            out["line_param"] = self.line_head(z)
            out["circle_param"] = self.circle_head(z)
            out["ellipse_param"] = self.ellipse_head(z)
            out["bspline_degree_logits"] = self.bspline_degree_head(z)
            out["bspline_logncp"] = self.bspline_ncp_head(z)
        return out


def build_model(spec: dict) -> CurveTokenModel:
    return CurveTokenModel(use_recon=spec["use_recon"], use_param=spec["use_param"])
