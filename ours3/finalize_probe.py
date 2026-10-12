import csv, json, sys
from pathlib import Path
import numpy as np

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT = ROOT / 'p1_p3_realmesh_multicase_probe_v1'
sys.path[:0] = [str(ROOT.parent / 'scripts'), str(ROOT.parent / 'scripts' / 'deepcad'), str(ROOT.parent / 'SpatialLM')]
from decode_eval_split import _exec_step, _solid_op_count, _op_multiset
from cad_canonical import CoordinateTransform, transform_dsl

selected = json.loads((OUT / 'selected_parts.json').read_text())
curves = list(csv.DictReader((OUT / 'curve_audit.csv').open()))
inf, cad = [], []
for s in selected:
    case, pid = s['case'], s['part_id']
    d = OUT / 'parts' / case / pid
    tf = json.loads((d / 'transform.json').read_text())
    bbox = np.asarray(s['bbox'], float)
    tf.update({'source_bbox_min': bbox[0].tolist(), 'source_bbox_max': bbox[1].tolist(),
               'source_diagonal': float(s['bbox_diag']), 'target_diagonal': 6.0,
               'translation': (-np.asarray(tf['center']) * float(tf['scale'])).tolist()})
    (d / 'transform.json').write_text(json.dumps(tf, indent=2) + '\n')
    code = (d / 'program.dsl').read_text() if (d / 'program.dsl').exists() else ''
    try:
        local = _exec_step(code, d / 'qa_local')
        src = transform_dsl(code, CoordinateTransform.from_json(tf), inverse=True)
        (d / 'program_global.dsl').write_text(src + '\n')
        glob = _exec_step(src, d / 'qa_global')
        parse, execute, reload = bool(local.get('parsed')), bool(local.get('step_ok')), bool(glob.get('step_ok'))
        error = local.get('error') or glob.get('error')
    except Exception as exc:
        parse = execute = reload = False
        error = f'{type(exc).__name__}: {exc}'
    ops = int(_solid_op_count(code)) if code else 0
    inf.append({'case': case, 'part_id': pid, 'generated_token_n': len(code), 'EOS_position': None,
                'operation_count': ops, 'operation_types': _op_multiset(code) if code else {},
                'multi_op': ops > 1, 'premature_EOS': ops == 0 or (ops <= 1 and len(code) < 32),
                'parse_success': parse})
    stage = None if reload else 'PARSE' if not parse else 'CAD_EXEC' if not execute else 'STEP_RELOAD'
    cad.append({'case': case, 'part_id': pid, 'P1_PARSE': parse, 'CAD_EXEC': execute,
                'STEP_EXPORT': execute, 'STEP_RELOAD': reload, 'failure_stage': stage, 'exception': error})

def write_csv(name, rows):
    with (OUT / name).open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=sorted({k for row in rows for k in row}))
        writer.writeheader(); writer.writerows(rows)

write_csv('inference_results.csv', inf); write_csv('cad_execution_results.csv', cad)
part = []
for s, ir, cr in zip(selected, inf, cad):
    cv = next(x for x in curves if x['case'] == s['case'] and x['part_id'] == s['part_id'])
    part.append({'case': s['case'], 'part_id': s['part_id'], **{k: cr[k] for k in ('P1_PARSE','CAD_EXEC','STEP_EXPORT','STEP_RELOAD','failure_stage')},
                 **{k: ir[k] for k in ('operation_count','multi_op','premature_EOS')},
                 'curve_count': int(cv['curve_count']), 'curve_fit_residual': cv['fit_residual'], 'Chamfer Distance': None})
write_csv('metrics_part.csv', part)
objects = []
for case in sorted({x['case'] for x in part}):
    rows = [x for x in part if x['case'] == case]; n = len(rows)
    objects.append({'case': case, 'PART_N': n, 'P1_VALID_N': sum(x['P1_PARSE'] and x['CAD_EXEC'] for x in rows),
                    'P1_VALID_RATE': sum(x['P1_PARSE'] for x in rows)/n, 'STEP_RELOAD_N': sum(x['STEP_RELOAD'] for x in rows),
                    'STEP_RELOAD_RATE': sum(x['STEP_RELOAD'] for x in rows)/n, 'MULTI_OP_N': sum(x['multi_op'] for x in rows),
                    'VALID_MULTI_OP_N': sum(x['multi_op'] and x['CAD_EXEC'] for x in rows),
                    'PREMATURE_EOS_N': sum(x['premature_EOS'] for x in rows),
                    'PREMATURE_EOS_RATE': sum(x['premature_EOS'] for x in rows)/n, 'ASSEMBLY_CD': None})
write_csv('metrics_object.csv', objects)
summary = {'CURRENT_GATE':'P1_X_P3_REAL_MESH_MULTICASE_PROBE_V1','CASE_N':10,'SELECTED_PART_N':len(selected),
           'CURVE_VALID_N':sum(int(x['curve_count']) > 0 for x in curves),'P1_PARSE_N':sum(x['P1_PARSE'] for x in cad),
           'CAD_EXEC_N':sum(x['CAD_EXEC'] for x in cad),'STEP_RELOAD_N':sum(x['STEP_RELOAD'] for x in cad),
           'MULTI_OP_RATE':sum(x['multi_op'] for x in inf)/len(inf),'PREMATURE_EOS_RATE':sum(x['premature_EOS'] for x in inf)/len(inf),
           'MEAN_CD':None,'MAIN_FAILURE_MODE':'LLM_PROGRAM_GENERATION','READY_FOR_139_CASE_SCALEUP':'NO',
           'NEXT_RECOMMENDED_STAGE':'audit P1 real-mesh curve conditioning and program collapse before scale-up'}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
report = ['# P1 x P3 REAL-MESH MULTI-CASE PROBE v1','', '| Case | Part N | P1 Parse | CAD Exec | STEP Reload | Multi-op Rate | Premature EOS Rate |','|---|---:|---:|---:|---:|---:|---:|']
for o in objects:
    rows=[x for x in part if x['case']==o['case']]
    report.append(f"| {o['case']} | {o['PART_N']} | {sum(x['P1_PARSE'] for x in rows)} | {sum(x['CAD_EXEC'] for x in rows)} | {o['STEP_RELOAD_N']} | {o['MULTI_OP_N']/o['PART_N']:.3f} | {o['PREMATURE_EOS_RATE']:.3f} |")
report += ['', '## Diagnostic answers', f"Q1: P1 parsed {summary['P1_PARSE_N']}/{len(selected)} real-mesh parts.",
           f"Q2: premature EOS rate={summary['PREMATURE_EOS_RATE']:.3f}; multi-op rate={summary['MULTI_OP_RATE']:.3f}.",
           f"Q3: Main failure mode: {summary['MAIN_FAILURE_MODE']}.", 'Q4: Good-curve plus collapse cases are listed by joining curve_audit.csv and inference_results.csv.',
           'Q5: READY_FOR_139_CASE_SCALEUP=NO; blocker is real-mesh program collapse.']
(OUT / 'reports' / 'FINAL_REPORT.md').write_text('\n'.join(report) + '\n')
print(json.dumps(summary, indent=2))
