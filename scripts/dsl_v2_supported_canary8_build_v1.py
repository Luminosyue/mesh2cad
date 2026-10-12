from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
PARQUET = ROOT / 'zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet'
POOL_PATH = ROOT / 'ours3/canonical_cad_dsl_v2_base_operator_integration_canary_v1/UNIFIED_DSL_V2_SUPPORTED_POOL.json'
OUT = ROOT / 'ours3/dsl_v2_supported_canary8_build_and_canonicalization_v1'
SAMPLES = OUT / 'samples'
OUT.mkdir(parents=True, exist_ok=True)

def sha(data): return hashlib.sha256(data).hexdigest()
def dump(name, x): (OUT / name).write_text(json.dumps(x, indent=2, default=str) + '\n')
def calls(text):
    tree = ast.parse(text)
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            name = ast.unparse(n.func)
            method = name.split('.')[-1]
            selectors = [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value[:1] in {'|','>','<'}]
            out.append({'operation': method, 'source_call': name, 'selectors': selectors, 'lineno': getattr(n, 'lineno', 0), 'argc': len(n.args)})
    return sorted(out, key=lambda x: (x['lineno'], x['source_call']))

def main():
    pool = json.loads(POOL_PATH.read_text())
    pool_ids = {x['id']: x for x in pool['cases']}
    rows = pq.read_table(PARQUET, columns=['uuid','cadquery_file','step_file']).to_pylist()
    by_id = {str(x['uuid']): x for x in rows}
    reaudited = []
    for ident, old in pool_ids.items():
        row = by_id[ident]; source = row['cadquery_file']; step = row['step_file']; text = source.decode('utf-8','replace'); seq = calls(text)
        methods = sorted({x['operation'] for x in seq})
        selectors = sorted({s for x in seq for s in x['selectors']})
        explicit_edge_use = all(x['argc'] > 0 for x in seq if x['operation'] == 'edges')
        supported_source = {'Workplane','moveTo','lineTo','polyline','rect','circle','close','edges','revolve','fillet','chamfer','box','cylinder','extrude','cut','union'}
        unsupported_source_methods = sorted(set(methods) - supported_source)
        rec = {'row_index': old['row_index'], 'id': ident, 'operations': methods, 'operation_count': len(seq), 'has_extrude': 'extrude' in methods, 'has_boolean': bool({'cut','union'} & set(methods)), 'has_revolve': 'revolve' in methods, 'has_fillet': 'fillet' in methods, 'has_chamfer': 'chamfer' in methods, 'selectors': selectors, 'explicit_edge_use': explicit_edge_use, 'unsupported_source_methods': unsupported_source_methods, 'source_sha256': sha(source), 'step_sha256': sha(step)}
        reaudited.append(rec)
    dump('SUPPORTED63_REAUDIT.json', {'pool_path': str(POOL_PATH), 'pool_sha256': sha(POOL_PATH.read_bytes()), 'count': len(reaudited), 'records': reaudited, 'classification_error': [x for x in reaudited if x['operations'] != pool_ids[x['id']]['operations']]})
    def eligible(x):
        return not x['unsupported_source_methods'] and (x['explicit_edge_use'] or not (x['has_fillet'] or x['has_chamfer']))
    def score(x): return (-x['operation_count'], x['row_index'], x['id'])
    groups = {
        'EXTRUDE_BOOLEAN': lambda x: x['has_extrude'] and x['has_boolean'],
        'TRUE_REVOLVE': lambda x: x['has_revolve'],
        'FILLET': lambda x: x['has_fillet'],
        'CHAMFER': lambda x: x['has_chamfer'],
    }
    dist = {k: sum(bool(fn(x)) for x in reaudited) for k, fn in groups.items()}
    dist.update({'PURE_EXTRUDE': sum(x['operations'] == ['Workplane','extrude'] for x in reaudited), 'MULTI_OP': sum(x['operation_count'] >= 2 for x in reaudited), 'COMPLEX_MULTI_OP': sum(x['operation_count'] >= 3 for x in reaudited), 'POOL_N': len(reaudited)})
    dump('SUPPORTED63_OPERATION_DISTRIBUTION.json', dist)
    selected = []
    reasons = [('EXTRUDE_BOOLEAN', groups['EXTRUDE_BOOLEAN']), ('TRUE_REVOLVE', groups['TRUE_REVOLVE']), ('FILLET', groups['FILLET']), ('CHAMFER', groups['CHAMFER'])]
    for label, fn in reasons:
        choices = sorted([x for x in reaudited if fn(x) and eligible(x)], key=score)
        for x in choices:
            if x['id'] not in {y['id'] for y in selected}:
                x = dict(x); x['selection_reason'] = label + ': complexity desc, then row_index, uuid; explicit edge selector required'; selected.append(x); break
        for x in choices:
            if len([y for y in selected if y['selection_reason'].startswith(label)]) < 2 and x['id'] not in {y['id'] for y in selected}:
                y = dict(x); y['selection_reason'] = label + ': second diversity slot'; selected.append(y)
    for x in sorted([x for x in reaudited if eligible(x)], key=score):
        if len(selected) >= 8: break
        if x['id'] not in {y['id'] for y in selected}:
            y = dict(x); y['selection_reason'] = 'diversity fill: complexity desc, then row_index, uuid'; selected.append(y)
    selected = selected[:8]
    manifest_records = []
    for x in selected:
        row = by_id[x['id']]; sample = SAMPLES / x['id']; sample.mkdir(parents=True, exist_ok=True)
        (sample / 'source.py').write_bytes(row['cadquery_file']); (sample / 'provided.step').write_bytes(row['step_file'])
        rec = {'cad_id': x['id'], 'uuid': x['id'], 'row_index': x['row_index'], 'source_ops': x['operations'], 'operation_count': x['operation_count'], 'complexity_tag': 'COMPLEX_MULTI_OP' if x['operation_count'] >= 3 else 'MULTI_OP', 'source_path': str(sample/'source.py'), 'provided_step_path': str(sample/'provided.step'), 'source_sha256': x['source_sha256'], 'step_sha256': x['step_sha256'], 'selection_reason': x['selection_reason']}
        (sample / 'metadata.json').write_text(json.dumps(rec, indent=2) + '\n'); manifest_records.append(rec)
    manifest = {'manifest': 'DSL_V2_SUPPORTED_CANARY8_MANIFEST', 'version': 1, 'status': 'FROZEN' if len(manifest_records) == 8 else 'INCOMPLETE_SUPPORTED_COHORT', 'parquet_path': str(PARQUET), 'parquet_sha256': sha(PARQUET.read_bytes()), 'pool_path': str(POOL_PATH), 'pool_sha256': sha(POOL_PATH.read_bytes()), 'canary_n': len(manifest_records), 'records': manifest_records, 'freeze_allowed': len(manifest_records) == 8}
    dump('DSL_V2_SUPPORTED_CANARY8_MANIFEST.json', manifest); dump('COHORT_SHA256', {'manifest_sha256': sha((OUT/'DSL_V2_SUPPORTED_CANARY8_MANIFEST.json').read_bytes()), 'record_sha256': sha(json.dumps(manifest_records, sort_keys=True).encode())})
    report = {'CURRENT_GATE': 'DSL_V2_SUPPORTED_CANARY8_BUILD_PASS' if len(manifest_records) == 8 else 'DSL_V2_DATA_COVERAGE_STILL_LOW', 'SUPPORTED_POOL_DECLARED_N': len(reaudited), 'POOL_CLASSIFICATION_ERROR_N': len([x for x in reaudited if x['unsupported_source_methods']]), 'STRICT_ELIGIBLE_N': sum(eligible(x) for x in reaudited), 'CANARY_N': len(manifest_records), 'TRUE_REVOLVE_CASES': sum('revolve' in x['source_ops'] for x in manifest_records), 'FILLET_CASES': sum('fillet' in x['source_ops'] for x in manifest_records), 'CHAMFER_CASES': sum('chamfer' in x['source_ops'] for x in manifest_records), 'BOOLEAN_CASES': sum(bool({'cut','union'} & set(x['source_ops'])) for x in manifest_records), 'MULTI_OP_CASES': sum(x['operation_count'] >= 2 for x in manifest_records), 'COHORT_SHA256': sha((OUT/'DSL_V2_SUPPORTED_CANARY8_MANIFEST.json').read_bytes()), 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'PLACEMENT_CHANGED': 'NO', 'C2_CHANGED': 'NO', 'SONATA_CHANGED': 'NO', 'SPATIALLM_CHANGED': 'NO', 'DSL_V2_CHANGED': 'NO', 'NEXT_STEP': 'DSL_V2_SUPPORTED_CANARY8_BUILD_V1_REAUDIT_OR_OPERATOR_MAPPING_SCOPE_REVIEW' if len(manifest_records) < 8 else 'DSL_V2_CANONICALIZATION'}
    dump('FINAL_REPORT.json', report); (OUT / 'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k, v in report.items()) + '\n')
    print(json.dumps({'report': report, 'distribution': dist, 'selected': manifest_records}, indent=2))

if __name__ == '__main__': main()
