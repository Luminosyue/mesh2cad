#!/usr/bin/env python3
import argparse,json,statistics
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); B=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'
ap=argparse.ArgumentParser();ap.add_argument('--n',type=int,required=True);a=ap.parse_args();N=a.n
ids=[json.loads(x)['cad_id'] for x in (B/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()[:N]]
def load(arm):return {p.parent.name:json.loads(p.read_text()) for p in (B/'predictions'/arm).glob('*/row.json')}
x,y=load('a0'),load('a3');assert all(i in x and i in y for i in ids)
def rate(rows,k):return sum(bool(rows[i].get(k)) for i in ids)/N
def vals(rows,k):
 return [rows[i].get('geometry',{}).get(k) for i in ids if isinstance(rows[i].get('geometry',{}).get(k),(int,float))]
op0=[x[i]['op_f1'] for i in ids];op3=[y[i]['op_f1'] for i in ids];c0=vals(x,'chamfer_norm');c3=vals(y,'chamfer_norm')
r={'schema_version':'INTERIM_PAIRED_V2','paired_n':N,'FORMAL_RESULT':'NO','INTERIM_DIAGNOSTIC_ONLY':'YES','DO_NOT_CHANGE_PROTOCOL':'YES','a0':{'exact':rate(x,'exact_match'),'op_f1':sum(op0)/N,'parse_rate':rate(x,'parsed'),'execution_rate':rate(x,'step_ok'),'step_export_rate':rate(x,'step_ok'),'step_reload':'DEFERRED_TO_FORMAL_BULK_RELOAD','exec_timeout_n':sum(bool(x[i].get('exec_timeout')) for i in ids),'geometry_valid_n':len(c0),'chamfer_mean':sum(c0)/len(c0) if c0 else None,'chamfer_median':statistics.median(c0) if c0 else None},'a3':{'exact':rate(y,'exact_match'),'op_f1':sum(op3)/N,'parse_rate':rate(y,'parsed'),'execution_rate':rate(y,'step_ok'),'step_export_rate':rate(y,'step_ok'),'step_reload':'DEFERRED_TO_FORMAL_BULK_RELOAD','exec_timeout_n':sum(bool(y[i].get('exec_timeout')) for i in ids),'geometry_valid_n':len(c3),'chamfer_mean':sum(c3)/len(c3) if c3 else None,'chamfer_median':statistics.median(c3) if c3 else None},'opf1_pair':{'a3_better_n':sum(b>a for a,b in zip(op0,op3)),'tie_n':sum(b==a for a,b in zip(op0,op3)),'a0_better_n':sum(b<a for a,b in zip(op0,op3))},'step_export_pair':{'a3_rescue_n':sum(not x[i].get('step_ok') and y[i].get('step_ok') for i in ids),'a3_regression_n':sum(x[i].get('step_ok') and not y[i].get('step_ok') for i in ids)}}
out=B/'interim'/f'INTERIM_PAIRED_N{N}.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(r,indent=2)+'\n');print(out)
