#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

root = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/parameter_head_oracle_v1/parameter_replacement_causality_audit_v1')
required = [
    'PARAMETER_FIELD_DIFF.jsonl', 'DSL_REPLACEMENT_AUDIT.json',
    'EXECUTOR_PARAMETER_SEMANTICS.json', 'SINGLE_PARAMETER_PERTURBATION.json',
    'OCC_CAUSALITY_AUDIT.json', 'FRESH_GEOMETRY_METRICS.json',
    'CACHE_ISOLATION_AUDIT.json', 'FILE_SHA256_MANIFEST.json',
]
assert all((root / name).is_file() for name in required)
audit = json.loads((root / 'DSL_REPLACEMENT_AUDIT.json').read_text())
assert audit['REPLACEMENT_PIPELINE_BUG'] and len(audit['SELECTED_CAD_IDS']) == 10
assert audit['MISMATCH_COUNT'] > 0
manifest = json.loads((root / 'FILE_SHA256_MANIFEST.json').read_text())
for entry in manifest['FILES']:
    actual = hashlib.sha256(Path(entry['path']).read_bytes()).hexdigest()
    assert actual == entry['sha256'], entry['path']
print('FINAL_AUDIT=PASS')
print('CURRENT_GATE=' + audit['CURRENT_GATE'])
print('FIELD_RECORD_COUNT=' + str(audit['FIELD_RECORD_COUNT']))
print('MISMATCH_COUNT=' + str(audit['MISMATCH_COUNT']))
print('MANIFEST_FILE_COUNT=' + str(manifest['FILE_COUNT']))
