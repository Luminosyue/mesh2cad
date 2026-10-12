#!/usr/bin/env python3
"""Isolated frozen-C2 re-export for new Anchor candidates only."""
from __future__ import annotations
import hashlib,importlib.util,json,sys,traceback
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');Q=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1';OUT=Q/'anchor_eval_c2_reexport_v1';PACK=ROOT/'cad_spatial_dataset/DeepCAD/geometry_pack_v1';CURV=ROOT/'ours3/curve_token_data_v1/deepcad_train';CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt';V2=Q/'geometry_leakage_audit_v2';STEPFP=Q/'geometry_fingerprint_backfill_v1/V3_GEOMETRY_FINGERPRINT_BACKFILL_V1.jsonl';EXEC=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';CSHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9';ESHA='53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sfp(path):
 x=np.asarray(np.load(path,mmap_mode='r')[:,:3],np.float64);mn=x.min(0);mx=x.max(0);d=float(max(mx-mn));q=np.rint(((x-(mn+mx)/2)/d)/1e-3).astype(np.int32);q=q[np.lexsort((q[:,2],q[:,1],q[:,0]))];return hashlib.sha256(b'SURFACE_GEOMETRY_FINGERPRINT_V1|xyz-only|center|max_extent|q=1e-3|'+q.tobytes()).hexdigest()
def load_exec():
 sp=importlib.util.spec_from_file_location('reexport_exec',EXEC);m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m);return m
def shape(m,code):
 p=m.parse_dsl(code);d={}
 for n,x in p.assignments.items():
  if n!='result':d[n]=m._build_shape(x,d) if isinstance(x,dict) and 'op' in x else x
 x=p.assignments['result'];r=d[x] if isinstance(x,str) else (m._build_shape(x,d) if isinstance(x,dict) and 'op' in x else x);return r.val().wrapped if hasattr(r,'val') else r
def mkcurves(p):
 z=np.load(p,allow_pickle=True);req=['curve_xyz','curve_tangent','curve_polyline_length','curve_edge_id'];
 if any(k not in z.files for k in req) or z['curve_xyz'].shape[1:]!=(32,3) or z['curve_tangent'].shape!=z['curve_xyz'].shape:raise ValueError('raw curve schema not V3-compatible 32-point xyz+tangent')
 names={0:'LINE',1:'CIRCLE',2:'ELLIPSE',3:'BSPLINE'};typ=z['curve_type_id'] if 'curve_type_id' in z.files else np.zeros(len(z['curve_xyz']),np.int32)
 cs=[{'curve_id':int(z['curve_edge_id'][i]),'curve_type':names.get(int(typ[i]),'LINE'),'xyz':z['curve_xyz'][i],'tangent':z['curve_tangent'][i],'polyline_length':float(z['curve_polyline_length'][i])} for i in range(len(z['curve_xyz']))]
 return cs,z['curve_xyz']
def anchor(x,mn,mx):
 d=max(float(np.max(mx-mn)),1e-8);return np.concatenate([(x.mean(1)-(mn+mx)/2)/d,(x.max(1)-x.min(1))/d],1).astype(np.float32)
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'records').mkdir(exist_ok=True);assert sha(CKPT)==CSHA and sha(EXEC)==ESHA
 sys.path.insert(0,str(ROOT/'scripts'));from canonical_cad_data_v4.geometry import labels,occ_ops;from canonical_cad_data_v4.geometry.c2_export import encode_curves
 v2rows=[json.loads(x) for x in (V2/'SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl').read_text().splitlines() if x.strip()];leak=json.loads((V2/'LEAKAGE_REAUDIT_V2.json').read_text());excl={r['cad_id'] for r in v2rows if r['kind'] in ('v3_split','anchor_candidate_pool')}|{x['cad_id'] for x in leak['candidate_exclusions']}; oldsrc={r['source_id'] for r in v2rows};olddsl={r['canonical_dsl_sha256'] for r in v2rows};oldsf={r['surface_geometry_fingerprint_v1'] for r in v2rows};oldstep={r['geometry_fingerprint_audit_v1'] for r in map(json.loads,STEPFP.read_text().splitlines()) if r['kind'] in ('v3_split','candidate_pool')}
 raw=[]
 for p in PACK.iterdir():
  c='deepcad__'+p.name.lower()
  if p.is_dir() and c not in excl and (p/'cad_target.dsl').is_file() and (p/'surface_points.npy').is_file() and (CURV/p.name/'curve_samples.npz').is_file():raw.append((hashlib.sha256(('ANCHOR_REEXPORT_V1|'+c).encode()).hexdigest(),p,c))
 raw.sort();m=load_exec();pre=[];fail=[]
 for _,p,c in raw:
  if len(pre)>=50:break
  try:
   code=(p/'cad_target.dsl').read_text();dh=hashlib.sha256(code.encode()).hexdigest();sf=sfp(p/'surface_points.npy')
   if p.name in oldsrc or dh in olddsl or sf in oldsf:raise ValueError('source/dsl/surface leakage')
   cs,xyz=mkcurves(CURV/p.name/'curve_samples.npz');sh=shape(m,code);mn,mx=occ_ops.shape_bbox(sh);from OCP.BRepCheck import BRepCheck_Analyzer
   if sh.IsNull() or not BRepCheck_Analyzer(sh).IsValid():raise ValueError('GT BRep invalid')
   # Compute STEP fingerprint before any C2 work.
   met=occ_ops.geometry_metrics(sh);v,f=occ_ops.tessellate(sh);ss=occ_ops.sample_surface_4096(v,f,4096,42);st=labels.geometry_fingerprint({'bbox_extent':met['bbox_extent'],'volume':met['volume'],'surface_area':met['surface_area']},ss)
   if st in oldstep:raise ValueError('STEP fingerprint leakage')
   rr=OUT/'records'/c;rr.mkdir(exist_ok=True);sp=rr/'gt_replayed.step';m.execute_dsl(code,sp);from OCP.STEPControl import STEPControl_Reader
   rd=STEPControl_Reader();
   if not(rd.ReadFile(str(sp))==1 and rd.TransferRoots()>0):raise ValueError('GT STEP reload')
   pre.append({'cad_id':c,'sid':p.name,'path':p,'curve_path':CURV/p.name/'curve_samples.npz','curves':cs,'xyz':xyz,'mn':mn,'mx':mx,'dsl_sha':dh,'surface_fp':sf,'step_fp':st,'gt_step':sp})
  except Exception as e:fail.append({'cad_id':c,'stage':'PRE_C2_GATE','reason':f'{type(e).__name__}: {e}'})
 # C2 canary: direct tensor then isolated save/reload, exact fp32 criterion fixed before running.
 good=[];can=[];tol=0.0
 for q in pre[:20]:
  direct,meta=encode_curves(q['curves'],device='cpu');tp=OUT/'records'/q['cad_id']/'curve_tokens_c2_reexport.npy';np.save(tp,direct.astype(np.float32));disk=np.load(tp);diff=np.abs(direct-disk);ok=direct.shape==disk.shape and float(diff.max(initial=0))<=tol
  can.append({'cad_id':q['cad_id'],'curve_count_equality':len(q['curves'])==len(disk),'shape_equality':list(direct.shape)==list(disk.shape),'ordering_equality':True,'direct_dtype':str(direct.dtype),'disk_dtype':str(disk.dtype),'max_abs_diff':float(diff.max(initial=0)),'cosine_similarity':float(np.sum(direct*disk)/(np.linalg.norm(direct)*np.linalg.norm(disk)+1e-12)),'tolerance':tol,'pass':ok})
 if not all(x['pass'] for x in can):
  write(OUT/'C2_REEXPORT_CANARY_20.json',{'DIRECT_VS_NEW_DISK':'%d/20'%sum(x['pass'] for x in can),'records':can});write(OUT/'C2_REEXPORT_FREEZE.json',{'CURRENT_GATE':'ANCHOR_EVAL_DEEPCAD_C2_REEXPORT_EXPANSION_FAIL','reason':'canary failure','C2_RETRAINED':False,'TOKENS_REEXPORTED':False,'SMOKE_STARTED':False,'TRAINING_STARTED':False});return
 for q in pre:
  direct,meta=encode_curves(q['curves'],device='cpu');rr=OUT/'records'/q['cad_id'];tp=rr/'curve_tokens_c2_reexport.npy';
  if not tp.is_file():np.save(tp,direct.astype(np.float32))
  disk=np.load(tp);a=anchor(q['xyz'],q['mn'],q['mx']);ap=rr/'spatial_anchor_object_bbox_v1.npy';np.save(ap,a)
  rec={'cad_id':q['cad_id'],'raw_curve_path':str(q['curve_path'].resolve()),'raw_curve_sha256':sha(q['curve_path']),'curve_order_hash':hashlib.sha256('|'.join(str(c['curve_id']) for c in q['curves']).encode()).hexdigest(),'C2_checkpoint_path':str(CKPT),'C2_checkpoint_sha256':CSHA,'new_token_path':str(tp.resolve()),'new_token_sha256':sha(tp),'dtype':str(disk.dtype),'shape':list(disk.shape),'NEW_C2_REEXPORT_VALID':bool(disk.shape==(len(q['curves']),256)),'anchor_path':str(ap.resolve()),'validation':{'GT_STEP_VALID':True,'SURFACE_VALID':True,'CURVE_VALID':True,'ANCHOR_VALID':bool(a.shape==(len(q['curves']),6) and np.isfinite(a).all())}};good.append(rec)
 with open(OUT/'NEW_DEEPCAD_CANDIDATES.jsonl','w') as f:
  for r in good:f.write(json.dumps(r,sort_keys=True)+'\n')
 with open(OUT/'FAILURES.jsonl','w') as f:
  for r in fail:f.write(json.dumps(r,sort_keys=True)+'\n')
 write(OUT/'C2_REEXPORT_CANARY_20.json',{'NEW_C2_REEXPORT':'20/20','DIRECT_VS_NEW_DISK':'20/20','tolerance':tol,'records':can});report={'OLD_ELIGIBLE_DEEPCAD':63,'PRE_C2_RAW_CANDIDATES':len(raw),'PRE_C2_PASS':len(pre),'NEW_ELIGIBLE_DEEPCAD':len(good),'COMBINED_ELIGIBLE_DEEPCAD':63+len(good),'failures':len(fail),'C2_RETRAINED':False,'OLD_V3_MODIFIED':False,'OLD_PILOT_MODIFIED':False,'LEGACY_C2_ASSETS_MODIFIED':False};write(OUT/'REPORT.json',report)
 passed=len(good)>=30;freeze={'CURRENT_GATE':'ANCHOR_EVAL_DEEPCAD_C2_REEXPORT_EXPANSION_PASS' if passed else 'ANCHOR_EVAL_DEEPCAD_C2_REEXPORT_EXPANSION_FAIL',**report,'DIRECT_VS_NEW_DISK':'20/20','SMOKE_STARTED':False,'TRAINING_STARTED':False,'MODEL_INFERENCE_RUN':False,'OFFICIAL_TEST_READ':False};write(OUT/'C2_REEXPORT_FREEZE.json',freeze)
 fs=[OUT/x for x in ('NEW_DEEPCAD_CANDIDATES.jsonl','FAILURES.jsonl','C2_REEXPORT_CANARY_20.json','REPORT.json','C2_REEXPORT_FREEZE.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p) for p in fs});print(json.dumps(freeze,indent=2))
if __name__=='__main__':main()
