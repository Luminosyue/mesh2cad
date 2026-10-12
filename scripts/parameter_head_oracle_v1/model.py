from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


FEATURE_DIM = 262


class TokenHead(nn.Module):
    def __init__(self, output_dim: int, hidden: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.LayerNorm(FEATURE_DIM),
            nn.Linear(FEATURE_DIM, hidden), nn.GELU(),
            nn.Linear(hidden, hidden), nn.GELU(),
            nn.Linear(hidden, output_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class ProfileAggregator(nn.Module):
    def __init__(self, hidden: int = 256, heads: int = 4):
        super().__init__()
        self.input = nn.Sequential(nn.LayerNorm(FEATURE_DIM), nn.Linear(FEATURE_DIM, hidden))
        self.query = nn.Parameter(torch.zeros(1, 1, hidden))
        nn.init.normal_(self.query, std=0.02)
        self.attention = nn.MultiheadAttention(hidden, heads, batch_first=True)
        self.output = nn.Sequential(nn.LayerNorm(hidden), nn.Linear(hidden, hidden), nn.GELU())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [K, 262], where K is the exact oracle profile/local edge set.
        z = self.input(x).unsqueeze(0)
        q = self.query.expand(1, -1, -1)
        pooled, _ = self.attention(q, z, z, need_weights=False)
        return self.output(pooled[:, 0])[0]


class ParameterHeads(nn.Module):
    def __init__(self, hidden: int = 256):
        super().__init__()
        self.circle = TokenHead(7, hidden)
        self.extrude_aggregator = ProfileAggregator(hidden)
        self.extrude = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 8))
        self.box_aggregator = ProfileAggregator(hidden)
        self.box = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 6))

    def forward(self, head_type: str, features: torch.Tensor) -> dict[str, torch.Tensor]:
        if head_type == 'circle':
            raw = self.circle(features[0])
            return {'center': raw[:3], 'radius': F.softplus(raw[3:4])[0], 'normal': F.normalize(raw[4:7], dim=0)}
        if head_type == 'extrude':
            raw = self.extrude(self.extrude_aggregator(features))
            return {'origin': raw[:3], 'direction': F.normalize(raw[3:6], dim=0), 'depth': raw[6], 'height_two': raw[7]}
        if head_type == 'box':
            raw = self.box(self.box_aggregator(features))
            return {'origin': raw[:3], 'extent': torch.stack((F.softplus(raw[3]), F.softplus(raw[4]), raw[5]))}
        raise KeyError(head_type)


def loss_for(head_type: str, prediction: dict, target: dict) -> torch.Tensor:
    if head_type == 'circle':
        center = F.smooth_l1_loss(prediction['center'], target['center'])
        radius = F.smooth_l1_loss(prediction['radius'], target['radius'])
        # A circle plane is invariant to n -> -n.
        orientation = 1.0 - torch.abs(torch.dot(prediction['normal'], target['normal']))
        return center + radius + orientation
    if head_type == 'extrude':
        origin = F.smooth_l1_loss(prediction['origin'], target['origin'])
        direction = 1.0 - torch.dot(prediction['direction'], target['direction'])
        depth = F.smooth_l1_loss(prediction['depth'], target['depth'])
        second = F.smooth_l1_loss(prediction['height_two'], target['height_two'])
        return origin + direction + depth + second
    if head_type == 'box':
        return F.smooth_l1_loss(prediction['origin'], target['origin']) + F.smooth_l1_loss(prediction['extent'], target['extent'])
    raise KeyError(head_type)
