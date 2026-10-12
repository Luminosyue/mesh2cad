#!/usr/bin/env python3
"""Strict GT-only geometry-fingerprint backfill; no model code is loaded."""
from __future__ import annotations
import hashlib, importlib.util, json, random, sys, traceback
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_fingerprint_backfill_v1'
SPLITDIR=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
POOL=ROOT/'ours3/canonical_cad_data_v4/records'
EXEC=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'
LABELS=ROOT/'scripts/canonical_cad_data_v4/geometry/labels.py'
OCCOPS=ROOT/'scripts/canonical_cad_data_v4/geometry/occ_ops.py'
EXEC_SHA='53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for x in iter(lambda:f.read(1<<20),b''):h.update(x)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def cid(source,sid): return f'{source.lower()}__{sid.lower()}'
def load_exec():
 sp=importlib.util.spec_from_file_location('fp_frozen_executor',EXEC); m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m);return m
def shape_from_dsl(m,code):
 p=m.parse_dsl(code); shapes={}
 for n,node in p.assignments.items():
  if n!='result': shapes[n]=m._build_shape(node,shapes) if isinstance(node,dict) and 'op' in node else node
 node=p.assignments['result']; r=shapes[node] if isinstance(node,str) else (m._build_shape(node,shapes) if isinstance(node,dict) and 'op' in node else node)
 return r.val().wrapped if hasattr(r,'val') else r
def fp_from_shape(shape, labels, occops):
 # Exactly original labels.geometry_fingerprint configuration/function; GT shape -> fixed tessellation + seed=42 surface.
 met=occops.geometry_metrics(shape); verts,faces=occops.tessellate(shape); surf=occops.sample_surface_4096(verts,faces,4096,42)
 rec={'bbox_extent':met['bbox_extent'],'volume':met['volume'],'surface_area':met['surface_area']}
 return labels.geometry_fingerprint(rec,surf),met
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if sha(EXEC)!=EXEC_SHA: raise RuntimeError('frozen executor hash mismatch')
 sys.path.insert(0,str(ROOT/'scripts'))
 from canonical_cad_data_v4.geometry.labels import geometry_fingerprint
 from canonical_cad_data_v4.geometry import labels,occ_ops
 executor=load_exec()
 prov={'FOUND_EXISTING_IMPLEMENTATION':True,'IMPLEMENTATION_PATH':str(LABELS),'IMPLEMENTATION_SHA256':sha(LABELS),'ALGORITHM_VERSION':'canonical_cad_data_v4.geometry.labels.geometry_fingerprint (existing)','INPUT_TYPE':'GT OCC shape metrics plus GT shape tessellation/surface sample','CONFIG':{'bbox_decimals':4,'metric_decimals':4,'xyz_quant':1e-3,'surface_points':4096},'SEED':42,'NORMALIZATION':'bbox_diag for extents/volume/area and xyz quantization; exactly existing implementation','EXECUTOR_PATH':str(EXEC),'EXECUTOR_SHA256':EXEC_SHA,'PILOT150_GT_GEOMETRY_READ_FOR_FINGERPRINT_BACKFILL':True,'PILOT150_MODEL_PREDICTIONS_READ':False,'PILOT150_MODEL_METRICS_READ':False,'PILOT150_MODEL_STEP_READ':False,'PILOT150_QUALITATIVE_READ':False,'PILOT150_REUSED_FOR_SELECTION':False}
 write(OUT/'GEOMETRY_FINGERPRINT_PROVENANCE_SEARCH.json',prov);write(OUT/'GEOMETRY_FINGERPRINT_METHOD.json',prov)
 rows=[]; failures=[]
 # All 1000 split records: GT target DSL only; no model assets/results read.
 for split,fn in [('train800','v3_1k_train.json'),('decode_dev50','v3_decode_dev_50.json'),('pilot150','v3_pilot_eval_150.json')]:
  for r in json.loads((SPLITDIR/fn).read_text())['records']:
   try:
    sh=shape_from_dsl(executor,Path(r['target_dsl']).read_text()); fp,met=fp_from_shape(sh,labels,occ_ops)
    rows.append({'kind':'v3_split','split':split,'cad_id':r['cad_id'],'source_dataset':r['source_dataset'],'source_id':r['cad_id'].split('__',1)[1],'canonical_dsl_sha256':r['target_dsl_sha256'],'geometry_fingerprint_audit_v1':fp,'fingerprint_input':'GT target DSL -> frozen executor -> GT OCC shape -> fixed seed surface','geometry_metrics':met})
   except Exception as e: failures.append({'kind':'v3_split','split':split,'cad_id':r['cad_id'],'error':f'{type(e).__name__}: {e}','trace':traceback.format_exc()[-1200:]})
 # Entire candidate pool uses its frozen canonical GT STEP; no old field is mixed in.
 for mp in sorted(POOL.glob('*/metadata.json')):
  m=json.loads(mp.read_text()); c=cid(m['source'],m['source_id'])
  try:
   sh=occ_ops.load_step_shape(Path(m['canonical_step_path'])); fp,met=fp_from_shape(sh,labels,occ_ops)
   rows.append({'kind':'candidate_pool','split':'candidate_pool','cad_id':c,'source_dataset':m['source'].lower(),'source_id':m['source_id'],'canonical_dsl_sha256':m['canonical_dsl_sha256'],'geometry_fingerprint_audit_v1':fp,'fingerprint_input':'GT canonical STEP -> GT OCC shape -> fixed seed surface','geometry_metrics':met})
  except Exception as e: failures.append({'kind':'candidate_pool','cad_id':c,'error':f'{type(e).__name__}: {e}','trace':traceback.format_exc()[-1200:]})
 with open(OUT/'V3_GEOMETRY_FINGERPRINT_BACKFILL_V1.jsonl','w') as f:
  for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
 # Determinism reruns (same exact input function) require 20 each source from V3 splits.
 by={}
 for r in rows:
  if r['kind']=='v3_split':by.setdefault(r['source_dataset'],[]).append(r)
 det=[]; rng=random.Random(20260829)
 for source in ('deepcad','fusion360'):
  sample=rng.sample(by.get(source,[]),20)
  for r in sample:
   try:
    sh=shape_from_dsl(executor,Path(next(x['target_dsl'] for x in json.loads((SPLITDIR/({'train800':'v3_1k_train.json','decode_dev50':'v3_decode_dev_50.json','pilot150':'v3_pilot_eval_150.json'}[r['split']])).read_text())['records'] if x['cad_id']==r['cad_id'])).read_text())
    second,_=fp_from_shape(sh,labels,occ_ops); det.append({'cad_id':r['cad_id'],'source':source,'equal':second==r['geometry_fingerprint_audit_v1']})
   except Exception as e: det.append({'cad_id':r['cad_id'],'source':source,'equal':False,'error':str(e)})
 write(OUT/'DETERMINISM_AUDIT.json',{'sampled':len(det),'deepcad':sum(x['source']=='deepcad' for x in det),'fusion360':sum(x['source']=='fusion360' for x in det),'FP_DETERMINISM_PASS':len(det)==40 and all(x['equal'] for x in det),'rerun_equality':'%d/%d'%(sum(x['equal'] for x in det),len(det)),'records':det})
 counts={s:sum(r['kind']=='v3_split' and r['split']==s for r in rows) for s in ('train800','decode_dev50','pilot150')}; pooln=sum(r['kind']=='candidate_pool' for r in rows)
 splitrows={s:[r for r in rows if r['kind']=='v3_split' and r['split']==s] for s in counts}; cand=[r for r in rows if r['kind']=='candidate_pool']
 overlap=[]
 for c in cand:
  for s,rr in splitrows.items():
   for key in ('source_id','canonical_dsl_sha256','geometry_fingerprint_audit_v1'):
    for old in rr:
     if c[key]==old[key]:overlap.append({'candidate_id':c['cad_id'],'old_split':s,'old_cad_id':old['cad_id'],'key':key,'value':c[key]})
 leakage={'SOURCE_ID_OVERLAP':sum(x['key']=='source_id' for x in overlap),'DSL_HASH_OVERLAP':sum(x['key']=='canonical_dsl_sha256' for x in overlap),'GEOMETRY_FINGERPRINT_OVERLAP':sum(x['key']=='geometry_fingerprint_audit_v1' for x in overlap),'duplicates':overlap,'FAMILY_OVERLAP_STATUS':'UNKNOWN','PILOT150_MODEL_RESULTS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False}
 write(OUT/'LEAKAGE_REAUDIT.json',leakage)
 coverage={'TRAIN800_FINGERPRINT':'%d/800'%counts['train800'],'DEV50_FINGERPRINT':'%d/50'%counts['decode_dev50'],'PILOT150_FINGERPRINT':'%d/150'%counts['pilot150'],'TOTAL_V3_FINGERPRINT':'%d/1000'%sum(counts.values()),'CANDIDATE_FP_COVERAGE':'%d/%d'%(pooln,len(list(POOL.glob('*/metadata.json')))),'failures':failures}
 write(OUT/'FINGERPRINT_COVERAGE_REPORT.json',coverage)
 detok=len(det)==40 and all(x['equal'] for x in det)
 passed=not failures and counts=={'train800':800,'decode_dev50':50,'pilot150':150} and pooln==len(list(POOL.glob('*/metadata.json'))) and detok
 freeze={'CURRENT_GATE':'V3_GEOMETRY_FINGERPRINT_BACKFILL_PASS' if passed else 'V3_GEOMETRY_FINGERPRINT_BACKFILL_FAIL',**coverage,'FP_DETERMINISM_PASS':detok,'PILOT150_MODEL_RESULTS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False,'OFFICIAL_TEST_READ':False,'SMOKE_STARTED':False,'TRAINING_STARTED':False}
 write(OUT/'BACKFILL_FREEZE.json',freeze)
 files=[OUT/x for x in ('GEOMETRY_FINGERPRINT_PROVENANCE_SEARCH.json','V3_GEOMETRY_FINGERPRINT_BACKFILL_V1.jsonl','GEOMETRY_FINGERPRINT_METHOD.json','DETERMINISM_AUDIT.json','FINGERPRINT_COVERAGE_REPORT.json','LEAKAGE_REAUDIT.json','BACKFILL_FREEZE.json')]
 write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in files})
 print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
