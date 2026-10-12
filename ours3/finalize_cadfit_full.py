import csv,json,os,sys,time,subprocess
from pathlib import Path
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3'); C=B/'cadfit_val1000_baseline_v1'; R=C/'full_runs'; V=B/'unified_step_geometry_evaluator_v2'; O=B/'baseline_comparison_closeout_v1'
PID=int(os.environ.get('CADFIT_PID','0'))
while True:
    n=sum(1 for _ in R.glob('*/final_iou.json')) if R.exists() else 0
    alive=False
    if PID:
        try: os.kill(PID,0); alive=True
        except OSError: alive=False
    if n>=1000 or (not alive and n>0): break
    time.sleep(60)
sys.path.insert(0,str(V)); from evaluator.unified_step_geometry_evaluator_v2 import load_adapted_shape,geometry_metrics,stable_seed
import cadquery as cq
man={}
for line in (B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v1/manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines():
    if line.strip():
        x=json.loads(line); man[x['cad_id']]=x
cadrows=[]
for cid,x in man.items():
    short=cid.replace('deepcad__',''); d=R/short; py=d/'best_greedy_parallel_iterative.py'; st=d/'cadfit_prediction.step'; rec={'case_id':cid,'input_path':str(C/'input_recovered_v2'/(short+'.stl')),'prediction_path':str(st),'step_reload_success':False,'geometry_eval_success':False,'chamfer':'','h95':'','relative_volume_error':'','iou':'','failure_reason':''}
    try:
        if not py.exists(): raise FileNotFoundError(str(py))
        ns=__import__('runpy').run_path(str(py)); result=ns.get('result')
        if result is None: raise ValueError('missing result')
        cq.exporters.export(result,str(st)); pred=load_adapted_shape(st,'DATASET_CANONICAL'); gt=load_adapted_shape(Path(x['gt_step_path']),'DATASET_CANONICAL'); rec['step_reload_success']=True
        m=geometry_metrics(pred,gt,10000,stable_seed(cid)); rec.update({'geometry_eval_success':True,'chamfer':m['chamfer'],'h95':m['h95'],'relative_volume_error':m['relative_volume_error']})
        va,vb=float(gt.Volume()),float(pred.Volume()); inter=float(gt.intersect(pred).Volume()); union=va+vb-inter; q=inter/union if union>1e-12 else None
        if q is not None and 0<=q<=1: rec['iou']=q
    except Exception as e: rec['failure_reason']=f'{type(e).__name__}: {e}'
    cadrows.append(rec)
with (C/'full_cadfit_unified_metrics.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(cadrows[0])); w.writeheader(); w.writerows(cadrows)
full=O/'tables/baseline_full_val1000.csv'; rows=list(csv.DictReader(full.open())); by={r['case_id']:r for r in cadrows}
for r in rows:
    if r['method']!='CADFit': continue
    c=by[r['case_id']]; r['input_path']=c['input_path']; r['prediction_path']=c['prediction_path']; r['IR']='1' if c['step_reload_success'] else '0'; r['STEP_Reload']='1' if c['step_reload_success'] else '0'; r['IoU']=c['iou']; r['Chamfer']=c['chamfer']; r['H95']=c['h95']; r['Volume_Error']=c['relative_volume_error']; r['denominator_method_valid']='1' if c['geometry_eval_success'] else '0'; r['failure_reason']=c['failure_reason']
with full.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
methods={m:{r['case_id']:r for r in rows if r['method']==m} for m in ['P1','CAD-Recode','CADFit']}
common=[c for c in man if all(methods[m].get(c,{}).get('denominator_method_valid')=='1' for m in methods)]
with (O/'tables/baseline_common_valid.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['case_id','P1_IoU','CAD-Recode_IoU','CADFit_IoU','P1_Chamfer','CAD-Recode_Chamfer','CADFit_Chamfer','P1_H95','CAD-Recode_H95','CADFit_H95','P1_Volume_Error','CAD-Recode_Volume_Error','CADFit_Volume_Error']);
    for c in common: w.writerow([c]+sum(([methods[m][c]['IoU'],methods[m][c]['Chamfer'],methods[m][c]['H95'],methods[m][c]['Volume_Error']] for m in ['P1','CAD-Recode','CADFit']),[]))
with (O/'tables/baseline_per_method_valid_summary.csv').open('w',newline='') as f:
    w=csv.writer(f); w.writerow(['method','full_denominator','step_reload_n','geometry_valid_n','metric','mean','median','max','strict_common_valid_n'])
    for m in ['P1','CAD-Recode','CADFit']:
        d=list(methods[m].values())
        for k in ['Chamfer','H95','Volume_Error','IoU']:
            a=sorted(float(x[k]) for x in d if x[k] not in ('',None)); w.writerow([m,1000,sum(x['STEP_Reload']=='1' for x in d),sum(x['denominator_method_valid']=='1' for x in d),k,len(a) and sum(a)/len(a) or '',a[len(a)//2] if a else '',max(a) if a else '',len(common)])
(O/'reports/BASELINE_COMPARISON_SUMMARY.md').write_text(f'''# Baseline Comparison Summary\n\nCADFit full inference and unified evaluation completed for {len(cadrows)}/1000 cases. P1/CAD-Recode/CADFit strict common-valid denominator: {len(common)}.\n\nPer-method-valid and strict common-valid values are in the CSV tables. Every row retains its exact case ID, input path, prediction/STEP path, denominator and failure reason. DeepCAD remains pending frozen prediction alignment; Cadrille remains audit-only.\n''')
print(json.dumps({'cadfit_total':1000,'prediction_n':sum(bool(x['prediction_path']) for x in cadrows),'step_reload_n':sum(x['step_reload_success'] for x in cadrows),'geometry_valid_n':sum(x['geometry_eval_success'] for x in cadrows),'iou_valid_n':sum(x['iou'] not in ('',None) for x in cadrows),'strict_common_n':len(common)},indent=2))
