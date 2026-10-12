#!/usr/bin/env python3
"""Operation-aligned parameter audit on the frozen 91-CAD common-valid pilot subset."""
from __future__ import annotations
import ast, json
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
PILOT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/pilot_eval_150_frozen_v1'
SPLIT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_pilot_eval_150.json'
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/reports/COMMON_VALID_91_PARAMETER_ERROR_AUDIT_V1.json'
ARMS={'B0':'b0_epoch09','B1_V3':'b1_epoch09','M2_V3':'m2_epoch10'}

def call_name(n): return n.func.id if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) else None
def scalar(n):
 try:
  x=ast.literal_eval(n)
  return float(x) if isinstance(x,(int,float)) else None
 except Exception:return None
def vector(n):
 try:
  x=ast.literal_eval(n)
  if isinstance(x,(tuple,list)) and all(isinstance(v,(int,float)) for v in x): return np.asarray(x,dtype=float)
 except Exception:pass
 return None
def calls(text):
 out=defaultdict(list)
 try: tree=ast.parse(text)
 except Exception:return out
 for n in ast.walk(tree):
  if isinstance(n,ast.Call) and call_name(n): out[call_name(n)].append(n)
 return out
def kw(c,name):
 for k in c.keywords:
  if k.arg==name:return k.value
 return None
def values(cs,name):
 out=[]
 for c in cs:
  n=kw(c,name)
  if n is not None:
   x=scalar(n)
   if x is not None:out.append(x)
 return out
def vecs(cs,name):
 out=[]
 for c in cs:
  n=kw(c,name)
  if n is not None:
   x=vector(n)
   if x is not None:out.append(x)
 return out
def summarize(x): return {'n':len(x),'median_abs_error':float(np.median(x)) if x else None,'p90_abs_error':float(np.quantile(x,.9)) if x else None}
def aligned_abs(a,b): return [abs(x-y) for x,y in zip(a,b)]
def aligned_vec(a,b): return [float(np.linalg.norm(x-y)) for x,y in zip(a,b)]
def refs(cs):
 out=[]
 for c in cs:
  out.append([a.id for a in c.args if isinstance(a,ast.Name)])
 return out
def main():
 if OUT.exists():raise FileExistsError(f'refusing overwrite {OUT}')
 targets={r['cad_id']:Path(r['target_dsl']).read_text() for r in json.loads(SPLIT.read_text())['records']}
 pred={k:{r['cad_id']:r for r in map(json.loads,(PILOT/v/'per_cad.jsonl').read_text().splitlines())} for k,v in ARMS.items()}
 common=set(targets)
 for q in pred.values(): common &= {i for i,r in q.items() if r['step_reload_success']}
 result={'subset':'pilot_eval_150 common STEP-valid intersection','common_valid_n':len(common),'official_test_read':False,'training_started':False,'arms':{}}
 for arm in ARMS:
  buckets=defaultdict(list); bool_total=bool_exact=0
  for cid in sorted(common):
   gt,pd=calls(targets[cid]),calls(pred[arm][cid]['generated_dsl'])
   for op,field,label in [('Extrude','height','extrusion_depth'),('Box','height','box_height'),('Box','width','profile_width'),('Box','depth','profile_depth'),('Circle','radius','circle_radius'),('Cylinder','radius','cylinder_radius')]:
    buckets[label]+=aligned_abs(values(gt[op],field),values(pd[op],field))
   for op,field,label in [('Extrude','origin','extrude_origin'),('Box','origin','box_origin'),('Cylinder','origin','cylinder_origin')]: buckets[label]+=aligned_vec(vecs(gt[op],field),vecs(pd[op],field))
   for op in ('Cut','Union'):
    a,b=refs(gt[op]),refs(pd[op]); bool_total+=min(len(a),len(b)); bool_exact+=sum(x==y for x,y in zip(a,b))
  result['arms'][arm]={'parameter_errors':{k:summarize(v) for k,v in sorted(buckets.items())},'boolean_reference':{'matched_calls':bool_total,'exact_reference_sequence':bool_exact,'exact_rate':bool(bool_total) and bool_exact/bool_total}}
 OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(result,indent=2)+'\n');print(OUT)
if __name__=='__main__':main()
