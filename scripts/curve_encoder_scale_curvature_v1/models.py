"""C0–C3 models: PointNet shape ± scale ± curvature ± straightness head."""

from __future__ import annotations

import torch
import torch.nn as nn

from curve_encoder_baseline_v1.config import MAX_PARAM_DIM, N_TYPES, TOKEN_DIM
from curve_encoder_baseline_v1.models import (
    ParameterHead,
    PointNetCurveEncoder,
    ReconstructionHead,
    TypeHead,
)

from .config import CURV_DIM, SCALE_DIM, SHAPE_DIM


class ScaleMLP(nn.Module):
    def __init__(self, in_dim: int = SCALE_DIM, out_dim: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64),
            nn.ReLU(inplace=True),
            nn.Linear(64, out_dim),
            nn.ReLU(inplace=True),
        )
        self.out_dim = out_dim

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class StraightnessHead(nn.Module):
    """Predict [normalized_chord_height, total_turn/360]."""

    def __init__(self, token_dim: int = TOKEN_DIM):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(token_dim, token_dim // 2),
            nn.ReLU(inplace=True),
            nn.Linear(token_dim // 2, 2),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.fc(z)


class ScaleCurvatureModel(nn.Module):
    def __init__(
        self,
        *,
        use_scale_branch: bool,
        use_curvature: bool,
        use_straightness_head: bool,
        token_dim: int = TOKEN_DIM,
        shape_dim: int = SHAPE_DIM,
    ):
        super().__init__()
        self.use_scale_branch = use_scale_branch
        self.use_curvature = use_curvature
        self.use_straightness_head = use_straightness_head
        self.shape_enc = PointNetCurveEncoder(shape_dim, token_dim)
        fuse_in = token_dim
        self.scale_mlp = None
        if use_scale_branch:
            self.scale_mlp = ScaleMLP(SCALE_DIM, 64)
            fuse_in += 64
        if use_curvature:
            fuse_in += CURV_DIM
        self.need_fuse = use_scale_branch or use_curvature
        if self.need_fuse:
            self.fuse = nn.Sequential(
                nn.Linear(fuse_in, token_dim),
                nn.ReLU(inplace=True),
                nn.Linear(token_dim, token_dim),
            )
        else:
            self.fuse = None  # C0/C1: token = PointNet output (P2-compatible)
        self.type_head = TypeHead(token_dim)
        self.recon_head = ReconstructionHead(token_dim)
        self.param_head = ParameterHead(token_dim)
        self.straight_head = StraightnessHead(token_dim) if use_straightness_head else None
        self.token_dim = token_dim

    def forward(
        self,
        shape_feats: torch.Tensor,
        scale_feat: torch.Tensor | None = None,
        curv_feat: torch.Tensor | None = None,
    ) -> dict[str, torch.Tensor]:
        h = self.shape_enc(shape_feats)
        if not self.need_fuse:
            z = h
        else:
            parts = [h]
            if self.use_scale_branch:
                assert scale_feat is not None and self.scale_mlp is not None
                parts.append(self.scale_mlp(scale_feat))
            if self.use_curvature:
                assert curv_feat is not None
                parts.append(curv_feat)
            z = self.fuse(torch.cat(parts, dim=-1))
        out = {
            "token": z,
            "type_logits": self.type_head(z),
            "recon_xyz": self.recon_head(z),
            "param": self.param_head(z),
        }
        if self.straight_head is not None:
            out["straight"] = self.straight_head(z)
        return out


def build_model(spec: dict) -> ScaleCurvatureModel:
    return ScaleCurvatureModel(
        use_scale_branch=spec["use_scale_branch"],
        use_curvature=spec["use_curvature"],
        use_straightness_head=spec["use_straightness_head"],
    )
