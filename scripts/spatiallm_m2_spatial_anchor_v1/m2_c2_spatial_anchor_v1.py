"""Trainable M2-C2-SPATIAL-ANCHOR-V1 branch; C2 inputs remain frozen/offline."""
from __future__ import annotations
import torch
from torch import nn
from .anchor_features import AnchorMLP, ANCHOR_VERSION

class M2C2SpatialAnchorV1(nn.Module):
    """Fuses 256-D frozen C2 tokens with 6-D CAD-object anchors before a V3 adapter.

    This owns only AnchorMLP and the supplied geometry adapter; it never owns C2.
    """
    def __init__(self, geometry_adapter: nn.Module, anchor_hidden_dim: int=128):
        super().__init__(); self.anchor_version=ANCHOR_VERSION
        self.anchor_mlp=AnchorMLP(token_dim=256,anchor_dim=6,hidden_dim=anchor_hidden_dim)
        self.geometry_adapter=geometry_adapter
    def forward(self, frozen_c2_tokens: torch.Tensor, object_anchors: torch.Tensor, raw_mask: torch.Tensor):
        fused=self.anchor_mlp(frozen_c2_tokens,object_anchors)
        return self.geometry_adapter(fused,raw_mask)
    def trainable_parameter_groups(self): return {'anchor_mlp':list(self.anchor_mlp.parameters()),'geometry_adapter':list(self.geometry_adapter.parameters()),'c2':[]}
