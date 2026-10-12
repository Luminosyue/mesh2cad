"""Fixed-query second-stream adapter for the isolated Geometry Prefix V3."""
from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class GeometryPrefixAdapter(nn.Module):
    """Aggregate any masked K-token geometry stream into fixed learned queries."""

    def __init__(
        self,
        input_dim: int,
        llm_dim: int = 2048,
        adapter_dim: int = 512,
        num_queries: int = 8,
        num_heads: int = 8,
        target_norm: float = 2.17,
    ) -> None:
        super().__init__()
        if adapter_dim % num_heads:
            raise ValueError("adapter_dim must be divisible by num_heads")
        self.pre_proj = nn.Linear(input_dim, adapter_dim)
        self.pre_norm = nn.LayerNorm(adapter_dim)
        self.query_tokens = nn.Parameter(torch.randn(1, num_queries, adapter_dim) * 0.02)
        self.cross_attn = nn.MultiheadAttention(adapter_dim, num_heads, batch_first=True)
        self.attn_norm = nn.LayerNorm(adapter_dim)
        self.ffn = nn.Sequential(
            nn.Linear(adapter_dim, adapter_dim * 4), nn.GELU(), nn.Linear(adapter_dim * 4, adapter_dim)
        )
        self.ffn_norm = nn.LayerNorm(adapter_dim)
        self.out_proj = nn.Linear(adapter_dim, llm_dim)
        self.log_scale = nn.Parameter(torch.tensor(math.log(float(target_norm)), dtype=torch.float32))
        self.num_queries = num_queries

    def forward(self, x: torch.Tensor, valid_mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """x is [B,K,Din], valid_mask marks real raw geometry tokens."""
        if x.ndim != 3 or valid_mask.shape != x.shape[:2]:
            raise ValueError(f"bad geometry/mask shapes {tuple(x.shape)} / {tuple(valid_mask.shape)}")
        if not bool(valid_mask.any(dim=1).all()):
            raise ValueError("V3 adapter requires at least one valid raw token per sample")
        h = self.pre_norm(self.pre_proj(x))
        q = self.query_tokens.expand(h.size(0), -1, -1).to(dtype=h.dtype)
        attn, _ = self.cross_attn(q, h, h, key_padding_mask=~valid_mask.bool())
        y = self.attn_norm(q + attn)
        y = self.ffn_norm(y + self.ffn(y))
        y = self.out_proj(y)
        y = F.normalize(y.float(), p=2, dim=-1).to(dtype=y.dtype) * self.log_scale.exp().to(dtype=y.dtype)
        return y, torch.ones((x.size(0), self.num_queries), dtype=torch.bool, device=x.device)
