#!/usr/bin/env python3
from __future__ import annotations

import ast
import collections
import json
import math
import shutil
from pathlib import Path

import numpy as np
import torch

from common import CHECKPOINT, CHECKPOINT_SHA256, DEV_MANIFEST, EXECUTOR, EXECUTOR_SHA256, OUTPUT_ROOT, load_manifest, parse_assignments, operation_parameters, sha256
from dsl_tools import compose, inverse_predictions, load_executor, replay
from model import ParameterHeads
from train_heads import FeatureStore, load_jsonl, predict_all


LLM_PREDICTIONS = Path('/var/tmp/cuiyuehan_mesh2cad/m2_spatial_anchor_q_ablation_formal_train800_v1/decode_dev50_all_epochs/A3_ANCHOR_Q32_RETRY2/epoch_07/per_cad.jsonl')


def finite(value) -> bool:
    if isinstance(value, dict):
        return all(finite(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return all(finite(item) for item in value)
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def generated_params(text: str) -> dict[tuple[str, str], dict]:
    try:
        ops = parse_assignments(text)
    except Exception:
        return {}
    out = {}
    for op in ops:
        params = operation_parameters(op)
        if params is None:
            continue
        if op['op'] == 'Extrude':
            circle = {'center': params['origin'].tolist(), 'radius': params['circle_radius'], 'normal': params['direction'].tolist()}
            extrude = {'origin': params['origin'].tolist(), 'direction': params['direction'].tolist(), 'depth': params['depth'], 'height_two': params['height_two']}
            if finite(list(circle.values())): out[(op['name'], 'circle')] = circle
            if finite(list(extrude.values())): out[(op['name'], 'extrude')] = extrude
        elif op['op'] == 'Box':
            box = {'origin': params['origin'].tolist(), 'extent': [params['width'], params['depth'], params['height']]}
            if finite(list(box.values())): out[(op['name'], 'box')] = box
    return out


def summary(values: list[float]) -> dict:
    arr = np.asarray(values, dtype=float)
    return {
        'n': int(arr.size), 'mean': float(arr.mean()) if arr.size else None,
        'median': float(np.median(arr)) if arr.size else None,
        'P25': float(np.percentile(arr, 25)) if arr.size else None,
        'P75': float(np.percentile(arr, 75)) if arr.size else None,
        'P90': float(np.percentile(arr, 90)) if arr.size else None,
    }


def parameter_errors(label: dict, prediction: dict) -> dict[str, float]:
    gt = label['target_world']; head = label['head_type']; eps = 1e-12
    if head == 'circle':
        dot = abs(float(np.dot(prediction['normal'], gt['normal'])))
        radius_abs = abs(float(prediction['radius']) - float(gt['radius']))
        return {
            'circle_center': float(np.linalg.norm(np.asarray(prediction['center']) - gt['center'])),
            'circle_radius_abs': radius_abs,
            'circle_radius_rel': radius_abs / max(abs(float(gt['radius'])), eps),
            'circle_normal_angular': float(np.degrees(np.arccos(np.clip(dot, -1, 1)))),
        }
    if head == 'extrude':
        dot = float(np.dot(prediction['direction'], gt['direction']))
        depth_abs = abs(float(prediction['depth']) - float(gt['depth']))
        return {
            'extrude_origin': float(np.linalg.norm(np.asarray(prediction['origin']) - gt['origin'])),
            'extrude_direction_angular': float(np.degrees(np.arccos(np.clip(dot, -1, 1)))),
            'extrude_depth_abs': depth_abs,
            'extrude_depth_rel': depth_abs / max(abs(float(gt['depth'])), eps),
        }
    extent = float(np.linalg.norm(np.asarray(prediction['extent']) - gt['extent']))
    return {
        'box_origin': float(np.linalg.norm(np.asarray(prediction['origin']) - gt['origin'])),
        'box_extent': extent,
    }


def aggregate_geometry(rows: list[dict], key: str, ids: set[str] | None = None) -> dict:
    selected = [row[key] for row in rows if ids is None or row['cad_id'] in ids]
    return {
        'CAD_COUNT': len(selected),
        'STEP_RELOAD_COUNT': sum(row['step_reload'] for row in selected),
        'Chamfer': summary([row['chamfer'] for row in selected if row['chamfer'] is not None]),
        'H95': summary([row['H95'] for row in selected if row['H95'] is not None]),
        'BBox_center': summary([row['bbox_center'] for row in selected if row['bbox_center'] is not None]),
        'BBox_extent': summary([row['bbox_extent'] for row in selected if row['bbox_extent'] is not None]),
    }


def main() -> None:
    labels = load_jsonl(OUTPUT_ROOT / 'oracle_labels_dev.jsonl')
    train_report = json.loads((OUTPUT_ROOT / 'train800/TRAIN_REPORT.json').read_text())
    checkpoint_path = OUTPUT_ROOT / 'train800/checkpoint_final.pt'
    checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=True)
    model = ParameterHeads(); model.load_state_dict(checkpoint['model']); model.eval()
    store = FeatureStore(labels)
    head_norm = predict_all(model, labels, store, torch.device('cpu'))
    head_world_by_identity = {}
    for label, pred in zip(labels, head_norm):
        world = inverse_predictions([label], [pred])
        values = world.get(label['assignment'])
        if values is None:
            # Circle-only conversion intentionally waits for paired Extrude;
            # reconstruct its metrics directly here.
            scale, center = float(label['object_scale']), np.asarray(label['object_center'])
            if label['head_type'] == 'circle':
                values = {'center': (np.asarray(pred['center']) * scale + center).tolist(), 'radius': float(pred['radius']) * scale, 'normal': pred['normal']}
            elif label['head_type'] == 'extrude':
                values = {'origin': (np.asarray(pred['origin']) * scale + center).tolist(), 'direction': pred['direction'], 'depth': float(pred['depth']) * scale, 'height_two': float(pred['height_two']) * scale}
            else:
                values = {'origin': (np.asarray(pred['origin']) * scale + center).tolist(), 'extent': (np.asarray(pred['extent']) * scale).tolist()}
        else:
            if label['head_type'] == 'circle':
                values = {'center': values['circle_center'], 'radius': values['circle_radius'], 'normal': values['circle_normal']}
            elif label['head_type'] == 'extrude':
                values = {k: values[k] for k in ('origin', 'direction', 'depth', 'height_two')}
        head_world_by_identity[(label['cad_id'], label['assignment'], label['head_type'])] = values

    llm_rows = load_jsonl(LLM_PREDICTIONS)
    llm_by_cad = {row['cad_id']: generated_params(row['generated_dsl']) for row in llm_rows}
    common_labels = []
    llm_values = []
    head_values = []
    missing = collections.Counter()
    metric_values = {'LLM': collections.defaultdict(list), 'HEAD': collections.defaultdict(list)}
    for label in labels:
        identity = (label['assignment'], label['head_type'])
        llm = llm_by_cad.get(label['cad_id'], {}).get(identity)
        if llm is None:
            missing[label['head_type']] += 1
            continue
        head = head_world_by_identity[(label['cad_id'], label['assignment'], label['head_type'])]
        common_labels.append(label); llm_values.append(llm); head_values.append(head)
        for system, value in (('LLM', llm), ('HEAD', head)):
            for metric, error in parameter_errors(label, value).items():
                metric_values[system][metric].append(error)
    parameter_report = {
        'COMMON_PARAMETER_INSTANCE_COUNT': len(common_labels),
        'COMMON_COUNTS': dict(collections.Counter(row['head_type'] for row in common_labels)),
        'LLM_MISSING_COUNTS': dict(missing),
        'METRICS': {system: {metric: summary(values) for metric, values in metrics.items()} for system, metrics in metric_values.items()},
        'HEAD_CHECKPOINT': str(checkpoint_path), 'HEAD_EPOCH': checkpoint['epoch'],
        'BEST_BACKBONE': str(CHECKPOINT), 'BEST_BACKBONE_SHA256': CHECKPOINT_SHA256,
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'DEV50_PARAMETER_METRICS.json').write_text(json.dumps(parameter_report, indent=2) + '\n')

    # Compose only the exact common LLM/head fields so B1 and B2 differ solely
    # in continuous values on an identical GT operation skeleton.
    grouped_labels = collections.defaultdict(list)
    grouped_head_norm = collections.defaultdict(list)
    common_identities = {(row['cad_id'], row['assignment'], row['head_type']) for row in common_labels}
    norm_by_identity = {(row['cad_id'], row['assignment'], row['head_type']): pred for row, pred in zip(labels, head_norm)}
    llm_common_by_cad = collections.defaultdict(dict)
    for label, llm in zip(common_labels, llm_values):
        grouped_labels[label['cad_id']].append(label)
        grouped_head_norm[label['cad_id']].append(norm_by_identity[(label['cad_id'], label['assignment'], label['head_type'])])
        item = llm_common_by_cad[label['cad_id']].setdefault(label['assignment'], {})
        if label['head_type'] == 'circle':
            item.update({'circle_radius': llm['radius'], 'circle_center': llm['center'], 'circle_normal': llm['normal']})
        elif label['head_type'] == 'extrude':
            item.update({'origin': llm['origin'], 'direction': llm['direction'], 'depth': llm['depth'], 'height_two': llm['height_two']})
        else:
            item.update({'origin': llm['origin'], 'extent': llm['extent']})

    dev_dir = OUTPUT_ROOT / 'dev50'
    if dev_dir.exists():
        shutil.rmtree(dev_dir)
    dev_dir.mkdir()
    executor = load_executor()
    replay_rows, replacement_audit = [], []
    # Replay the complete frozen dev50. CADs without an oracle-supported
    # replacement remain byte-identical to GT in all three branches.
    dev_records = load_manifest(DEV_MANIFEST)
    cad_to_target = {row['cad_id']: Path(row['target_dsl']) for row in dev_records}
    if len(cad_to_target) != 50:
        raise RuntimeError(f'fixed dev manifest is not 50 CADs: {len(cad_to_target)}')
    for cad_id in sorted(cad_to_target):
        target_path = cad_to_target[cad_id]
        gt_text = target_path.read_text()
        head_replacements = inverse_predictions(grouped_labels.get(cad_id, []), grouped_head_norm.get(cad_id, []))
        # Require paired Circle+Extrude fields for that assignment, matching compose contract.
        llm_replacements = {name: value for name, value in llm_common_by_cad.get(cad_id, {}).items() if ('extent' in value or {'circle_radius', 'origin', 'direction', 'depth', 'height_two'} <= set(value))}
        shared_assignments = set(head_replacements) & set(llm_replacements)
        head_replacements = {k: v for k, v in head_replacements.items() if k in shared_assignments}
        llm_replacements = {k: v for k, v in llm_replacements.items() if k in shared_assignments}
        llm_text, llm_audit = compose(gt_text, llm_replacements)
        head_text, head_audit = compose(gt_text, head_replacements)
        cad_dir = dev_dir / cad_id; cad_dir.mkdir()
        (cad_dir / 'GT_PARAMETER_DSL.dsl').write_text(gt_text)
        (cad_dir / 'LLM_PARAMETER_DSL.dsl').write_text(llm_text)
        (cad_dir / 'HEAD_PARAMETER_DSL.dsl').write_text(head_text)
        gt_result = replay(gt_text, target_path.parent / 'mesh.obj', cad_dir / 'gt', executor)
        llm_result = replay(llm_text, target_path.parent / 'mesh.obj', cad_dir / 'llm', executor)
        head_result = replay(head_text, target_path.parent / 'mesh.obj', cad_dir / 'head', executor)
        replay_rows.append({'cad_id': cad_id, 'GT': gt_result, 'LLM': llm_result, 'HEAD': head_result, 'replacement_assignments': sorted(shared_assignments)})
        for system, items in (('LLM', llm_audit), ('HEAD', head_audit)):
            for item in items:
                replacement_audit.append({'phase': 'DEV50', 'cad_id': cad_id, 'system': system, **item})
    with (OUTPUT_ROOT / 'PARAMETER_REPLACEMENT_AUDIT.jsonl').open('w') as handle:
        for row in replacement_audit:
            handle.write(json.dumps(row) + '\n')
    occ_report = {
        'EXECUTOR_PATH': str(EXECUTOR), 'EXECUTOR_SHA256': EXECUTOR_SHA256,
        'CAD_COUNT': len(replay_rows),
        'COUNTS': {system: {stage: sum(row[system][stage] for row in replay_rows) for stage in ('parse', 'execute', 'brep_valid', 'step_reload')} for system in ('GT', 'LLM', 'HEAD')},
        'PER_CAD': replay_rows,
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'DEV50_OCC_REPLAY.json').write_text(json.dumps(occ_report, indent=2) + '\n')
    common_valid = {row['cad_id'] for row in replay_rows if all(row[system]['step_reload'] and row[system]['chamfer'] is not None for system in ('GT', 'LLM', 'HEAD'))}
    geometry = {
        'ALL_VALID': {system: aggregate_geometry(replay_rows, system) for system in ('GT', 'LLM', 'HEAD')},
        'COMMON_VALID_COUNT': len(common_valid),
        'COMMON_VALID_CAD_IDS': sorted(common_valid),
        'COMMON_VALID': {system: aggregate_geometry(replay_rows, system, common_valid) for system in ('GT', 'LLM', 'HEAD')},
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'DEV50_GEOMETRY_METRICS.json').write_text(json.dumps(geometry, indent=2) + '\n')

    def median(system, key):
        return parameter_report['METRICS'][system].get(key, {}).get('median')
    parameter_improvements = {
        key: {'LLM': median('LLM', key), 'HEAD': median('HEAD', key), 'improved': median('HEAD', key) is not None and median('LLM', key) is not None and median('HEAD', key) < median('LLM', key)}
        for key in ('circle_center', 'circle_radius_abs', 'extrude_origin', 'extrude_depth_abs', 'box_origin', 'box_extent')
    }
    llm_step = occ_report['COUNTS']['LLM']['step_reload']; head_step = occ_report['COUNTS']['HEAD']['step_reload']
    llm_ch = geometry['COMMON_VALID']['LLM']['Chamfer']['median']; head_ch = geometry['COMMON_VALID']['HEAD']['Chamfer']['median']
    parameter_pass = all(item['improved'] for item in parameter_improvements.values())
    geometry_pass = head_step >= llm_step and head_ch is not None and llm_ch is not None and head_ch < llm_ch
    comparison = {
        'PARAMETER_IMPROVEMENTS': parameter_improvements,
        'PARAMETER_PASS': parameter_pass, 'GEOMETRY_PASS': geometry_pass,
        'LLM_STEP': llm_step, 'HEAD_STEP': head_step,
        'LLM_COMMON_VALID_CHAMFER': llm_ch, 'HEAD_COMMON_VALID_CHAMFER': head_ch,
        'OVERALL_SUCCESS': parameter_pass and geometry_pass,
        'FAILURE_ANALYSIS': None if parameter_pass and geometry_pass else [
            'Raw C2 token plus anchor may encode local curve geometry but not operation-specific extrusion depth/origin across the full dataset.',
            'Unsupported fields remain GT; Boolean and sketch-plane dependencies can dominate final geometry.',
            'Strict oracle coverage is partial, so many operations remain unchanged and geometry sensitivity is uneven.',
        ],
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'LLM_VS_HEAD_COMMON_VALID.json').write_text(json.dumps(comparison, indent=2) + '\n')
    print(json.dumps({'PARAMETER': parameter_report, 'OCC_COUNTS': occ_report['COUNTS'], 'COMMON_VALID': geometry['COMMON_VALID'], 'COMPARISON': comparison}, indent=2))


if __name__ == '__main__':
    main()
