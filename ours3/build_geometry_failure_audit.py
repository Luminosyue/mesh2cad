import csv
from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3'); O=B/'baseline_comparison_closeout_v1'; V=B/'unified_step_geometry_evaluator_v2'
def bucket(reason):
    s=(reason or '').lower()
    if 'empty' in s and 'solid' in s: return 'empty solid'
    if 'non-solid' in s or 'not solid' in s: return 'non-solid'
    if 'brep' in s or 'could not be loaded' in s or 'step file' in s: return 'invalid BRep'
    if 'boolean' in s or 'intersection' in s or 'fuse' in s: return 'boolean failure'
    if 'zero' in s and 'volume' in s: return 'zero volume'
    if 'sampl' in s or 'tessell' in s: return 'sampling failure'
    if 'normal' in s or 'scale' in s or 'frame' in s: return 'normalization failure'
    return 'other'
counts={}
rows=[]
for method,fn in [('P1',V/'per_case/P1_GEOMETRY_METRICS_V2.csv'),('CAD-Recode',V/'per_case/CAD_RECODE_GEOMETRY_METRICS_V2.csv')]:
    for r in csv.DictReader(fn.open()):
        if r['step_reload_success']=='True' and r['geometry_eval_success']!='True':
            b=bucket(r.get('failure_reason','')); counts[(method,b)]=counts.get((method,b),0)+1; rows.append((method,r['case_id'],b,r.get('failure_reason','')))
smoke= B/'cadfit_val1000_baseline_v1/smoke10_verification.csv'
for r in csv.DictReader(smoke.open()):
    if r['step_reload']=='PASS' and r['unified_evaluator']!='PASS':
        b=bucket(r.get('failure_reason','')); counts[('CADFit',b)]=counts.get(('CADFit',b),0)+1; rows.append(('CADFit',r['case_id'],b,r.get('failure_reason','')))
cats=['empty solid','non-solid','invalid BRep','boolean failure','zero volume','sampling failure','normalization failure','other']
lines=['# Geometry Validity Failure Audit','','Definition: STEP reload success is tracked separately from geometry validity. This audit counts only `STEP_RELOAD_PASS_BUT_GEOMETRY_INVALID`.','','| Method | STEP reload pass but geometry invalid | empty solid | non-solid | invalid BRep | boolean failure | zero volume | sampling failure | normalization failure | other |','|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for m in ['P1','CAD-Recode','CADFit']:
    vals=[counts.get((m,c),0) for c in cats]; lines.append('| '+m+' | '+str(sum(vals))+' | '+' | '.join(map(str,vals))+' |')
lines += ['', 'Case-level evidence is retained in the per-case CSVs; unavailable full CADFit cases remain pending until the detached official inference finishes.']
(O/'reports/geometry_validity_failure_audit.md').write_text('\n'.join(lines)+'\n')
