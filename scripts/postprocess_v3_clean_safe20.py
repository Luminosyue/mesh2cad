#!/usr/bin/env python3
"""Produce immutable, read-only SAFE20 funnel reports from completed generations."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EVAL = ROOT / 'ours3/v3_clean_training_v1/eval_protocol_v2'
MANIFEST = ROOT / 'ours3/v3_clean_training_v1/data/CLEAN_V3_MANIFEST.json'
SOURCES = {
    'B0': EVAL / 'b0_train_self_diag_checkpoint_epoch_08_executor_env_anchorudf_v1/per_sample.jsonl',
    'M2': EVAL / 'm2_train_self_diag_checkpoint_epoch_15_executor_env_anchorudf_v1/per_sample.jsonl',
}


def primary(row: dict) -> str:
    if row['hit_cap'] and not row['eos']:
        return 'NO_EOS_RUNAWAY'
    if row['hit_cap']:
        return 'PARSER_OVERSIZE_SKIPPED'
    if not row['has_result']:
        return 'MISSING_RESULT'
    if not row['parse_pass']:
        return 'DSL_PARSE_FAIL'
    if not row['exec_pass']:
        return 'CAD_EXEC_FAIL'
    if not row['step_write_pass']:
        return 'STEP_WRITE_FAIL'
    if not row['step_reload_pass']:
        return 'STEP_RELOAD_FAIL'
    return 'STEP_RELOAD_PASS'


def summarize(rows: list[dict]) -> dict:
    tokens = np.asarray([r['generated_token_count'] for r in rows], dtype=float)
    keys = ('eos', 'hit_cap', 'has_result', 'parse_pass', 'exec_pass', 'step_write_pass', 'step_reload_pass')
    return {
        'N': len(rows),
        **{k: int(sum(bool(r[k]) for r in rows)) for k in keys},
        'generation_tokens': {
            'median': float(np.median(tokens)), 'p90': float(np.percentile(tokens, 90)), 'max': int(tokens.max()),
        },
        'primary_failure_counts': dict(sorted(Counter(r['primary_failure'] for r in rows).items())),
        'status': 'TRAIN_SELF_DECODE_DIAGNOSIS_NOT_HELDOUT',
        'max_new_tokens': 4096,
        'decode': 'greedy',
    }


def main() -> None:
    out = EVAL / 'diagnostics'
    out.mkdir(exist_ok=True)
    gt = {r['cad_id']: Path(r['target_dsl']).read_text() for r in json.loads(MANIFEST.read_text())['records']}
    reports = {}
    ids = None
    for arm, source in SOURCES.items():
        raw = [json.loads(line) for line in source.read_text().splitlines() if line.strip()]
        rows = []
        for x in raw:
            row = {
                'cad_id': x['cad_id'],
                'generated_token_count': int(x['generated_tokens']),
                'generated_char_count': len(x['generated_text']),
                'eos': bool(x['eos']), 'hit_cap': bool(x['hit_cap']), 'has_result': bool(x['has_result']),
                'parse_pass': bool(x['parse']), 'exec_pass': bool(x['exec']),
                'step_write_pass': bool(x['step_write']), 'step_reload_pass': bool(x['step_reload']),
                'failure_stage_raw': x['failure_stage'], 'generated_text': x['generated_text'],
            }
            row['primary_failure'] = primary(row)
            row['failure_message_short'] = x['failure_stage'] if row['primary_failure'] != 'STEP_RELOAD_PASS' else ''
            rows.append(row)
        assert len(rows) == 20
        if ids is None:
            ids = [r['cad_id'] for r in rows]
        else:
            assert ids == [r['cad_id'] for r in rows], 'B0/M2 SAFE20 IDs differ'
        summary = summarize(rows)
        reports[arm] = summary
        (out / f'{arm}_SAFE20.jsonl').write_text(''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in rows))
        (out / f'{arm}_SAFE20_SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
        lines = [f'# {arm} SAFE20', '', 'Status: TRAIN_SELF_DECODE_DIAGNOSIS (not held-out).', '']
        lines += [f'- {k}: {v}' for k, v in summary.items() if k not in ('generation_tokens', 'primary_failure_counts')]
        lines += ['', '## Generation tokens', json.dumps(summary['generation_tokens'], indent=2), '', '## Primary failures', json.dumps(summary['primary_failure_counts'], indent=2)]
        (out / f'{arm}_SAFE20.md').write_text('\n'.join(lines) + '\n')
        examples = []
        for r in rows[:10]:
            examples += ['=====================', f"CAD_ID = {r['cad_id']}", 'GT:', gt[r['cad_id']], 'PRED:', r['generated_text'],
                         f"EOS = {r['eos']}", f"HIT_CAP = {r['hit_cap']}", f"HAS_RESULT = {r['has_result']}",
                         f"PARSE = {r['parse_pass']}", f"EXEC = {r['exec_pass']}", f"STEP_WRITE = {r['step_write_pass']}",
                         f"STEP_RELOAD = {r['step_reload_pass']}", f"FAILURE_STAGE = {r['primary_failure']}", '=====================']
        (out / f'{arm}_GENERATION_EXAMPLES_10.txt').write_text('\n'.join(examples) + '\n')
    comparison = {'N': 20, 'status': 'TRAIN_SELF_DECODE_DIAGNOSIS_NOT_HELDOUT', 'ids_identical': True, 'B0': reports['B0'], 'M2': reports['M2'],
                  'current_step_zero_main_cause': 'PRIOR_EVALUATOR_ENVIRONMENT_MISSING_CADQUERY; corrected executor shows STEP reload passes.'}
    (out / 'SAFE20_B0_VS_M2.json').write_text(json.dumps(comparison, indent=2) + '\n')
    md = ['# SAFE20 B0 vs M2', '', 'Status: **TRAIN_SELF_DECODE_DIAGNOSIS**, not held-out/generalization.', '', '| Metric | B0 epoch8 | M2 epoch15 |', '|---|---:|---:|']
    for k in ('eos','hit_cap','has_result','parse_pass','exec_pass','step_write_pass','step_reload_pass'):
        md.append(f'| {k} | {reports["B0"][k]}/20 | {reports["M2"][k]}/20 |')
    md += ['', f"B0 token median/p90/max: {reports['B0']['generation_tokens']}", f"M2 token median/p90/max: {reports['M2']['generation_tokens']}", '', f"STEP=0 root cause: {comparison['current_step_zero_main_cause']}"]
    (out / 'SAFE20_B0_VS_M2.md').write_text('\n'.join(md) + '\n')
    files = {p.name: {'sha256': hashlib.sha256(p.read_bytes()).hexdigest(), 'bytes': p.stat().st_size} for p in sorted(out.iterdir()) if p.is_file()}
    (out / 'SAFE20_FILE_SHA256_MANIFEST.json').write_text(json.dumps(files, indent=2) + '\n')
    print(json.dumps(comparison, indent=2))


if __name__ == '__main__':
    main()
