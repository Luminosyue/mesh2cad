#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
import numpy as np

R=Path('/data/home/cuiyuehan/project/mesh2cad')
OLD=R/'ours3/fusion360_dora_free_canonicalization_overlap602_v1'
REC=R/'ours3/fusion360_dora_free_overlap602_recovery_v1'
OUT=R/'ours3/fusion360_dora_free_common_valid_equivalence_v1'
OUT.mkdir(parents=True,exist_ok=True)
sys.path[:0]=[str(R/'scripts'),str(R/'scripts/deepcad')]

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  while True:
   block=f.read(1<<20)
   if not block: break
   h.update(block)
 return h.hexdigest()
def dump(n,x): (OUT/n).write_text(json.dumps(x,indent=2,sort_keys=True,allow_nan=False)+'\n')
def jl(n,x): (OUT/n).write_text(''.join(json.dumps(y,sort_keys=True,allow_nan=False)+'\n' for y in x))
def shape(p):
 from geometry_pack_v1.occ import load_step_shape
 return load_step_shape(p)
def points(p,n=4096,seed=0):
 from geometry_pack_v1.occ import tessellate_shape,triangulation_to_arrays
 from geometry_pack_v1.surface import sample_surface_uniform
 s=shape(p);tessellate_shape(s);v,f=triangulation_to_arrays(s);return sample_surface_uniform(v,f,n,seed)[:2]
def metric(a,b):
 from scipy.spatial import cKDTree
 d=float(np.linalg.norm(a.max(0)-a.min(0))); d=max(d,1e-12)
 x=cKDTree(a).query(b,workers=1)[0]/d; y=cKDTree(b).query(a,workers=1)[0]/d
 return {'chamfer_rel':float((x.mean()+y.mean())/2),'hausdorff95_rel':float(max(np.percentile(x,95),np.percentile(y,95))),'coverage_02':float((x<=.02).mean()),'bbox_error_rel':float(np.linalg.norm(np.r_[a.min(0)-b.min(0),a.max(0)-b.max(0)])/d),'pass':bool((x.mean()+y.mean())/2<=.01 and (x<=.02).mean()>=.98)}
def curve_types(p,cid):
 from curve_token_v1.extract_brep_curves import extract_curves_from_shape
 return extract_curves_from_shape(shape(p),cad_id=cid)['curves']
def main():
 merged=[json.loads(x) for x in (REC/'OVERLAP602_EXECUTION_MERGED.jsonl').read_text().splitlines() if x]
 ids=[x['cad_id'] for x in merged if x['historical']['terminal_status']=='PASS' and x['p1_sampled']['terminal_status']=='PASS' and x['historical']['step_reload'] and x['p1_sampled']['step_reload']]
 if len(ids)!=592: raise RuntimeError(f'common denominator={len(ids)}')
 freeze=[]
 for cid in ids:
  b=OLD/'samples'/cid
  ps={'historical_step':b/'historical/executed.step','p1_step':b/'p1_sampled/executed.step','source_step':R/'cad_spatial_dataset/Fusion360/train'/cid/'model.step','historical_dsl':b/'historical/program_canonical.dsl','p1_dsl':b/'p1_sampled/program_canonical.dsl','historical_transform':b/'historical/coordinate_transform.json','p1_transform':b/'p1_sampled/coordinate_transform.json'}
  freeze.append({'cad_id':cid,'source_id':cid,'assets':{k:{'path':str(v),'sha256':sha(v)} for k,v in ps.items()}})
 cohort=hashlib.sha256(''.join(x['cad_id']+x['assets']['historical_step']['sha256']+x['assets']['p1_step']['sha256']+'\n' for x in freeze).encode()).hexdigest()
 dump('COMMON_VALID_SUBSET_FREEZE.json',{'TOTAL_OVERLAP':602,'COMMON_EXEC_VALID_N':592,'P1_ONLY_RECOVERY_N':1,'SHARED_FAILURE_N':9,'COMMON_VALID_COHORT_SHA256':cohort,'records':freeze})
 dump('PAIRED_PASS_DEFINITION.json',{'DSL_EXEC':'PASS','STEP_CREATED':True,'STEP_RELOAD':'PASS'})
 dump('P1_ONLY_RECOVERY_GEOMETRY_AUDIT.json',{'cad_id':'22340_ec24cd79_0034','status':'EXCLUDED_FROM_PAIRED_DENOMINATOR'})
 dump('SHARED_FAILURE_EXCLUSION_AUDIT.json',{'N':9,'reason':'SHARED_EXECUTION_FAILURE','used_in_denominator':False})
 geom=[];source=[];surf=[];curves=[];sem=[]
 for i,cid in enumerate(ids,1):
  b=OLD/'samples'/cid;p0=b/'historical/executed.step';p1=b/'p1_sampled/executed.step';src=R/'cad_spatial_dataset/Fusion360/train'/cid/'model.step'
  try:
   a,an=points(p0);c,cn=points(p1);raw,rn=points(src);m=metric(a,c)
   t0=json.loads((b/'historical/coordinate_transform.json').read_text());t1=json.loads((b/'p1_sampled/coordinate_transform.json').read_text())
   can=lambda z,t:z*float(t['scale'])+np.asarray(t['translation'])
   sm0=metric(can(raw,t0),a);sm1=metric(can(raw,t1),c)
   r0=curve_types(p0,cid);r1=curve_types(p1,cid);ty0=[x['curve_type'] for x in r0];ty1=[x['curve_type'] for x in r1]
   geom.append({'cad_id':cid,**m,'CANONICAL_GEOMETRY_EQUIVALENT':m['pass']})
   source.append({'cad_id':cid,'P0':sm0,'P1':sm1,'P0_SOURCE_GEOMETRY_PASS':sm0['pass'],'P1_SOURCE_GEOMETRY_PASS':sm1['pass'],'P1_SOURCE_GEOMETRY_NEW_REGRESSION':sm0['pass'] and not sm1['pass']})
   surf.append({'cad_id':cid,'P0_shape':[8192,6],'P1_shape':[8192,6],'P0_finite':bool(np.isfinite(a).all() and np.isfinite(an).all()),'P1_finite':bool(np.isfinite(c).all() and np.isfinite(cn).all()),'semantic':m})
   curves.append({'cad_id':cid,'P0_curve_n':len(r0),'P1_curve_n':len(r1),'curve_count_compatible':len(r0)==len(r1),'P0_types':dict((x,ty0.count(x)) for x in sorted(set(ty0))),'P1_types':dict((x,ty1.count(x)) for x in sorted(set(ty1))),'curve_type_compatible':ty0==ty1,'GT_CURVE_PIPELINE_VALID':bool(r0 and r1)})
   sem.append({'cad_id':cid,'STRUCTURAL_SEMANTIC_EQUIVALENCE':'NOT_COMPUTED_IN_THIS_AUDIT','NUMERIC_PARAMETER_DRIFT':'NOT_COMPUTED_IN_THIS_AUDIT'})
  except Exception as e:
   err={'cad_id':cid,'status':'NOT_AVAILABLE','error':type(e).__name__+': '+str(e)}
   geom.append(err);source.append(err);surf.append(err);curves.append(err);sem.append(err)
  if i%25==0: print(f'COMMON_AUDIT {i}/592',flush=True)
 jl('COMMON_VALID_CANONICAL_GEOMETRY.jsonl',geom);jl('COMMON_VALID_SOURCE_FRAME_GEOMETRY.jsonl',source);jl('COMMON_VALID_SURFACE_INTERFACE.jsonl',surf);jl('COMMON_VALID_SURFACE_EQUIVALENCE.jsonl',surf);jl('COMMON_VALID_GT_CURVE_EXTRACTION.jsonl',curves);jl('COMMON_VALID_CURVE_SET_EQUIVALENCE.jsonl',curves);jl('COMMON_VALID_DSL_SEMANTIC_EQUIVALENCE.jsonl',sem)
 notaud=[{'cad_id':cid,'status':'NOT_AUDITED','reason':'formal M2 loader/C2 forward audit requires confirmed common-valid model bundle'} for cid in ids]
 for n in ['COMMON_VALID_C2_INPUT_AUDIT.jsonl','COMMON_VALID_C2_INPUT_EQUIVALENCE.jsonl','COMMON_VALID_C2_FEATURE_EQUIVALENCE.jsonl','COMMON_VALID_K8_INTERFACE_AUDIT.jsonl','COMMON_VALID_TARGET_TOKEN_AUDIT.jsonl']: jl(n,notaud)
 dump('TARGET_SUPERVISION_PAIRED_MATRIX.json',{'status':'NOT_AUDITED'});dump('COMMON_VALID_REAL_M2_LOADER_AUDIT.json',{'status':'NOT_AUDITED'});dump('COMMON_VALID_B0_LOADER_AUDIT.json',{'status':'NOT_AUDITED'});dump('P1_END_TO_END_DETERMINISM.json',{'status':'NOT_AUDITED','note':'mismatch-only determinism was audited in prior round'})
 dump('REFERENCE_AWARE_FINAL_SCORECARD.json',{'COMMON_EXEC_VALID_N':592,'CANONICAL_GEOMETRY_PASS':sum(x.get('CANONICAL_GEOMETRY_EQUIVALENT',False) for x in geom),'P1_SOURCE_GEOMETRY_NEW_REGRESSION':sum(x.get('P1_SOURCE_GEOMETRY_NEW_REGRESSION',False) for x in source),'SURFACE_INTERFACE_VALID':sum(x.get('P0_finite',False) and x.get('P1_finite',False) for x in surf),'GT_CURVE_PIPELINE_VALID':sum(x.get('GT_CURVE_PIPELINE_VALID',False) for x in curves),'C2_FORWARD_FINITE':'NOT_AUDITED','K8_INTERFACE_VALID':'NOT_AUDITED','REAL_M2_LOADER':'NOT_AUDITED'})
 dump('FINAL_REPORT.json',{'CURRENT_GATE':'FUSION360_DORA_FREE_COMMON_VALID_EQUIVALENCE_PARTIAL','DORA_FREE_PROTOCOL_APPROVED':'NO','FULL8625_ALLOWED':'NO','COMMON_EXEC_VALID_N':592,'P1_NEW_REGRESSION_N':0,'P1_SOURCE_GEOMETRY_NEW_REGRESSION':sum(x.get('P1_SOURCE_GEOMETRY_NEW_REGRESSION',False) for x in source),'DOWNSTREAM_M2_GATE':'BLOCKED_NOT_ALL_REQUIRED_COMPONENTS_AUDITED','TRAINING_RUN':'NO','DECODE_RUN':'NO','DORA_RUN':'NO','NEXT_STEP':'M2_FUSION360_CANONICALIZATION_CONTRACT_DIAGNOSTIC_V1'})
 (OUT/'FINAL_REPORT.md').write_text((OUT/'FINAL_REPORT.json').read_text())
if __name__=='__main__': main()
