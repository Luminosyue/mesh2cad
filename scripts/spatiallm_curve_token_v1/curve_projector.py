"""Step 1: the Curve Token Adapter.

The frozen Curve Encoder emits 256-D tokens; SpatialLM1.1-Llama-1B has
``hidden_size = 2048`` (not 4096). The adapter is the only new trainable module
on the curve path.

Shape parity with the B1 edge projector matters for a fair comparison: B1 uses
``Linear(512,512) → GELU → Linear(512,2048)``, so the default here is the same
two-layer MLP at 256 width. ``CURVE_PROJECTOR=linear`` switches to a bare
``Linear(256, 2048)``.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class CurveProjector(nn.Module):
    def __init__(self, in_dim: int = 256, hidden_size: int = 2048, kind: str = "mlp"):
        super().__init__()
        self.in_dim = in_dim
        self.hidden_size = hidden_size
        self.kind = kind
        if kind == "linear":
            self.net: nn.Module = nn.Linear(in_dim, hidden_size)
        elif kind == "mlp":
            self.net = nn.Sequential(
                nn.Linear(in_dim, in_dim),
                nn.GELU(),
                nn.Linear(in_dim, hidden_size),
            )
        else:
            raise ValueError(f"unknown curve projector kind {kind!r}")

    def forward(self, curve_tokens: torch.Tensor) -> torch.Tensor:
        """``[K, in_dim]`` frozen curve tokens → ``[K, hidden_size]`` LLM embeddings."""
        if curve_tokens.shape[-1] != self.in_dim:
            raise ValueError(
                f"curve tokens must have {self.in_dim} channels, got {curve_tokens.shape}"
            )
        return self.net(curve_tokens)


def build_curve_projector(
    in_dim: int, hidden_size: int, kind: str | None = None
) -> CurveProjector:
    import os

    return CurveProjector(in_dim, hidden_size, kind or os.environ.get("CURVE_PROJECTOR", "mlp"))
