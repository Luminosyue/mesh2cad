#!/usr/bin/env python3
"""Prepare Qwen V3 extras: surface-token target_norm and native B1 encoder tokens."""
from __future__ import annotations
import argparse, json, pathlib, sys
import numpy as np
import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3_qwen'))
import train_v3_qwen as core

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
SPLITS = ('v3_1k_train.json', 'v3_decode_dev_50.json')


def load_rows():
    rows = []
    for name in SPLITS:
        rows.extend(json.loads((DATA / name).read_text())['records'])
    by_id = {}
    for r in rows:
        by_id.setdefault(r['cad_id'], r)
    return list(by_id.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--device', default='cuda:0')
    a = ap.parse_args()
    out_norm = core.RUN / 'norm_reference_v1'
    out_norm.mkdir(parents=True, exist_ok=True)
    if (out_norm / 'SURFACE_REFERENCE_NORM.json').exists() and core.B1_TOKEN_ROOT.exists():
        print('prepare artifacts already exist', flush=True)
        return
    device = torch.device(a.device)
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    model = core.SpatialLMQwenForCausalLM.from_pretrained(
        core.BASE_MODEL, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    ).eval()
    core.attach_llama_geometry_forward(model)
    for p in list(model.point_backbone.parameters()) + list(model.point_proj.parameters()):
        p.requires_grad_(False)

    rows = load_rows()
    vals = []
    core.B1_TOKEN_ROOT.mkdir(parents=True, exist_ok=True)
    mismatches = []
    with torch.no_grad():
        for i, row in enumerate(rows, 1):
            surface, edge = plugin._load_cad_separate_edge(row['surface_input'])
            y = model.forward_point_cloud(torch.tensor(surface, device=device), device, torch.bfloat16, projector=model.point_proj)
            vals.extend(y.float().norm(dim=-1).flatten().cpu().tolist())
            b1 = model.forward_point_cloud(torch.tensor(edge, device=device), device, torch.bfloat16, projector=model.point_proj)
            b1_np = b1.squeeze(0).float().cpu().numpy().astype(np.float16)
            if b1_np.shape[0] != int(row['b1_post_encoder_count']):
                mismatches.append({'cad_id': row['cad_id'], 'qwen': int(b1_np.shape[0]), 'llama': int(row['b1_post_encoder_count'])})
            dest = core.B1_TOKEN_ROOT / row['cad_id']
            dest.mkdir(parents=True, exist_ok=True)
            np.save(dest / 'b1_full_tokens_fp16.npy', b1_np)
            if i % 50 == 0:
                print(f'{i}/{len(rows)}', flush=True)
    if mismatches:
        raise RuntimeError(f'B1 token-count mismatch on {len(mismatches)} samples, e.g. {mismatches[:3]}')
    report = {
        'split': 'v3_1k_train+decode_dev_50 unique',
        'samples': len(rows),
        'surface_token_norm_count': len(vals),
        'mean': float(np.mean(vals)),
        'median': float(np.median(vals)),
        'p10': float(np.percentile(vals, 10)),
        'p90': float(np.percentile(vals, 90)),
        'b1_input_dim': int(np.load(next(core.B1_TOKEN_ROOT.glob('*/b1_full_tokens_fp16.npy'))).shape[1]),
        'official_test_read': False,
        'llama_v3_run_untouched': True,
    }
    (out_norm / 'SURFACE_REFERENCE_NORM.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
