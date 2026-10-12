#!/usr/bin/env python3
"""Frozen-checkpoint, one-pass V3 pilot-eval executor and geometry evaluation."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import sys
import tempfile

import numpy as np
import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
V3 = ROOT / 'scripts/spatiallm_geometry_prefix_v3'
sys.path.insert(0, str(V3))
import train_v3_smoke as core
import train_v3_1k_dev as util
import cad_execution_failure_audit as audit
from geometry_prefix_adapter import GeometryPrefixAdapter

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
EOS_IDS = (128001, 128008, 128009)


def metric(step_path: pathlib.Path, row: dict, work: pathlib.Path) -> dict:
    out = {'chamfer_norm': None, 'hausdorff95_norm': None, 'coverage_at_0p01': None, 'bbox_error_norm': None, 'volume_relative_error': None}
    try:
        import cadquery as cq
        import trimesh
        from scipy.spatial import cKDTree
        stl = work / 'pred.stl'
        cq.exporters.export(cq.importers.importStep(str(step_path)), str(stl))
        gt = trimesh.load(str(pathlib.Path(row['surface_input']).parent / 'mesh.obj'), force='mesh')
        pred = trimesh.load(str(stl), force='mesh')
        if isinstance(gt, trimesh.Scene): gt = gt.dump(concatenate=True)
        if isinstance(pred, trimesh.Scene): pred = pred.dump(concatenate=True)
        diag = float(np.linalg.norm(gt.bounds[1] - gt.bounds[0]))
        if diag <= 1e-12: return out
        np.random.seed(41); a, _ = trimesh.sample.sample_surface(gt, 3000)
        np.random.seed(43); b, _ = trimesh.sample.sample_surface(pred, 3000)
        da = cKDTree(b).query(a, k=1)[0]; db = cKDTree(a).query(b, k=1)[0]
        d = np.concatenate((da, db)) / diag
        out['chamfer_norm'] = float(d.mean())
        out['hausdorff95_norm'] = float(np.quantile(d, 0.95))
        out['coverage_at_0p01'] = float(np.mean((da / diag) <= 0.01))
        out['bbox_error_norm'] = float(np.linalg.norm((pred.bounds - gt.bounds).ravel()) / diag)
        if abs(float(gt.volume)) > 1e-12: out['volume_relative_error'] = float(abs(float(pred.volume) - float(gt.volume)) / abs(float(gt.volume)))
    except Exception as exc:
        out['geometry_error'] = f'{type(exc).__name__}: {exc}'[-500:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=['b0', 'b1', 'm2'], required=True)
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--target-norm', type=float, default=1.9414176940917969)
    a = ap.parse_args(); out = pathlib.Path(a.output); out.mkdir(parents=True, exist_ok=False)
    rows = json.loads((DATA / 'v3_pilot_eval_150.json').read_text())['records']
    if len(rows) != 150: raise RuntimeError('pilot-eval split mismatch')
    device = torch.device(a.device); torch.backends.cuda.matmul.allow_tf32 = True
    core.heldout_geometry.install(); plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(a.checkpoint, local_files_only=True, use_fast=False)
    model = core.module.SpatialLMLlamaForCausalLM.from_pretrained(a.checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True)
    if a.arm == 'b1': model.edge_proj = GeometryPrefixAdapter(model.config.hidden_size, model.config.hidden_size, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
    elif a.arm == 'm2': model.edge_proj = GeometryPrefixAdapter(256, model.config.hidden_size, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
    if a.arm != 'b0':
        model.edge_proj.load_state_dict(torch.load(pathlib.Path(a.checkpoint) / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        model.config.separate_edge_tokens = True; model.separate_edge_tokens = True
    else: model.edge_proj = None
    for p in model.parameters(): p.requires_grad_(False)
    model.eval(); state = {}; original = core.install_precomputed_second(model, a.arm, state)
    per = []; work_root = out / 'tmp'; work_root.mkdir()
    try:
        for i, row in enumerate(rows, 1):
            ids, labels, _, _ = core.encode(tok, row, a.arm); prompt = int((labels[0] == -100).sum())
            surface, _ = plugin._load_cad_separate_edge(row['surface_input']); surface = torch.tensor(surface, device=device).unsqueeze(0)
            second, mask = core.second_input(row, a.arm); state['raw_mask'] = mask; edge = None if second is None else second.to(device).unsqueeze(0)
            with torch.no_grad(): gen = model.generate(input_ids=ids[:, :prompt].to(device), attention_mask=torch.ones((1, prompt), dtype=torch.long, device=device), point_clouds=surface, edge_clouds=edge, max_new_tokens=4096, do_sample=False, use_cache=True, eos_token_id=list(EOS_IDS), pad_token_id=128001)
            new = gen[0, prompt:].cpu(); text = tok.decode(new, skip_special_tokens=True); target = pathlib.Path(row['target_dsl']).read_text(); gt_len = len(tok.encode(target, add_special_tokens=False))
            with tempfile.TemporaryDirectory(dir=work_root) as d:
                audit_result = audit.staged_execute(text, pathlib.Path(d))
                geom = metric(pathlib.Path(d) / 'pred.step', row, pathlib.Path(d)) if audit_result['step_reload_success'] else {}
            per.append({'cad_id': row['cad_id'], 'source_dataset': row['source_dataset'], 'k_valid': row['k_valid'], 'target_token_length': gt_len, 'generated_token_length': int(new.numel()), 'generated_target_ratio': float(new.numel() / max(gt_len, 1)), 'hit_max_new_tokens': bool(new.numel() >= 4096), 'unexpected_runaway': bool(new.numel() >= 4096 and gt_len <= 4096), 'eos_emitted': bool(new.numel() and int(new[-1]) in EOS_IDS), 'op_f1': util.f1(util.ops(target), util.ops(text)), 'exact_match': text.strip() == target.strip(), 'generated_dsl': text, **audit_result, **geom})
            if i % 10 == 0: print(f'{a.arm} {i}/150', flush=True)
    finally:
        core.module._splice_geometry = original
    fields = ('dsl_parse_success','dsl_execute_success','occ_shape_non_null','brep_valid','step_write_success','step_reload_success','unexpected_runaway','eos_emitted','exact_match')
    summary = {'arm': a.arm, 'checkpoint': str(pathlib.Path(a.checkpoint).resolve()), 'n': 150, 'decode': 'greedy', 'max_new_tokens': 4096, 'official_test_read': False, 'executor_module': str(EXECUTOR), 'executor_sha256': hashlib.sha256(EXECUTOR.read_bytes()).hexdigest(), **{f: sum(bool(x.get(f)) for x in per) for f in fields}, 'mean_op_f1': float(np.mean([x['op_f1'] for x in per]))}
    for f in ('chamfer_norm','hausdorff95_norm','coverage_at_0p01','bbox_error_norm','volume_relative_error'):
        vals = [x[f] for x in per if x.get(f) is not None]; summary['mean_' + f] = float(np.mean(vals)) if vals else None; summary[f + '_n'] = len(vals)
    (out / 'per_cad.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in per)); (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')


if __name__ == '__main__': main()
