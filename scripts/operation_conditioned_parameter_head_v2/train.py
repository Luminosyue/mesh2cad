#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import torch

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
CACHE = Path('/var/tmp/cuiyuehan_mesh2cad/operation_conditioned_parameter_head_v2')
OUT = CACHE / 'training'
OLD_OUT = ROOT / 'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1'
from model import LAMBDA_ATTENTION, OperationConditionedHead, supervised_loss  # noqa: E402

ARMS = ['P1_OPQUERY_CURVE_ONLY', 'P2_OPQUERY_SURFACE_ONLY', 'P3_OPQUERY_SURFACE_CURVE']


def deterministic_overfit_cads(labels):
    kinds = collections.defaultdict(set)
    for row in labels: kinds[row['cad_id']].add(row['head_type'])
    all3 = sorted(cad for cad, value in kinds.items() if value == {'circle', 'extrude', 'box'})
    circle = sorted(cad for cad, value in kinds.items() if value == {'circle', 'extrude'})
    box = sorted(cad for cad, value in kinds.items() if value == {'box'})
    chosen = all3[:7] + circle[:7] + box[:6]
    if len(chosen) != 20 or len(set(chosen)) != 20: raise RuntimeError('deterministic 20-CAD selection failed')
    return chosen


def load_rows():
    return [json.loads(x) for x in (CACHE / 'instances.jsonl').read_text().splitlines() if x.strip()]


class Dataset:
    def __init__(self, rows):
        self.rows = rows; self.cache = {}

    def __len__(self): return len(self.rows)

    def one(self, index):
        row = self.rows[index]; path = row['feature_path']
        if path not in self.cache:
            z = np.load(path)
            self.cache[path] = {k: np.asarray(z[k], dtype=np.float32) for k in z.files}
        z = self.cache[path]
        target = row['targets']
        return row, z['operation_queries'][row['feature_operation_index']], z['surface_memory'], z['curve_memory'], target


def collate(dataset: Dataset, indices, device):
    items = [dataset.one(i) for i in indices]; b = len(items)
    max_s = max(len(x[2]) for x in items); max_c = max(len(x[3]) for x in items)
    query = torch.zeros(b, 2048); surface = torch.zeros(b, max_s, 2048); curve = torch.zeros(b, max_c, 262)
    spad = torch.ones(b, max_s, dtype=torch.bool); cpad = torch.ones(b, max_c, dtype=torch.bool)
    circle = torch.zeros(b, 7); extrude = torch.zeros(b, 2); box = torch.zeros(b, 6); active2 = torch.zeros(b, dtype=torch.bool)
    related, op_types = [], []
    for i, (row, q, s, c, target) in enumerate(items):
        query[i] = torch.from_numpy(q); surface[i, :len(s)] = torch.from_numpy(s); curve[i, :len(c)] = torch.from_numpy(c)
        spad[i, :len(s)] = False; cpad[i, :len(c)] = False; related.append(row['related_curve_full_indices']); op_types.append(row['operation_type'])
        if 'circle' in target:
            t = target['circle']; circle[i] = torch.tensor(t['center'] + [t['radius']] + t['normal'])
            e = target['extrude']; extrude[i] = torch.tensor([e['depth'], e['height_two']]); active2[i] = bool(e['depth_two_active'])
        else:
            t = target['box']; box[i] = torch.tensor(t['origin'] + t['extent'])
    return {k: v.to(device) if torch.is_tensor(v) else v for k, v in {
        'query': query, 'surface': surface, 'curve': curve, 'surface_padding': spad, 'curve_padding': cpad,
        'circle_target': circle, 'extrude_target': extrude, 'box_target': box, 'depth_two_active': active2,
        'related_indices': related, 'operation_type': op_types,
    }.items()}


def metrics(model, dataset, device):
    vals = collections.defaultdict(list); masses = []
    model.eval()
    with torch.no_grad():
        for start in range(0, len(dataset), 16):
            batch = collate(dataset, range(start, min(start + 16, len(dataset))), device)
            pred = model(batch['query'], batch['surface'], batch['surface_padding'], batch['curve'], batch['curve_padding'])
            for i, op in enumerate(batch['operation_type']):
                if op == 'Extrude':
                    t = batch['circle_target'][i]
                    vals['circle_center'].append(float(torch.linalg.norm(pred['circle_center'][i] - t[:3])))
                    vals['circle_radius'].append(float(torch.abs(pred['circle_radius'][i] - t[3])))
                    vals['extrude_depth'].append(float(torch.abs(pred['extrude_depth_one'][i] - batch['extrude_target'][i, 0])))
                else:
                    vals['box_origin'].append(float(torch.linalg.norm(pred['box_origin'][i] - batch['box_target'][i, :3])))
                    vals['box_extent'].append(float(torch.linalg.norm(pred['box_extent'][i] - batch['box_target'][i, 3:6])))
                if pred['curve_attention'] is not None:
                    w = pred['curve_attention'][i, :, 0, :]
                    masses.append(float(w[:, batch['related_indices'][i]].sum(-1).mean()))
    model.train()
    return {k: {'n': len(v), 'mean': float(np.mean(v)), 'median': float(np.median(v)), 'P90': float(np.percentile(v, 90))} for k, v in vals.items()} | {'attention_mass_mean': float(np.mean(masses)) if masses else None}


def train_one(arm, mode, rows, device, epochs):
    run = OUT / mode / arm
    if run.exists(): raise RuntimeError(f'refusing overwrite {run}')
    run.mkdir(parents=True)
    torch.manual_seed(42); torch.cuda.manual_seed_all(42); np.random.seed(42); random.seed(42)
    data = Dataset(rows); model = OperationConditionedHead(arm).to(device)
    initial = metrics(model, data, device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.0)
    history = []; nan = inf = 0
    for epoch in range(1, epochs + 1):
        order = list(range(len(data))); random.Random(42 + epoch).shuffle(order)
        losses = []; parameters = []; attentions = []
        for start in range(0, len(order), 16):
            batch = collate(data, order[start:start + 16], device); optimizer.zero_grad(set_to_none=True)
            pred = model(batch['query'], batch['surface'], batch['surface_padding'], batch['curve'], batch['curve_padding'])
            loss, ploss, aloss = supervised_loss(pred, batch, model.use_curve)
            if not torch.isfinite(loss):
                nan += int(torch.isnan(loss)); inf += int(torch.isinf(loss)); raise RuntimeError('nonfinite loss')
            loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); optimizer.step()
            losses.append(float(loss.detach())); parameters.append(float(ploss)); attentions.append(float(aloss))
        history.append({'epoch': epoch, 'loss': float(np.mean(losses)), 'parameter_loss': float(np.mean(parameters)), 'attention_loss': float(np.mean(attentions))})
        if mode == 'train800':
            torch.save({'arm': arm, 'epoch': epoch, 'model': model.state_dict()}, run / f'checkpoint_epoch_{epoch:03d}.pt')
        if epoch % (100 if mode == 'overfit20' else 10) == 0 or epoch == epochs:
            print(f'[{mode}/{arm}] epoch={epoch}/{epochs} loss={history[-1]["loss"]:.6f}', flush=True)
    final = metrics(model, data, device)
    final_path = run / 'checkpoint_final.pt'; torch.save({'arm': arm, 'epoch': epochs, 'model': model.state_dict()}, final_path)
    report = {'ARM': arm, 'MODE': mode, 'SEED': 42, 'EPOCHS': epochs, 'LEARNING_RATE': 3e-4, 'BATCH_SIZE': 16,
              'LAMBDA_ATTENTION': LAMBDA_ATTENTION, 'CAD_COUNT': len({r['cad_id'] for r in rows}), 'OPERATION_COUNT': len(rows),
              'INITIAL_METRICS_NORMALIZED': initial, 'FINAL_METRICS_NORMALIZED': final, 'HISTORY': history,
              'NAN_COUNT': nan, 'INF_COUNT': inf, 'CHECKPOINT_FINAL': str(final_path),
              'BACKBONE_FROZEN_OFFLINE_FEATURE_CACHE': True, 'GT_RELATED_CURVES_USED_AS_HARD_MASK': False,
              'TRAINABLE_MODULES': ['operation query projection','surface cross attention','curve cross attention','fusion module','parameter heads'],
              'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False}
    (run / 'TRAINING_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--mode', choices=['overfit20','train800'], required=True); parser.add_argument('--device', default='cuda:0'); args = parser.parse_args()
    torch.manual_seed(42); np.random.seed(42); random.seed(42); torch.backends.cuda.matmul.allow_tf32 = True
    rows = [r for r in load_rows() if r['split'] == 'train']
    if args.mode == 'overfit20':
        old_labels = [json.loads(x) for x in (OLD_OUT / 'oracle_labels_train.jsonl').read_text().splitlines() if x.strip()]
        cads = set(deterministic_overfit_cads(old_labels)); rows = [r for r in rows if r['cad_id'] in cads]; epochs = 1200
    else:
        overfit = json.loads((OUT / 'overfit20/OVERFIT_GATE.json').read_text())
        if not overfit['OVERFIT20_PASS']: raise RuntimeError('overfit gate not passed')
        epochs = 60
    reports = [train_one(arm, args.mode, rows, torch.device(args.device), epochs) for arm in ARMS]
    if args.mode == 'overfit20':
        p3 = next(r for r in reports if r['ARM'].startswith('P3_'))
        before, after = p3['INITIAL_METRICS_NORMALIZED']['extrude_depth']['median'], p3['FINAL_METRICS_NORMALIZED']['extrude_depth']['median']
        passed = after < before * 0.2 and all(r['NAN_COUNT'] == 0 and r['INF_COUNT'] == 0 for r in reports)
        gate = {'OVERFIT20_PASS': passed, 'P3_EXTRUDE_DEPTH_INITIAL_MEDIAN': before, 'P3_EXTRUDE_DEPTH_FINAL_MEDIAN': after,
                'P3_EXTRUDE_DEPTH_RECOVERY_RATIO': after / before, 'SIGNIFICANT_FIT_THRESHOLD': 'final < 0.2 * initial',
                'P0_SIMPLE_HEAD_V1_REFERENCE': str(OLD_OUT / 'OVERFIT20_REPORT.json'), 'REPORTS': [r['CHECKPOINT_FINAL'] for r in reports]}
        (OUT / 'overfit20/OVERFIT_GATE.json').write_text(json.dumps(gate, indent=2) + '\n')
        print(json.dumps(gate, indent=2))


if __name__ == '__main__': main()
