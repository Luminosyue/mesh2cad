from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F

LAMBDA_ATTENTION = 0.1


class OperationConditionedHead(nn.Module):
    def __init__(self, arm: str, hidden: int = 512, heads: int = 8):
        super().__init__()
        if arm not in {'P1_OPQUERY_CURVE_ONLY', 'P2_OPQUERY_SURFACE_ONLY', 'P3_OPQUERY_SURFACE_CURVE'}:
            raise ValueError(arm)
        self.arm = arm
        self.use_surface = arm in {'P2_OPQUERY_SURFACE_ONLY', 'P3_OPQUERY_SURFACE_CURVE'}
        self.use_curve = arm in {'P1_OPQUERY_CURVE_ONLY', 'P3_OPQUERY_SURFACE_CURVE'}
        self.query_projection = nn.Sequential(nn.LayerNorm(2048), nn.Linear(2048, hidden))
        self.surface_projection = nn.Sequential(nn.Linear(2048, hidden), nn.LayerNorm(hidden))
        self.curve_projection = nn.Sequential(nn.Linear(262, hidden), nn.LayerNorm(hidden))
        self.surface_cross_attention = nn.MultiheadAttention(hidden, heads, batch_first=True)
        self.curve_cross_attention = nn.MultiheadAttention(hidden, heads, batch_first=True)
        self.fusion = nn.Sequential(nn.LayerNorm(hidden * 3), nn.Linear(hidden * 3, hidden), nn.GELU(), nn.Linear(hidden, hidden), nn.GELU())
        self.sketch_head = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 7))
        self.extrude_head = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 2))
        self.box_head = nn.Sequential(nn.Linear(hidden, hidden), nn.GELU(), nn.Linear(hidden, 6))

    def forward(self, query, surface, surface_padding, curve, curve_padding):
        q = self.query_projection(query).unsqueeze(1)
        zero = torch.zeros_like(q[:, 0])
        surface_weights = None
        if self.use_surface:
            sm = self.surface_projection(surface)
            gs, surface_weights = self.surface_cross_attention(q, sm, sm, key_padding_mask=surface_padding, need_weights=True, average_attn_weights=False)
            gs = gs[:, 0]
        else:
            gs = zero
        curve_weights = None
        if self.use_curve:
            cm = self.curve_projection(curve)
            gc, curve_weights = self.curve_cross_attention(q, cm, cm, key_padding_mask=curve_padding, need_weights=True, average_attn_weights=False)
            gc = gc[:, 0]
        else:
            gc = zero
        fused = self.fusion(torch.cat([q[:, 0], gs, gc], dim=-1))
        sketch = self.sketch_head(fused)
        extrude = self.extrude_head(fused)
        box = self.box_head(fused)
        return {
            'circle_center': sketch[:, :3], 'circle_radius': F.softplus(sketch[:, 3]),
            'circle_normal': F.normalize(sketch[:, 4:7], dim=-1),
            'extrude_depth_one': extrude[:, 0], 'extrude_depth_two': extrude[:, 1],
            'box_origin': box[:, :3],
            'box_extent': torch.stack([F.softplus(box[:, 3]), F.softplus(box[:, 4]), box[:, 5]], dim=-1),
            'curve_attention': curve_weights, 'surface_attention': surface_weights,
        }


def supervised_loss(pred, batch, use_curve: bool):
    losses = []
    attention_losses = []
    for i, op_type in enumerate(batch['operation_type']):
        if op_type == 'Extrude':
            target = batch['circle_target'][i]
            losses.extend([
                F.smooth_l1_loss(pred['circle_center'][i], target[:3]),
                F.smooth_l1_loss(pred['circle_radius'][i], target[3]),
                1.0 - torch.abs(torch.dot(pred['circle_normal'][i], target[4:7])),
                F.smooth_l1_loss(pred['extrude_depth_one'][i], batch['extrude_target'][i, 0]),
            ])
            if batch['depth_two_active'][i]:
                losses.append(F.smooth_l1_loss(pred['extrude_depth_two'][i], batch['extrude_target'][i, 1]))
        elif op_type == 'Box':
            losses.extend([
                F.smooth_l1_loss(pred['box_origin'][i], batch['box_target'][i, :3]),
                F.smooth_l1_loss(pred['box_extent'][i], batch['box_target'][i, 3:6]),
            ])
        if use_curve:
            weights = pred['curve_attention'][i, :, 0, :]
            related = batch['related_indices'][i]
            mass = weights[:, related].sum(dim=-1).mean()
            attention_losses.append(-torch.log(mass.clamp_min(1e-8)))
    parameter = torch.stack(losses).mean()
    attention = torch.stack(attention_losses).mean() if attention_losses else parameter.new_zeros(())
    return parameter + LAMBDA_ATTENTION * attention, parameter.detach(), attention.detach()
