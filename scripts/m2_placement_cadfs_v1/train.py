#!/usr/bin/env python3
"""PHASE D/E: train M2-Placement on frozen CADFS train100. Independent checkpoint."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import pathlib
import random
import shutil
import sys
import time
from contextlib import nullcontext

import numpy as np
import torch
import torch.nn as nn
from transformers import get_cosine_schedule_with_warmup

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts'))
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
sys.path.insert(0, str(ROOT / 'scripts/m2_placement_cadfs_v1'))
import cadfs_noisy100_overfit_v1 as old
import train_v3_smoke as core
import train_v3_1k_dev as util

EXP = ROOT / 'ours3/m2_placement_cadfs_v1'
TRAIN_MAN = ROOT / 'ours3/cadfs_noisy_overfit100_v1/CADFS_NOISY_OVERFIT100_MANIFEST.json'
GATE = EXP / 'audits/ALIGNMENT_GATE.json'
INDEX = EXP / 'data/TRAIN100_INDEX.json'
OLD_M2 = ROOT / 'ours3/cadfs_noisy_overfit100_v1/runs_retrain_v1/M2_ORACLE_CADFS100_NOISY_RETRAIN_V1/checkpoint_epoch_20'
C2_CKPT = ROOT / 'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'
SEED = 42
EPOCHS = 20
LR = 2e-5
ACCUM = 4
TARGET_NORM = 1.9414176940917969
KCAP = core.KCAP


class PlacementMLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(17, 64), nn.GELU(), nn.Linear(64, 256))
        nn.init.zeros_(self.net[-1].weight)
        nn.init.zeros_(self.net[-1].bias)

    def forward(self, g):
        return self.net(g)


def dump(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(x, indent=2, allow_nan=False) + '\n')


def append_jsonl(p, x):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'a') as f:
        f.write(json.dumps(x) + '\n')
        f.flush()
        os.fsync(f.fileno())


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def tensor_sha(sd):
    h = hashlib.sha256()
    for k, v in sorted(sd.items()):
        x = v.detach().cpu().contiguous()
        h.update(k.encode() + b'\0' + str(tuple(x.shape)).encode() + b'\0' + str(x.dtype).encode() + b'\0')
        h.update(x.reshape(-1).view(torch.uint8).numpy().tobytes())
    return h.hexdigest()


def l2_delta(a, b):
    tot = 0.0
    for k in a:
        tot += float((a[k].float() - b[k].float()).pow(2).sum().cpu())
    return float(tot ** 0.5)


def set_seed():
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    torch.cuda.manual_seed_all(SEED)


def rows():
    man = {r['cad_id']: r for r in json.loads(TRAIN_MAN.read_text())['records']}
    out = []
    for rec in json.loads(INDEX.read_text())['records']:
        m = man[rec['cad_id']]
        n = int(np.load(rec['c2_token_path'], mmap_mode='r').shape[0])
        d = np.load(rec['placement_descriptor'], mmap_mode='r')
        if n < 1 or tuple(d.shape) != (n, 17):
            raise RuntimeError(f'row mismatch {rec["cad_id"]}')
        out.append({
            'cad_id': rec['cad_id'],
            'surface_input': m['noisy_surface_path'],
            'target_dsl': m['cad_target_dsl'],
            'm2_full_c2_tokens': rec['c2_token_path'],
            'placement_descriptor': rec['placement_descriptor'],
            'selected_m2_indices': list(range(n)),
            'k_valid': n,
            'surface_tokens': int(m['surface_token_count']),
            'source_step': m['source_step'],
        })
    if len(out) != 100:
        raise RuntimeError('train100 count mismatch')
    return out


def load_c2_desc(row):
    raw = np.load(row['m2_full_c2_tokens'])
    desc = np.load(row['placement_descriptor'])
    k = int(row['k_valid'])
    if raw.shape[0] != k or desc.shape != (k, 17):
        raise RuntimeError(f'C2/desc mismatch {row["cad_id"]}')
    c2 = np.zeros((KCAP, raw.shape[1]), np.float32)
    g = np.zeros((KCAP, 17), np.float32)
    c2[:k] = raw
    g[:k] = desc
    mask = torch.zeros(KCAP, dtype=torch.bool)
    mask[:k] = True
    return torch.from_numpy(c2), torch.from_numpy(g), mask


def install_placement(model, placement_mlp, state):
    original = core.install_precomputed_second(model, 'm2', state)

    def forward_geometry(self, surface_points, edge_points=None, device=None, dtype=None):
        with torch.no_grad():
            surface = self.forward_point_cloud(surface_points, device, dtype, projector=self.point_proj)
        proj_dtype = next(self.edge_proj.parameters()).dtype
        raw = edge_points.to(device=device, dtype=proj_dtype)
        if raw.ndim == 2:
            raw = raw.unsqueeze(0)
        desc = state['placement'].to(device=device, dtype=proj_dtype)
        if desc.ndim == 2:
            desc = desc.unsqueeze(0)
        residual = placement_mlp(desc)
        mask = state['raw_mask'].to(device=device)
        if mask.ndim == 1:
            mask_b = mask.unsqueeze(0)
        else:
            mask_b = mask
        residual = residual * mask_b.to(dtype=residual.dtype).unsqueeze(-1)
        enhanced = raw + residual
        valid = mask_b[0]
        if bool(valid.any()):
            state['c2_token_norm'] = float(raw[0, valid].float().norm(dim=-1).mean().detach().cpu())
            state['placement_residual_norm'] = float(residual[0, valid].float().norm(dim=-1).mean().detach().cpu())
            state['enhanced_norm'] = float(enhanced[0, valid].float().norm(dim=-1).mean().detach().cpu())
        second, summary_mask = self.edge_proj(enhanced, mask_b)
        second = second.to(dtype)
        state['summary_mask'] = summary_mask[0]
        state['summary_norm_mean'] = float(second.float().norm(dim=-1).mean().detach().cpu())
        return surface, second

    import types
    model.forward_geometry = types.MethodType(forward_geometry, model)
    return original


def one_forward(model, plugin, tok, row, device, state, train=True):
    ids, labels, tn, pred = old.encode_full(tok, row, 'm2')
    ids = ids.to(device)
    labels = labels.to(device)
    att = torch.ones_like(ids)
    surface, _ = plugin._load_cad_separate_edge(row['surface_input'])
    surface = torch.tensor(surface, device=device).unsqueeze(0)
    c2, g, mask = load_c2_desc(row)
    state['raw_mask'] = mask
    state['placement'] = g
    ctx = nullcontext() if train else torch.no_grad()
    with ctx:
        out = model(input_ids=ids, attention_mask=att, labels=labels, point_clouds=surface, edge_clouds=c2.to(device).unsqueeze(0))
    return out.loss, tn, pred


def grad_norm(params):
    tot = 0.0
    n = 0
    for p in params:
        if p.grad is None:
            continue
        tot += float(p.grad.detach().float().pow(2).sum().cpu())
        n += 1
    return float(tot ** 0.5), n


def rng_state():
    return {
        'python_random_state': random.getstate(),
        'numpy_random_state': np.random.get_state(),
        'torch_cpu_rng_state': torch.get_rng_state(),
        'torch_cuda_rng_state_all': torch.cuda.get_rng_state_all(),
    }


def save_ckpt(ck, model, tok, opt, sched, epoch, global_step, cfg, placement_mlp, keep_latest=True):
    tmp = ck.with_name(ck.name + '.partial')
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    model.save_pretrained(tmp, safe_serialization=True, max_shard_size='2GB')
    tok.save_pretrained(tmp)
    torch.save(model.edge_proj.state_dict(), tmp / 'geometry_prefix_adapter.pt')
    torch.save(placement_mlp.state_dict(), tmp / 'placement_mlp.pt')
    state = {
        'optimizer_state': opt.state_dict(),
        'scheduler_state': sched.state_dict(),
        'epoch': epoch,
        'global_step': global_step,
        'rng_state': rng_state(),
        'training_config': cfg,
    }
    torch.save(state, tmp / 'training_state.pt')
    dump(tmp / 'checkpoint_metadata.json', {'ARM_NAME': 'm2_placement', 'epoch': epoch, 'global_step': global_step})
    tmp.rename(ck)
    if keep_latest:
        for old in sorted(ck.parent.glob('checkpoint_epoch_*')):
            if old.is_dir() and old.resolve() != ck.resolve() and '.partial' not in old.name:
                shutil.rmtree(old, ignore_errors=True)


def restore_rng(x):
    random.setstate(x['python_random_state'])
    np.random.set_state(x['numpy_random_state'])
    torch.set_rng_state(x['torch_cpu_rng_state'])
    torch.cuda.set_rng_state_all(x['torch_cuda_rng_state_all'])


def load_model_state(model, ck):
    from transformers.modeling_utils import load_sharded_checkpoint
    if not (ck / 'model.safetensors.index.json').exists():
        raise RuntimeError(f'no sharded safetensors in {ck}')
    info = load_sharded_checkpoint(model, str(ck), strict=False, prefer_safe=True)
    missing = list(getattr(info, 'missing_keys', []) or [])
    unexpected = list(getattr(info, 'unexpected_keys', []) or [])
    missing = [k for k in missing if k != 'lm_head.weight' and not k.startswith('edge_proj.')]
    if missing or unexpected:
        raise RuntimeError(f'checkpoint load mismatch missing={missing} unexpected={unexpected}')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', type=pathlib.Path, default=EXP / 'checkpoints/M2_PLACEMENT_CADFS_V1')
    ap.add_argument('--device', default='cuda:3')
    ap.add_argument('--smoke', action='store_true')
    ap.add_argument('--resume', type=pathlib.Path)
    a = ap.parse_args()
    gate = json.loads(GATE.read_text())
    if gate.get('CURRENT_GATE') != 'PLACEMENT_DATA_ALIGNMENT_PASS' or gate.get('TRAINING_READY') != 'YES':
        raise RuntimeError('refusing to train: placement alignment gate not PASS')
    a.output.mkdir(parents=True, exist_ok=True)
    set_seed()
    device = torch.device(a.device)
    torch.backends.cuda.matmul.allow_tf32 = True
    records = rows()
    c2_hashes = {r['cad_id']: sha_file(r['m2_full_c2_tokens']) for r in records}
    dump(a.output / 'C2_TOKEN_SHA256_START.json', c2_hashes)
    old.core.encode = old.encode_full
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    model = core.make_model('m2', device, TARGET_NORM)
    contract = json.loads((core.BASE_MODEL / 'BASE_CONTRACT.json').read_text())
    llm = util.llm_hash(model)
    if llm != contract['llm']['state_sha256']:
        raise RuntimeError('official parent LLM hash mismatch')
    placement_mlp = PlacementMLP().to(device=device, dtype=torch.bfloat16)
    init_place = {k: v.detach().cpu().clone() for k, v in placement_mlp.state_dict().items()}
    adapter_init = {k: v.detach().cpu().clone() for k, v in model.edge_proj.state_dict().items()}
    state = {}
    original = install_placement(model, placement_mlp, state)
    point, adapter, llm_params = core.groups(model, 'm2')
    params = [p for p in model.parameters() if p.requires_grad] + list(placement_mlp.parameters())
    opt = torch.optim.AdamW(params, lr=LR, weight_decay=0.0)
    updates = math.ceil(len(records) / ACCUM) * (1 if a.smoke else EPOCHS)
    sched = get_cosine_schedule_with_warmup(opt, int(updates * 0.03), updates)
    cfg = {
        'EXPERIMENT': 'M2_PLACEMENT_CADFS_V1',
        'seed': SEED,
        'epochs': 1 if a.smoke else EPOCHS,
        'optimizer': 'AdamW',
        'learning_rate': LR,
        'scheduler': 'cosine_with_warmup',
        'warmup_ratio': 0.03,
        'weight_decay': 0.0,
        'batch_size': 1,
        'gradient_accumulation': ACCUM,
        'max_context': 4096,
        'precision': 'bfloat16',
        'gradient_clip': 1.0,
        'SONATA_FROZEN': True,
        'C2_FROZEN': True,
        'C2_IN_TRAINING_GRAPH': False,
        'DSL_UNCHANGED': True,
        'EIGHT_TOKEN_SUMMARY_UNCHANGED': True,
        'LLM_ARCHITECTURE_UNCHANGED': True,
        'placement_mlp': 'Linear(17,64)->GELU->Linear(64,256) zero_init_last',
        'fusion': 'enhanced_curve_token = frozen_c2_token + placement_mlp(descriptor)',
        'OLD_M2_CHECKPOINT': str(OLD_M2),
        'C2_CHECKPOINT': str(C2_CKPT),
        'C2_CHECKPOINT_SHA256': sha_file(C2_CKPT) if C2_CKPT.is_file() else None,
        'DOES_NOT_OVERWRITE_OLD_M2': True,
    }
    dump(a.output / 'CONFIG.json', cfg)
    report = {'CURRENT_GATE': 'M2_PLACEMENT_TRAINING', 'TRAINING_STARTED': 'YES', 'status': 'RUNNING'}
    dump(GATE.with_name('TRAINING_GATE.json'), {'CURRENT_GATE': 'M2_PLACEMENT_TRAINING', 'TRAINING_READY': 'YES', 'TRAINING_STARTED': 'YES'})
    start_epoch = 1
    global_step = 0
    if a.resume:
        prior = torch.load(a.resume / 'training_state.pt', map_location='cpu', weights_only=False)
        load_model_state(model, a.resume)
        model.edge_proj.load_state_dict(torch.load(a.resume / 'geometry_prefix_adapter.pt', map_location=device, weights_only=True))
        placement_mlp.load_state_dict(torch.load(a.resume / 'placement_mlp.pt', map_location=device, weights_only=True))
        opt.load_state_dict(prior['optimizer_state'])
        sched.load_state_dict(prior['scheduler_state'])
        restore_rng(prior['rng_state'])
        start_epoch = int(prior['epoch']) + 1
        global_step = int(prior['global_step'])
        report['resumed_from'] = str(a.resume)
        report['start_epoch'] = start_epoch
        print(f'resuming from {a.resume} epoch={prior["epoch"]} step={global_step}', flush=True)
    try:
        first = json.loads((a.output / 'FIRST_BACKWARD_AUDIT.json').read_text()) if (a.output / 'FIRST_BACKWARD_AUDIT.json').exists() else None
        if a.smoke:
            opt.zero_grad(set_to_none=True)
            loss, tn, pred = one_forward(model, plugin, tok, records[0], device, state, train=True)
            (loss / ACCUM).backward()
            first = {
                'LOSS_FINITE': bool(torch.isfinite(loss)),
                'C2_IN_GRAPH': False,
                'C2_GRAD': 0.0,
                'C2_GRAD_NONE': True,
                'PLACEMENT_MLP_GRAD': grad_norm(list(placement_mlp.parameters()))[0],
                'PLACEMENT_MLP_GRAD_TENSORS': grad_norm(list(placement_mlp.parameters()))[1],
                'ADAPTER_GRAD': grad_norm(adapter)[0],
                'LLM_GRAD': grad_norm(llm_params)[0],
                'SONATA_GRAD': grad_norm(point)[0],
                'SONATA_GRAD_TENSORS': grad_norm(point)[1],
                'mean_c2_token_norm': state.get('c2_token_norm'),
                'mean_placement_residual_norm': state.get('placement_residual_norm'),
                'mean_enhanced_norm': state.get('enhanced_norm'),
                'M2_CURVE_TOKEN_COUNT': 8,
                'second_stream_active': (state.get('entry') or {}).get('second_stream_active'),
            }
            dump(a.output / 'FIRST_BACKWARD_AUDIT.json', first)
            if (not first['LOSS_FINITE']) or first['PLACEMENT_MLP_GRAD'] <= 0 or first['SONATA_GRAD_TENSORS'] != 0:
                raise RuntimeError(f'placement branch audit failed: {first}')
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            opt.zero_grad(set_to_none=True)
            after = {k: v.detach().cpu().clone() for k, v in placement_mlp.state_dict().items()}
            smoke = {**first, 'C2_WEIGHT_CHANGE': 0.0, 'PLACEMENT_MLP_WEIGHT_CHANGE': l2_delta(after, init_place), 'status': 'PASS'}
            dump(a.output / 'SMOKE_REPORT.json', smoke)
            report.update(smoke)
            report['status'] = 'SMOKE_PASS'
        else:
            hist = a.output / 'TRAIN_HISTORY.jsonl'
            for epoch in range(start_epoch, EPOCHS + 1):
                order = list(range(len(records)))
                random.Random(SEED + epoch).shuffle(order)
                losses = []
                c2_ns, r_ns, e_ns, pgrads = [], [], [], []
                started = time.time()
                opt.zero_grad(set_to_none=True)
                for pos, ix in enumerate(order, 1):
                    loss, tn, pred = one_forward(model, plugin, tok, records[ix], device, state, train=True)
                    (loss / ACCUM).backward()
                    losses.append(float(loss.detach().cpu()))
                    c2_ns.append(state.get('c2_token_norm'))
                    r_ns.append(state.get('placement_residual_norm'))
                    e_ns.append(state.get('enhanced_norm'))
                    if epoch == 1 and pos == 1:
                        first = {
                            'LOSS_FINITE': bool(torch.isfinite(loss)),
                            'C2_IN_GRAPH': False,
                            'C2_GRAD': 0.0,
                            'C2_GRAD_NONE': True,
                            'PLACEMENT_MLP_GRAD': grad_norm(list(placement_mlp.parameters()))[0],
                            'PLACEMENT_MLP_GRAD_TENSORS': grad_norm(list(placement_mlp.parameters()))[1],
                            'ADAPTER_GRAD': grad_norm(adapter)[0],
                            'LLM_GRAD': grad_norm(llm_params)[0],
                            'SONATA_GRAD': grad_norm(point)[0],
                            'SONATA_GRAD_TENSORS': grad_norm(point)[1],
                            'mean_c2_token_norm': state.get('c2_token_norm'),
                            'mean_placement_residual_norm': state.get('placement_residual_norm'),
                            'mean_enhanced_norm': state.get('enhanced_norm'),
                            'M2_CURVE_TOKEN_COUNT': 8,
                            'second_stream_active': (state.get('entry') or {}).get('second_stream_active'),
                        }
                        dump(a.output / 'FIRST_BACKWARD_AUDIT.json', first)
                        if (not first['LOSS_FINITE']) or first['PLACEMENT_MLP_GRAD'] <= 0 or first['SONATA_GRAD_TENSORS'] != 0:
                            raise RuntimeError(f'placement branch audit failed: {first}')
                    if pos % ACCUM == 0 or pos == len(order):
                        pgn, _ = grad_norm(list(placement_mlp.parameters()))
                        pgrads.append(pgn)
                        torch.nn.utils.clip_grad_norm_(params, 1.0)
                        opt.step()
                        sched.step()
                        opt.zero_grad(set_to_none=True)
                        global_step += 1
                ck = a.output / f'checkpoint_epoch_{epoch:02d}'
                save_ckpt(ck, model, tok, opt, sched, epoch, global_step, cfg, placement_mlp)
                place_now = {k: v.detach().cpu().clone() for k, v in placement_mlp.state_dict().items()}
                row = {
                    'epoch': epoch,
                    'train_ce': float(np.mean(losses)),
                    'lr': sched.get_last_lr()[0],
                    'global_step': global_step,
                    'seconds': time.time() - started,
                    'C2_GRAD': 0.0,
                    'PLACEMENT_MLP_GRAD_MEAN': float(np.mean(pgrads)),
                    'mean_c2_token_norm': float(np.mean([x for x in c2_ns if x is not None])),
                    'mean_placement_residual_norm': float(np.mean([x for x in r_ns if x is not None])),
                    'mean_enhanced_norm': float(np.mean([x for x in e_ns if x is not None])),
                    'PLACEMENT_MLP_WEIGHT_CHANGE_FROM_INIT': l2_delta(place_now, init_place),
                    'ADAPTER_WEIGHT_CHANGE_FROM_INIT': l2_delta({k: v.detach().cpu() for k, v in model.edge_proj.state_dict().items()}, adapter_init),
                    'checkpoint': str(ck),
                }
                append_jsonl(hist, row)
                dump(a.output / 'TRAINING_REPORT.json', {'status': 'RUNNING', **row})
                print(f'[m2_placement] epoch={epoch}/{EPOCHS} ce={row["train_ce"]:.6f} place_dW={row["PLACEMENT_MLP_WEIGHT_CHANGE_FROM_INIT"]:.6g}', flush=True)
            end_hashes = {r['cad_id']: sha_file(r['m2_full_c2_tokens']) for r in records}
            c2_changed = sum(end_hashes[k] != c2_hashes[k] for k in c2_hashes)
            place_final = {k: v.detach().cpu().clone() for k, v in placement_mlp.state_dict().items()}
            report.update({
                'status': 'COMPLETE',
                'FINAL_EPOCH': EPOCHS,
                'final_checkpoint': str(a.output / f'checkpoint_epoch_{EPOCHS:02d}'),
                'C2_WEIGHT_CHANGE': 0 if c2_changed == 0 else c2_changed,
                'C2_GRAD': 0,
                'C2_FILES_MUTATED': c2_changed,
                'PLACEMENT_MLP_WEIGHT_CHANGE': l2_delta(place_final, init_place),
                'OLD_M2_UNTOUCHED': not pathlib.Path(str(OLD_M2)).samefile(a.output / f'checkpoint_epoch_{EPOCHS:02d}') if OLD_M2.exists() else True,
            })
            dump(a.output / 'PLACEMENT_BRANCH_AUDIT.json', {
                'C2_WEIGHT_CHANGE': report['C2_WEIGHT_CHANGE'],
                'C2_GRAD': 0,
                'PLACEMENT_MLP_WEIGHT_CHANGE': report['PLACEMENT_MLP_WEIGHT_CHANGE'],
                'PLACEMENT_MLP_GRAD': first['PLACEMENT_MLP_GRAD'],
                'C2_IN_TRAINING_GRAPH': False,
            })
    finally:
        core.module._splice_geometry = original
        dump(a.output / ('SMOKE_REPORT.json' if a.smoke else 'TRAINING_REPORT.json'), report)
    print(json.dumps({k: report[k] for k in report if k != 'python_random_state'}, indent=2, default=str))


if __name__ == '__main__':
    main()
