from __future__ import annotations

import ast
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

PARQUET = Path('/data/home/cuiyuehan/project/mesh2cad/zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet')
OUT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3/zero_to_cad_local_parquet_audit_v1')
SAMPLES = OUT / 'samples'

DIRECT_NAMES = {'Workplane', 'Sketch', 'box', 'cylinder', 'sphere', 'rect', 'circle', 'polyline', 'polygon', 'moveTo', 'lineTo', 'threePointArc', 'close', 'extrude', 'revolve', 'loft', 'sweep', 'shell', 'fillet', 'chamfer', 'cut', 'union', 'intersect'}
FORBIDDEN_NAMES = {'eval', 'exec', 'compile', '__import__', 'open', 'system', 'popen', 'run', 'call', 'check_call', 'check_output', 'urlopen', 'requests', 'socket'}

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write(name: str, value) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, default=str) + '\n')

def calls(tree: ast.AST):
    return [ast.unparse(n.func) for n in ast.walk(tree) if isinstance(n, ast.Call)]

def audit_source(source: bytes):
    text = source.decode('utf-8', 'replace')
    try:
        tree = ast.parse(text)
    except Exception as exc:
        return {'parse': False, 'safe': False, 'classification': 'UNKNOWN', 'error': repr(exc), 'operations': [], 'calls': []}
    call_names = calls(tree)
    lower = ' '.join(call_names).lower()
    operations = sorted({name for name in ('extrude', 'revolve', 'fillet', 'chamfer', 'loft', 'sweep', 'shell', 'cut', 'union', 'intersect', 'box', 'cylinder') if name in lower})
    forbidden = []
    imported_external = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split('.')[0]
                if root not in {'cadquery', 'cq', 'math', 'numpy'}:
                    imported_external.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            root = (node.module or '').split('.')[0]
            if root not in {'cadquery', 'cq', 'math', 'numpy'}:
                imported_external.append(node.module or '')
        elif isinstance(node, ast.Call):
            name = ast.unparse(node.func).split('.')[-1]
            if name in FORBIDDEN_NAMES or any(x in ast.unparse(node.func).lower() for x in ('subprocess', 'os.', 'pathlib', 'requests', 'socket')):
                forbidden.append(ast.unparse(node.func))
    direct = any(any(part in DIRECT_NAMES for part in name.split('.')) for name in call_names)
    has_result = any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'result' for t in n.targets) for n in ast.walk(tree))
    has_export = any('export' in name.lower() for name in call_names)
    if forbidden or imported_external or not direct or not has_result:
        classification = 'EXCLUDED'
    elif has_export and not direct:
        classification = 'EXPORT_WRAPPER'
    else:
        classification = 'DIRECT_CONSTRUCTION'
    return {'parse': True, 'safe': not forbidden and not imported_external, 'classification': classification, 'operations': operations, 'calls': call_names[:80], 'external_imports': imported_external, 'forbidden_calls': forbidden, 'has_result_assignment': has_result, 'has_export_call': has_export}

def step_info(path: Path):
    import cadquery as cq
    obj = cq.importers.importStep(str(path))
    shape = obj.val() if hasattr(obj, 'val') else obj
    bb = shape.BoundingBox()
    return {'valid': True, 'solids': len(shape.Solids()), 'faces': len(shape.Faces()), 'volume': float(shape.Volume()), 'surface_area': float(shape.Area()), 'bbox': [float(x) for x in (bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax)]}

def execute_source(source_path: Path, output_path: Path):
    text = source_path.read_text()
    runner = text + '\n\n# audit export appended outside the source provenance\nimport cadquery as _audit_cq\n_audit_cq.exporters.export(result, ' + repr(str(output_path)) + ', exportType="STEP")\n'
    with tempfile.TemporaryDirectory(prefix='cadquery_audit_') as td:
        run_path = Path(td) / 'run.py'
        run_path.write_text(runner)
        proc = subprocess.run(['python3', str(run_path)], text=True, capture_output=True, timeout=180)
    return {'returncode': proc.returncode, 'stdout': proc.stdout[-4000:], 'stderr': proc.stderr[-4000:], 'output_exists': output_path.exists(), 'output_size': output_path.stat().st_size if output_path.exists() else 0}

def main():
    import pyarrow.parquet as pq
    if not PARQUET.exists():
        write('FINAL_REPORT.json', {'CURRENT_GATE': 'ZERO_TO_CAD_LOCAL_PARQUET_NOT_FOUND', 'PARQUET_PATH': str(PARQUET)})
        return
    rows = pq.read_table(PARQUET, columns=['uuid', 'cadquery_file', 'step_file', 'cadquery_ops_json']).to_pylist()
    audits = []
    eligible = []
    for i, row in enumerate(rows):
        a = audit_source(row['cadquery_file'] or b'')
        rec = {'row_index': i, 'id': str(row['uuid']), 'source_sha256': sha256(row['cadquery_file'] or b''), 'step_sha256': sha256(row['step_file'] or b''), **a}
        audits.append(rec)
        if a['classification'] == 'DIRECT_CONSTRUCTION' and a['safe'] and a['parse'] and row['step_file']:
            eligible.append((i, row, a))
    (OUT / 'CADQUERY_SOURCE_CLASSIFICATION.jsonl').write_text('\n'.join(json.dumps(x) for x in audits) + '\n')
    # Stable stratification: cover the core V2-relevant operations, then fill by row order.
    selected = []
    covered = set()
    for wanted in ('revolve', 'fillet', 'chamfer', 'extrude', 'loft', 'shell'):
        for item in eligible:
            if wanted in item[2]['operations'] and item[0] not in {x[0] for x in selected}:
                selected.append(item); covered.add(wanted); break
    for item in eligible:
        if len(selected) >= 8: break
        if item[0] not in {x[0] for x in selected}: selected.append(item)
    provisional = [{'row_index': i, 'id': str(row['uuid']), 'operations': a['operations'], 'source_sha256': sha256(row['cadquery_file']), 'step_sha256': sha256(row['step_file'])} for i, row, a in selected]
    write('PROVISIONAL_CANARY8.json', {'status': 'NOT_FROZEN', 'count': len(provisional), 'covered': sorted(covered), 'candidates': provisional})
    ast_path = OUT / 'CANARY8_SOURCE_AST_AUDIT.jsonl'; exec_path = OUT / 'CANARY8_SOURCE_EXECUTION.jsonl'; geom_path = OUT / 'CANARY8_PAIR_GEOMETRY.jsonl'
    ast_lines, exec_lines, geom_lines = [], [], []
    for i, row, a in selected:
        sample = SAMPLES / str(row['uuid']); sample.mkdir(parents=True, exist_ok=True)
        source_path, provided_path, executed_path = sample / 'source.py', sample / 'provided.step', sample / 'executed.step'
        source_path.write_bytes(row['cadquery_file']); provided_path.write_bytes(row['step_file'])
        metadata = {'row_index': i, 'uuid': str(row['uuid']), 'operations': a['operations'], 'source_sha256': sha256(row['cadquery_file']), 'provided_step_sha256': sha256(row['step_file'])}
        (sample / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
        ast_lines.append({'row_index': i, 'id': str(row['uuid']), **a})
        er = execute_source(source_path, executed_path) if a['safe'] else {'returncode': -1, 'output_exists': False, 'stderr': 'source not safe'}
        exec_lines.append({'row_index': i, 'id': str(row['uuid']), **er})
        g = {'row_index': i, 'id': str(row['uuid']), 'provided': None, 'executed': None, 'verified': False}
        try:
            g['provided'] = step_info(provided_path)
        except Exception as exc: g['provided_error'] = repr(exc)
        try:
            g['executed'] = step_info(executed_path)
        except Exception as exc: g['executed_error'] = repr(exc)
        if g['provided'] and g['executed']:
            pb, eb = g['provided']['bbox'], g['executed']['bbox']
            scale = max(1.0, max(abs(x) for x in pb + eb))
            bbox_err = max(abs(x-y) for x,y in zip(pb, eb)) / scale
            vol_err = abs(g['provided']['volume'] - g['executed']['volume']) / max(1.0, abs(g['provided']['volume']))
            area_err = abs(g['provided']['surface_area'] - g['executed']['surface_area']) / max(1.0, abs(g['provided']['surface_area']))
            g.update({'bbox_relative_linf': bbox_err, 'volume_relative_error': vol_err, 'surface_area_relative_error': area_err, 'verified': bbox_err < 1e-6 and vol_err < 1e-5 and area_err < 1e-5 and g['provided']['solids'] == g['executed']['solids'] and g['provided']['faces'] == g['executed']['faces']})
        geom_lines.append(g)
    ast_path.write_text('\n'.join(json.dumps(x) for x in ast_lines) + '\n'); exec_path.write_text('\n'.join(json.dumps(x) for x in exec_lines) + '\n'); geom_path.write_text('\n'.join(json.dumps(x) for x in geom_lines) + '\n')
    verified = sum(bool(x.get('verified')) for x in geom_lines)
    executed = sum(x.get('returncode') == 0 and x.get('output_exists') for x in exec_lines)
    report = {'CURRENT_GATE': 'CADQUERY_NATIVE_CANARY8_FROZEN' if verified == len(selected) and selected else 'CADQUERY_NATIVE_CANARY8_VALIDATION_FAILED', 'PARQUET_PATH': str(PARQUET), 'ROW_COUNT': len(rows), 'ELIGIBLE_DIRECT_SAFE': len(eligible), 'SELECTED_N': len(selected), 'COVERED_OPERATIONS': sorted(covered), 'AST_PARSE': f'{sum(x["parse"] for _,_,x in selected)}/{len(selected)}', 'SOURCE_SAFE': f'{sum(x["safe"] for _,_,x in selected)}/{len(selected)}', 'SOURCE_EXEC': f'{executed}/{len(selected)}', 'STEP_RELOAD': f'{sum(bool(x.get("provided") and x.get("executed")) for x in geom_lines)}/{len(selected)}', 'PAIR_GEOMETRY_VERIFIED': f'{verified}/{len(selected)}', 'VALID_NATIVE_DSL_V2_CASE': 0, 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'PLACEMENT_CHANGED': 'NO', 'C2_CHANGED': 'NO', 'SONATA_CHANGED': 'NO', 'SPATIALLM_CHANGED': 'NO', 'DSL_V2_CHANGED': 'NO', 'NEXT_STEP': 'DSL_V2_CANONICALIZATION_ONLY_AFTER_NATIVE_CANARY_PASS' if verified == len(selected) and selected else 'SOURCE_EXECUTION_OR_GEOMETRY_REVIEW'}
    if verified == len(selected) and selected:
        manifest = {'manifest': 'CADQUERY_NATIVE_CANARY8_MANIFEST', 'version': 1, 'status': 'FROZEN', 'parquet_path': str(PARQUET), 'parquet_sha256': sha256(PARQUET.read_bytes()), 'samples': provisional, 'validation': {'ast_parse': '8/8', 'source_safe': '8/8', 'source_exec': '8/8', 'executed_step_reload': '8/8', 'pair_geometry_verified': f'{verified}/{len(selected)}'}, 'excluded_from_scope': ['CADFS', 'CADFit', 'DeepCAD', 'Fusion360', 'tank_case'], 'dsl_v2_changed': False, 'training_run': False, 'decode_run': False}
        write('CADQUERY_NATIVE_CANARY8_MANIFEST.json', manifest)
    write('FINAL_REPORT.json', report); (OUT / 'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items()) + '\n')
    print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
