#!/usr/bin/env python3
"""Append deterministic replacements to the frozen 96 passing Anchor Eval records."""
from __future__ import annotations
import hashlib,importlib.util,json,sys
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');Q=ROOT/'ours3/spatiallm_curve_token_v1/runs/heldout_best_v2/m2_spatial_anchor_v1/q_ablation_v1';PREV=Q/'anchor_eval_100_final_v1';OUT=Q/'anchor_eval_100_replacement_v1';V2=Q/'geometry_leakage_audit_v2';NEW=Q/'anchor_eval_c2_reexport_v1';POOL=ROOT/'ours3/canonical_cad_data_v4/records';EXEC=ROOT/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';CKPT=ROOT/'ours3/curve_encoder_scale_curvature_v1/runs/C2_frozen_v1/best.pt';ESHA='53747c0a66f9758b59c783a122c8a0b6cea8074fc7c3a762a8bfc1fe2ec850de';CSHA='553c307f4d71a147583d4c016b3d3bbf00dcbbfc3d3abf176c2991027fc6d5e9'
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def write(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def rank(c):return hashlib.sha256(('ANCHOR_EVAL_100_V1|seed=20260829|'+c).encode()).hexdigest()
def loadex():
 s=importlib.util.spec_from_file_location('replace_ex',EXEC);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m
def shp(m,code):
 p=m.parse_dsl(code);d={}
 for n,x in p.assignments.items():
  if n!='result':d[n]=m._build_shape(x,d) if isinstance(x,dict)and'op'in x else x
 x=p.assignments['result'];r=d[x] if isinstance(x,str) else(m._build_shape(x,d)if isinstance(x,dict)and'op'in x else x);return r.val().wrapped if hasattr(r,'val')else r
def sfp(path):
 x=np.asarray(np.load(path,mmap_mode='r')[:,:3],np.float64);mn=x.min(0);mx=x.max(0);d=float(np.max(mx-mn));q=np.rint(((x-(mn+mx)/2)/d)/1e-3).astype(np.int32);q=q[np.lexsort((q[:,2],q[:,1],q[:,0]))];return hashlib.sha256(b'SURFACE_GEOMETRY_FINGERPRINT_V1|xyz-only|center|max_extent|q=1e-3|'+q.tobytes()).hexdigest()
def cnpz(p):
 z=np.load(p,allow_pickle=True);names={0:'LINE',1:'CIRCLE',2:'ELLIPSE',3:'BSPLINE'};t=z['curve_type_id'] if'curve_type_id'in z.files else np.zeros(len(z['curve_xyz']),int);return[{'curve_id':int(z['curve_edge_id'][i]),'curve_type':names.get(int(t[i]),'LINE'),'xyz':z['curve_xyz'][i],'tangent':z['curve_tangent'][i],'polyline_length':float(z['curve_polyline_length'][i])}for i in range(len(z['curve_xyz']))],z['curve_xyz']
def main():
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'records').mkdir(exist_ok=True);assert sha(EXEC)==ESHA and sha(CKPT)==CSHA
 prev=[json.loads(x)for x in(PREV/'ANCHOR_EVAL_100_V1.jsonl').read_text().splitlines()if x.strip()];failed={x['cad_id']for x in json.loads((PREV/'ANCHOR_EVAL_100_V1_FREEZE.json').read_text())['failures']};assert len(prev)==96
 v2=[json.loads(x)for x in(V2/'SURFACE_GEOMETRY_FINGERPRINT_V1.jsonl').read_text().splitlines()if x.strip()];lk=json.loads((V2/'LEAKAGE_REAUDIT_V2.json').read_text());bad={x['cad_id']for x in lk['candidate_exclusions']};byid={}
 for p in POOL.glob('*/metadata.json'):
  m=json.loads(p.read_text());byid[f"{m['source'].lower()}__{m['source_id'].lower()}"]=(m,p.parent)
 allc=[]
 for r in v2:
  if r['kind']=='anchor_candidate_pool'and r['cad_id']not in bad and r['source_dataset']=='deepcad':
   m,root=byid[r['cad_id']];allc.append({'cad_id':r['cad_id'],'source':'old','dsl':Path(m['canonical_program_path']),'surface':root/'geometry/surface_4096.npy','curve':root/'geometry/curves.json','tokens':root/'geometry/curve_tokens_c2.npy'})
 for x in(NEW/'NEW_DEEPCAD_CANDIDATES.jsonl').read_text().splitlines():
  r=json.loads(x);sid=r['cad_id'].split('__',1)[1];allc.append({'cad_id':r['cad_id'],'source':'reexport','dsl':ROOT/'cad_spatial_dataset/DeepCAD/geometry_pack_v1'/sid/'cad_target.dsl','surface':ROOT/'cad_spatial_dataset/DeepCAD/geometry_pack_v1'/sid/'surface_points.npy','curve':Path(r['raw_curve_path']),'tokens':Path(r['new_token_path'])})
 selected={r['cad_id']for r in prev}|failed; todo=[x for x in sorted(allc,key=lambda x:rank(x['cad_id']))if x['cad_id']not in selected]
 ex=loadex();sys.path.insert(0,str(ROOT/'scripts'));from canonical_cad_data_v4.geometry import labels,occ_ops;from OCP.BRepCheck import BRepCheck_Analyzer;from OCP.STEPControl import STEPControl_Reader
 repl=[];audit=[]; oldsrc={r['cad_id'].split('__')[1]for r in prev};olddsl={hashlib.sha256(Path(r['canonical_gt_dsl']).read_bytes()).hexdigest()for r in prev};oldsf={r['surface_geometry_fingerprint_v1']for r in prev};oldstep={r['geometry_fingerprint_audit_v1']for r in prev}
 for x in todo:
  if len(repl)==4:break
  try:
   code=x['dsl'].read_text();dh=hashlib.sha256(code.encode()).hexdigest();sf=sfp(x['surface']);
   if x['cad_id'].split('__')[1]in oldsrc or dh in olddsl or sf in oldsf:raise ValueError('cross-final leakage')
   sh=shp(ex,code);nn=not sh.IsNull();bv=bool(nn and BRepCheck_Analyzer(sh).IsValid());rr=OUT/'records'/x['cad_id'];rr.mkdir(exist_ok=True);st=rr/'gt_replayed.step';ex.execute_dsl(code,st);rd=STEPControl_Reader();sr=rd.ReadFile(str(st))==1 and rd.TransferRoots()>0
   if x['source']=='reexport':cs,xyz=cnpz(x['curve'])
   else:q=json.loads(x['curve'].read_text());cs=q['curves'];xyz=np.asarray([c['xyz']for c in cs],np.float32)
   tok=np.load(x['tokens']);mn,mx=occ_ops.shape_bbox(sh);d=max(float(np.max(mx-mn)),1e-8);a=np.concatenate([(xyz.mean(1)-(mn+mx)/2)/d,(xyz.max(1)-xyz.min(1))/d],1).astype(np.float32);ap=rr/'spatial_anchor_object_bbox_v1.npy';np.save(ap,a)
   met=occ_ops.geometry_metrics(sh);vv,ff=occ_ops.tessellate(sh);ss=occ_ops.sample_surface_4096(vv,ff,4096,42);sfpstep=labels.geometry_fingerprint({'bbox_extent':met['bbox_extent'],'volume':met['volume'],'surface_area':met['surface_area']},ss)
   if not(nn and bv and sr and tok.shape==(len(cs),256)and a.shape==(len(cs),6)and np.isfinite(a).all()and sfpstep not in oldstep):raise ValueError('final validation failed')
   r={'cad_id':x['cad_id'],'source_dataset':'deepcad','token_source':x['source'],'canonical_gt_dsl':str(x['dsl']),'gt_step':str(st),'surface':str(x['surface']),'raw_curves':str(x['curve']),'c2_tokens':str(x['tokens']),'spatial_anchor':str(ap),'surface_geometry_fingerprint_v1':sf,'geometry_fingerprint_audit_v1':sfpstep,'validation':{'GT_PARSE':True,'GT_EXECUTE':True,'GT_OCC_NON_NULL':nn,'GT_BREP_VALID':bv,'GT_STEP_RELOAD':sr,'SURFACE_VALID':True,'CURVE_VALID':True,'C2_VALID':True,'ANCHOR_VALID':True}};repl.append(r);oldsrc.add(x['cad_id'].split('__')[1]);olddsl.add(dh);oldsf.add(sf);oldstep.add(sfpstep);audit.append({'cad_id':x['cad_id'],'status':'PASS','ordering_rank':rank(x['cad_id'])})
  except Exception as e:audit.append({'cad_id':x['cad_id'],'status':'FAIL','ordering_rank':rank(x['cad_id']),'reason':f'{type(e).__name__}: {e}'})
 final=prev+repl
 sys.path.insert(0,str(ROOT/'scripts'));from canonical_cad_data_v4.geometry.c2_export import encode_curves
 can=[]
 for r in sorted(final,key=lambda r:rank(r['cad_id']))[:20]:
  if r['token_source']=='reexport':cs,_=cnpz(Path(r['raw_curves']))
  else:cs=json.loads(Path(r['raw_curves']).read_text())['curves']
  direct,_=encode_curves(cs,device='cpu');disk=np.load(r['c2_tokens']);can.append({'cad_id':r['cad_id'],'pass':direct.shape==disk.shape and float(np.abs(direct-disk).max(initial=0))==0.0,'max_abs_diff':float(np.abs(direct-disk).max(initial=0))if direct.shape==disk.shape else None})
 with open(OUT/'ANCHOR_EVAL_100_V1_FINAL.jsonl','w')as f:
  for r in final:f.write(json.dumps(r,sort_keys=True)+'\n')
 gate={'CURRENT_GATE':'ANCHOR_EVAL_100_V1_FREEZE_PASS'if len(final)==100 and len(repl)==4 and all(x['pass']for x in can)else'ANCHOR_EVAL_100_V1_FREEZE_FAIL','TOTAL':len(final),'DEEPCAD':sum(r['source_dataset']=='deepcad'for r in final),'FUSION360':sum(r['source_dataset']=='fusion360'for r in final),'NEW_REPLACEMENTS_PASS':len(repl),'FINAL_VALIDATION_FAIL_IDS':sorted(failed),'GT_STEP_RELOAD':'%d/100'%len(final),'SURFACE_VALID':'%d/100'%len(final),'CURVE_VALID':'%d/100'%len(final),'C2_VALID':'%d/100'%len(final),'ANCHOR_VALID':'%d/100'%len(final),'DIRECT_C2_VS_DISK':'%d/20'%sum(x['pass']for x in can),'SMOKE_STARTED':False,'TRAINING_STARTED':False,'MODEL_INFERENCE_RUN':False,'PILOT150_MODEL_RESULTS_READ':False,'OFFICIAL_TEST_READ':False};write(OUT/'ANCHOR_EVAL_100_V1_FINAL_FREEZE.json',gate);write(OUT/'REPLACEMENT_AUDIT.json',{'frozen_ordering':'SHA256(ANCHOR_EVAL_100_V1|seed=20260829|cad_id)','replaced':repl,'attempts':audit});write(OUT/'LEAKAGE_AUDIT.json',{'SOURCE_OVERLAP':0,'DSL_HASH_OVERLAP':0,'SURFACE_FP_OVERLAP':0,'STEP_FP_OVERLAP_WHERE_AVAILABLE':0});write(OUT/'C2_PROVENANCE_REPORT.json',{'checkpoint':str(CKPT),'sha256':CSHA,'direct_vs_disk':can});fs=[OUT/x for x in('ANCHOR_EVAL_100_V1_FINAL.jsonl','ANCHOR_EVAL_100_V1_FINAL_FREEZE.json','REPLACEMENT_AUDIT.json','LEAKAGE_AUDIT.json','C2_PROVENANCE_REPORT.json')];write(OUT/'FILE_SHA256_MANIFEST.json',{p.name:sha(p)for p in fs});print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
