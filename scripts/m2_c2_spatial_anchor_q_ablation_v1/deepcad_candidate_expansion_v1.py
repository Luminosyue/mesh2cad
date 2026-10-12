#!/usr/bin/env python3
"""Build new V3-compatible DeepCAD candidates only; no model inference/training."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,traceback
from collections import Counter
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); PACK=ROOT/'cad_spatial_dataset/DeepCAD/geometry_pack_v1'; CURVES=ROOT/'ours3/curve_token_data_v1/deepcad_train'; TOKENS=ROOT/'ours3/spatiallm_curve_token_v1/curve_tokens_c2_frozen_v2/deepcad'; OUT=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/anchor_eval_deepcad_candidate_expansion_v1'; V2=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_leakage_audit_v2'; STEPFP=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1/geometry_fingerprint_backfill_v1/V3_GEOMETRY_FINGERPRINT_BACKFILL_V1.jsonl'; EXEC=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py'; C2=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt'; ESHA='53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'; CSHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sfp(path):
 a=np.load(path,mmap_mode='r');x=np.asarray(a[:,:3],np.float64)
 if x.ndim!=2 or x.shape[1]!=3 or not len(x) or not np.isfinite(x).all():raise ValueError('invalid surface')
 mn=x.min(0);mx=x.max(0);d=float(max(mx-mn));
 if d<=0:raise ValueError('degenerate surface')
 q=np.rint(((x-(mn+mx)/2)/d)/1e-3).astype(np.int32);q=q[np.lexsort((q[:,2],q[:,1],q[:,0]))]
 return hashlib.sha256(b'SURFACE_GEOMETRY_FINGERPRINT_V1|xyz-only|center|max_extent|q=1e-3|'+q.tobytes()).hexdigest()
def load_exec():
 sp=importlib.util.spec_from_file_location('exp_frozen_executor',EXEC);m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m);return m
def shape(m,code):
 p=m.parse_dsl(code);d={}
 for n,node in p.assignments.items():
  if n!='result':d[n]=m._build_shape(node,d) if isinstance(node,dict) and 'op' in node else node
 n=p.assignments['result'];r=d[n] if isinstance(n,str) else (m._build_shape(n,d) if isinstance(n,dict) and 'op' in n else n);return r.val().wrapped if hasattr(r,'val') else r
def anchor(curve,mn,mx):
 den=max(float(np.max(mx-mn)),1e-8);return np.concatenate([(curve.mean(1)-(mn+mx)/2)/den,(curve.max(1)-curve.min(1))/den],1).astype(np.float32)
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'records').mkdir(exist_ok=True);assert sha(EXEC)==ESHA and sha(C2)==CSHA
 sys.path.insert(0,str(ROOT/'scripts'));from canonical_cad_data_v4.geometry import labels,occ_ops
 # Full V3 + all prior candidate identities are exclusions; V2 is the frozen surface guard.
 v2rows=[json.loads(x) for x in (V2/'SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl').read_text().splitlines() if x.strip()];leak=json.loads((V2/'LEAKAGE_REAUDIT_V2.json').read_text()); excl={r['cad_id'] for r in v2rows if r['kind'] in ('v3_split','anchor_candidate_pool')}|{x['cad_id'] for x in leak['candidate_exclusions']}; old_src={r['source_id'] for r in v2rows};old_dsl={r['canonical_dsl_sha256'] for r in v2rows};old_sf={r['surface_geometry_fingerprint_v1'] for r in v2rows}; oldstep={r['geometry_fingerprint_audit_v1'] for r in map(json.loads,STEPFP.read_text().splitlines()) if r['kind'] in ('v3_split','candidate_pool')}
 raw=[]
 for p in PACK.iterdir():
  if not p.is_dir():continue
  c='deepcad__'+p.name.lower()
  if c in excl:continue
  req=[p/'cad_target.dsl',p/'surface_points.npy',CURVES/p.name/'curve_samples.npz',TOKENS/p.name/'curve_tokens.npy',TOKENS/p.name/'curve_tokens_meta.json']
  if all(x.is_file() for x in req):raw.append((hashlib.sha256(('ANCHOR_EVAL_DEEPCAD_CANDIDATE_EXPANSION_V1|'+c).encode()).hexdigest(),p,c))
 raw.sort();write(OUT/'DEEPCAD_CANDIDATE_SOURCE_SCAN.json',{'raw_deepcad_dirs':len([x for x in PACK.iterdir() if x.is_dir()]),'exclusion_union_count':len(excl),'raw_asset_complete_after_source_exclusion':len(raw),'executor_sha256':ESHA,'c2_checkpoint':str(C2),'c2_sha256':CSHA,'task_definition':'V3-compatible existing geometry_pack_v1 DSL/surface/curve/C2 assets; no advanced grammar'})
 m=load_exec(); good=[];fail=[]
 from OCP.BRepCheck import BRepCheck_Analyzer
 from OCP.STEPControl import STEPControl_Reader
 for _,p,c in raw:
  if len(good)>=35:break
  try:
   code=(p/'cad_target.dsl').read_text(); dh=hashlib.sha256(code.encode()).hexdigest();surface=p/'surface_points.npy'; sf=sfp(surface)
   if p.name in old_src or dh in old_dsl or sf in old_sf:raise ValueError('cross-set source/dsl/surface overlap')
   sh=shape(m,code);mn,mx=occ_ops.shape_bbox(sh); nonnull=not sh.IsNull();brep=bool(nonnull and BRepCheck_Analyzer(sh).IsValid());
   if not brep:raise ValueError('invalid GT BRep')
   rr=OUT/'records'/c;rr.mkdir(exist_ok=True);step=rr/'gt_replayed.step';m.execute_dsl(code,step);rd=STEPControl_Reader();reload=rd.ReadFile(str(step))==1 and rd.TransferRoots()>0
   if not reload:raise ValueError('GT STEP reload failure')
   z=np.load(CURVES/p.name/'curve_samples.npz',allow_pickle=True);curve=np.asarray(z['curve_xyz'],np.float32);tok=np.load(TOKENS/p.name/'curve_tokens.npy');meta=json.loads((TOKENS/p.name/'curve_tokens_meta.json').read_text())
   if not(len(curve)>0 and tok.shape==(len(curve),256) and meta.get('C2_CHECKPOINT_SHA256')==CSHA):raise ValueError('invalid C2 asset/provenance')
   a=anchor(curve,mn,mx)
   if not(np.isfinite(a).all() and a.shape==(len(curve),6)):raise ValueError('invalid anchor')
   np.save(rr/'spatial_anchor_object_bbox_v1.npy',a); rawc=[{'curve_id':int(i),'xyz':curve[i].tolist()} for i in range(len(curve))];write(rr/'raw_curves.json',{'cad_id':c,'curves':rawc})
   # Existing original STEP fingerprint algorithm; fixed GT tessellation/surface seed=42.
   met=occ_ops.geometry_metrics(sh);verts,faces=occ_ops.tessellate(sh);ss=occ_ops.sample_surface_4096(verts,faces,4096,42);stfp=labels.geometry_fingerprint({'bbox_extent':met['bbox_extent'],'volume':met['volume'],'surface_area':met['surface_area']},ss)
   if stfp in oldstep:raise ValueError('STEP fingerprint overlap')
   r={'cad_id':c,'source_id':p.name,'canonical_dsl_sha256':dh,'surface_geometry_fingerprint_v1':sf,'geometry_fingerprint_audit_v1':stfp,'assets':{'canonical_gt_dsl':str((p/'cad_target.dsl').resolve()),'gt_step':str(step.resolve()),'surface':str(surface.resolve()),'raw_curves':str((rr/'raw_curves.json').resolve()),'curve_samples':str((CURVES/p.name/'curve_samples.npz').resolve()),'c2_tokens':str((TOKENS/p.name/'curve_tokens.npy').resolve()),'spatial_anchor':str((rr/'spatial_anchor_object_bbox_v1.npy').resolve())},'validation':{'GT_PARSE':True,'GT_EXECUTE':True,'GT_OCC_NON_NULL':nonnull,'GT_BREP_VALID':brep,'GT_STEP_WRITE':True,'GT_STEP_RELOAD':reload,'SURFACE_VALID':True,'CURVE_VALID':True,'C2_VALID':True,'ANCHOR_VALID':True},'c2_provenance':meta};good.append(r)
  except Exception as e:fail.append({'cad_id':c,'reason':f'{type(e).__name__}: {e}','trace':traceback.format_exc()[-800:]})
 with open(OUT/'DEEPCAD_NEW_CANDIDATES.jsonl','w') as f:
  for r in good:f.write(json.dumps(r,sort_keys=True)+'\n')
 with open(OUT/'DEEPCAD_ELIGIBLE_CANDIDATES.jsonl','w') as f:
  for r in good:f.write(json.dumps(r,sort_keys=True)+'\n')
 with open(OUT/'DEEPCAD_FAILURES.jsonl','w') as f:
  for r in fail:f.write(json.dumps(r,sort_keys=True)+'\n')
 leakout={'SOURCE_ID_OVERLAP':0,'DSL_HASH_OVERLAP':0,'SURFACE_FP_OVERLAP':0,'STEP_FP_OVERLAP':0,'FAMILY_OVERLAP_STATUS':'UNKNOWN','checked_against':'train800+decode_dev50+pilot150+prior eligible candidates+prior exclusions','prior_explicit_exclusion':'deepcad__0072_00724841:MISSING_GT_STEP'}
 dist={'OLD_ELIGIBLE_DEEPCAD':63,'NEW_RAW_DEEPCAD_CANDIDATES':len(raw),'NEW_ELIGIBLE_DEEPCAD':len(good),'COMBINED_ELIGIBLE_DEEPCAD':63+len(good),'GT_STEP_PASS':'%d/%d'%(len(good),len(good)),'SURFACE_PASS':'%d/%d'%(len(good),len(good)),'CURVE_PASS':'%d/%d'%(len(good),len(good)),'C2_PASS':'%d/%d'%(len(good),len(good)),'ANCHOR_PASS':'%d/%d'%(len(good),len(good)),'failure_count':len(fail)};write(OUT/'DEEPCAD_LEAKAGE_AUDIT.json',leakout);write(OUT/'DEEPCAD_DISTRIBUTION_REPORT.json',dist)
 passed=len(good)>=30;freeze={'CURRENT_GATE':'ANCHOR_EVAL_DEEPCAD_CANDIDATE_EXPANSION_PASS' if passed else 'ANCHOR_EVAL_DEEPCAD_CANDIDATE_EXPANSION_FAIL',**dist,**leakout,'SMOKE_STARTED':False,'TRAINING_STARTED':False,'MODEL_INFERENCE_RUN':False,'PILOT150_MODEL_RESULTS_READ':False,'OFFICIAL_TEST_READ':False};write(OUT/'EXPANSION_FREEZE.json',freeze)
 files=[OUT/x for x in ('DEEPCAD_CANDIDATE_SOURCE_SCAN.json','DEEPCAD_NEW_CANDIDATES.jsonl','DEEPCAD_ELIGIBLE_CANDIDATES.jsonl','DEEPCAD_FAILURES.jsonl','DEEPCAD_LEAKAGE_AUDIT.json','DEEPCAD_DISTRIBUTION_REPORT.json','EXPANSION_FREEZE.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in files});print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
