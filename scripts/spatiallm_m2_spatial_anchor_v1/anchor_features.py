"""Object-frame spatial anchors for frozen 256-D C2 curve tokens."""
from __future__ import annotations
import numpy as np
import torch
from torch import nn

ANCHOR_VERSION = 'M2_C2_ANCHOR_V1_OBJECT_BBOX'

def object_anchor(curve_xyz: np.ndarray, bbox_min: np.ndarray, bbox_max: np.ndarray) -> np.ndarray:
    """Return centroid xyz + extent xyz in CAD-object coordinates, not curve-local coordinates."""
    xyz = np.asarray(curve_xyz, dtype=np.float32)
    if xyz.ndim != 3 or xyz.shape[-1] != 3: raise ValueError('curve_xyz must be [K,N,3]')
    lo, hi = np.asarray(bbox_min,np.float32), np.asarray(bbox_max,np.float32)
    ext = np.maximum(hi - lo, 1e-8); center = (lo + hi) * 0.5
    centroid = xyz.mean(axis=1); curve_extent = xyz.max(axis=1) - xyz.min(axis=1)
    return np.concatenate(((centroid - center) / ext, curve_extent / ext), axis=-1).astype(np.float32)

class AnchorMLP(nn.Module):
    """Trainable fusion only; frozen C2 tokens are inputs and receive no optimizer ownership."""
    def __init__(self, token_dim=256, anchor_dim=6, hidden_dim=128):
        super().__init__()
        self.anchor = nn.Sequential(nn.LayerNorm(anchor_dim), nn.Linear(anchor_dim, hidden_dim), nn.GELU(), nn.Linear(hidden_dim, hidden_dim))
        self.fuse = nn.Sequential(nn.LayerNorm(token_dim + hidden_dim), nn.Linear(token_dim + hidden_dim, token_dim), nn.GELU())
    def forward(self, frozen_c2_token, anchor):
        if frozen_c2_token.shape[:-1] != anchor.shape[:-1]: raise ValueError('token/anchor leading dimensions differ')
        return self.fuse(torch.cat((frozen_c2_token, self.anchor(anchor)), dim=-1))
