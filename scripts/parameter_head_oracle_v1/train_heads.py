#!/usr/bin/env python3
from __future__ import annotations

import argparse
import collections
import json
import math
import random
from pathlib import Path

import numpy as np
import torch

from common import CHECKPOINT, CHECKPOINT_SHA256, OUTPUT_ROOT, object_frame, token_contract
from model import ParameterHeads, loss_for


def load_jsonl(path: Path) -> list[dict]:
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def deterministic_overfit_cads(labels: list[dict]) -> list[str]:
    kinds = collections.defaultdict(set)
    for row in labels:
        kinds[row['cad_id']].add(row['head_type'])
    all3 = sorted(cad for cad, value in kinds.items() if value == {'circle', 'extrude', 'box'})
    circle = sorted(cad for cad, value in kinds.items() if value == {'circle', 'extrude'})
    box = sorted(cad for cad, value in kinds.items() if value == {'box'})
    chosen = all3[:7] + circle[:7] + box[:6]
    if len(chosen) != 20 or len(set(chosen)) != 20:
        raise RuntimeError('Unable to build deterministic balanced 20-CAD set')
    return chosen


class FeatureStore:
    def __init__(self, labels: list[dict]):
        self.labels = labels
        self.cache = {}

    def features(self, label: dict) -> torch.Tensor:
        cad_id = label['cad_id']
        if cad_id not in self.cache:
            row = {
                'target_dsl': label['target_dsl'], 'm2_full_c2_tokens': label['m2_full_c2_tokens'],
                'm2_full_curves': label['m2_full_curves'], 'selected_m2_indices': label['selected_m2_indices'],
                'k_valid': len(label['selected_m2_indices']),
            }
            tokens, anchors, _, _ = token_contract(row)
            self.cache[cad_id] = np.concatenate([tokens, anchors], axis=1).astype(np.float32)
        return torch.from_numpy(self.cache[cad_id][label['token_indices']])


def tensor_target(label: dict, device: torch.device) -> dict:
    return {key: torch.as_tensor(value, dtype=torch.float32, device=device) for key, value in label['target_norm'].items()}


def predict_all(model, labels, store, device) -> list[dict]:
    model.eval()
    out = []
    with torch.no_grad():
        for label in labels:
            pred = model(label['head_type'], store.features(label).to(device))
            out.append({key: value.detach().cpu().numpy().tolist() for key, value in pred.items()})
    return out


def metrics(labels, predictions) -> dict:
    values = collections.defaultdict(list)
    for label, pred in zip(labels, predictions):
        gt = label['target_norm']
        head = label['head_type']
        if head == 'circle':
            values['circle_center'].append(float(np.linalg.norm(np.asarray(pred['center']) - gt['center'])))
            values['circle_radius'].append(abs(float(pred['radius']) - float(gt['radius'])))
            dot = abs(float(np.dot(pred['normal'], gt['normal'])))
            values['circle_normal_deg'].append(float(np.degrees(np.arccos(np.clip(dot, -1, 1)))))
        elif head == 'extrude':
            values['extrude_origin'].append(float(np.linalg.norm(np.asarray(pred['origin']) - gt['origin'])))
            values['extrude_depth'].append(abs(float(pred['depth']) - float(gt['depth'])))
            dot = float(np.dot(pred['direction'], gt['direction']))
            values['extrude_direction_deg'].append(float(np.degrees(np.arccos(np.clip(dot, -1, 1)))))
        elif head == 'box':
            values['box_origin'].append(float(np.linalg.norm(np.asarray(pred['origin']) - gt['origin'])))
            values['box_extent'].append(float(np.linalg.norm(np.asarray(pred['extent']) - gt['extent'])))
    result = {}
    for key, vals in values.items():
        arr = np.asarray(vals)
        result[key] = {'n': len(vals), 'mean': float(arr.mean()), 'median': float(np.median(arr)), 'p90': float(np.percentile(arr, 90))}
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['overfit20', 'full'], required=True)
    parser.add_argument('--device', default='cuda:0')
    parser.add_argument('--epochs', type=int, default=None)
    args = parser.parse_args()
    torch.manual_seed(42); np.random.seed(42); random.seed(42)
    device = torch.device(args.device)
    all_labels = load_jsonl(OUTPUT_ROOT / 'oracle_labels_train.jsonl')
    if args.mode == 'overfit20':
        cads = deterministic_overfit_cads(all_labels)
        labels = [row for row in all_labels if row['cad_id'] in set(cads)]
        epochs = args.epochs or 1200
        run_dir = OUTPUT_ROOT / 'overfit20'
    else:
        gate = json.loads((OUTPUT_ROOT / 'OVERFIT20_REPORT.json').read_text())
        if gate.get('OVERFIT20_PASS') is not True:
            raise RuntimeError('20-CAD gate not passed')
        cads = sorted({row['cad_id'] for row in all_labels})
        labels = all_labels
        epochs = args.epochs or 60
        run_dir = OUTPUT_ROOT / 'train800'
    if run_dir.exists():
        raise RuntimeError(f'Refusing to overwrite: {run_dir}')
    run_dir.mkdir()
    store = FeatureStore(labels)
    model = ParameterHeads().to(device)
    initial_predictions = predict_all(model, labels, store, device)
    initial_metrics = metrics(labels, initial_predictions)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-6)
    history = []
    nan_count = inf_count = 0
    order = list(range(len(labels)))
    for epoch in range(1, epochs + 1):
        random.Random(42 + epoch).shuffle(order)
        model.train()
        losses = []
        for index in order:
            label = labels[index]
            optimizer.zero_grad(set_to_none=True)
            prediction = model(label['head_type'], store.features(label).to(device))
            target = tensor_target(label, device)
            loss = loss_for(label['head_type'], prediction, target)
            nan_count += int(torch.isnan(loss))
            inf_count += int(torch.isinf(loss))
            if not torch.isfinite(loss):
                raise RuntimeError(f'non-finite loss epoch={epoch} label={index}')
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            optimizer.step()
            losses.append(float(loss.detach()))
        if epoch == 1 or epoch % (100 if args.mode == 'overfit20' else 1) == 0 or epoch == epochs:
            current = metrics(labels, predict_all(model, labels, store, device))
            entry = {'epoch': epoch, 'mean_loss': float(np.mean(losses)), 'metrics': current}
            history.append(entry)
            print(json.dumps(entry), flush=True)
        if args.mode == 'full':
            checkpoint = run_dir / f'checkpoint_epoch_{epoch:03d}.pt'
            torch.save({'model': model.state_dict(), 'epoch': epoch, 'seed': 42}, checkpoint)
    final_predictions = predict_all(model, labels, store, device)
    final_metrics = metrics(labels, final_predictions)
    torch.save({'model': model.state_dict(), 'epoch': epochs, 'seed': 42}, run_dir / 'checkpoint_final.pt')
    prediction_rows = []
    for label, before, after in zip(labels, initial_predictions, final_predictions):
        prediction_rows.append({'cad_id': label['cad_id'], 'assignment': label['assignment'], 'head_type': label['head_type'], 'before_norm': before, 'after_norm': after})
    with (run_dir / 'predictions.jsonl').open('w') as handle:
        for row in prediction_rows:
            handle.write(json.dumps(row) + '\n')
    report = {
        'MODE': args.mode, 'BEST_ARM': 'A3_ANCHOR_Q32', 'BEST_EPOCH': 7,
        'BEST_CHECKPOINT': str(CHECKPOINT), 'BEST_CHECKPOINT_SHA256': CHECKPOINT_SHA256,
        'BACKBONE_LOADED_FOR_GRADIENTS': False, 'BACKBONE_FROZEN_BY_OFFLINE_FEATURE_CONTRACT': True,
        'TRAINABLE_MODULES': ['CircleParameterHead', 'ExtrudeParameterHead', 'BoxParameterHead', 'ExtrudeProfileAggregator', 'BoxLocalAggregator'],
        'TRAINABLE_PARAMETER_COUNT': sum(p.numel() for p in model.parameters()),
        'CAD_COUNT': len(cads), 'CAD_IDS': cads, 'INSTANCE_COUNT': len(labels),
        'INSTANCE_COUNTS': dict(collections.Counter(row['head_type'] for row in labels)),
        'EPOCHS': epochs, 'SEED': 42, 'OPTIMIZER': 'AdamW', 'LEARNING_RATE': 1e-3,
        'NAN_COUNT': nan_count, 'INF_COUNT': inf_count,
        'INITIAL_METRICS_NORMALIZED': initial_metrics, 'FINAL_METRICS_NORMALIZED': final_metrics,
        'HISTORY': history, 'STATUS': 'TRAINING_FINISHED',
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (run_dir / 'TRAIN_REPORT.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'run_dir': str(run_dir), 'initial': initial_metrics, 'final': final_metrics}, indent=2))


if __name__ == '__main__':
    main()
