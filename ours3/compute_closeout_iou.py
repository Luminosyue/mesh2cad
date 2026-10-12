import csv, json, sys
from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3'); O=B/'baseline_comparison_closeout_v1'; V=B/'unified_step_geometry_evaluator_v2'
sys.path.insert(0,str(V)); import cadquery as cq
from evaluator.unified_step_geometry_evaluator_v2 import load_adapted_shape
man={}
for line in (B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v1/manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines():
    if line.strip():
        r=json.loads(line); man[r['cad_id']]=Path(r['gt_step_path'])
def calc(pred,gt,frame):
    a=load_adapted_shape(gt,'DATASET_CANONICAL'); b=load_adapted_shape(pred,frame)
    va=float(a.Volume()); vb=float(b.Volume()); inter=float(a.intersect(b).Volume()); union=va+vb-inter
    score=inter/union if union>1e-12 else None
    return score if score is not None and -1e-9 <= score <= 1+1e-9 else None
full=O/'tables/baseline_full_val1000.csv'; rows=list(csv.DictReader(full.open()))
vals={}; fail={}
for r in rows:
    if r['method'] not in ('P1','CAD-Recode') or r['geometry_valid_n' if 'geometry_valid_n' in r else 'denominator_method_valid'] not in ('1',): continue
    try:
        vals[(r['method'],r['case_id'])]=calc(Path(r['prediction_path']),man[r['case_id']], 'DATASET_CANONICAL' if r['method']=='P1' else 'OFFICIAL_CENTERED_CUBE2')
    except Exception as e: fail[(r['method'],r['case_id'])]=f'{type(e).__name__}: {e}'
for r in rows:
    k=(r['method'],r['case_id'])
    if k in vals: r['IoU']='' if vals[k] is None else f'{vals[k]:.12g}'
    elif k in fail: r['failure_reason']=(r['failure_reason']+'; ' if r['failure_reason'] else '')+'IoU: '+fail[k]
with full.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
pm={}; cm={}
for r in rows:
    if r['method']=='P1': pm[r['case_id']]=r
    elif r['method']=='CAD-Recode': cm[r['case_id']]=r
common=[c for c in pm if pm[c]['denominator_method_valid']=='1' and cm[c]['denominator_method_valid']=='1']
out=O/'tables/baseline_common_valid.csv';
with out.open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['case_id','P1_IoU','CAD-Recode_IoU','P1_Chamfer','CAD-Recode_Chamfer','P1_H95','CAD-Recode_H95','P1_Volume_Error','CAD-Recode_Volume_Error'])
    for c in common: w.writerow([c,pm[c]['IoU'],cm[c]['IoU'],pm[c]['Chamfer'],cm[c]['Chamfer'],pm[c]['H95'],cm[c]['H95'],pm[c]['Volume_Error'],cm[c]['Volume_Error']])
print({'p1_iou_n':sum(bool(r['IoU']) for r in pm.values()),'cad_iou_n':sum(bool(r['IoU']) for r in cm.values()),'common_iou_n':sum(bool(pm[c]['IoU'] and cm[c]['IoU']) for c in common),'iou_failures':len(fail)})
