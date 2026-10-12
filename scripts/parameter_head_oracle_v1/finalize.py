#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from common import CHECKPOINT, CHECKPOINT_SHA256, CODE_ROOT, EXECUTOR, EXECUTOR_SHA256, OUTPUT_ROOT, sha256


def write(name: str, value: dict) -> None:
    (OUTPUT_ROOT / name).write_text(json.dumps(value, indent=2) + '\n')


def main() -> None:
    stats = json.loads((OUTPUT_ROOT / 'DATASET_PARAMETER_STATS.json').read_text())
    audit = json.loads((OUTPUT_ROOT / 'ORACLE_CORRESPONDENCE_AUDIT.json').read_text())
    overfit = json.loads((OUTPUT_ROOT / 'OVERFIT20_REPORT.json').read_text())
    train = json.loads((OUTPUT_ROOT / 'train800/TRAIN_REPORT.json').read_text())
    params = json.loads((OUTPUT_ROOT / 'DEV50_PARAMETER_METRICS.json').read_text())
    occ = json.loads((OUTPUT_ROOT / 'DEV50_OCC_REPLAY.json').read_text())
    geom = json.loads((OUTPUT_ROOT / 'DEV50_GEOMETRY_METRICS.json').read_text())
    compare = json.loads((OUTPUT_ROOT / 'LLM_VS_HEAD_COMMON_VALID.json').read_text())

    required = [
        'ORACLE_CORRESPONDENCE_AUDIT.json', 'PARAMETER_NORMALIZATION_CONTRACT.json',
        'OVERFIT20_REPORT.json', 'DEV50_PARAMETER_METRICS.json', 'DEV50_OCC_REPLAY.json',
        'DEV50_GEOMETRY_METRICS.json', 'LLM_VS_HEAD_COMMON_VALID.json',
        'PARAMETER_REPLACEMENT_AUDIT.jsonl',
    ]
    missing = [name for name in required if not (OUTPUT_ROOT / name).is_file()]
    epoch_checkpoints = sorted((OUTPUT_ROOT / 'train800').glob('checkpoint_epoch_*.pt'))
    forbidden_flags = [
        document.get(key) is False
        for document in (audit, overfit, train, params, occ, geom, compare)
        for key in ('ANCHOR_EVAL_100_READ', 'PILOT150_READ', 'OFFICIAL_TEST_READ')
    ]
    integrity = {
        'REQUIRED_ARTIFACTS_PRESENT': not missing,
        'MISSING_ARTIFACTS': missing,
        'ORACLE_MAPPING_VALID': audit['ORACLE_MAPPING_VALID'] is True,
        'OVERFIT20_PASS': overfit['OVERFIT20_PASS'] is True,
        'TRAIN_STATUS_COMPLETE': train['STATUS'] == 'TRAINING_FINISHED' and train['NAN_COUNT'] == 0 and train['INF_COUNT'] == 0,
        'EPOCH_CHECKPOINT_COUNT': len(epoch_checkpoints),
        'DEV50_CAD_COUNT': occ['CAD_COUNT'],
        'DEV50_THREE_BRANCH_COMPLETE': occ['CAD_COUNT'] == 50 and all(occ['COUNTS'][s]['parse'] == 50 and occ['COUNTS'][s]['execute'] == 50 for s in ('GT', 'LLM', 'HEAD')),
        'FORBIDDEN_SPLITS_UNREAD': all(forbidden_flags),
    }
    experiment_complete = all([
        integrity['REQUIRED_ARTIFACTS_PRESENT'], integrity['ORACLE_MAPPING_VALID'],
        integrity['OVERFIT20_PASS'], integrity['TRAIN_STATUS_COMPLETE'],
        integrity['EPOCH_CHECKPOINT_COUNT'] == 60,
        integrity['DEV50_THREE_BRANCH_COMPLETE'], integrity['FORBIDDEN_SPLITS_UNREAD'],
    ])
    if not experiment_complete:
        raise RuntimeError(f'final integrity gate failed: {integrity}')

    common = params['METRICS']
    final_values = {
        'CURRENT_GATE': 'PARAMETER_HEAD_ORACLE_V1_COMPLETE',
        'EXPERIMENT_COMPLETE': True,
        'OVERALL_SUCCESS': compare['OVERALL_SUCCESS'],
        'CIRCLE_ORACLE_COUNT': stats['TRAIN_CIRCLE_COUNT'],
        'EXTRUDE_ORACLE_COUNT': stats['TRAIN_EXTRUDE_COUNT'],
        'BOX_ORACLE_COUNT': stats['TRAIN_BOX_COUNT'],
        'LLM_CIRCLE_RADIUS_MEDIAN': common['LLM']['circle_radius_abs']['median'],
        'HEAD_CIRCLE_RADIUS_MEDIAN': common['HEAD']['circle_radius_abs']['median'],
        'LLM_EXTRUDE_ORIGIN_MEDIAN': common['LLM']['extrude_origin']['median'],
        'HEAD_EXTRUDE_ORIGIN_MEDIAN': common['HEAD']['extrude_origin']['median'],
        'LLM_EXTRUDE_DEPTH_MEDIAN': common['LLM']['extrude_depth_abs']['median'],
        'HEAD_EXTRUDE_DEPTH_MEDIAN': common['HEAD']['extrude_depth_abs']['median'],
        'LLM_BOX_ORIGIN_MEDIAN': common['LLM']['box_origin']['median'],
        'HEAD_BOX_ORIGIN_MEDIAN': common['HEAD']['box_origin']['median'],
        'LLM_COMMON_VALID_CHAMFER': compare['LLM_COMMON_VALID_CHAMFER'],
        'HEAD_COMMON_VALID_CHAMFER': compare['HEAD_COMMON_VALID_CHAMFER'],
        'LLM_STEP': compare['LLM_STEP'], 'HEAD_STEP': compare['HEAD_STEP'],
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    report = {
        **final_values,
        'EXPERIMENT': 'PARAMETER_HEAD_ORACLE_V1',
        'BEST_BACKBONE': 'A3_ANCHOR_Q32', 'BEST_EPOCH': 7,
        'BEST_CHECKPOINT': str(CHECKPOINT), 'BEST_CHECKPOINT_SHA256': CHECKPOINT_SHA256,
        'HEAD_CHECKPOINT': str(OUTPUT_ROOT / 'train800/checkpoint_final.pt'),
        'HEAD_EPOCH': train['EPOCHS'],
        'TRAIN800_SOURCE_CAD_COUNT': 800,
        'ORACLE_AVAILABLE_TRAIN_CAD_COUNT': train['CAD_COUNT'],
        'ORACLE_INSTANCE_COUNTS': train['INSTANCE_COUNTS'],
        'DEV_COMMON_PARAMETER_COUNTS': params['COMMON_COUNTS'],
        'COMMON_VALID_CAD_COUNT': geom['COMMON_VALID_COUNT'],
        'PARAMETER_PASS': compare['PARAMETER_PASS'], 'GEOMETRY_PASS': compare['GEOMETRY_PASS'],
        'CONCLUSION': 'Experiment completed, but the Parameter Head did not satisfy the frozen HEAD-vs-LLM success criterion.',
        'FAILURE_ANALYSIS': compare['FAILURE_ANALYSIS'],
        'INTEGRITY_GATE': integrity,
    }
    write('TRAINING_REPORT.json', report)

    base_config = {
        'INPUT_DIM': 262, 'C2_DIM': 256, 'SPATIAL_ANCHOR_DIM': 6,
        'HIDDEN_DIM': 256, 'NORMALIZATION_CONTRACT': 'PARAMETER_NORMALIZATION_CONTRACT.json',
        'BACKBONE_FROZEN': True, 'BEST_CHECKPOINT_SHA256': CHECKPOINT_SHA256,
    }
    write('CIRCLE_HEAD_CONFIG.json', {**base_config, 'HEAD': 'CircleParameterHead', 'AGGREGATOR': None, 'OUTPUTS': ['center_xyz', 'radius_softplus', 'normal_unit'], 'LOSS': ['center_SmoothL1', 'radius_SmoothL1', 'normal_n_sign_invariant_angular']})
    write('EXTRUDE_HEAD_CONFIG.json', {**base_config, 'HEAD': 'ExtrudeParameterHead', 'AGGREGATOR': {'type': 'MultiheadAttention', 'heads': 4, 'oracle_profile_tokens': 'all_exact_mapped_tokens'}, 'OUTPUTS': ['origin_xyz', 'direction_unit', 'depth_signed', 'height_two_signed'], 'LOSS': ['origin_SmoothL1', 'direction_angular', 'depth_SmoothL1', 'height_two_SmoothL1']})
    write('BOX_HEAD_CONFIG.json', {**base_config, 'HEAD': 'BoxParameterHead', 'AGGREGATOR': {'type': 'MultiheadAttention', 'heads': 4, 'oracle_edge_tokens': 12}, 'OUTPUTS': ['origin_xyz', 'extent_width_positive', 'extent_depth_positive', 'extent_height_signed'], 'LOSS': ['origin_SmoothL1', 'extent_SmoothL1']})
    write('FINAL_GATE.json', final_values)

    manifest_targets = [
        *(OUTPUT_ROOT / name for name in required), OUTPUT_ROOT / 'DATASET_PARAMETER_STATS.json',
        OUTPUT_ROOT / 'TRAINING_REPORT.json', OUTPUT_ROOT / 'CIRCLE_HEAD_CONFIG.json',
        OUTPUT_ROOT / 'EXTRUDE_HEAD_CONFIG.json', OUTPUT_ROOT / 'BOX_HEAD_CONFIG.json',
        OUTPUT_ROOT / 'FINAL_GATE.json', OUTPUT_ROOT / 'train800/TRAIN_REPORT.json',
        OUTPUT_ROOT / 'train800/checkpoint_final.pt', *epoch_checkpoints,
        *(sorted(CODE_ROOT.glob('*.py'))), EXECUTOR,
    ]
    entries = [{'path': str(path), 'sha256': sha256(path), 'bytes': path.stat().st_size} for path in manifest_targets]
    manifest = {
        'EXPERIMENT': 'PARAMETER_HEAD_ORACLE_V1', 'HASH_ALGORITHM': 'SHA256',
        'BEST_CHECKPOINT_PATH': str(CHECKPOINT), 'BEST_CHECKPOINT_TREE_SHA256': CHECKPOINT_SHA256,
        'EXECUTOR_PATH': str(EXECUTOR), 'EXECUTOR_SHA256': EXECUTOR_SHA256,
        'FILE_COUNT': len(entries), 'FILES': entries,
        'ANCHOR_EVAL_100_READ': False, 'PILOT150_READ': False, 'OFFICIAL_TEST_READ': False,
    }
    write('FILE_SHA256_MANIFEST.json', manifest)
    print(json.dumps(final_values, indent=2))


if __name__ == '__main__':
    main()
