#!/usr/bin/env python3
"""Read-only V3 checkpoint evaluator for one frozen data split."""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_smoke as core
import train_v3_1k_dev as util
from geometry_prefix_adapter import GeometryPrefixAdapter

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'


def load_split(name: str):
    return json.loads((DATA / name).read_text())['records']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=['b0', 'b1', 'm2'], required=True)
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--split', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--target-norm', type=float, required=True)
    ap.add_argument('--max-new-tokens', type=int, default=4096)
    a = ap.parse_args()
    out = pathlib.Path(a.output)
    out.mkdir(parents=True, exist_ok=False)
    rows = load_split(a.split)
    device = torch.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(a.checkpoint, local_files_only=True, use_fast=False)
    model = core.module.SpatialLMLlamaForCausalLM.from_pretrained(a.checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    if a.arm == 'b1':
        model.edge_proj = GeometryPrefixAdapter(model.config.hidden_size, model.config.hidden_size, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
        model.edge_proj.load_state_dict(torch.load(pathlib.Path(a.checkpoint) / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        model.config.separate_edge_tokens = True; model.separate_edge_tokens = True
    elif a.arm == 'm2':
        model.edge_proj = GeometryPrefixAdapter(256, model.config.hidden_size, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
        model.edge_proj.load_state_dict(torch.load(pathlib.Path(a.checkpoint) / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        model.config.separate_edge_tokens = True; model.separate_edge_tokens = True
    else:
        model.edge_proj = None
    for p in model.parameters():
        p.requires_grad_(False)
    model.eval()
    state = {}
    original = core.install_precomputed_second(model, a.arm, state)
    try:
        summary = util.eval_dev(model, plugin, tok, rows, a.arm, device, state, a.max_new_tokens, 0, out)
        per_src = out / 'decode_dev_epoch_00.jsonl'
        per_dst = out / 'per_cad.jsonl'
        per_src.rename(per_dst)
        summary.update({'arm': a.arm, 'checkpoint': str(pathlib.Path(a.checkpoint).resolve()), 'split': a.split, 'max_new_tokens': a.max_new_tokens, 'target_norm': a.target_norm, 'official_test_read': False})
        (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    finally:
        core.module._splice_geometry = original


if __name__ == '__main__':
    main()
