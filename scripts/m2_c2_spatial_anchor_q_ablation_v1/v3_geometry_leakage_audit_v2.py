#!/usr/bin/env python3
"""V2 leakage audit: GT/frozen surface canonical fingerprints only; no models."""
from __future__ import annotations
import hashlib,json,random
from collections import Counter
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_leakage_audit_v2'
SPLITDIR=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data'
POOL=ROOT/'ours3/canonical_cad_data_v4/records'
STEP_BACKFILL=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_fingerprint_backfill_v1/V3_GEOMETRY_FINGERPRINT_BACKFILL_V1.jsonl'
EXCLUDED='deepcad__0072_00724841'
CFG={'algorithm':'SURFACE_GEOMETRY_FINGERPRINT_V1','input':'frozen GT surface xyz only; normals excluded','normalization':'subtract xyz bbox center; divide by max bbox extent','quantization':1e-3,'ordering':'lexicographic x,y,z after quantization','seed':'not applicable; frozen surface input','finite_required':True}
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sid(c):return c.split('__',1)[1]
def surf_fp(path):
 a=np.load(path,mmap_mode='r'); xyz=np.asarray(a[:,:3],dtype=np.float64)
 if xyz.ndim!=2 or xyz.shape[1]!=3 or len(xyz)==0 or not np.isfinite(xyz).all():raise ValueError('invalid/nonfinite surface xyz')
 mn=xyz.min(0);mx=xyz.max(0); scale=float(np.max(mx-mn))
 if not np.isfinite(scale) or scale<=0:raise ValueError('degenerate surface bbox')
 q=np.rint(((xyz-(mn+mx)/2)/scale)/CFG['quantization']).astype(np.int32)
 q=q[np.lexsort((q[:,2],q[:,1],q[:,0]))]
 raw=json.dumps(CFG,sort_keys=True,separators=(',',':')).encode()+b'|'+q.tobytes()
 return hashlib.sha256(raw).hexdigest(),{'bbox_min':mn.tolist(),'bbox_max':mx.tolist(),'max_bbox_extent':scale,'point_count':int(len(xyz))}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 method={**CFG,'GT_ONLY':True,'MODEL_INFERENCE_RUN':False,'TRAINING_STARTED':False,'PILOT150_GT_SURFACE_READ_FOR_LEAKAGE':True,'PILOT150_MODEL_PREDICTIONS_READ':False,'PILOT150_MODEL_METRICS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False}
 write(OUT/'SURFACE_GEOMETRY_FINGERPRINT_METHOD.json',method)
 rows=[];fails=[]; bysplit={}
 for split,fn in [('train800','v3_1k_train.json'),('decode_dev50','v3_decode_dev_50.json'),('pilot150','v3_pilot_eval_150.json')]:
  for r in json.loads((SPLITDIR/fn).read_text())['records']:
   try:
    fp,meta=surf_fp(r['surface_input']); z={'kind':'v3_split','split':split,'cad_id':r['cad_id'],'source_id':sid(r['cad_id']),'source_dataset':r['source_dataset'],'canonical_dsl_sha256':r['target_dsl_sha256'],'surface_geometry_fingerprint_v1':fp,'surface_path':r['surface_input'],'surface_meta':meta}; rows.append(z);bysplit.setdefault(split,[]).append(z)
   except Exception as e:fails.append({'kind':'v3_split','split':split,'cad_id':r['cad_id'],'error':f'{type(e).__name__}: {e}'})
 candidates=[]; exclusions=[]
 for p in sorted(POOL.glob('*/metadata.json')):
  m=json.loads(p.read_text()); c=f"{m['source'].lower()}__{m['source_id'].lower()}"
  # Explicit protocol amendment record, even if this legacy row is otherwise
  # outside the clean/fair pool filters.
  if c==EXCLUDED:
   exclusions.append({'cad_id':c,'ANCHOR_CANDIDATE_EXCLUDED':True,'EXCLUSION_REASON':'MISSING_GT_STEP'});continue
  # Anchor candidates are exactly clean/fair DeepCAD/Fusion records; CADFS is not in scope.
  if m.get('source') not in ('DEEPCAD','FUSION360') or m.get('status')!='clean' or not m.get('fair_three_arm'):continue
  try:
   fp,meta=surf_fp(p.parent/'geometry/surface_4096.npy');z={'kind':'anchor_candidate_pool','split':'candidate_pool','cad_id':c,'source_id':m['source_id'],'source_dataset':m['source'].lower(),'canonical_dsl_sha256':m['canonical_dsl_sha256'],'surface_geometry_fingerprint_v1':fp,'surface_path':str((p.parent/'geometry/surface_4096.npy').resolve()),'surface_meta':meta};rows.append(z);candidates.append(z)
  except Exception as e:fails.append({'kind':'candidate_pool','cad_id':c,'error':f'{type(e).__name__}: {e}'})
 with open(OUT/'SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl','w') as f:
  for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
 # Same function, all sets: source / DSL / full surface comparisons.
 cross=[]
 for c in candidates:
  for split,oldrs in bysplit.items():
   for old in oldrs:
    for key in ('source_id','canonical_dsl_sha256','surface_geometry_fingerprint_v1'):
     if c[key]==old[key]:cross.append({'candidate_id':c['cad_id'],'old_split':split,'old_cad_id':old['cad_id'],'kind':key,'value':c[key]})
 # Existing step fingerprint remains deliberately incomplete: no invented entry for one pilot record.
 steprows=[json.loads(x) for x in STEP_BACKFILL.read_text().splitlines() if x.strip()]
 stby={r['cad_id']:r['geometry_fingerprint_audit_v1'] for r in steprows if r['kind']=='v3_split'}
 candidate_step={r['cad_id']:r['geometry_fingerprint_audit_v1'] for r in steprows if r['kind']=='candidate_pool'}
 stepover=[]
 for c in candidates:
  if c['cad_id'] in candidate_step:
   for oldid,fp in stby.items():
    if candidate_step[c['cad_id']]==fp:stepover.append({'candidate_id':c['cad_id'],'old_cad_id':oldid,'fingerprint':fp})
 # Deterministic rerun: at least 20 each source over V3 complete sets.
 rng=random.Random(20260829);det=[]
 for source in ('deepcad','fusion360'):
  avail=[r for r in rows if r['kind']=='v3_split' and r['source_dataset']==source];assert len(avail)>=20
  for r in rng.sample(avail,20):
   again,_=surf_fp(r['surface_path']);det.append({'cad_id':r['cad_id'],'source':source,'identical':again==r['surface_geometry_fingerprint_v1']})
 detok=len(det)==40 and all(x['identical'] for x in det)
 srcn=sum(x['kind']=='source_id' for x in cross); dsln=sum(x['kind']=='canonical_dsl_sha256' for x in cross); surf_n=sum(x['kind']=='surface_geometry_fingerprint_v1' for x in cross)
 # Raw-pool overlaps are audit findings, not permitted Anchor candidates.  Exclude
 # every source/DSL/surface collision; STEP collisions are excluded where a STEP FP exists.
 unsafe={x['candidate_id'] for x in cross}|{x['candidate_id'] for x in stepover}
 for c in candidates:
  if c['cad_id'] in unsafe: exclusions.append({'cad_id':c['cad_id'],'ANCHOR_CANDIDATE_EXCLUDED':True,'EXCLUSION_REASON':'CROSS_SET_LEAKAGE_MATCH'})
 eligible=[c for c in candidates if c['cad_id'] not in unsafe]
 guard_cross=[x for x in cross if x['candidate_id'] in {c['cad_id'] for c in eligible}]
 guard_step=[x for x in stepover if x['candidate_id'] in {c['cad_id'] for c in eligible}]
 repl=sorted((c for c in eligible if c['source_dataset']=='deepcad'),key=lambda c:hashlib.sha256(('V3_GEOMETRY_LEAKAGE_AUDIT_V2|replacement|'+c['cad_id']).encode()).hexdigest())[0]
 coverage={'TRAIN800_SURFACE_FP':'%d/800'%len(bysplit.get('train800',[])),'DEV50_SURFACE_FP':'%d/50'%len(bysplit.get('decode_dev50',[])),'PILOT150_SURFACE_FP':'%d/150'%len(bysplit.get('pilot150',[])),'V3_TOTAL_SURFACE_FP':'%d/1000'%sum(len(x) for x in bysplit.values()),'RAW_ANCHOR_CANDIDATE_SURFACE_FP':'%d/%d'%(len(candidates),len(candidates)+1),'ANCHOR_ELIGIBLE_CANDIDATE_SURFACE_FP':'%d/%d'%(len(eligible),len(eligible)),'STEP_FP_V3_TOTAL':'999/1000','STEP_FP_COMPLETE':False,'SURFACE_FP_COMPLETE':sum(len(x) for x in bysplit.values())==1000,'FULL_GEOMETRY_LEAKAGE_GUARD':bool(sum(len(x) for x in bysplit.values())==1000 and not guard_cross),'failures':fails}
 leak={'RAW_SOURCE_ID_OVERLAP':srcn,'RAW_DSL_HASH_OVERLAP':dsln,'RAW_STEP_FP_OVERLAP':len(stepover),'RAW_SURFACE_FP_OVERLAP':surf_n,'SOURCE_ID_OVERLAP':sum(x['kind']=='source_id' for x in guard_cross),'DSL_HASH_OVERLAP':sum(x['kind']=='canonical_dsl_sha256' for x in guard_cross),'STEP_FP_OVERLAP':len(guard_step),'SURFACE_FP_OVERLAP':sum(x['kind']=='surface_geometry_fingerprint_v1' for x in guard_cross),'STEP_FP_COMPLETE':False,'SURFACE_FP_COMPLETE':coverage['SURFACE_FP_COMPLETE'],'FULL_GEOMETRY_LEAKAGE_GUARD':coverage['FULL_GEOMETRY_LEAKAGE_GUARD'],'RAW_CANDIDATE_POOL_COUNT':len(candidates),'ANCHOR_ELIGIBLE_CANDIDATE_POOL_COUNT':len(eligible),'FAMILY_OVERLAP_STATUS':'UNKNOWN','cross_set_matches':cross,'step_fp_matches':stepover,'candidate_exclusions':exclusions,'DETERMINISTIC_REPLACEMENT_CANDIDATE':repl['cad_id'],'PILOT150_GT_SURFACE_READ_FOR_LEAKAGE':True,'PILOT150_MODEL_PREDICTIONS_READ':False,'PILOT150_MODEL_METRICS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False}
 write(OUT/'DETERMINISM_AUDIT.json',{'sampled':40,'deepcad':20,'fusion360':20,'FP_DETERMINISM_PASS':detok,'records':det});write(OUT/'SURFACE_FP_COVERAGE_REPORT.json',coverage);write(OUT/'LEAKAGE_REAUDIT_V2.json',leak)
 passed=not fails and coverage['SURFACE_FP_COMPLETE'] and len(eligible)>0 and detok and not guard_cross and not guard_step
 freeze={'CURRENT_GATE':'V3_GEOMETRY_LEAKAGE_AUDIT_V2_PASS' if passed else 'V3_GEOMETRY_LEAKAGE_AUDIT_V2_FAIL',**coverage,'SOURCE_ID_OVERLAP':leak['SOURCE_ID_OVERLAP'],'DSL_HASH_OVERLAP':leak['DSL_HASH_OVERLAP'],'STEP_FP_OVERLAP':leak['STEP_FP_OVERLAP'],'SURFACE_GEOMETRY_OVERLAP':leak['SURFACE_FP_OVERLAP'],'RAW_SOURCE_ID_OVERLAP':srcn,'RAW_DSL_HASH_OVERLAP':dsln,'RAW_SURFACE_GEOMETRY_OVERLAP':surf_n,'FP_DETERMINISM_PASS':detok,'PILOT150_MODEL_PREDICTIONS_READ':False,'PILOT150_MODEL_METRICS_READ':False,'PILOT150_REUSED_FOR_SELECTION':False,'OFFICIAL_TEST_READ':False,'SMOKE_STARTED':False,'TRAINING_STARTED':False}
 write(OUT/'V3_GEOMETRY_LEAKAGE_AUDIT_V2_FREEZE.json',freeze)
 files=[OUT/x for x in ('SURFACE_GEOMETRY_FINGERPRINT_METHOD.json','SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl','DETERMINISM_AUDIT.json','SURFACE_FP_COVERAGE_REPORT.json','LEAKAGE_REAUDIT_V2.json','V3_GEOMETRY_LEAKAGE_AUDIT_V2_FREEZE.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in files})
 print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
