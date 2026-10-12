#!/usr/bin/env python3
"""Single-GPU V3-1k trainer on the isolated Qwen geometry base."""
from __future__ import annotations
import argparse, json, pathlib, random, sys
import numpy as np
import torch
from transformers import get_cosine_schedule_with_warmup

ROOT = pathlib.Path('/data/home/cuiyuehan/project/mesh2cad')
sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3_qwen'))
import train_v3_qwen as core

sys.path.insert(0, str(ROOT / 'scripts/spatiallm_geometry_prefix_v3'))
import train_v3_1k_dev as util

DATA = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'


def load(name):
    return json.loads((DATA / name).read_text())['records']


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--arm', choices=['b0', 'b1', 'm2'], required=True)
    ap.add_argument('--output', required=True)
    ap.add_argument('--device', default='cuda:0')
    ap.add_argument('--epochs', type=int, default=10)
    ap.add_argument('--target-norm', type=float, required=True)
    a = ap.parse_args()
    out = pathlib.Path(a.output)
    out.mkdir(parents=True, exist_ok=False)
    device = torch.device(a.device)
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    torch.backends.cuda.matmul.allow_tf32 = True
    train, dev = load('v3_1k_train.json'), load('v3_decode_dev_50.json')
    if (len(train), len(dev)) != (800, 50):
        raise RuntimeError('split mismatch')
    core.heldout_geometry.install()
    plugin = core.get_cad_mm_plugin(point_token='<|point_pad|>', num_bins=1280, use_edge_score=False, separate_edge_tokens=True)
    tok = core.AutoTokenizer.from_pretrained(core.BASE_MODEL, local_files_only=True, use_fast=False)
    model = core.make_model(a.arm, device, a.target_norm)
    contract = json.loads((core.BASE_MODEL / 'BASE_CONTRACT.json').read_text())
    initial = util.llm_hash(model)
    if initial != contract['llm']['state_sha256']:
        raise RuntimeError('qwen parent hash mismatch')
    state = {}
    original = core.install_precomputed_second(model, a.arm, state)
    point, adapter, llm = core.groups(model, a.arm)
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=2e-5, weight_decay=0.0)
    sched = get_cosine_schedule_with_warmup(opt, int(200 * a.epochs * .03), 200 * a.epochs)
    report = {
        'current_gate': 'V3_1K_TRAIN_ONLY_QWEN05',
        'backbone': 'Qwen2.5-0.5B-Instruct',
        'arm': a.arm,
        'fresh_from_qwen_geometry_base': True,
        'official_llm_hash': initial,
        'train_count': 800,
        'decode_dev_count': 50,
        'pilot_eval_read': False,
        'official_test_read': False,
        'llama_v3_run_untouched': True,
        'epochs': a.epochs,
        'optimizer': 'AdamW',
        'scheduler': 'cosine',
        'hidden_size': int(model.config.hidden_size),
        'status': 'RUNNING',
        'epochs_report': [],
    }
    try:
        for epoch in range(1, a.epochs + 1):
            order = list(range(800))
            random.Random(42 + epoch).shuffle(order)
            opt.zero_grad(set_to_none=True)
            losses = []
            for pos, ix in enumerate(order, 1):
                row = train[ix]
                loss, _, _ = core.one_forward(model, plugin, tok, row, a.arm, device, state, train=True)
                if not torch.isfinite(loss):
                    raise RuntimeError(f'nonfinite e{epoch}')
                (loss / 4).backward()
                losses.append(float(loss.detach()))
                if epoch == 1 and pos == 1:
                    audit = {
                        'SONATA_AND_SURFACE_PROJECTOR': core.audit_group(point),
                        'GEOMETRY_PREFIX_ADAPTER': core.audit_group(adapter),
                        'LLM': core.audit_group(llm),
                        'C2_GRAD_NON_NONE': 0,
                        'B1_ENCODER_GRAD_NON_NONE': 0,
                    }
                    if (
                        audit['SONATA_AND_SURFACE_PROJECTOR']['grad_non_none_parameter_count']
                        or audit['SONATA_AND_SURFACE_PROJECTOR']['trainable_parameter_count']
                        or audit['LLM']['grad_non_none_parameter_count'] == 0
                        or (a.arm != 'b0' and audit['GEOMETRY_PREFIX_ADAPTER']['grad_non_none_parameter_count'] == 0)
                    ):
                        raise RuntimeError('gradient hard stop')
                    report['first_backward_gradient_audit'] = audit
                if a.arm != 'b0' and (
                    state['entry']['second_stream_active'] != 8
                    or state['entry']['padding_attention'] != 0
                    or not state['entry']['position_ids_contiguous']
                ):
                    raise RuntimeError('V3 interface hard stop')
                if pos % 4 == 0 or pos == 800:
                    torch.nn.utils.clip_grad_norm_(params, 1.0)
                    opt.step()
                    sched.step()
                    opt.zero_grad(set_to_none=True)
            dev_ce, _ = core.validate(model, plugin, tok, dev, a.arm, device, state, 50)
            ckpt = out / f'checkpoint_epoch_{epoch:02d}'
            ckpt.mkdir()
            model.save_pretrained(ckpt, safe_serialization=True, max_shard_size='2GB')
            tok.save_pretrained(ckpt)
            if a.arm != 'b0':
                torch.save(model.edge_proj.state_dict(), ckpt / 'geometry_prefix_adapter.pt')
            item = {
                'epoch': epoch,
                'train_ce': float(np.mean(losses)),
                'decode_dev_ce': dev_ce,
                'lr': sched.get_last_lr()[0],
                'checkpoint': str(ckpt),
            }
            report['epochs_report'].append(item)
            (out / 'TRAINING_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
            print(f'[{a.arm}] epoch={epoch}/10 train_ce={item["train_ce"]:.5f} dev_ce={dev_ce:.5f}', flush=True)
        report['status'] = 'PASS'
    finally:
        core.llama_module._splice_geometry = original
        (out / 'TRAINING_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
