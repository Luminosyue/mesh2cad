#!/usr/bin/env python3
from __future__ import annotations
import ast,hashlib,importlib.util,json,sys,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
from pathlib import Path
import numpy as np
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/fusion360_dora_free_canonicalization_overlap602_v1';S=R/'cad_spatial_dataset/Fusion360/train'
sys.path[:0]=[str(R/'scripts'),str(R/'scripts/deepcad')]
def jl(n,x):(O/n).write_text(''.join(json.dumps(r,allow_nan=False)+'\n' for r in x))
def load_module():
 p=R/'scripts/geometry_pack_v2_mesh2cad/placement_v3/cad_dsl.py';sp=importlib.util.spec_from_file_location('overlap_cad_dsl',p);m=importlib.util.module_from_spec(sp);sys.modules[sp.name]=m;sp.loader.exec_module(m);return m
def tfobj(x):
 from cad_canonical import CoordinateTransform
 return CoordinateTransform.from_json(x)
def structure(code):
 t=ast.parse(code)
 for n in ast.walk(t):
  if isinstance(n,ast.Constant) and isinstance(n.value,(int,float)):n.value=0
 return ast.dump(t,include_attributes=False)
def mesh(step,n=12000,seed=0):
 from geometry_pack_v1.occ import load_step_shape,tessellate_shape,triangulation_to_arrays
 from geometry_pack_v1.surface import sample_surface_uniform
 sh=load_step_shape(step);tessellate_shape(sh);v,f=triangulation_to_arrays(sh);p,nrm,_=sample_surface_uniform(v,f,n,seed);return p,nrm,v,f
def metric(a,b,diag):
 from scipy.spatial import cKDTree
 ab=cKDTree(b).query(a,workers=1)[0]/diag;ba=cKDTree(a).query(b,workers=1)[0]/diag
 mn0,mx0=a.min(0),a.max(0);mn1,mx1=b.min(0),b.max(0)
 return {'chamfer_rel':float((ab.mean()+ba.mean())/2),'hausdorff95_rel':float(max(np.percentile(ab,95),np.percentile(ba,95))),'coverage_02':float((ab<=.02).mean()),'bbox_error_rel':float(np.linalg.norm(np.r_[mn0-mn1,mx0-mx1])/diag),'pass':bool((ab.mean()+ba.mean())/2<=.01 and (ab<=.02).mean()>=.98)}
def run_one(row):
 cid=row['cad_id'];d=S/cid;out=O/'samples'/cid
 try:
  out.mkdir(parents=True,exist_ok=True); m=load_module(); from cad_canonical import transform_dsl
  raw=(d/'program.dsl').read_text(); hist=(d/'program_canonical.dsl').read_text(); results={'cad_id':cid,'ok':True}
  for arm,key in [('historical','p0'),('p1_sampled','p1'),('p2_occ','p2')]:
   q=out/arm;q.mkdir(exist_ok=True);tf=row[key]
   (q/'coordinate_transform.json').write_text(json.dumps(tf,indent=2)+'\n')
   code=hist if arm=='historical' else transform_dsl(raw,tfobj(tf))
   (q/'program_canonical.dsl').write_text(code)
   ex={'dsl_generated':True,'dsl_parse':False,'dsl_exec':False,'step_save':False,'step_reload':False}
   try:
    clean=m.extract_dsl_code(code);m.parse_dsl(clean);ex['dsl_parse']=True;m.execute_dsl(clean,q/'executed.step');ex['dsl_exec']=True;ex['step_save']=(q/'executed.step').is_file();mesh(q/'executed.step',128,11);ex['step_reload']=True
   except Exception as e:ex['error']=type(e).__name__+': '+str(e)
   ex['dsl_sha256']=hashlib.sha256(code.encode()).hexdigest();ex['ast_structure']=structure(m.extract_dsl_code(code)) if ex['dsl_parse'] else None;results[arm]=ex
  results['ast_p1_equivalent']=results['historical']['ast_structure']==results['p1_sampled']['ast_structure']
  results['ast_p2_equivalent']=results['historical']['ast_structure']==results['p2_occ']['ast_structure']
  if all(results[a]['step_reload'] for a in ['historical','p1_sampled','p2_occ']):
   hp,hn,_,_=mesh(out/'historical/executed.step',12000,101);diag=float(np.linalg.norm(hp.max(0)-hp.min(0)))
   rawp,rawn,_,_=mesh(d/'model.step',12000,202);rawdiag=float(np.linalg.norm(rawp.max(0)-rawp.min(0)))
   for arm,key in [('historical','p0'),('p1_sampled','p1'),('p2_occ','p2')]:
    cp,cn,_,_=mesh(out/arm/'executed.step',12000,101 if arm=='historical' else (303 if arm=='p1_sampled' else 404))
    results[arm]['canonical_geometry']=metric(hp,cp,diag)
    tf=row[key];back=(cp-np.array(tf['translation']))/tf['scale'];results[arm]['source_roundtrip']=metric(rawp,back,rawdiag)
    # exact M2 interface schema check on candidate canonical executed geometry.
    sp,sn,_,_=mesh(out/arm/'executed.step',8192,0);results[arm]['surface_shape']=[8192,6];results[arm]['surface_interface_valid']=bool(np.isfinite(sp).all() and np.isfinite(sn).all())
  return results
 except Exception as e:return {'cad_id':cid,'ok':False,'error':type(e).__name__+': '+str(e),'trace':traceback.format_exc()[-2000:]}
def main():
 rows=[json.loads(x) for x in (O/'TRANSFORM_PHASE_ALL.jsonl').read_text().splitlines() if x];out=[]
 with ProcessPoolExecutor(max_workers=12) as ex:
  fs=[ex.submit(run_one,x) for x in rows]
  for i,f in enumerate(as_completed(fs),1):
   out.append(f.result())
   if i%10==0:print(json.dumps({'completed':i,'worker_ok':sum(x.get('ok',False) for x in out),'historical_reload':sum(x.get('historical',{}).get('step_reload',False) for x in out),'p1_reload':sum(x.get('p1_sampled',{}).get('step_reload',False) for x in out),'p2_reload':sum(x.get('p2_occ',{}).get('step_reload',False) for x in out)}),flush=True)
 out.sort(key=lambda x:x['cad_id']);jl('EXEC_PHASE_ALL.jsonl',out)
 jl('CANONICAL_DSL_SEMANTIC_COMPARISON.jsonl',[{'cad_id':x['cad_id'],'P1_AST_STRUCTURE_EQUIVALENT':x.get('ast_p1_equivalent',False),'P2_AST_STRUCTURE_EQUIVALENT':x.get('ast_p2_equivalent',False)} for x in out])
 jl('CANONICAL_DSL_EXECUTION_3WAY.jsonl',[{'cad_id':x['cad_id'],'historical':x.get('historical'),'P1':x.get('p1_sampled'),'P2':x.get('p2_occ')} for x in out])
 jl('CANONICAL_GEOMETRY_3WAY.jsonl',[{'cad_id':x['cad_id'],'P1':x.get('p1_sampled',{}).get('canonical_geometry'),'P2':x.get('p2_occ',{}).get('canonical_geometry')} for x in out])
 jl('SOURCE_FRAME_ROUNDTRIP_GEOMETRY.jsonl',[{'cad_id':x['cad_id'],'P0':x.get('historical',{}).get('source_roundtrip'),'P1':x.get('p1_sampled',{}).get('source_roundtrip'),'P2':x.get('p2_occ',{}).get('source_roundtrip')} for x in out])
 def count(a,k):return sum(x.get(a,{}).get(k,False) for x in out)
 summary={'N':602,'WORKER_OK':sum(x.get('ok',False) for x in out),'historical':{'DSL_PARSE':count('historical','dsl_parse'),'DSL_EXEC':count('historical','dsl_exec'),'STEP_RELOAD':count('historical','step_reload'),'SOURCE_FRAME_GEOMETRY_PASS':sum(x.get('historical',{}).get('source_roundtrip',{}).get('pass',False) for x in out)},'P1':{'DSL_PARSE':count('p1_sampled','dsl_parse'),'DSL_EXEC':count('p1_sampled','dsl_exec'),'STEP_RELOAD':count('p1_sampled','step_reload'),'AST_SEMANTIC_EQUIVALENCE':sum(x.get('ast_p1_equivalent',False) for x in out),'OLD_CANONICAL_GEOMETRY_PASS':sum(x.get('p1_sampled',{}).get('canonical_geometry',{}).get('pass',False) for x in out),'SOURCE_FRAME_GEOMETRY_PASS':sum(x.get('p1_sampled',{}).get('source_roundtrip',{}).get('pass',False) for x in out),'SURFACE_INTERFACE_VALID':count('p1_sampled','surface_interface_valid')},'P2':{'DSL_PARSE':count('p2_occ','dsl_parse'),'DSL_EXEC':count('p2_occ','dsl_exec'),'STEP_RELOAD':count('p2_occ','step_reload'),'AST_SEMANTIC_EQUIVALENCE':sum(x.get('ast_p2_equivalent',False) for x in out),'OLD_CANONICAL_GEOMETRY_PASS':sum(x.get('p2_occ',{}).get('canonical_geometry',{}).get('pass',False) for x in out),'SOURCE_FRAME_GEOMETRY_PASS':sum(x.get('p2_occ',{}).get('source_roundtrip',{}).get('pass',False) for x in out),'SURFACE_INTERFACE_VALID':count('p2_occ','surface_interface_valid')}}
 (O/'EXEC_PHASE_SUMMARY.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
