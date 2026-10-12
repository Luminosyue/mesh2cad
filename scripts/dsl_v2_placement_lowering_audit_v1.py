from __future__ import annotations

import ast
import hashlib
import json
from collections import Counter
from pathlib import Path

import pyarrow.parquet as pq

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
PARQUET = ROOT / 'zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet'
POOL = ROOT / 'ours3/canonical_cad_dsl_v2_base_operator_integration_canary_v1/UNIFIED_DSL_V2_SUPPORTED_POOL.json'
OUT = ROOT / 'ours3/dsl_v2_placement_lowering_audit_v1'
OUT.mkdir(parents=True, exist_ok=True)

SUPPORTED = {'Workplane','moveTo','lineTo','polyline','rect','circle','close','edges','revolve','fillet','chamfer','box','cylinder','extrude','cut','union'}
PLACEMENT_A = {'center','workplane'}
TRANSFORM_B = {'translate','rotate','mirrorY'}
TOPOLOGY_C = {'faces','wires','val','findSolid','normalAt','toWorldCoords','workplane'}
FEATURE_D = {'polarArray','rarray','cskHole','csk_face_hole','hole','cboreHole','cutBlind','cutThruAll','shell','loft','sweep','twistExtrude','placeSketch','mirror'}
PY_CALLS = {'range','len','int','float','abs','min','max','sum','sin','cos','tan','radians','degrees','isinstance','setattr','deepcopy','print'}

def sha(b): return hashlib.sha256(b).hexdigest()
def dump(n, x): (OUT / n).write_text(json.dumps(x, indent=2, default=str) + '\n')

def call_chain(source):
    tree = ast.parse(source)
    calls = []
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call): continue
        name = ast.unparse(n.func); method = name.split('.')[-1]
        if method in PY_CALLS: continue
        if isinstance(n.func, ast.Name) and n.func.id in {'model','build','finalize','add','split','rotate','translate'} and n.func.id not in SUPPORTED | PLACEMENT_A | TRANSFORM_B: continue
        selectors = [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str) and a.value[:1] in {'|','>','<'}]
        calls.append({'call': name, 'method': method, 'lineno': getattr(n, 'lineno', 0), 'selectors': selectors, 'args': [ast.unparse(a) for a in n.args], 'keywords': {k.arg: ast.unparse(k.value) for k in n.keywords if k.arg}})
    return sorted(calls, key=lambda x: (x['lineno'], x['call']))

def main():
    pool = json.loads(POOL.read_text()); ids = {x['id'] for x in pool['cases']}
    rows = {str(x['uuid']): x for x in pq.read_table(PARQUET, columns=['uuid','cadquery_file','step_file']).to_pylist()}
    records = []; counts = Counter(); recovered = Counter()
    for ident in sorted(ids, key=lambda x: (pool['cases'][next(i for i,y in enumerate(pool['cases']) if y['id']==x)]['row_index'], x)):
        row = rows[ident]; source = (row['cadquery_file'] or b'').decode('utf-8','replace'); chain = call_chain(source); methods = [x['method'] for x in chain]
        unsupported = sorted(set(methods) - SUPPORTED)
        a = sorted(set(unsupported) & PLACEMENT_A); b = sorted(set(unsupported) & TRANSFORM_B); c = sorted(set(unsupported) & TOPOLOGY_C); d = sorted(set(unsupported) & FEATURE_D); other = sorted(set(unsupported) - set(a) - set(b) - set(c) - set(d))
        categories = []
        if a: categories.append('A_PLACEMENT_ONLY')
        if b: categories.append('B_DETERMINISTIC_TRANSFORM')
        if c: categories.append('C_TOPOLOGY_SELECTION')
        if d or other: categories.append('D_GENUINE_FEATURE_OR_OTHER')
        lowerable = bool(a or b) and not (c or d or other)
        confidence = 'HIGH' if lowerable and not b else 'MEDIUM' if lowerable else 'NONE'
        positions = [{'call': x['call'], 'lineno': x['lineno']} for x in chain if x['method'] in unsupported]
        dep = 'UNKNOWN'
        for x in chain:
            if x['method'] in unsupported:
                dep = next((y['method'] for y in chain if y['lineno'] >= x['lineno'] and y['method'] in SUPPORTED), 'result')
                break
        rec = {'cad_id': ident, 'row_index': next(x['row_index'] for x in pool['cases'] if x['id']==ident), 'full_call_chain': [x['call'] for x in chain], 'unsupported_calls': unsupported, 'unsupported_call_positions': positions, 'dependent_operator': dep, 'whether_geometry_semantics_are_deterministic': lowerable, 'candidate_lowering': 'bake into origin/profile coordinates/axis' if lowerable else 'none', 'lowering_confidence': confidence, 'categories': categories, 'source_sha256': sha(row['cadquery_file']), 'step_sha256': sha(row['step_file'])}
        records.append(rec)
        for key, vals in [('CENTER_CASES', a),('TRANSLATE_CASES', [x for x in b if x=='translate']),('WORKPLANE_CASES', [x for x in a if x=='workplane']),('ROTATE_CASES', [x for x in b if x=='rotate']),('MIRRORY_CASES', [x for x in b if x=='mirrorY']),('FACES_CASES', c),('POLARARRAY_CASES', [x for x in d if x in {'polarArray','rarray'}]),('CSKHOLE_CASES', [x for x in d if x in {'cskHole','csk_face_hole'}])]:
            if vals: counts[key] += 1
        if lowerable:
            recovered['LOWERING_CANDIDATE'] += 1
            for key in ('center','translate','workplane','rotate','mirrorY'):
                if key in unsupported: recovered['RECOVERED_BY_' + key.upper()] += 1
        if not unsupported: recovered['STRICT_ALREADY_ELIGIBLE'] += 1
    (OUT/'UNSUPPORTED_CALL_CHAIN_AUDIT.json').write_text(json.dumps({'records': records}, indent=2) + '\n')
    (OUT/'UNSUPPORTED_CALL_CHAIN_AUDIT.md').write_text('\n'.join(f"{x['cad_id']} | {x['categories']} | {x['unsupported_calls']} | lowerable={x['whether_geometry_semantics_are_deterministic']}" for x in records) + '\n')
    for x in records:
        if x['whether_geometry_semantics_are_deterministic']: recovered['STRICT_ELIGIBLE_AFTER'] += 1
    semantic_path = OUT / 'PLACEMENT_LOWERING_SEMANTIC_CANARY.json'
    semantic = json.loads(semantic_path.read_text()) if semantic_path.exists() else {'pass': 0, 'count': 0}
    report = {'CURRENT_GATE': 'DSL_V2_PLACEMENT_LOWERING_SEMANTIC_CANARY_PASS' if semantic.get('pass') == semantic.get('count') and semantic.get('count', 0) >= 3 else 'DSL_V2_PLACEMENT_LOWERING_AUDIT_COMPLETE', 'STRICT_ELIGIBLE_BEFORE': 3, 'STRICT_ELIGIBLE_AFTER_POTENTIAL': recovered['STRICT_ELIGIBLE_AFTER'] + 3, 'RECOVERED_BY_CENTER': recovered['RECOVERED_BY_CENTER'], 'RECOVERED_BY_TRANSLATE': recovered['RECOVERED_BY_TRANSLATE'], 'RECOVERED_BY_WORKPLANE': recovered['RECOVERED_BY_WORKPLANE'], 'RECOVERED_BY_ROTATE': recovered['RECOVERED_BY_ROTATE'], 'RECOVERED_BY_MIRRORY': recovered['RECOVERED_BY_MIRRORY'], 'LOWERING_CANDIDATES': recovered['LOWERING_CANDIDATE'], 'SEMANTIC_LOWERING_CANARY': f"{semantic.get('pass', 0)}/{semantic.get('count', 0)}", 'LOWERING_VALIDATED_RULES': ['center_to_origin', 'translate_to_origin', 'workplane_offset_to_origin'] if semantic.get('pass') == semantic.get('count') and semantic.get('count', 0) >= 3 else [], 'STILL_BLOCKED_BY_FACES': counts['FACES_CASES'], 'STILL_BLOCKED_BY_POLAR_ARRAY': counts['POLARARRAY_CASES'], 'STILL_BLOCKED_BY_CSK_HOLE': counts['CSKHOLE_CASES'], 'NEW_DSL_OPERATOR_ADDED': 'NO', 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'freeze_allowed': False, 'NEXT_STEP': 'BATCH_APPLY_VALIDATED_PLACEMENT_LOWERING_THEN_REAUDIT'}
    dump('FINAL_REPORT.json', report); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items()) + '\n'); print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
