#!/usr/bin/env python3
from __future__ import annotations

import collections
import json
import random
from pathlib import Path

import numpy as np

from common import OUTPUT_ROOT
from dsl_tools import compose, inverse_predictions, load_executor, replay


def load_jsonl(path: Path):
    with path.open() as handle:
        return [json.loads(line) for line in handle if line.strip()]


def main() -> None:
    run = OUTPUT_ROOT / 'overfit20'
    report = json.loads((run / 'TRAIN_REPORT.json').read_text())
    labels = load_jsonl(OUTPUT_ROOT / 'oracle_labels_train.jsonl')
    chosen = set(report['CAD_IDS'])
    labels = [row for row in labels if row['cad_id'] in chosen]
    predictions = load_jsonl(run / 'predictions.jsonl')
    if len(labels) != len(predictions):
        raise RuntimeError('prediction/label count mismatch')
    by_cad_labels = collections.defaultdict(list)
    by_cad_before = collections.defaultdict(list)
    by_cad_after = collections.defaultdict(list)
    for label, prediction in zip(labels, predictions):
        if (label['cad_id'], label['assignment'], label['head_type']) != (prediction['cad_id'], prediction['assignment'], prediction['head_type']):
            raise RuntimeError('prediction identity mismatch')
        by_cad_labels[label['cad_id']].append(label)
        by_cad_before[label['cad_id']].append(prediction['before_norm'])
        by_cad_after[label['cad_id']].append(prediction['after_norm'])
    sampled = random.Random(42).sample(report['CAD_IDS'], 5)
    replay_root = run / 'occ_replay5'
    replay_root.mkdir()
    executor = load_executor()
    rows, replacement_audit = [], []
    for cad_id in sampled:
        these = by_cad_labels[cad_id]
        gt_path = Path(these[0]['target_dsl'])
        gt_text = gt_path.read_text()
        before_text, before_audit = compose(gt_text, inverse_predictions(these, by_cad_before[cad_id]))
        after_text, after_audit = compose(gt_text, inverse_predictions(these, by_cad_after[cad_id]))
        cad_dir = replay_root / cad_id
        cad_dir.mkdir()
        (cad_dir / 'BEFORE_HEAD.dsl').write_text(before_text)
        (cad_dir / 'AFTER_HEAD.dsl').write_text(after_text)
        before = replay(before_text, gt_path.parent / 'mesh.obj', cad_dir / 'before', executor)
        after = replay(after_text, gt_path.parent / 'mesh.obj', cad_dir / 'after', executor)
        rows.append({'cad_id': cad_id, 'before': before, 'after': after})
        for stage, items in (('before', before_audit), ('after', after_audit)):
            for item in items:
                replacement_audit.append({'phase': 'OVERFIT20', 'cad_id': cad_id, 'stage': stage, **item})
    with (run / 'PARAMETER_REPLACEMENT_AUDIT.jsonl').open('w') as handle:
        for row in replacement_audit:
            handle.write(json.dumps(row) + '\n')
    before_step = sum(row['before']['step_reload'] for row in rows)
    after_step = sum(row['after']['step_reload'] for row in rows)
    common = [row for row in rows if row['before']['step_reload'] and row['after']['step_reload']]
    before_ch = [row['before']['chamfer'] for row in common if row['before']['chamfer'] is not None and row['after']['chamfer'] is not None]
    after_ch = [row['after']['chamfer'] for row in common if row['before']['chamfer'] is not None and row['after']['chamfer'] is not None]
    initial, final = report['INITIAL_METRICS_NORMALIZED'], report['FINAL_METRICS_NORMALIZED']
    parameter_pass = all([
        final['circle_radius']['median'] < 0.5 * initial['circle_radius']['median'],
        final['extrude_origin']['median'] < 0.5 * initial['extrude_origin']['median'],
        final['extrude_depth']['median'] < 0.5 * initial['extrude_depth']['median'],
        final['box_origin']['median'] < 0.5 * initial['box_origin']['median'],
        final['box_extent']['median'] < 0.5 * initial['box_extent']['median'],
    ])
    geometry_pass = after_step > before_step or (before_ch and float(np.median(after_ch)) < float(np.median(before_ch)))
    passed = parameter_pass and geometry_pass and report['NAN_COUNT'] == 0 and report['INF_COUNT'] == 0
    output = {
        'CURRENT_GATE': 'PARAMETER_HEAD_ORACLE_20CAD_OVERFIT_PASS' if passed else 'PARAMETER_HEAD_ORACLE_20CAD_OVERFIT_FAIL',
        'OVERFIT20_PASS': passed, 'PARAMETER_PASS': parameter_pass, 'GEOMETRY_PASS': geometry_pass,
        'CAD_COUNT': 20, 'REPLAY_CAD_COUNT': 5, 'REPLAY_CAD_IDS': sampled,
        'INITIAL_METRICS_NORMALIZED': initial, 'FINAL_METRICS_NORMALIZED': final,
        'BEFORE_STEP': before_step, 'AFTER_STEP': after_step,
        'COMMON_VALID_COUNT': len(before_ch),
        'BEFORE_COMMON_VALID_CHAMFER_MEDIAN': float(np.median(before_ch)) if before_ch else None,
        'AFTER_COMMON_VALID_CHAMFER_MEDIAN': float(np.median(after_ch)) if after_ch else None,
        'OCC_REPLAY': rows, 'NAN_COUNT': report['NAN_COUNT'], 'INF_COUNT': report['INF_COUNT'],
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    (OUTPUT_ROOT / 'OVERFIT20_REPORT.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
