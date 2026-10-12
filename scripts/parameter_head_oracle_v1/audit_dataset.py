#!/usr/bin/env python3
from __future__ import annotations

import collections
import json
from pathlib import Path

import numpy as np

from common import (
    CHECKPOINT, CHECKPOINT_SHA256, C2_SHA256, DEV_MANIFEST, EXECUTOR,
    EXECUTOR_SHA256, OUTPUT_ROOT, TRAIN_MANIFEST, box_edge_match,
    finite_array, load_manifest, object_frame, operation_parameters,
    parse_assignments, sha256, circle_edge_match, token_contract,
)


def one_split(split: str, manifest: Path) -> tuple[list[dict], dict]:
    rows = load_manifest(manifest)
    labels = []
    candidate = collections.Counter()
    available = collections.Counter()
    reasons = collections.Counter()
    cad_available = collections.Counter()
    invalid = collections.Counter()

    for row in rows:
        center, scale, lo, hi = object_frame(row)
        tokens, anchors, _, _ = token_contract(row)
        if tokens.shape[1] != 256 or anchors.shape != (len(tokens), 6):
            raise RuntimeError(f"representation shape failure: {row['cad_id']}")
        ops = parse_assignments(Path(row['target_dsl']).read_text())
        cad_seen = set()
        for op in ops:
            params = operation_parameters(op)
            if params is None:
                continue
            if op['op'] == 'Extrude':
                classes = ('circle', 'extrude')
                candidate.update(classes)
                token_i, reason = circle_edge_match(row, params)
                mapping_ok = token_i is not None
                for kind in classes:
                    reasons[f'{kind}:{reason}'] += 1
                if not mapping_ok:
                    continue
                normal = params['direction']
                base = {
                    'split': split, 'cad_id': row['cad_id'], 'source_dataset': row['source_dataset'],
                    'assignment': op['name'], 'operation_order': op['order'],
                    'mapping_method': reason, 'token_indices': [token_i],
                    'object_center': center.tolist(), 'object_scale': scale,
                    'object_bbox_min': lo.tolist(), 'object_bbox_max': hi.tolist(),
                    'target_dsl': row['target_dsl'], 'm2_full_c2_tokens': row['m2_full_c2_tokens'],
                    'm2_full_curves': row['m2_full_curves'], 'selected_m2_indices': row['selected_m2_indices'],
                }
                circle = dict(base)
                circle.update({
                    'head_type': 'circle',
                    'target_world': {'center': params['origin'].tolist(), 'radius': params['circle_radius'], 'normal': normal.tolist()},
                    'target_norm': {'center': ((params['origin'] - center) / scale).tolist(), 'radius': params['circle_radius'] / scale, 'normal': normal.tolist()},
                })
                extrude = dict(base)
                extrude.update({
                    'head_type': 'extrude',
                    'target_world': {'origin': params['origin'].tolist(), 'direction': normal.tolist(), 'depth': params['depth'], 'height_two': params['height_two']},
                    'target_norm': {'origin': ((params['origin'] - center) / scale).tolist(), 'direction': normal.tolist(), 'depth': params['depth'] / scale, 'height_two': params['height_two'] / scale},
                    'symmetric': params['symmetric'], 'two_sided': abs(params['height_two']) > 1e-12,
                })
                for label in (circle, extrude):
                    if not finite_array(list(label['target_norm'].values())):
                        invalid[f"{label['head_type']}:nonfinite"] += 1
                        continue
                    labels.append(label)
                    available[label['head_type']] += 1
                    cad_seen.add(label['head_type'])
            elif op['op'] == 'Box':
                candidate['box'] += 1
                token_indices, reason = box_edge_match(row, params)
                reasons[f'box:{reason}'] += 1
                if token_indices is None:
                    continue
                label = {
                    'split': split, 'cad_id': row['cad_id'], 'source_dataset': row['source_dataset'],
                    'assignment': op['name'], 'operation_order': op['order'], 'head_type': 'box',
                    'mapping_method': reason, 'token_indices': token_indices,
                    'object_center': center.tolist(), 'object_scale': scale,
                    'object_bbox_min': lo.tolist(), 'object_bbox_max': hi.tolist(),
                    'target_dsl': row['target_dsl'], 'm2_full_c2_tokens': row['m2_full_c2_tokens'],
                    'm2_full_curves': row['m2_full_curves'], 'selected_m2_indices': row['selected_m2_indices'],
                    'target_world': {'origin': params['origin'].tolist(), 'extent': [params['width'], params['depth'], params['height']]},
                    'target_norm': {'origin': ((params['origin'] - center) / scale).tolist(), 'extent': (np.asarray([params['width'], params['depth'], params['height']]) / scale).tolist()},
                    'orientation_gt_kept': {'axis': params['axis'].tolist(), 'x_axis': params['x_axis'].tolist(), 'height_two': params['height_two'], 'symmetric': params['symmetric']},
                }
                if not finite_array(list(label['target_norm'].values())):
                    invalid['box:nonfinite'] += 1
                    continue
                labels.append(label)
                available['box'] += 1
                cad_seen.add('box')
        cad_available.update(cad_seen)

    summary = {
        'split': split, 'cad_count': len(rows),
        'candidate_operations': dict(candidate), 'available_instances': dict(available),
        'available_cads': dict(cad_available),
        'coverage': {k: available[k] / candidate[k] if candidate[k] else None for k in ('circle', 'extrude', 'box')},
        'mapping_reason_counts': dict(reasons), 'invalid_label_counts': dict(invalid),
    }
    return labels, summary


def main() -> None:
    if not CHECKPOINT.is_dir():
        raise RuntimeError('Frozen checkpoint missing')
    if sha256(EXECUTOR) != EXECUTOR_SHA256:
        raise RuntimeError('placement_v3 executor hash mismatch')
    if OUTPUT_ROOT.exists():
        raise RuntimeError(f'Refusing to overwrite: {OUTPUT_ROOT}')
    train_labels, train_summary = one_split('train', TRAIN_MANIFEST)
    dev_labels, dev_summary = one_split('dev', DEV_MANIFEST)
    train_ids = {row['cad_id'] for row in load_manifest(TRAIN_MANIFEST)}
    dev_ids = {row['cad_id'] for row in load_manifest(DEV_MANIFEST)}
    leakage = sorted(train_ids & dev_ids)

    OUTPUT_ROOT.mkdir(parents=True)
    with (OUTPUT_ROOT / 'oracle_labels_train.jsonl').open('w') as handle:
        for row in train_labels:
            handle.write(json.dumps(row) + '\n')
    with (OUTPUT_ROOT / 'oracle_labels_dev.jsonl').open('w') as handle:
        for row in dev_labels:
            handle.write(json.dumps(row) + '\n')

    mapping_valid = not leakage and all(train_summary['available_instances'].get(k, 0) > 0 for k in ('circle', 'extrude', 'box'))
    audit = {
        'EXPERIMENT': 'PARAMETER_HEAD_ORACLE_V1', 'PHASE': 'A_ORACLE_CORRESPONDENCE_AUDIT',
        'ORACLE_MAPPING_VALID': mapping_valid,
        'MAPPING_CONTRACT': 'STRICT_ANALYTIC_IDENTITY_JOIN_ONLY',
        'MAPPING_RULES': {
            'circle': 'Unique exact canonical center/radius/normal identity between GT Circle profile and a frozen C2 sharp-edge token.',
            'extrude': 'GT Extrude(Circle) profile inherits the same unique exact GT Circle token; no polygon or inferred profile mapping.',
            'box': 'All 12 analytically generated GT Box edges must each map uniquely to frozen C2 sharp-edge tokens.',
            'forbidden_fallbacks': ['nearest_neighbor', 'predicted_operation', 'Hungarian', 'manual_selection'],
        },
        'TRAIN': train_summary, 'DEV': dev_summary,
        'TRAIN_DEV_LEAKAGE_COUNT': len(leakage), 'TRAIN_DEV_LEAKAGE_IDS': leakage,
        'BEST_ARM': 'A3_ANCHOR_Q32', 'BEST_EPOCH': 7,
        'BEST_CHECKPOINT': str(CHECKPOINT), 'BEST_CHECKPOINT_SHA256': CHECKPOINT_SHA256,
        'C2_SHA256': C2_SHA256, 'EXECUTOR_PATH': str(EXECUTOR), 'EXECUTOR_SHA256': EXECUTOR_SHA256,
        'ANCHOR_RECIPE': 'Exact frozen A3 load_anchor behavior from run_four_arm_100step_impl.py',
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'ORACLE_CORRESPONDENCE_AUDIT.json').write_text(json.dumps(audit, indent=2) + '\n')

    def values(labels, head, field):
        out = []
        for row in labels:
            if row['head_type'] != head:
                continue
            value = row['target_world'][field]
            out.extend(np.asarray(value, dtype=float).reshape(-1).tolist())
        return out

    stats = {
        'TRAIN_CIRCLE_COUNT': train_summary['available_instances'].get('circle', 0),
        'TRAIN_EXTRUDE_COUNT': train_summary['available_instances'].get('extrude', 0),
        'TRAIN_BOX_COUNT': train_summary['available_instances'].get('box', 0),
        'DEV_CIRCLE_COUNT': dev_summary['available_instances'].get('circle', 0),
        'DEV_EXTRUDE_COUNT': dev_summary['available_instances'].get('extrude', 0),
        'DEV_BOX_COUNT': dev_summary['available_instances'].get('box', 0),
        'DISTRIBUTIONS': {},
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    for split, labels in (('train', train_labels), ('dev', dev_labels)):
        stats['DISTRIBUTIONS'][split] = {}
        for head, fields in {'circle': ['radius'], 'extrude': ['depth', 'height_two'], 'box': ['extent']}.items():
            stats['DISTRIBUTIONS'][split][head] = {}
            for field in fields:
                arr = np.asarray(values(labels, head, field), dtype=float)
                stats['DISTRIBUTIONS'][split][head][field] = {
                    'n_scalar': int(arr.size), 'min': float(arr.min()) if arr.size else None,
                    'median': float(np.median(arr)) if arr.size else None,
                    'max': float(arr.max()) if arr.size else None,
                }
    (OUTPUT_ROOT / 'DATASET_PARAMETER_STATS.json').write_text(json.dumps(stats, indent=2) + '\n')
    normalization = {
        'CONTRACT': 'OBJECT_BBOX_MAX_EXTENT_V1',
        'object_center': '(object_bbox_min + object_bbox_max) / 2',
        'object_scale': 'max(object_bbox_max - object_bbox_min)',
        'position_norm': '(position - object_center) / object_scale',
        'length_norm': 'length / object_scale',
        'inverse_position': 'position_norm * object_scale + object_center',
        'inverse_length': 'length_norm * object_scale',
        'bbox_source': 'frozen decode/train mesh.obj vertices',
        'minimum_scale': 1e-8, 'orientation_vectors': 'unit vectors; not magnitude-normalized',
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'PARAMETER_NORMALIZATION_CONTRACT.json').write_text(json.dumps(normalization, indent=2) + '\n')
    print(json.dumps({'ORACLE_MAPPING_VALID': mapping_valid, 'TRAIN': train_summary, 'DEV': dev_summary}, indent=2))


if __name__ == '__main__':
    main()
