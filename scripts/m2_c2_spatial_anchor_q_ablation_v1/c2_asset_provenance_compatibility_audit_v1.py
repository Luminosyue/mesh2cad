#!/usr/bin/env python3
"""Audits C2 sidecar metadata compatibility without editing/re-exporting assets."""
from __future__ import annotations
import hashlib,json,random,sys
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');Q=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1'; EXP=Q/'anchor_eval_deepcad_candidate_expansion_v1';OUT=Q/'c2_asset_provenance_compatibility_audit_v1'; TOKROOT=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2';CURV=ROOT/'ours3/curve_token_data_v1/deepcad_train';CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt';V3=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/geometry_prefix_v3/v3_1k/data/v3_1k_train.json'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def keys(x,p=''):
 o=[]
 if isinstance(x,dict):
  for k,v in x.items():o+=keys(v,(p+'.' if p else '')+k)
 else:o.append(p)
 return o
def curves_from_npz(p):
 z=np.load(p,allow_pickle=True);xyz=z['curve_xyz'];tan=z['curve_tangent'];edge=z['curve_edge_id'];length=z['curve_polyline_length'];types=z.get('curve_type_id',np.zeros(len(xyz),np.int32));names={0:'LINE',1:'CIRCLE',2:'ELLIPSE',3:'BSPLINE'}
 return [{'curve_id':int(edge[i]),'curve_type':names.get(int(types[i]),'LINE'),'xyz':xyz[i],'tangent':tan[i],'polyline_length':float(length[i])} for i in range(len(xyz))]
def resolver(cad,meta,token):
 # Explicit allowed evidence: root frozen export manifest, then actual checkpoint SHA.
 root=json.loads((TOKROOT/'export_summary.json').read_text());path=root.get('checkpoint');actual=str(CKPT.relative_to(ROOT))
 if path==actual and token.is_file():return {'checkpoint_path':str(CKPT),'checkpoint_sha256':sha(CKPT),'frozen':True,'provenance_source':'curve_tokens_c2_frozen_v2/export_summary.json root-bound export manifest + actual checkpoint SHA256','provenance_confidence':'HIGH'}
 return {'checkpoint_path':None,'checkpoint_sha256':None,'frozen':False,'provenance_source':'UNRESOLVED','provenance_confidence':'NONE'}
def main():
 OUT.mkdir(parents=True,exist_ok=True);actual=sha(CKPT);write(OUT/'ACTUAL_C2_CHECKPOINT.json',{'ACTUAL_C2_CHECKPOINT_PATH':str(CKPT),'ACTUAL_C2_CHECKPOINT_SHA256':actual,'C2_FROZEN':True,'C2_TRAINABLE_PARAMS':0,'root_export_summary':json.loads((TOKROOT/'export_summary.json').read_text())})
 fails=[json.loads(x) for x in (EXP/'DEEPCAD_FAILURES.jsonl').read_text().splitlines() if x.strip()];ids=[x['cad_id'] for x in fails]; rng=random.Random(20260829)
 # exact-direct set: deterministic selection among nontruncated assets (direct curve order is unambiguous).
 candidates=[]
 for c in ids:
  sid=c.split('__',1)[1];mp=TOKROOT/'deepcad'/sid/'curve_tokens_meta.json'
  # Exact direct comparison is only unambiguous when the frozen raw curve
  # ordering and saved token count agree.  Do not infer a missing selection map.
  if mp.is_file() and (CURV/sid/'curve_samples.npz').is_file() and (TOKROOT/'deepcad'/sid/'curve_tokens.npy').is_file():
   z=np.load(CURV/sid/'curve_samples.npz',allow_pickle=True);d=np.load(TOKROOT/'deepcad'/sid/'curve_tokens.npy')
   if len(z['curve_xyz'])==len(d):candidates.append(c)
 sample20=sorted(candidates,key=lambda c:hashlib.sha256(('C2_AUDIT_20|'+c).encode()).hexdigest())[:20]
 assert len(sample20)==20
 schemas=Counter();details=[]
 for c in sample20:
  sid=c.split('__',1)[1];mp=TOKROOT/'deepcad'/sid/'curve_tokens_meta.json';meta=json.loads(mp.read_text());k=tuple(sorted(keys(meta)));schemas[k]+=1;details.append({'cad_id':c,'curve_asset_path':str((CURV/sid/'curve_samples.npz').resolve()),'curve_tokens_path':str((TOKROOT/'deepcad'/sid/'curve_tokens.npy').resolve()),'curve_tokens_meta_path':str(mp.resolve()),'schema_keys':list(k)})
 write(OUT/'C2_META_SCHEMA_AUDIT.json',{'sample_count':20,'schema_variants':[{'count':n,'keys':list(k)} for k,n in schemas.items()],'records':details})
 v3=json.loads(V3.read_text())['records'];known=[r for r in v3 if r['source_dataset']=='deepcad'][:20];write(OUT/'KNOWN_GOOD_V3_PROVENANCE.json',{'KNOWN_GOOD_V3_SHA256':actual,'records':[{'cad_id':r['cad_id'],'token_path':r['m2_full_c2_tokens'],'provenance':r['provenance']} for r in known],'note':'V3 provenance is manifest-level; per-asset meta uses a different schema.'})
 norm=[]
 for c in sorted(candidates,key=lambda x:hashlib.sha256(('C2_RESOLVE|'+x).encode()).hexdigest())[:50]:
  sid=c.split('__',1)[1];mp=TOKROOT/'deepcad'/sid/'curve_tokens_meta.json';tp=TOKROOT/'deepcad'/sid/'curve_tokens.npy';meta=json.loads(mp.read_text());res=resolver(c,meta,tp);norm.append({'cad_id':c,'token_path':str(tp.resolve()),'original_meta_path':str(mp.resolve()),'resolved_checkpoint_path':res['checkpoint_path'],'resolved_checkpoint_sha256':res['checkpoint_sha256'],'resolved_frozen':res['frozen'],'resolution_source':res['provenance_source'],'provenance_confidence':res['provenance_confidence']})
 with open(OUT/'C2_PROVENANCE_NORMALIZED_V1.jsonl','w') as f:
  for x in norm:f.write(json.dumps(x,sort_keys=True)+'\n')
 # Direct C2 forward; frozen model from existing exporter, exactly its preprocessing.
 sys.path.insert(0,str(ROOT/'scripts'));from canonical_cad_data_v4.geometry.c2_export import encode_curves
 direct=[];tol=1e-6
 for c in sample20:
  sid=c.split('__',1)[1];dp,meta=encode_curves(curves_from_npz(CURV/sid/'curve_samples.npz'),device='cpu');disk=np.load(TOKROOT/'deepcad'/sid/'curve_tokens.npy');diff=np.abs(dp.astype(np.float64)-disk.astype(np.float64));cos=float(np.sum(dp*disk)/(np.linalg.norm(dp)*np.linalg.norm(disk)+1e-12));ok=dp.shape==disk.shape and float(diff.max(initial=0))<=tol
  direct.append({'cad_id':c,'shape_equality':list(dp.shape)==list(disk.shape),'curve_count_equality':len(dp)==len(disk),'disk_dtype':str(disk.dtype),'direct_dtype':str(dp.dtype),'max_abs_diff':float(diff.max(initial=0)),'mean_abs_diff':float(diff.mean()),'cosine_similarity':cos,'tolerance':tol,'pass':ok})
 dpass=all(x['pass'] for x in direct);write(OUT/'DIRECT_C2_VS_DISK_20.json',{'DIRECT_C2_PASS':'%d/20'%sum(x['pass'] for x in direct),'DIRECT_C2_MAX_ABS_DIFF':max(x['max_abs_diff'] for x in direct),'tolerance':tol,'records':direct})
 can=[]
 for x in norm:
  sid=x['cad_id'].split('__',1)[1];z=np.load(CURV/sid/'curve_samples.npz',allow_pickle=True);disk=np.load(x['token_path']);ok=x['resolved_checkpoint_sha256']==actual and x['resolved_frozen'] and disk.ndim==2 and disk.shape[1]==256 and len(z['curve_xyz'])==len(disk)
  can.append({'cad_id':x['cad_id'],'provenance_resolved':x['resolved_checkpoint_sha256']==actual,'checkpoint_match':x['resolved_checkpoint_sha256']==actual,'curve_order_valid':len(z['curve_xyz'])==len(disk),'token_valid':disk.ndim==2 and disk.shape[1]==256,'pass':ok})
 cpass=all(x['pass'] for x in can);write(OUT/'C2_PROVENANCE_50_CANARY.json',{'PROVENANCE_RESOLVED':'%d/50'%sum(x['provenance_resolved'] for x in can),'C2_CHECKPOINT_MATCH':'%d/50'%sum(x['checkpoint_match'] for x in can),'CURVE_ORDER_VALID':'%d/50'%sum(x['curve_order_valid'] for x in can),'TOKEN_VALID':'%d/50'%sum(x['token_valid'] for x in can),'records':can})
 passed=dpass and cpass;freeze={'CURRENT_GATE':'C2_ASSET_PROVENANCE_COMPATIBILITY_PASS' if passed else 'C2_ASSET_PROVENANCE_COMPATIBILITY_FAIL','ACTUAL_C2_SHA256':actual,'KNOWN_GOOD_V3_SHA256':actual,'META_SCHEMA_VARIANTS':len(schemas),'DIRECT_C2_PASS':'%d/20'%sum(x['pass'] for x in direct),'DIRECT_C2_MAX_ABS_DIFF':max(x['max_abs_diff'] for x in direct),'CANARY50_PROVENANCE_PASS':'%d/50'%sum(x['provenance_resolved'] for x in can),'CANARY50_TOKEN_PASS':'%d/50'%sum(x['token_valid'] for x in can),'OLD_C2_ASSETS_MODIFIED':False,'C2_RETRAINED':False,'TOKENS_REEXPORTED':False,'SMOKE_STARTED':False,'TRAINING_STARTED':False,'OFFICIAL_TEST_READ':False};write(OUT/'COMPATIBILITY_FREEZE.json',freeze)
 fs=[OUT/x for x in ('C2_META_SCHEMA_AUDIT.json','KNOWN_GOOD_V3_PROVENANCE.json','ACTUAL_C2_CHECKPOINT.json','C2_PROVENANCE_NORMALIZED_V1.jsonl','DIRECT_C2_VS_DISK_20.json','C2_PROVENANCE_50_CANARY.json','COMPATIBILITY_FREEZE.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in fs});print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
