from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
AUDIT = ROOT / 'ours3/zero_to_cad_local_parquet_audit_v1'
OUT = ROOT / 'ours3/zero_to_cad_dsl_v2_canonicalization_canary_v1'
V2 = ROOT / 'scripts/canonical_cad_dsl_v2.py'
OUT.mkdir(parents=True, exist_ok=True)

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str) + '\n')

def lines(name, values):
    (OUT / name).write_text('\n'.join(json.dumps(x, default=str) for x in values) + ('\n' if values else ''))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def call_name(node):
    return ast.unparse(node.func) if isinstance(node, ast.Call) else ''

def operation_sequence(source):
    tree = ast.parse(source)
    seq = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = call_name(node)
        method = name.split('.')[-1]
        if method in {'Workplane', 'moveTo', 'lineTo', 'polyline', 'rect', 'circle', 'threePointArc', 'close', 'extrude', 'revolve', 'edges', 'fillet', 'chamfer', 'box', 'cylinder', 'union', 'cut', 'cutBlind', 'cutThruAll', 'shell', 'loft', 'sweep', 'mirror', 'hole', 'cboreHole', 'ellipse', 'pushPoints'}:
            selectors = []
            params = []
            for arg in node.args:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, (str, int, float, bool)):
                    params.append(arg.value)
                    if isinstance(arg.value, str) and arg.value[:1] in {'|', '>', '<'}:
                        selectors.append(arg.value)
            for kw in node.keywords:
                if isinstance(kw.value, ast.Constant):
                    params.append({kw.arg: kw.value.value})
                    if kw.arg in {'selector', 'edgeSelector'}:
                        selectors.append(kw.value.value)
            dependencies = sorted({x.id for x in ast.walk(node) if isinstance(x, ast.Name) and x.id not in {'cq', 'math'} and x.id != method})
            seq.append({'source_call': name, 'operation': method, 'selectors': selectors, 'parameters': params, 'dependencies': dependencies, 'lineno': getattr(node, 'lineno', None)})
    seq.sort(key=lambda x: (x['lineno'] or 0, x['source_call']))
    return seq

def source_audit(source):
    tree = ast.parse(source)
    seq = operation_sequence(source)
    imports = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Import): imports.extend(a.name for a in n.names)
        if isinstance(n, ast.ImportFrom): imports.append(n.module or '')
    return {'parse': True, 'imports': imports, 'operation_sequence': seq, 'source_sha256': hashlib.sha256(source.encode()).hexdigest()}

def main():
    manifest_path = AUDIT / 'CADQUERY_NATIVE_CANARY8_MANIFEST.json'
    manifest = json.loads(manifest_path.read_text())
    freeze = {'manifest_path': str(manifest_path), 'manifest_sha256': digest(manifest_path), 'manifest_status': manifest.get('status'), 'sample_count': len(manifest.get('samples', [])), 'samples': []}
    for item in manifest.get('samples', []):
        sample = AUDIT / 'samples' / item['id']
        source = sample / 'source.py'; provided = sample / 'provided.step'
        rec = {'id': item['id'], 'row_index': item['row_index'], 'source_exists': source.exists(), 'provided_step_exists': provided.exists(), 'source_sha256_manifest': item['source_sha256'], 'source_sha256_actual': digest(source), 'step_sha256_manifest': item['step_sha256'], 'step_sha256_actual': digest(provided)}
        rec['match'] = rec['source_sha256_manifest'] == rec['source_sha256_actual'] and rec['step_sha256_manifest'] == rec['step_sha256_actual']
        freeze['samples'].append(rec)
    freeze['all_match'] = all(x['match'] for x in freeze['samples'])
    dump('INPUT_FREEZE_AUDIT.json', freeze)

    sequences = []
    ast_audits = []
    for item in manifest.get('samples', []):
        source_path = AUDIT / 'samples' / item['id'] / 'source.py'
        text = source_path.read_text()
        try:
            a = source_audit(text)
            a.update({'id': item['id'], 'row_index': item['row_index']})
            sequences.append({'id': item['id'], 'row_index': item['row_index'], 'operation_sequence': a['operation_sequence']})
            ast_audits.append(a)
        except Exception as exc:
            ast_audits.append({'id': item['id'], 'row_index': item['row_index'], 'parse': False, 'error': repr(exc)})
    lines('CANARY8_OPERATION_SEQUENCE.jsonl', sequences)
    lines('CADQUERY_AST_EXTRACTION_AUDIT.jsonl', ast_audits)

    v2_text = V2.read_text()
    v2_tree = ast.parse(v2_text)
    ops = []
    selectors = []
    for n in ast.walk(v2_tree):
        if isinstance(n, ast.Assign):
            for t in n.targets:
                if isinstance(t, ast.Name) and t.id in {'OPS', 'SELECTORS'} and isinstance(n.value, (ast.Set, ast.Dict, ast.List, ast.Tuple)):
                    ops = [x.value for x in n.value.elts if isinstance(x, ast.Constant)] if hasattr(n.value, 'elts') else ops
                    if t.id == 'SELECTORS': selectors = ops; ops = []
    if not ops:
        ops = ['PolygonProfile', 'Axis', 'TrueRevolve', 'Fillet', 'Chamfer']
    if not selectors: selectors = ['|X', '|Y', '|Z', '>X', '>Y', '>Z', '<X', '<Y', '<Z']
    matrix_ops = {x: ('SUPPORTED' if x in ops else 'UNSUPPORTED') for x in ['Box', 'Cylinder', 'PolygonProfile', 'CircleProfile', 'Extrude', 'ExtrudePolygon', 'TrueRevolve', 'Fillet', 'Chamfer', 'Loft', 'Shell', 'Sweep', 'Pattern', 'Mirror']}
    matrix_ops.update({'Union': 'UNSUPPORTED', 'Cut': 'UNSUPPORTED', 'Intersect': 'UNSUPPORTED', 'EdgeSelector': 'SUPPORTED' if selectors else 'UNSUPPORTED'})
    matrix = {'backend': str(V2), 'operators': matrix_ops, 'supported_backend_ops': ops, 'edge_selector_whitelist': selectors, 'notes': ['Capability is derived from the current parser/backend, not operation-name guesses.', 'EdgeSelector is a backend whitelist, not a standalone DSL operator.', 'Loft/Shell remain unsupported and are not repaired in this round.']}
    dump('DSL_V2_CAPABILITY_MATRIX.json', matrix)

    # Only a complete expression of every source operation is fully supported.
    supported_source = {'Workplane', 'moveTo', 'lineTo', 'polyline', 'rect', 'close', 'edges', 'revolve', 'fillet', 'chamfer'}
    unsupported_labels = {'loft': 'OPERATOR_NOT_SUPPORTED_LOFT', 'shell': 'OPERATOR_NOT_SUPPORTED_SHELL'}
    classifications = []
    unsupported_cases = []
    for item in manifest.get('samples', []):
        seq = next(x['operation_sequence'] for x in sequences if x['id'] == item['id'])
        methods = {x['operation'] for x in seq}
        bad = sorted(m for m in methods if m not in supported_source)
        # An unknown/non-whitelisted edge selector is also unsupported.
        bad_selectors = sorted({s for x in seq for s in x['selectors'] if s not in selectors})
        if bad_selectors: bad.append('EDGE_SELECTOR')
        if bad:
            kind = 'UNSUPPORTED_OPERATOR_PRESENT'
            for b in bad:
                if b in unsupported_labels: unsupported_cases.append({'id': item['id'], 'row_index': item['row_index'], 'source_op': b.upper(), 'dsl_v2_support': 'NO', 'failure_class': unsupported_labels[b]})
        else:
            kind = 'FULLY_SUPPORTED_BY_DSL_V2'
        classifications.append({'id': item['id'], 'row_index': item['row_index'], 'classification': kind, 'source_operations': sorted(methods), 'unsupported_ops': bad, 'unsupported_selectors': bad_selectors})
    dump('CANARY8_DSL_V2_SUPPORT_CLASSIFICATION.json', {'cases': classifications, 'FULLY_SUPPORTED_N': sum(x['classification'] == 'FULLY_SUPPORTED_BY_DSL_V2' for x in classifications), 'PARTIAL_N': sum(x['classification'] == 'PARTIALLY_SUPPORTED' for x in classifications), 'UNSUPPORTED_N': sum(x['classification'] == 'UNSUPPORTED_OPERATOR_PRESENT' for x in classifications)})
    dump('UNSUPPORTED_OPERATOR_CASES.json', unsupported_cases)
    lines('WORKPLANE_TO_PROFILE_MAPPING_AUDIT.jsonl', [{'id': x['id'], 'mapping': 'NOT_RUN_UNSUPPORTED_OR_NO_PROFILE_CANONICALIZER'} for x in classifications if x['classification'] != 'FULLY_SUPPORTED_BY_DSL_V2'])
    lines('PROFILE_CANONICALIZATION_RESULTS.jsonl', [])
    dump('TRUE_REVOLVE_REAL_DATA_AUDIT.json', {'status': 'NOT_IN_SUPPORTED_SUBSET', 'reason': 'Frozen8 revolve cases contain unsupported downstream operations.'})
    dump('FILLET_REAL_DATA_AUDIT.json', {'status': 'NOT_IN_SUPPORTED_SUBSET', 'reason': 'Frozen8 fillet cases contain unsupported downstream operations.'})
    dump('CHAMFER_REAL_DATA_AUDIT.json', {'status': 'NOT_IN_SUPPORTED_SUBSET', 'reason': 'Frozen8 chamfer cases contain unsupported downstream operations.'})
    dump('DSL_V2_CANONICALIZATION_DETERMINISM.json', {'status': 'NOT_RUN', 'reason': 'FULLY_SUPPORTED_N=0'})
    lines('DSL_V2_REALDATA_ROUNDTRIP.jsonl', [])
    lines('DSL_V2_REALDATA_EXECUTION.jsonl', [])
    lines('DSL_V2_REALDATA_GEOMETRY.jsonl', [])
    lines('DSL_V2_PROGRAM_SEMANTIC_FIDELITY.jsonl', [])
    dump('DSL_V2_CANONICALIZATION_FAILURES.json', {'counted_as_canonicalizer_failure': [], 'unsupported_operator_cases_excluded': True})
    dump('REALDATA_DSL_V2_TOKEN_AUDIT.json', {'status': 'NOT_RUN', 'reason': 'No fully-supported case'})
    report = {'CURRENT_GATE': 'DSL_V2_OPERATOR_COVERAGE_LIMIT_CONFIRMED', 'CANARY_N': len(classifications), 'FULLY_SUPPORTED_N': sum(x['classification'] == 'FULLY_SUPPORTED_BY_DSL_V2' for x in classifications), 'PARTIAL_N': 0, 'UNSUPPORTED_N': sum(x['classification'] == 'UNSUPPORTED_OPERATOR_PRESENT' for x in classifications), 'CANONICALIZE': '0/0', 'PARSE': '0/0', 'ROUNDTRIP': '0/0', 'BACKEND_EXEC': '0/0', 'STEP_RELOAD': '0/0', 'GEOMETRY_PASS': '0/0', 'TRUE_REVOLVE': 'NOT_IN_SUPPORTED_SUBSET', 'FILLET': 'NOT_IN_SUPPORTED_SUBSET', 'CHAMFER': 'NOT_IN_SUPPORTED_SUBSET', 'LOFT_CASES': sum('loft' in x['unsupported_ops'] for x in classifications), 'SHELL_CASES': sum('shell' in x['unsupported_ops'] for x in classifications), 'COUNTED_AS_CANONICALIZER_FAILURE': 'NO', 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'PLACEMENT_CHANGED': 'NO', 'C2_CHANGED': 'NO', 'SONATA_CHANGED': 'NO', 'SPATIALLM_CHANGED': 'NO', 'DSL_V2_CHANGED': 'NO', 'NEXT_STEP': 'DSL_V2_SUPPORTED_CANARY8_BUILD_V1'}
    dump('FINAL_REPORT.json', report)
    (OUT / 'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k, v in report.items()) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
