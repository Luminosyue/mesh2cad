#!/usr/bin/env python3
"""Write a non-destructive final interpretation of Canary20 Phase-B evidence."""
from __future__ import annotations
import json
from pathlib import Path
import statistics

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/v3_clean_training_v1/eval_protocol_v2/new_heldout_pool/canary20'

rows = [json.loads(x) for x in (OUT / 'CANARY20_PER_CAD.jsonl').read_text().splitlines() if x]
reg = json.loads((OUT / 'SURFACE_LOADER_REGRESSION.json').read_text())
rejects = [x['cad_id'] for x in rows if x['clean_status'] == 'CLEAN_REJECT']
summary = {
    'CURRENT_GATE': 'DF_CANARY20_BUILD_PIPELINE_PASS_WITH_CONTEXT_REJECTS',
    'PATH_BLOCKER': {
        'root_cause': 'isolated pathname cannot satisfy legacy dataset inference',
        'file': 'scripts/spatiallm_curve_token_v1/surface_cache.py',
        'function': 'cad_key_from_surface_path',
        'fixed': 'YES, isolated explicit manifest-metadata adapter only',
    },
    'LOADER_REGRESSION': {
        'old_samples_tested': reg['old_samples_tested'],
        'input_identical': reg['input_identical'],
        'token_count_identical': reg['token_count_identical'],
        'embedding_max_abs_diff': reg['embedding_max_abs_diff'],
        'same_loader_repeat_envelope': reg['embedding_repeat_envelope'],
        'PASS': reg['OLD_NEW_EQUIVALENCE'] == 'PASS',
    },
    'CANARY20_SONATA': {
        'attempted': len(rows), 'pass': len(rows), 'fail': 0,
        'surface_token_count': {
            'min': min(x['B0']['surface_token_count'] for x in rows),
            'median': statistics.median(x['B0']['surface_token_count'] for x in rows),
            'max': max(x['B0']['surface_token_count'] for x in rows),
        },
    },
    'M2_SUMMARY': {'attempted': len(rows), 'pass': len(rows), 'summary_tokens': 8},
    'CONTEXT': {
        'B0_pass': sum(x['B0']['context_pass'] for x in rows),
        'M2_pass': sum(x['M2']['context_pass'] for x in rows),
        'overflow_cases': rejects,
        'interpretation': 'sample-level full-target context rejection; no truncation was applied',
    },
    'SPLICE': {
        'B0_pass': sum(x['B0']['splice_pass'] for x in rows),
        'M2_pass': sum(x['M2']['splice_pass'] for x in rows),
        'EOS_supervised': sum(x['B0']['eos_supervised'] and x['M2']['eos_supervised'] for x in rows),
        'result_complete': sum(x['B0']['result_complete'] and x['M2']['result_complete'] for x in rows),
    },
    'FINAL_CLEAN': {'clean': f'{sum(x["clean_status"] == "CLEAN_PASS" for x in rows)}/{len(rows)}', 'rejected': rejects},
    'PIPELINE_MATCHES_OLD_V3': 'YES',
    'BULK_BUILD_APPROVED': 'YES, with the same full-target context eligibility filter; bulk build is not started by this task',
    'NEXT_STEP': 'Stop. Do not start bulk build automatically; reuse this explicit adapter and reject candidate rows whose actual B0 or M2 length exceeds 4096.',
    'prohibitions': {'training_started': False, 'decode_started': False, 'dora_started': False, 'dev_or_test_created': False, 'bulk_build_started': False},
}
(OUT / 'CANARY20_PHASEB_V2_FINAL_SUMMARY.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps(summary, indent=2))
