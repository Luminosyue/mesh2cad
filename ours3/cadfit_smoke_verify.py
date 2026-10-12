import csv, json, runpy, sys, traceback
from pathlib import Path
import cadquery as cq
B=Path('/data/home/cuiyuehan/project/mesh2cad/ours3'); C=B/'cadfit_val1000_baseline_v1'; R=C/'smoke10_runs'; V=B/'unified_step_geometry_evaluator_v2'
sys.path.insert(0,str(V)); from evaluator.unified_step_geometry_evaluator_v2 import load_adapted_shape, geometry_metrics, stable_seed
man={}
for line in (B/'m2_exact9998_a0_vs_a3_unified_val1000_eval_v1/manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines():
    if line.strip():
        x=json.loads(line); man[x['cad_id']]=Path(x['gt_step_path'])
out=[]
for cid in [x.strip() for x in (C/'smoke10_case_ids.txt').read_text().splitlines() if x.strip()]:
    d=R/cid; py=d/'best_greedy_parallel_iterative.py'; stl=d/'best_greedy_parallel_iterative.stl'; step=d/'cadfit_prediction.step'
    rec={'case_id':cid,'input_load':'PASS' if (C/'smoke10_input'/(cid+'.stl')).exists() else 'FAIL','cadfit_inference':'PASS' if (d/'final_iou.json').exists() else 'FAIL','prediction_artifact':'PASS' if py.exists() and stl.exists() else 'FAIL','step_export':'FAIL','step_reload':'FAIL','unified_evaluator':'FAIL','failure_reason':''}
    try:
        ns=runpy.run_path(str(py)); result=ns.get('result')
        if result is None: raise ValueError('generated program did not define result')
        cq.exporters.export(result,str(step)); rec['step_export']='PASS'
        pred=load_adapted_shape(step,'DATASET_CANONICAL'); gt=load_adapted_shape(man[cid],'DATASET_CANONICAL'); rec['step_reload']='PASS'
        m=geometry_metrics(pred,gt,10000,stable_seed(cid)); rec.update({'unified_evaluator':'PASS','chamfer':m['chamfer'],'h95':m['h95'],'volume_error':m['relative_volume_error']})
    except Exception as e:
        rec['failure_reason']=f'{type(e).__name__}: {e}'
    out.append(rec)
with (C/'smoke10_verification.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
print(json.dumps({'N':len(out),'all_pass':all(all(r[k]=='PASS' for k in ['input_load','cadfit_inference','prediction_artifact','step_export','step_reload','unified_evaluator']) for r in out),'rows':out},indent=2))
