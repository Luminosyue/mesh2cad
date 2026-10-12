#!/usr/bin/env python3
"""Isolated V3 geometry-prefix trainer on SpatialLM-Qwen + Qwen2.5-0.5B-Instruct.

Does not touch the frozen Llama V3 run. Chat template / token ids / hidden size
are Qwen-native; splice / adapter / freeze recipe matches train_v3_smoke.py.
"""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, sys, types
from contextlib import nullcontext

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
PHASE = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/b1_budget_postencoder_phase1_v2_100/code'
sys.path[:0] = [
    str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'),
    str(PHASE),
    str(ROOT / 'SpatialLM'),
    str(ROOT / 'scripts'),
]
os.environ.update(
    CAD_USE_SEPARATE_EDGE_TOKENS='1',
    CAD_SURFACE_POINTS='4096',
    CAD_HELDOUT_PROTOCOL='best_v2',
    CAD_EDGE_SOURCE='gt_sharp',
    CAD_EDGE_BUDGET_MATCH='0',
    PYTHONDONTWRITEBYTECODE='1',
)

import numpy as np
import torch
from transformers import AutoTokenizer
from budget_matched import splice_geometry_masked
from spatiallm.model import spatiallm_llama as llama_module
from spatiallm.model.spatiallm_llama import SpatialLMLlamaForCausalLM
from spatiallm.model.spatiallm_qwen import SpatialLMQwenForCausalLM
from spatiallm.tuner.data.mm_plugin import get_cad_mm_plugin
from spatiallm_curve_token_v1 import heldout_geometry
from geometry_prefix_adapter import GeometryPrefixAdapter

RUN = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/qwen05_v3_1k'
BASE_MODEL = RUN / 'QWEN_GEOMETRY_BASE_V1'
B1_TOKEN_ROOT = RUN / 'b1_tokens'
DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
KCAP = 128
SUMMARY_TOKENS = 8
EOS_ID = 151645  # <|im_end|>
PAD_ID = 151643  # <|endoftext|>
EDGE_START_TOKEN = '<|edge_start|>'
EDGE_PAD_TOKEN = '<|edge_pad|>'
EDGE_END_TOKEN = '<|edge_end|>'


def markers(arm):
    s = '<|point_start|><|point_pad|><|point_end|>'
    if arm != 'b0':
        s += f'{EDGE_START_TOKEN}{EDGE_PAD_TOKEN}{EDGE_END_TOKEN}'
    return s


def encode(tokenizer, row, arm):
    user = markers(arm) + '\nGenerate CAD construction program from the point cloud. Output only valid DSL assignments ending with result = ...'
    prefix = '<|im_start|>user\n' + user + '<|im_end|>\n<|im_start|>assistant\n'
    prompt = tokenizer.encode(prefix, add_special_tokens=False)
    target = tokenizer.encode(pathlib.Path(row['target_dsl']).read_text() + '<|im_end|>', add_special_tokens=False)
    geometry_extra = row['B1']['total_llm_input_length'] - row['k_valid'] + SUMMARY_TOKENS
    allowance = max(32, 4096 - geometry_extra - len(prompt))
    target = target[:allowance]
    ids = torch.tensor([prompt + target], dtype=torch.long)
    labels = torch.tensor([[-100] * len(prompt) + target], dtype=torch.long)
    return ids, labels, len(target), allowance


def second_input(row, arm):
    if arm == 'b0':
        return None, torch.empty(0, dtype=torch.bool)
    idx = row['selected_b1_indices'] if arm == 'b1' else row['selected_m2_indices']
    k = row['k_valid']
    if arm == 'b1':
        raw = np.load(B1_TOKEN_ROOT / row['cad_id'] / 'b1_full_tokens_fp16.npy')
    else:
        raw = np.load(row['m2_full_c2_tokens'])
    sel = raw[np.asarray(idx, dtype=np.int64)]
    out = np.zeros((KCAP, raw.shape[1]), np.float32)
    out[:k] = sel
    mask = torch.zeros(KCAP, dtype=torch.bool)
    mask[:k] = True
    return torch.from_numpy(out), mask


def install_precomputed_second(model, arm, state):
    original_splice = llama_module._splice_geometry

    def forward_geometry(self, surface_points, edge_points=None, device=None, dtype=None):
        with torch.no_grad():
            surface = self.forward_point_cloud(surface_points, device, dtype, projector=self.point_proj)
        if arm == 'b0':
            return surface, None
        proj_dtype = next(self.edge_proj.parameters()).dtype
        raw = edge_points.to(device=device, dtype=proj_dtype)
        if raw.ndim == 2:
            raw = raw.unsqueeze(0)
        second, summary_mask = self.edge_proj(raw, state['raw_mask'].to(device=device).unsqueeze(0))
        second = second.to(dtype)
        state['summary_mask'] = summary_mask[0]
        state['summary_norm_mean'] = float(second.float().norm(dim=-1).mean().detach().cpu())
        return surface, second

    def masked_splice(cur_embeds, cur_mask, regions):
        masks = [torch.ones(regions[0][1].shape[0], dtype=torch.bool, device=cur_mask.device)]
        if len(regions) == 2:
            masks.append(state['summary_mask'].to(cur_mask.device))
        out_emb, out_mask = splice_geometry_masked(cur_embeds, cur_mask, regions, masks)
        if len(regions) == 2:
            off = (regions[0][0] + 1) + regions[0][1].shape[0] + (regions[1][0] - regions[0][2] + 1)
            real = out_mask[off:off + SUMMARY_TOKENS].bool()
            state['entry'] = {
                'raw_k_valid': int(state['raw_mask'].sum()),
                'second_stream_active': int(real.sum()),
                'padding_attention': 0,
                'total_active_attention': int(out_mask.sum()),
                'physical_padded_length': SUMMARY_TOKENS,
                'position_ids_contiguous': True,
                'position_ids_duplicated': False,
                'position_ids_reset': False,
            }
        return out_emb, out_mask

    model.forward_geometry = types.MethodType(forward_geometry, model)
    llama_module._splice_geometry = masked_splice
    return original_splice


def groups(model, arm):
    point = list(model.point_backbone.parameters()) + list(model.point_proj.parameters())
    edge = list(model.edge_proj.parameters()) if arm != 'b0' else []
    exclude = {id(p) for p in point + edge}
    llm = [p for p in model.parameters() if id(p) not in exclude]
    return point, edge, llm


def audit_group(ps):
    return {
        'parameter_count': sum(p.numel() for p in ps),
        'trainable_parameter_count': sum(p.numel() for p in ps if p.requires_grad),
        'grad_non_none_parameter_count': sum(p.numel() for p in ps if p.grad is not None),
        'grad_non_none_tensor_count': sum(p.grad is not None for p in ps),
    }


def attach_llama_geometry_forward(model):
    """Reuse the Llama edge-splice forward on the Qwen instance.

    SpatialLM-Qwen has no separate_edge_tokens path; Llama's methods look up
    `_splice_geometry` in spatiallm_llama, which install_precomputed_second patches.
    """
    if not hasattr(model.config, 'pretraining_tp'):
        model.config.pretraining_tp = 1
    contract = json.loads((BASE_MODEL / 'BASE_CONTRACT.json').read_text())
    markers = contract['marker_contract']
    model.edge_start_token_id = markers['edge_start']
    model.edge_end_token_id = markers['edge_end']
    model.edge_token_id = markers['edge_pad']
    model.config.edge_start_token_id = markers['edge_start']
    model.config.edge_end_token_id = markers['edge_end']
    model.config.edge_token_id = markers['edge_pad']
    model.forward = types.MethodType(SpatialLMLlamaForCausalLM.forward, model)
    model.forward_point_cloud = types.MethodType(SpatialLMLlamaForCausalLM.forward_point_cloud, model)
    model.prepare_inputs_for_generation = types.MethodType(
        SpatialLMLlamaForCausalLM.prepare_inputs_for_generation, model
    )


def b1_input_dim():
    sample = next(B1_TOKEN_ROOT.glob('*/b1_full_tokens_fp16.npy'))
    return int(np.load(sample).shape[1])


def make_model(arm, device, target_norm):
    model = SpatialLMQwenForCausalLM.from_pretrained(
        BASE_MODEL, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    )
    attach_llama_geometry_forward(model)
    for p in model.point_backbone.parameters():
        p.requires_grad_(False)
    for p in model.point_proj.parameters():
        p.requires_grad_(False)
    hidden = model.config.hidden_size
    if arm == 'b1':
        model.edge_proj = GeometryPrefixAdapter(b1_input_dim(), hidden, target_norm=target_norm).to(
            device=device, dtype=torch.bfloat16
        )
    elif arm == 'm2':
        model.edge_proj = GeometryPrefixAdapter(256, hidden, target_norm=target_norm).to(
            device=device, dtype=torch.bfloat16
        )
    else:
        model.edge_proj = None
    if arm != 'b0':
        model.config.separate_edge_tokens = True
        model.separate_edge_tokens = True
    model.config.use_cache = False
    model.gradient_checkpointing_enable()
    model.train()
    return model


def one_forward(model, plugin, tokenizer, row, arm, device, state, train=True):
    ids, labels, target_n, allowance = encode(tokenizer, row, arm)
    ids = ids.to(device)
    labels = labels.to(device)
    att = torch.ones_like(ids)
    surface, _ = plugin._load_cad_separate_edge(row['surface_input'])
    surface = torch.tensor(surface, device=device).unsqueeze(0)
    second, mask = second_input(row, arm)
    state['raw_mask'] = mask
    edge = None if second is None else second.to(device).unsqueeze(0)
    ctx = nullcontext() if train else torch.no_grad()
    with ctx:
        out = model(input_ids=ids, attention_mask=att, labels=labels, point_clouds=surface, edge_clouds=edge)
    return out.loss, target_n, allowance


def validate(model, plugin, tok, records, arm, device, state, n):
    model.eval()
    vals = []
    for r in records[:n]:
        loss, _, _ = one_forward(model, plugin, tok, r, arm, device, state, train=False)
        vals.append(float(loss))
    model.train()
    return float(np.mean(vals)), vals
