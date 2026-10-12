#!/usr/bin/env python3
"""Qwen V3 decode-dev evaluator. Isolated; does not touch Llama results or official test."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, sys, tempfile
import numpy as np
import torch

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path[:0] = [
    str(ROOT / 'scripts/spatiallm_geometry_prefix_v3_qwen'),
    str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'),
]
import train_v3_qwen as core
import train_v3_1k_dev as util
import cad_execution_failure_audit as audit
from geometry_prefix_adapter import GeometryPrefixAdapter

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
EXECUTOR = ROOT / 'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
EOS_IDS = (core.EOS_ID, core.PAD_ID)
NORM = 1.2624025344848633


def geom_metric(step_path: pathlib.Path, row: dict, work: pathlib.Path) -> dict:
    out = {'chamfer_norm': None, 'hausdorff95_norm': None}
    try:
        import cadquery as cq
        import trimesh
        from scipy.spatial import cKDTree
        stl = work / 'pred.stl'
        cq.exporters.export(cq.importers.importStep(str(step_path)), str(stl))
        gt = trimesh.load(str(pathlib.Path(row['surface_input']).parent / 'mesh.obj'), force='mesh')
        pred = trimesh.load(str(stl), force='mesh')
        if isinstance(gt, trimesh.Scene):
            gt = gt.dump(concatenate=True)
        if isinstance(pred, trimesh.Scene):
            pred = pred.dump(concatenate=True)
        diag = float(np.linalg.norm(gt.bounds[1] - gt.bounds[0]))
        if diag <= 1e-12:
            return out
        np.random.seed(41)
        a, _ = trimesh.sample.sample_surface(gt, 3000)
        np.random.seed(43)
        b, _ = trimesh.sample.sample_surface(pred, 3000)
        da = cKDTree(b).query(a, k=1)[0]
        db = cKDTree(a).query(b, k=1)[0]
        d = np.concatenate((da, db)) / diag
        out['chamfer_norm'] = float(d.mean())
        out['hausdorff95_norm'] = float(np.quantile(d, 0.95))
    except Exception as exc:
        out['geometry_error'] = f'{type(exc).__name__}: {exc}'[-500:]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=['b0', 'b1', 'm2'], required=True)
    ap.add_argument('--checkpoint', required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--split', default='v3_decode_dev_50.json')
    ap.add_argument('--target-norm', type=float, default=NORM)
    a = ap.parse_args()
    out = pathlib.Path(a.output)
    out.mkdir(parents=True, exist_ok=False)
    rows = json.loads((DATA / a.split).read_text())['records']
    device = torch.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(a.checkpoint, local_files_only=True, use_fast=False)
    model = core.SpatialLMQwenForCausalLM.from_pretrained(
        a.checkpoint, torch_dtype=torch.bfloat16, device_map=device, local_files_only=True
    )
    core.attach_llama_geometry_forward(model)
    hidden = model.config.hidden_size
    if a.arm == 'b1':
        model.edge_proj = GeometryPrefixAdapter(core.b1_input_dim(), hidden, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
    elif a.arm == 'm2':
        model.edge_proj = GeometryPrefixAdapter(256, hidden, target_norm=a.target_norm).to(device=device, dtype=torch.bfloat16)
    else:
        model.edge_proj = None
    if a.arm != 'b0':
        model.edge_proj.load_state_dict(torch.load(pathlib.Path(a.checkpoint) / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        model.config.separate_edge_tokens = True
        model.separate_edge_tokens = True
    for p in model.parameters():
        p.requires_grad_(False)
    model.eval()
    state = {}
    original = core.install_precomputed_second(model, a.arm, state)
    per = []
    work_root = out / 'tmp'
    work_root.mkdir()
    try:
        for i, row in enumerate(rows, 1):
            ids, labels, _, _ = core.encode(tok, row, a.arm)
            prompt = int((labels[0] == -100).sum())
            surface, _ = plugin._load_cad_separate_edge(row['surface_input'])
            surface = torch.tensor(surface, device=device).unsqueeze(0)
            second, mask = core.second_input(row, a.arm)
            state['raw_mask'] = mask
            edge = None if second is None else second.to(device).unsqueeze(0)
            with torch.no_grad():
                gen = model.generate(
                    input_ids=ids[:, :prompt].to(device),
                    attention_mask=torch.ones((1, prompt), dtype=torch.long, device=device),
                    point_clouds=surface,
                    edge_clouds=edge,
                    max_new_tokens=4096,
                    do_sample=False,
                    use_cache=True,
                    eos_token_id=list(EOS_IDS),
                    pad_token_id=core.PAD_ID,
                )
            new = gen[0, prompt:].cpu()
            text = tok.decode(new, skip_special_tokens=True)
            target = pathlib.Path(row['target_dsl']).read_text()
            gt_len = len(tok.encode(target, add_special_tokens=False))
            with tempfile.TemporaryDirectory(dir=work_root) as d:
                audit_result = audit.staged_execute(text, pathlib.Path(d))
                geom = geom_metric(pathlib.Path(d) / 'pred.step', row, pathlib.Path(d)) if audit_result.get('step_reload_success') else {}
            per.append({
                'cad_id': row['cad_id'],
                'target_token_length': gt_len,
                'generated_token_length': int(new.numel()),
                'hit_max_new_tokens': bool(new.numel() >= 4096),
                'unexpected_runaway': bool(new.numel() >= 4096 and gt_len <= 4096),
                'eos_emitted': bool(new.numel() and int(new[-1]) in EOS_IDS),
                'op_f1': util.f1(util.ops(target), util.ops(text)),
                'exact_match': text.strip() == target.strip(),
                'generated_dsl': text,
                **audit_result,
                **geom,
            })
            if i % 10 == 0:
                print(f'{a.arm} {i}/{len(rows)} runaway={sum(x["unexpected_runaway"] for x in per)} parse={sum(x.get("dsl_parse_success", False) for x in per)}', flush=True)
    finally:
        core.llama_module._splice_geometry = original
    fields = ('dsl_parse_success', 'step_reload_success', 'unexpected_runaway', 'eos_emitted', 'exact_match')
    summary = {
        'arm': a.arm,
        'backbone': 'Qwen2.5-0.5B-Instruct',
        'checkpoint': str(pathlib.Path(a.checkpoint).resolve()),
        'n': len(per),
        'split': a.split,
        'decode': 'greedy',
        'max_new_tokens': 4096,
        'official_test_read': False,
        'llama_v3_run_untouched': True,
        'executor_module': str(EXECUTOR),
        'executor_sha256': hashlib.sha256(EXECUTOR.read_bytes()).hexdigest(),
        **{f: sum(bool(x.get(f)) for x in per) for f in fields},
        'mean_op_f1': float(np.mean([x['op_f1'] for x in per])),
    }
    for f in ('chamfer_norm', 'hausdorff95_norm'):
        vals = [x[f] for x in per if x.get(f) is not None]
        summary['mean_' + f] = float(np.mean(vals)) if vals else None
        summary[f + '_n'] = len(vals)
    (out / 'per_cad.jsonl').write_text(''.join(json.dumps(x) + '\n' for x in per))
    (out / 'SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k != 'generated_dsl'}, indent=2))


if __name__ == '__main__':
    main()
