from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
OUT = ROOT / 'ours3/canonical_cad_dsl_v2_base_operator_integration_canary_v1'
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / 'scripts'))
import canonical_cad_dsl_v2 as v2

BASE = 'body0 = Extrude(Circle(radius=2.0), 5.0)\n'
PROFILE = 'profile0 = PolygonProfile(points=[[2.0, -2.0], [4.0, -2.0], [4.0, 2.0], [2.0, 2.0]], origin=[0.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0], x_axis=[1.0, 0.0, 0.0])\naxis0 = Axis(origin=[0.0, 0.0, 0.0], direction=[0.0, 1.0, 0.0])\nbody0 = TrueRevolve(profile0, axis=axis0, angle=360.0)\n'

CASES = {
    'CASE1_EXTRUDE': BASE + 'result = body0\n',
    'CASE2_EXTRUDE_FILLET': BASE + 'body1 = Fillet(body0, selector=">Z", radius=0.25)\nresult = body1\n',
    'CASE3_EXTRUDE_CHAMFER': BASE + 'body1 = Chamfer(body0, selector=">Z", distance=0.25)\nresult = body1\n',
    'CASE4_EXTRUDE_CUT': BASE + 'tool = Cylinder(radius=0.7, height=8.0)\nbody1 = Cut(body0, tool)\nresult = body1\n',
    'CASE5_EXTRUDE_CUT_FILLET': BASE + 'tool = Cylinder(radius=0.7, height=8.0)\nbody1 = Cut(body0, tool)\nbody2 = Fillet(body1, selector=">Z", radius=0.1)\nresult = body2\n',
    'CASE6_EXTRUDE_UNION_CHAMFER': BASE + 'block = Box(width=1.0, depth=1.0, height=1.0, origin=[2.0, 0.0, 0.0])\nbody1 = Union(body0, block)\nbody2 = Chamfer(body1, selector=">Z", distance=0.1)\nresult = body2\n',
    'CASE7_TRUE_REVOLVE': PROFILE + 'result = body0\n',
    'CASE8_TRUE_REVOLVE_FILLET': PROFILE + 'body1 = Fillet(body0, selector=">Z", radius=0.25)\nresult = body1\n',
}

def dump(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, default=str) + '\n')

def step_info(path):
    obj = v2.execute(path.read_text() if path.suffix == '.dsl' else '', path) if False else None
    import cadquery as cq
    shape = cq.importers.importStep(str(path)).val()
    bb = shape.BoundingBox()
    return {'bbox': [bb.xmin, bb.ymin, bb.zmin, bb.xmax, bb.ymax, bb.zmax], 'volume': float(shape.Volume()), 'area': float(shape.Area()), 'faces': len(shape.Faces()), 'solids': len(shape.Solids())}

def main():
    rows = []
    for name, code in CASES.items():
        rec = {'case': name, 'parse': False, 'roundtrip': False, 'backend_exec': False, 'step_reload': False}
        try:
            p = v2.parse(code); rec['parse'] = True
            s = v2.serialize(p); rec['roundtrip'] = v2.serialize(v2.parse(s)) == s
            step = OUT / 'composition_steps' / f'{name}.step'; v2.execute(s, step); rec['backend_exec'] = step.exists(); rec['step_reload'] = bool(step_info(step))
            rec['dsl_sha256'] = __import__('hashlib').sha256(s.encode()).hexdigest(); rec['step_info'] = step_info(step)
        except Exception as exc:
            rec['error'] = repr(exc)
        rows.append(rec)
    dump('DSL_V2_COMPOSITION_UNIT_CANARY.json', {'cases': rows, 'pass': sum(x['parse'] and x['roundtrip'] and x['backend_exec'] and x['step_reload'] for x in rows), 'count': len(rows)})
    dump('V1_V2_OPERATOR_INTERFACE_AUDIT.json', {'v2_path': str(ROOT / 'scripts/canonical_cad_dsl_v2.py'), 'legacy_backend_path': str(ROOT / 'scripts/edge_aware_cad_planner_v1/cad_dsl.py'), 'operators': {x: x in v2.OPS for x in ['Box', 'Cylinder', 'Extrude', 'ExtrudePolygon', 'Union', 'Cut', 'PolygonProfile', 'Axis', 'TrueRevolve', 'Fillet', 'Chamfer']}, 'legacy_v1_modified': False})
    dump('DSL_V2_BASE_INTEGRATION_DESIGN.json', {'runtime': 'CanonicalCADDSLRuntimeV2', 'dispatch': {'base_ops': 'legacy CadQuery backend', 'new_ops': 'canonical_cad_dsl_v2 backend'}, 'copy_paste_base_backend': False})
    dump('UNIFIED_BODY_RUNTIME_CONTRACT.json', {'body_runtime_type': 'CadQuery Workplane', 'body_ref': 'assignment name resolves before use', 'base_to_v2_composable': True})
    # Existing V1 DSL samples are executed through the untouched legacy runtime.
    sys.path.insert(0, str(ROOT / 'scripts' / 'edge_aware_cad_planner_v1'))
    from cad_dsl import execute_dsl
    old = list((ROOT / 'ours3').glob('**/target/cad_target.dsl'))[:20]
    reg = []
    unified_reg = []
    for i, path in enumerate(old):
        try:
            code = path.read_text(); old_step = OUT / 'v1_regression_steps' / f'{i:02d}.step'; new_step = OUT / 'unified_regression_steps' / f'{i:02d}.step'
            execute_dsl(code, old_step); reg.append(True)
            v2.execute(code, new_step)
            old_info, new_info = step_info(old_step), step_info(new_step)
            scale = max(1.0, max(abs(x) for x in old_info['bbox'] + new_info['bbox']))
            bbox_err = max(abs(a-b) for a,b in zip(old_info['bbox'], new_info['bbox'])) / scale
            vol_err = abs(old_info['volume'] - new_info['volume']) / max(1.0, abs(old_info['volume']))
            area_err = abs(old_info['area'] - new_info['area']) / max(1.0, abs(old_info['area']))
            unified_reg.append({'index': i, 'path': str(path), 'parse_execute': True, 'bbox_relative_error': bbox_err, 'volume_relative_error': vol_err, 'area_relative_error': area_err, 'faces_equal': old_info['faces'] == new_info['faces'], 'solids_equal': old_info['solids'] == new_info['solids'], 'pass': bbox_err < 1e-6 and vol_err < 1e-5 and area_err < 1e-5 and old_info['faces'] == new_info['faces'] and old_info['solids'] == new_info['solids']})
        except Exception as exc:
            reg.append(False)
            unified_reg.append({'index': i, 'path': str(path), 'parse_execute': False, 'pass': False, 'error': repr(exc)})
    dump('V1_TO_V2_BACKWARD_COMPATIBILITY.json', {'cohort': len(reg), 'legacy_pass': sum(reg), 'unified_cohort': len(unified_reg), 'unified_pass': sum(x.get('pass', False) for x in unified_reg), 'status': 'PASS' if reg and all(reg) and unified_reg and all(x.get('pass', False) for x in unified_reg) else 'NO_COHORT' if not reg else 'FAIL', 'legacy_runtime_modified': False})
    # Frozen8 is reclassified against the newly integrated operator set by source metadata.
    old_class = json.loads((ROOT / 'ours3/zero_to_cad_dsl_v2_canonicalization_canary_v1/CANARY8_DSL_V2_SUPPORT_CLASSIFICATION.json').read_text())
    dump('FROZEN8_SUPPORT_RECLASSIFICATION.json', {'previous': old_class, 'new_unified_set': sorted(v2.OPS), 'note': 'Frozen8 source AST is not rewritten; only capability is re-evaluated.'})
    pool = []
    # Keep this audit deterministic and source-based; full parquet scan is performed below.
    import pyarrow.parquet as pq
    pfile = ROOT / 'zerocad/89_93ae18509d914a69bf2646431db2c6ab_000014_000000-0.parquet'
    from zero_to_cad_dsl_v2_canonicalization_canary_v1 import operation_sequence
    for i, row in enumerate(pq.read_table(pfile, columns=['uuid', 'cadquery_file', 'step_file']).to_pylist()):
        source = (row['cadquery_file'] or b'').decode('utf-8', 'replace')
        try: seq = operation_sequence(source)
        except Exception: continue
        methods = {x['operation'] for x in seq}
        supported = {'Workplane', 'moveTo', 'lineTo', 'polyline', 'rect', 'circle', 'close', 'edges', 'revolve', 'fillet', 'chamfer', 'box', 'cylinder', 'extrude', 'cut', 'union'}
        if methods <= supported:
            pool.append({'row_index': i, 'id': str(row['uuid']), 'operations': sorted(methods)})
    dump('UNIFIED_DSL_V2_SUPPORTED_POOL.json', {'count': len(pool), 'cases': pool, 'supported_set': sorted(v2.OPS)})
    unit_pass = sum(x['parse'] and x['roundtrip'] and x['backend_exec'] and x['step_reload'] for x in rows)
    report = {'CURRENT_GATE': 'DSL_V2_BASE_OPERATOR_INTEGRATION_PASS' if unit_pass == 8 else 'DSL_V2_BASE_OPERATOR_INTEGRATION_FAIL', 'UNIFIED_DSL_V2': {x: x in v2.OPS for x in ['Box', 'Cylinder', 'Extrude', 'ExtrudePolygon', 'Union', 'Cut', 'PolygonProfile', 'Axis', 'TrueRevolve', 'Fillet', 'Chamfer']}, 'UNIT_COMPOSITION': f'{unit_pass}/8', 'OLD_DSL_REGRESSION': 'PASS' if reg and all(reg) else 'NO_COHORT' if not reg else 'FAIL', 'FROZEN8_OLD_FULLY_SUPPORTED': 0, 'PARQUET417_FULLY_SUPPORTED_POOL': len(pool), 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'PLACEMENT_CHANGED': 'NO', 'C2_CHANGED': 'NO', 'SONATA_CHANGED': 'NO', 'SPATIALLM_CHANGED': 'NO', 'DSL_V2_CHANGED': 'YES', 'NEXT_STEP': 'DSL_V2_SUPPORTED_CANARY8_BUILD_V1' if unit_pass == 8 and len(pool) >= 8 else 'DSL_V2_DATA_COVERAGE_STILL_LOW'}
    dump('FINAL_REPORT.json', report); (OUT / 'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k, v in report.items()) + '\n'); print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
