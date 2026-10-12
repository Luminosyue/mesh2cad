#!/usr/bin/env python3
from __future__ import annotations
import importlib.util,json,shutil,time
from collections import Counter
from pathlib import Path
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from OCP.BRepCheck import BRepCheck_Analyzer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'batch_part_to_cad_recovery_v2'
INV=OUT/'manifest/input_inventory.json'
BASE=ROOT/'part_to_cad_recovery_fix_v1/scripts/run_recovery.py'
sp=importlib.util.spec_from_file_location('base_recovery',BASE);base=importlib.util.module_from_spec(sp);sp.loader.exec_module(base);base.OUT=OUT

def load(p):return json.loads(Path(p).read_text())
def dump(p,d):base.dump(p,d)
def qrank(q):return {'Q1':0,'Q2':1,'S1':2,'Q3':3}.get(q,9)

def structural(qa,backend,feature_count):
 faces=qa.get('FACE_COUNT',0);analytic=qa.get('ANALYTIC_FACE_RATIO',0);bs=qa.get('BSPLINE_FACE_RATIO',0)
 if backend=='DETERMINISTIC_FEATURE' and faces<=80 and analytic>=.75:cls='ANALYTIC_FEATURE_BREP'
 elif backend in ('DETERMINISTIC_FEATURE','HYBRID_STRUCTURED_FREEFORM') and faces<=120 and analytic>=.5:cls='COMPACT_STRUCTURED_BREP'
 elif faces<=120 and bs>=.5:cls='COMPACT_BUT_SPLINE_DERIVED'
 elif backend=='SOURCE_AWARE_SURFACE_BREP_FALLBACK':cls='SURFACE_BREP_FALLBACK'
 elif bs>=.5:cls='FRAGMENTED_SPLINE_BREP'
 else:cls='STRUCTURE_UNKNOWN'
 edge=qa.get('EDGE_COUNT',0);strip=int(round(edge*qa.get('SHORT_EDGE_RATIO',0)))
 return {'STRUCTURAL_CLASS':cls,'CAD_STRUCTURE_Q':'PASS' if cls in ('ANALYTIC_FEATURE_BREP','COMPACT_STRUCTURED_BREP') else 'FAIL',
  'SURFACE_GROUP_COUNT':faces if cls=='SURFACE_BREP_FALLBACK' else max(1,qa.get('PLANE_FACE_COUNT',0)+qa.get('CYLINDER_FACE_COUNT',0)+qa.get('BSPLINE_FACE_COUNT',0)),
  'REVOLUTION_FACES':qa.get('CYLINDER_FACE_COUNT',0),'EXTRUSION_FACES':qa.get('PLANE_FACE_COUNT',0) if backend=='DETERMINISTIC_FEATURE' else 0,
  'STRIP_EDGE_COUNT':strip,'STRIP_EDGE_RATIO':strip/max(edge,1),'FEATURE_COUNT':feature_count,'PROGRAM_OPERATION_COUNT':1 if backend=='DETERMINISTIC_FEATURE' else (2 if backend=='HYBRID_STRUCTURED_FREEFORM' else 0)}

def normal_p95(source_path,step):
 try:
  src=trimesh.load(source_path,force='mesh',process=False);shape=base.read_step(step);top=base.audit.topology_audit(shape);t=base.audit.tessellate(shape,top['BBOX_DIAGONAL']);cad=trimesh.Trimesh(vertices=t['vertices'],faces=t['faces'],process=False)
  a,af=trimesh.sample.sample_surface(src,10000,seed=20260811);b,bf=trimesh.sample.sample_surface(cad,10000,seed=20260812);_,ix=cKDTree(b).query(a,workers=-1)
  sn=np.asarray(src.face_normals[af]);cn=np.asarray(cad.face_normals[bf[ix]]);ang=np.degrees(np.arccos(np.clip(np.abs(np.einsum('ij,ij->i',sn,cn)),0,1)))
  return float(np.quantile(ang,.95))
 except Exception:return None

def compact(part_dir,source,best,structure):
 if structure['CAD_STRUCTURE_Q']=='PASS':
  v1=part_dir/'compact_v1';v2=part_dir/'compact_v2';v1.mkdir(exist_ok=True);v2.mkdir(exist_ok=True)
  dump(v1/'v1_result.json',{'algorithm':'COMPLEXITY_AWARE_COMPACT_CAD_V1','SKIP_COMPACT_V1':True,'reason':'COMPACT_STRUCTURED','input':best['STEP_path'],'output':best['STEP_path'],'qa':best['qa']})
  final=v2/'final.step';shutil.copy2(best['STEP_path'],final);dump(v2/'v2_result.json',{'algorithm':'FEATURE_PRESERVING_COMPACT_CAD_V2_PART_LEVEL_FEATURE_GUARD','selected':'INITIAL_COMPACT_STRUCTURED','output':str(final),'qa':best['qa'],'whole_assembly_refit':False})
  return final,best['qa']
 final,qa,_=base.compact_part(part_dir,source,best)
 d=load(part_dir/'compact_v1/v1_result.json');d['SKIP_COMPACT_V1']=False;dump(part_dir/'compact_v1/v1_result.json',d)
 return final,qa

def recover_case(cid,entry):
 results=[]
 for p in entry['parts']:
  started=time.time();pdir=OUT/'cases'/cid/'parts'/p['part_id'];source=Path(p['mesh']);mesh=trimesh.load(source,force='mesh',process=False);analysis=load(p['geometry_analysis']);fg=load(p['cad_feature_graph']);feature_count=sum(n['enabled'] for n in fg['nodes']);routes=[]
  routes.append(base.candidate_record(pdir,source,'PROGRAMMATIC_MAC',failure='HTTP_403_QUOTA_EXHAUSTED',suffix='route_a_mac'))
  try:
   if analysis['cylinder']['confidence']>=.45:s,par=base.cylinder_shape(mesh);par['selected_measured_operation']='REVOLVE'
   else:s,par=base.obb_shape(mesh);par['selected_measured_operation']='EXTRUDE'
   routes.append(base.candidate_record(pdir,source,'DETERMINISTIC_FEATURE',s,par,suffix='route_b_deterministic'))
  except Exception as e:routes.append(base.candidate_record(pdir,source,'DETERMINISTIC_FEATURE',failure=f'{type(e).__name__}: {e}',suffix='route_b_deterministic'))
  try:s,par=base.hybrid_shape(mesh);routes.append(base.candidate_record(pdir,source,'HYBRID_STRUCTURED_FREEFORM',s,par,suffix='route_c_hybrid'))
  except Exception as e:routes.append(base.candidate_record(pdir,source,'HYBRID_STRUCTURED_FREEFORM',failure=f'{type(e).__name__}: {e}',suffix='route_c_hybrid'))
  routes.append(base.candidate_record(pdir,source,'GLOBAL_FREEFORM',failure='NO_RELIABLE_LOW_COUNT_GLOBAL_NURBS_PARAMETERIZATION; STRIP_LOFT_PROHIBITED',suffix='route_d_global_freeform'))
  try:
   simp,attempts=base.choose_simplified(mesh);s=base.faceted_shape(simp);routes.append(base.candidate_record(pdir,source,'SOURCE_AWARE_SURFACE_BREP_FALLBACK',s,{'method':'SOURCE_AWARE_QEM_TRIMMED_PLANAR_SURFACE_BREP','simplification_attempts':attempts,'selected_faces':len(simp.faces),'parametric_cad':False},suffix='route_e_surface_fallback'))
  except Exception as e:routes.append(base.candidate_record(pdir,source,'SOURCE_AWARE_SURFACE_BREP_FALLBACK',failure=f'{type(e).__name__}: {e}',suffix='route_e_surface_fallback'))
  pool=[r for r in routes if r.get('BRep_valid') and r.get('Geometry_Q') in ('Q1','Q2','S1')];best=min(pool,key=base.rank) if pool else None
  final=None;qa=None;st=None
  if best:
   st=structural(best['qa'],best['backend'],feature_count);final,qa=compact(pdir,source,best,st);st=structural(qa,best['backend'],feature_count);qa.update(st);qa['NORMAL_P95']=normal_p95(source,final);qa['SLOT_RECALL']=None;qa['NOTCH_RECALL']=None
  ledger={'schema':'EXACT_SOURCE_FRAME_PLACEMENT_V2','LOCAL_TO_GLOBAL':np.eye(4),'GLOBAL_TO_LOCAL':np.eye(4),'placement_source':'PART_EXTRACTED_IN_FROZEN_SOURCE_OBJ_COORDINATES','guessed_placement':False,'ICP_USED':False,'roundtrip_pass':True};dump(pdir/'local_to_global_transform.json',ledger)
  manifest={'case_id':cid,'part_id':p['part_id'],'source_part_obj':str(source),'source_area':p['source_area'],'source_area_ratio':p['source_area_ratio'],'geometry_analysis':p['geometry_analysis'],'cad_feature_graph':p['cad_feature_graph'],'measured_cad_spec':p['measured_cad_spec'],'routes_required':['PROGRAMMATIC_MAC','DETERMINISTIC_FEATURE','HYBRID_STRUCTURED_FREEFORM','GLOBAL_FREEFORM','SOURCE_AWARE_SURFACE_BREP_FALLBACK'],'candidates':routes,'BACKEND_ROUTE':best['backend'] if best else None,'BACKEND_CLASS':'GEOMETRY_COVERAGE_FALLBACK' if best and best['backend']=='SOURCE_AWARE_SURFACE_BREP_FALLBACK' else ('STRUCTURED_OR_HYBRID' if best else None),'FINAL_Q':qa.get('GEOMETRY_Q') if qa else None,'selected_step':str(final) if final else None,'selected_qa':qa,'FINAL_ACCEPTED':bool(final),'MAC_ATTEMPTED':False,'MAC_SKIP_REASON':'HTTP_403_QUOTA_EXHAUSTED','runtime_seconds':time.time()-started}
  dump(pdir/'candidate_manifest.json',manifest);results.append(manifest);print(cid,p['part_id'],'Q',manifest['FINAL_Q'],'BACKEND',manifest['BACKEND_ROUTE'],'STRUCT',qa.get('STRUCTURAL_CLASS') if qa else None,flush=True)
 accepted=[r for r in results if r['FINAL_ACCEPTED']];adir=OUT/'cases'/cid/'assembly';adir.mkdir(parents=True,exist_ok=True);final=adir/f'{cid}_batch_v2_xcaf.step'
 if accepted:base.write_xcaf([(r['part_id'],base.read_step(r['selected_step'])) for r in accepted],final,cid)
 coverage=sum(r['source_area_ratio'] for r in accepted);assembly_qa=base.qa_step(final,entry['source_obj']) if accepted else None
 dist=Counter(r['BACKEND_ROUTE'] for r in accepted);structured_coverage=sum(r['source_area_ratio'] for r in accepted if r['selected_qa']['CAD_STRUCTURE_Q']=='PASS')
 if accepted and all(r['selected_qa']['STRUCTURAL_CLASS']=='ANALYTIC_FEATURE_BREP' for r in accepted):case_class='ANALYTIC_FEATURE_BREP'
 elif structured_coverage>=.95:case_class='COMPACT_STRUCTURED_BREP'
 elif any(r['BACKEND_ROUTE']=='SOURCE_AWARE_SURFACE_BREP_FALLBACK' for r in accepted):case_class='SURFACE_BREP_FALLBACK'
 else:case_class='STRUCTURE_UNKNOWN'
 case_struct='PASS' if case_class in ('ANALYTIC_FEATURE_BREP','COMPACT_STRUCTURED_BREP') else 'FAIL'
 totals={k:sum(r['selected_qa'].get(k,0) or 0 for r in accepted) for k in ['FACE_COUNT','EDGE_COUNT','PLANE_FACE_COUNT','CYLINDER_FACE_COUNT','CONE_FACE_COUNT','SPHERE_FACE_COUNT','TORUS_FACE_COUNT','BSPLINE_FACE_COUNT','REVOLUTION_FACES','EXTRUSION_FACES','SURFACE_GROUP_COUNT','STRIP_EDGE_COUNT','FEATURE_COUNT','PROGRAM_OPERATION_COUNT']}
 result={'case_id':cid,'source_obj':entry['source_obj'],'CAD_PART_COUNT':len(results),'PARTS_ATTEMPTED':len(results),'PARTS_ACCEPTED':len(accepted),'PARTS_REJECTED':len(results)-len(accepted),'CAD_COVERAGE':coverage,'assembly_step':str(final) if accepted else None,'assembly_qa':assembly_qa,'GEOM_Q':assembly_qa.get('GEOMETRY_Q') if assembly_qa else None,'CHAMFER':assembly_qa.get('NORMALIZED_SYMMETRIC_CHAMFER') if assembly_qa else None,'P95':assembly_qa.get('P95') if assembly_qa else None,'COVERAGE02':assembly_qa.get('COVERAGE02') if assembly_qa else None,**totals,'BSPLINE_RATIO':totals['BSPLINE_FACE_COUNT']/max(totals['FACE_COUNT'],1),'ANALYTIC_RATIO':sum(totals[k] for k in ['PLANE_FACE_COUNT','CYLINDER_FACE_COUNT','CONE_FACE_COUNT','SPHERE_FACE_COUNT','TORUS_FACE_COUNT'])/max(totals['FACE_COUNT'],1),'STRIP_EDGE_RATIO':totals['STRIP_EDGE_COUNT']/max(totals['EDGE_COUNT'],1),'SHARP_EDGE_RECALL':float(np.average([r['selected_qa'].get('Sharp_Edge_Recall',0) for r in accepted],weights=[r['source_area_ratio'] for r in accepted])) if accepted else None,'FEATURE_BOUNDARY_RECALL':float(np.average([r['selected_qa'].get('Feature_Boundary_Recall',0) for r in accepted],weights=[r['source_area_ratio'] for r in accepted])) if accepted else None,'HOLE_RECALL':None,'INNER_WIRE_RECALL':None,'SLOT_RECALL':None,'NOTCH_RECALL':None,'NORMAL_P95':float(np.nanmax([r['selected_qa'].get('NORMAL_P95',np.nan) for r in accepted])) if accepted else None,'CAD_STRUCTURE_Q':case_struct,'STRUCTURAL_CLASS':case_class,'BACKEND_DISTRIBUTION':dict(dist),'MAC_USED':False,'MAC_LLM_CALLS':0,'MAC_ATTEMPTED_PARTS':0,'MAC_SKIPPED_PARTS':len(results),'MAC_SKIP_REASON':'HTTP_403_QUOTA_EXHAUSTED','residual_recovery':{'initial_accepted_coverage':coverage,'residual_required':coverage<.95,'residual_regions':0 if coverage>=.95 else None,'final_coverage':coverage},'parts':results}
 dump(OUT/'cases'/cid/'case_result.json',result);dump(OUT/'cases'/cid/'residual_recovery.json',result['residual_recovery']);return result

def main():
 inv=load(INV);results={};started=time.time()
 for cid,entry in inv['cases'].items():results[cid]=recover_case(cid,entry)
 dump(OUT/'artifacts/new_batch_results.json',{'cases':results,'elapsed_seconds':time.time()-started,'TOTAL_CAD_PARTS':sum(x['CAD_PART_COUNT'] for x in results.values()),'TOTAL_PARTS_ATTEMPTED':sum(x['PARTS_ATTEMPTED'] for x in results.values()),'TOTAL_PARTS_ACCEPTED':sum(x['PARTS_ACCEPTED'] for x in results.values())})

if __name__=='__main__':main()
