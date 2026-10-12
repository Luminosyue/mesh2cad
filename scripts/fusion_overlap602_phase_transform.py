#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,sys,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np

R=Path('/data/home/cuiyuehan/project/mesh2cad'); S=R/'cad_spatial_dataset/Fusion360/train'
O=R/'ours3/fusion360_dora_free_canonicalization_overlap602_v1'; SEED=0
sys.path[:0]=[str(R/'scripts'),str(R/'scripts/deepcad')]

def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def transform(mn,mx):
 mn=np.asarray(mn,float);mx=np.asarray(mx,float);diag=float(np.linalg.norm(mx-mn));s=6/diag
 return {'source_bbox_min':mn.tolist(),'source_bbox_max':mx.tolist(),'source_diagonal':diag,'target_diagonal':6.0,'scale':s,'translation':(-s*mn).tolist()}
def dif(a,b):
 amn,amx=np.array(a['source_bbox_min']),np.array(a['source_bbox_max']);bmn,bmx=np.array(b['source_bbox_min']),np.array(b['source_bbox_max'])
 return {'bbox_min_delta_xyz':(bmn-amn).tolist(),'bbox_max_delta_xyz':(bmx-amx).tolist(),'bbox_diag_abs_error':abs(b['source_diagonal']-a['source_diagonal']),'bbox_diag_rel_error':abs(b['source_diagonal']-a['source_diagonal'])/a['source_diagonal'],'scale_abs_error':abs(b['scale']-a['scale']),'scale_rel_error':abs(b['scale']-a['scale'])/abs(a['scale']),'translation_delta_xyz':(np.array(b['translation'])-np.array(a['translation'])).tolist(),'translation_L2':float(np.linalg.norm(np.array(b['translation'])-np.array(a['translation']))),'translation_L2_over_6':float(np.linalg.norm(np.array(b['translation'])-np.array(a['translation']))/6)}
def occ_bbox(step):
 from OCP.Bnd import Bnd_Box
 from OCP.BRepBndLib import BRepBndLib
 from geometry_pack_v1.occ import load_step_shape
 sh=load_step_shape(step)
 box=Bnd_Box(); box.SetGap(0.0); BRepBndLib.AddOptimal_s(sh,box,False,False)
 return np.array(box.Get()[:3]),np.array(box.Get()[3:])
def sample_p1(obj):
 import trimesh
 from geometry_pack_v1.surface import sample_surface_uniform
 m=trimesh.load(str(obj),force='mesh',process=False)
 if isinstance(m,trimesh.Scene):m=m.dump(concatenate=True)
 p,n,_=sample_surface_uniform(np.asarray(m.vertices),np.asarray(m.faces),8192,SEED)
 return p,n,np.asarray(m.vertices)
def point_disp(pts,a,b):
 A=pts*a['scale']+np.array(a['translation']);B=pts*b['scale']+np.array(b['translation']);d=np.linalg.norm(A-B,axis=1)
 return {'mean':float(d.mean()),'median':float(np.median(d)),'p95':float(np.percentile(d,95)),'max':float(d.max()),'mean_over_6':float(d.mean()/6),'p95_over_6':float(np.percentile(d,95)/6)}
def worker(path):
 d=Path(path);cid=d.name
 try:
  feat=np.load(d/'features.npy',mmap_mode='r');p0=transform(np.min(feat[:,:3],0),np.max(feat[:,:3],0));hist=json.loads((d/'coordinate_transform.json').read_text())
  p1xyz,p1n,verts=sample_p1(d/'model.obj');p1=transform(p1xyz.min(0),p1xyz.max(0));mn,mx=occ_bbox(d/'model.step');p2=transform(mn,mx)
  ref=dif(hist,p0); refpass=ref['scale_abs_error']<=1e-12 and ref['translation_L2']<=1e-12
  # Same deterministic raw-space probe set for all mappings: first 4096 lexicographically sorted OBJ vertices, tiled if needed.
  ix=np.lexsort((verts[:,2],verts[:,1],verts[:,0]));v=verts[ix];probe=np.resize(v,(4096,3))
  from scipy.spatial import cKDTree
  hxyz=np.asarray(feat[:,:3]);ab=cKDTree(p1xyz).query(hxyz,workers=1)[0];ba=cKDTree(hxyz).query(p1xyz,workers=1)[0]
  ps={'chamfer_raw':float((ab.mean()+ba.mean())/2),'bbox_error_l2':float(np.linalg.norm(np.r_[p1xyz.min(0)-hxyz.min(0),p1xyz.max(0)-hxyz.max(0)])),'historical_n':len(hxyz),'p1_n':len(p1xyz)}
  return {'cad_id':cid,'ok':True,'p0':p0,'historical':hist,'reference_comparison':ref,'reference_pass':refpass,'p1':p1,'p2':p2,'p0_vs_p1':dif(p0,p1),'p0_vs_p2':dif(p0,p2),'point_displacement_p1':point_disp(probe,p0,p1),'point_displacement_p2':point_disp(probe,p0,p2),'pointset':ps,'p1_seed':SEED}
 except Exception as e:return {'cad_id':cid,'ok':False,'error':type(e).__name__+': '+str(e),'trace':traceback.format_exc()[-2000:]}
def jl(name,rows):
 (O/name).write_text(''.join(json.dumps(x,allow_nan=False)+'\n' for x in rows))
def stats(vals):
 a=np.array(vals,float);return {k:float(np.percentile(a,q)) for k,q in [('min',0),('median',50),('p90',90),('p95',95),('max',100)]}
def main():
 O.mkdir(parents=True,exist_ok=False);(O/'samples').mkdir();(O/'figures/overlap602_qa').mkdir(parents=True)
 ds=[d for d in sorted(S.iterdir()) if d.is_dir() and all((d/n).is_file() for n in ['features.npy','coordinate_transform.json','program_canonical.dsl','program.dsl','source.json','model.step','model.obj'])]
 assert len(ds)==602,len(ds)
 records=[]
 for d in ds:
  paths={k:str(d/n) for k,n in {'raw_json':'source.json','raw_step':'model.step','raw_obj':'model.obj','historical_features':'features.npy','historical_transform':'coordinate_transform.json','historical_dsl':'program_canonical.dsl'}.items()}
  records.append({'cad_id':d.name,'source_id':d.name,**{k:{'path':p,'sha256':sha(p)} for k,p in paths.items()}})
 cohort=hashlib.sha256(''.join(x['cad_id']+'|'+x['historical_transform']['sha256']+'\n' for x in records).encode()).hexdigest()
 (O/'OVERLAP602_INPUT_FREEZE.json').write_text(json.dumps({'OVERLAP_INPUT_COMPLETE':'602/602','OVERLAP602_COHORT_SHA256':cohort,'records':records},indent=2)+'\n')
 prov={'sampling_code_path':str(R/'scripts/geometry_pack_v1/surface.py'),'sampling_code_sha256':sha(R/'scripts/geometry_pack_v1/surface.py'),'sampling_method':'triangle area-weighted uniform barycentric sampling','sample_count':8192,'seed_behavior':'numpy.default_rng(seed); formal DEFAULT_SEED=0','frozen_seed':SEED,'mesh_source':'historical official model.obj','normal_source':'triangle face normals from formal sampler','SAMPLING_PROTOCOL_NONDETERMINISTIC':False}
 (O/'DORA_FREE_SAMPLING_PROVENANCE.json').write_text(json.dumps(prov,indent=2)+'\n')
 rows=[]
 with ProcessPoolExecutor(max_workers=16) as ex:
  fs={ex.submit(worker,str(d)):d.name for d in ds}
  for i,f in enumerate(as_completed(fs),1):
   rows.append(f.result())
   if i%20==0:print(json.dumps({'completed':i,'ok':sum(x['ok'] for x in rows),'reference_pass':sum(x.get('reference_pass',False) for x in rows)}),flush=True)
 rows.sort(key=lambda x:x['cad_id']);jl('TRANSFORM_PHASE_ALL.jsonl',rows)
 jl('REFERENCE_TRANSFORM_REPRODUCTION.jsonl',[{'cad_id':x['cad_id'],**x.get('reference_comparison',{}),'pass':x.get('reference_pass',False),'error':x.get('error')} for x in rows])
 jl('P1_SAMPLED_XYZ_TRANSFORM.jsonl',[{'cad_id':x['cad_id'],'transform':x.get('p1'),'seed':x.get('p1_seed'),'error':x.get('error')} for x in rows])
 jl('P2_OCC_BBOX_TRANSFORM.jsonl',[{'cad_id':x['cad_id'],'transform':x.get('p2'),'bbox_api':'OCP BRepBndLib.AddOptimal_s','gap':0.0,'useTriangulation':False,'useShapeTolerance':False,'error':x.get('error')} for x in rows])
 jl('TRANSFORM_NUMERIC_COMPARISON.jsonl',[{'cad_id':x['cad_id'],'P0_vs_P1':x.get('p0_vs_p1'),'P0_vs_P2':x.get('p0_vs_p2'),'error':x.get('error')} for x in rows])
 jl('CANONICAL_FRAME_POINT_DISPLACEMENT.jsonl',[{'cad_id':x['cad_id'],'P0_vs_P1':x.get('point_displacement_p1'),'P0_vs_P2':x.get('point_displacement_p2'),'error':x.get('error')} for x in rows])
 good=[x for x in rows if x['ok']];point=[x['pointset'] for x in good]
 summary={'OVERLAP_N':602,'TRANSFORM_WORKER_OK':len(good),'REFERENCE_TRANSFORM_REPRODUCTION':sum(x['reference_pass'] for x in rows),'P1':{'TRANSFORM_GENERATED':len(good),'scale_rel_error':stats([x['p0_vs_p1']['scale_rel_error'] for x in good]),'translation_L2_over_6':stats([x['p0_vs_p1']['translation_L2_over_6'] for x in good]),'point_displacement_mean_over_6':stats([x['point_displacement_p1']['mean_over_6'] for x in good])},'P2':{'TRANSFORM_GENERATED':len(good),'scale_rel_error':stats([x['p0_vs_p2']['scale_rel_error'] for x in good]),'translation_L2_over_6':stats([x['p0_vs_p2']['translation_L2_over_6'] for x in good]),'point_displacement_mean_over_6':stats([x['point_displacement_p2']['mean_over_6'] for x in good])},'POINTSET':{'historical_vs_p1_chamfer_raw':stats([x['chamfer_raw'] for x in point]),'historical_vs_p1_bbox_error_l2':stats([x['bbox_error_l2'] for x in point])},'DORA_RUN':False,'TRAINING_RUN':False,'DECODE_RUN':False}
 (O/'TRANSFORM_PHASE_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');(O/'HISTORICAL_VS_DORAFREE_POINTSET_AUDIT.json').write_text(json.dumps(summary['POINTSET'],indent=2)+'\n')
 if summary['REFERENCE_TRANSFORM_REPRODUCTION']<602:
  (O/'FINAL_REPORT.json').write_text(json.dumps({'CURRENT_GATE':'HISTORICAL_TRANSFORM_REFERENCE_REPRODUCTION_FAIL',**summary},indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
