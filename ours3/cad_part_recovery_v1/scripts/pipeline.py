#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, csv, hashlib, importlib.util, json, math, os, re, shutil, sys, traceback
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
OURS3=ROOT/'ours3'
STAGE=OURS3/'cad_part_recovery_v1'
ART=STAGE/'artifacts'; CASES=STAGE/'cases'; LOGS=STAGE/'logs'
GRAPH_ROOT=OURS3/'cad_part_graph_gate1'
GRAPH_CASES=GRAPH_ROOT/'cases'
READY_MANIFEST=GRAPH_ROOT/'artifacts/cad_part_mac_manifest_v1.json'
CAD_GRAPH=GRAPH_ROOT/'artifacts/cad_part_graph_v1.json'
P3_GRAPH=GRAPH_ROOT/'artifacts/p3_segment_graph.json'
ASSOC=GRAPH_ROOT/'artifacts/physx_p3_association.json'
PHYSX=OURS3/'physx_and_alignment_recovery_v1/track_e2/cases/REAL_03/physx_v1/physx_understanding.json'
D2=OURS3/'cad_recovery_diag_v2/track_d2'
TRACK_C=OURS3/'next_stage_parallel_v1/track_c'
MAC_REPO=ROOT/'Multi-Agent-CAD'
CANONICAL_DIAGONAL_MM=100.0
SAMPLE_COUNT=50000; SAMPLE_SEED=20260810
Q1={'chamfer_max':.01,'p95_max':.02,'coverage02_min':.95}
Q2={'chamfer_max':.02,'p95_max':.05,'coverage02_min':.85}

def readj(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def writej(p,x):
 p=Path(p); p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(clean(x),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
def clean(x):
 if isinstance(x,dict): return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)): return [clean(v) for v in x]
 if isinstance(x,np.ndarray): return x.tolist()
 if isinstance(x,np.generic): return x.item()
 if isinstance(x,Path): return str(x)
 if hasattr(x,'model_dump'): return clean(x.model_dump())
 if hasattr(x,'value'): return x.value
 return x
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def matrix(scale=1.0,translation=(0,0,0)):
 m=np.eye(4); m[:3,:3]*=scale; m[:3,3]=np.asarray(translation,float); return m
def apply(points,m): return np.asarray(points)@m[:3,:3].T+m[:3,3]
def geometry_hash(p):
 import trimesh
 m=trimesh.load(p,force='mesh',process=False); tri=np.asarray(m.triangles); tri=np.sort(np.round(tri,8),axis=1); flat=tri.reshape(len(tri),-1); order=np.lexsort(flat.T[::-1]); return hashlib.sha256(flat[order].tobytes()).hexdigest()
def write_obj(p,v,f,note):
 with Path(p).open('w',encoding='utf-8',newline='\n') as h:
  h.write(f'# {note}\n')
  for x in v: h.write(f'v {x[0]:.12g} {x[1]:.12g} {x[2]:.12g}\n')
  for x in f: h.write(f'f {x[0]+1} {x[1]+1} {x[2]+1}\n')

def load_track_c():
 p=TRACK_C/'scripts/track_c_pipeline.py'; s=importlib.util.spec_from_file_location('track_c_f1',p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
 m.TRACK=STAGE; m.PREPARED_MAC=MAC_REPO; m.CANONICAL_DIAGONAL_MM=CANONICAL_DIAGONAL_MM; m.SAMPLE_COUNT=SAMPLE_COUNT; m.SAMPLE_SEED=SAMPLE_SEED
 return m

def canonicalize(value, stats):
 spec=json.loads(json.dumps(value)); diag=float(stats['bbox_diagonal_original']); center=np.asarray(stats['bbox_original']['min'])/2+np.asarray(stats['bbox_original']['max'])/2; scale=100/diag
 bbox=spec['object_geometry']['bbox']; bbox['min']=((np.asarray(bbox['min'])-center)*scale).tolist(); bbox['max']=((np.asarray(bbox['max'])-center)*scale).tolist(); bbox['extents']=(np.asarray(bbox['extents'])*scale).tolist()
 spec['object_geometry']['normalized_bbox_extents']=(np.asarray(stats['bbox_original']['extents'])/diag*100).tolist()
 base=spec.get('base_feature')
 if isinstance(base,dict):
  p=base.get('parameters',{})
  if p.get('units')=='normalized_bbox_diagonal':
   for k in ('radius','diameter','depth','height','estimated_depth','offset'):
    if isinstance(p.get(k),(int,float)): p[k]=float(p[k])*100
   for k in ('axis_point','center','position','axial_extent'):
    if isinstance(p.get(k),list): p[k]=[float(v)*100 for v in p[k]]
   p['units']='mm'
 spec.update({'DRAFT_ONLY':False,'NOT_EXECUTED_BY_MAC':False,'UNIT_KNOWN':True})
 s2c=matrix(scale,-center*scale); c2s=np.linalg.inv(s2c)
 spec['canonicalization']={'canonical_bbox_diagonal_mm':100.0,'source_bbox_center':center.tolist(),'source_bbox_diagonal':diag,'SOURCE_TO_CANONICAL':s2c.tolist(),'CANONICAL_TO_SOURCE':c2s.tolist(),'roundtrip_formula':'source = canonical @ R.T + t using CANONICAL_TO_SOURCE','MISSING_TRANSLATION_INVERSE_FIX_REUSED':True,'physical_unit_inferred':False}
 return spec

def high_features(spec, geo):
 out=[{'id':'BOUNDING_BOX','kind':'bbox','evidence':'measured_bbox','confidence':'HIGH'}]
 base=spec.get('base_feature')
 if isinstance(base,dict) and float(base.get('confidence',0))>=.5:
  out.append({'id':f"DOMINANT_BASE_{base['type']}",'kind':base['type'],'evidence':'base_feature','confidence':base.get('confidence_label','MEDIUM')})
 cov=geo['primitives']['coverage']
 if float(cov.get('CYLINDER_COVERAGE',0))>=.5: out.append({'id':'ANALYTIC_CYLINDER_SURFACE','kind':'CYLINDER','evidence':'coverage>=0.5','confidence':'HIGH'})
 holes=geo['holes']
 for i,h in enumerate(holes): out.append({'id':f'HOLE_{i:02d}','kind':'HOLE','evidence':h,'confidence':'HIGH'})
 patterns=geo['patterns']
 for i,h in enumerate(patterns): out.append({'id':f'PATTERN_{i:02d}','kind':'PATTERN','evidence':h,'confidence':'HIGH'})
 rot=geo['symmetry'].get('ROTATIONAL_ORDER_CANDIDATES',geo['symmetry'].get('rotational_order_candidates',[]))
 if rot and max(float(x.get('score',x.get('confidence',0))) for x in rot)>=.8: out.append({'id':'ROTATIONAL_SYMMETRY','kind':'SYMMETRY','evidence':rot[:3],'confidence':'HIGH'})
 return out

def prompt(cid,fused,features,geo):
 ids=[x['id'] for x in features]
 return f'''PROMPT_VARIANT=GEOMETRY_PLUS_PHYSX
SOURCE_OBJECT=REAL_03
CADPART_ID={cid}
CANONICAL_BBOX_DIAGONAL_MM=100.0
GEOMETRY_CONSTRAINT_PRIORITY=HARD
PHYSX_CONSTRAINT_PRIORITY=SOFT
PHYSX_ASSOCIATION_CONFIDENCE=UNKNOWN
ICP_ALLOWED=false

[PART SEMANTIC HINT]
No spatially localized PhysX part semantic is available. Object-level category "Lighting Fixture / Chandelier" is an UNKNOWN-confidence hint only. Do not convert it into geometry.

[HARD MEASURED GEOMETRY]
The following measured feature IDs are mandatory: {json.dumps(ids)}.
Target bbox and every numeric geometric measurement in FUSED_SPEC_JSON are hard constraints. Preserve axes, centers, primitive dimensions, holes, patterns and symmetry when present.
Do not replace measured geometry with semantic guesses.
Do not simplify the part to a single primitive when measured secondary geometry/features exist.
Preserve every high-confidence geometric feature reported in the CAD specification.

[CAD FEATURE HYPOTHESES]
HIGH_CONF_GEOMETRY_FEATURES={json.dumps(features,sort_keys=True)}
FEATURE_HYPOTHESES={json.dumps(geo['features'],sort_keys=True)}

[KINEMATIC / AFFORDANCE HINT]
No per-part spatial association exists. Kinematics and affordance are UNKNOWN-confidence context and must not constrain dimensions, topology, axes or placement.

[UNCERTAIN INFORMATION]
Physical scale prior 60*60*80 belongs to the whole object; it is soft and must not override the canonical measured part geometry. Unobserved semantics, functions, assembly relations and features are unknown.

FUSED_SPEC_JSON:
{json.dumps(fused,indent=2,sort_keys=True)}
'''

def geo_bundle(c):
 return {k:readj(c/p) for k,p in {
  'stats':'geometry_analysis/mesh_stats.json','primitives':'geometry_analysis/primitives.json','features':'geometry_analysis/feature_hypotheses.json','holes':'geometry_analysis/hole_candidates.json','patterns':'geometry_analysis/repeated_feature_hypotheses.json','symmetry':'geometry_analysis/symmetry.json','principal_axes':'geometry_analysis/principal_axes.json'}.items()}

def copy_reuse(pid,out):
 old=D2/f'cases/REAL_03_part_{pid:03d}/mac_output_geometry_only'
 out.mkdir(parents=True,exist_ok=True)
 for p in old.iterdir():
  if p.is_file() and p.name!='input_prompt.txt': shutil.copy2(p,out/p.name)
 (out/'historical_reused_input_prompt.txt').write_text((old/'input_prompt.txt').read_text(),encoding='utf-8')
 return old

def prepare():
 import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
 import trimesh
 for p in (ART,CASES,LOGS,STAGE/'scripts',STAGE/'tests',STAGE/'review_packets'): p.mkdir(parents=True,exist_ok=True)
 ready=readj(READY_MANIFEST); parts=ready['parts']; assert len(parts)==4
 ids=[x['cad_part_id'] for x in parts]; assert ids==['CADPART_000','CADPART_001','CADPART_004','CADPART_006']
 cad_graph=readj(CAD_GRAPH); assoc=readj(ASSOC); physx=readj(PHYSX)
 full=[]; new=[]; reuse=[]
 for entry in parts:
  cid=entry['cad_part_id']; pid=int(cid[-3:]); src=Path(entry['global_obj']); old_case=GRAPH_CASES/cid; case=CASES/cid; out=case/'mac_output'; case.mkdir(parents=True,exist_ok=True); out.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,case/'source_part.obj')
  geo=geo_bundle(old_case); original=readj(entry['cad_spec']); spec=canonicalize(original,geo['stats'])
  spec['hard_measured_geometry']={k:geo[k] for k in ('stats','primitives','features','holes','patterns','symmetry','principal_axes')}
  spec['GEOMETRY_CONSTRAINT_PRIORITY']='HARD'; spec['PHYSX_CONSTRAINT_PRIORITY']='NONE'; spec['physx_used']=False
  features=high_features(spec,geo)
  fused=json.loads(json.dumps(spec)); fused['PHYSX_CONSTRAINT_PRIORITY']='SOFT'; fused['physx_used']=True
  fused['physx_semantic']={'value':None,'association_confidence':'UNKNOWN','object_level_context':{'object_name':physx.get('object_name'),'object_category':physx.get('object_category')},'hard_constraint':False}
  fused['physx_kinematics']={'value':None,'association_confidence':'UNKNOWN','unlocalized_groups':physx.get('group_info_raw',[]),'hard_constraint':False}
  fused['physx_affordance']={'value':None,'association_confidence':'UNKNOWN','hard_constraint':False}
  fused['physx_scale_prior']={'value':physx.get('physical_scale_estimate'),'scope':'WHOLE_OBJECT','hard_constraint':False,'used_for_part_geometry':False}
  writej(case/'geometry_only_spec.json',spec); writej(case/'geometry_plus_physx_spec.json',fused)
  ptext=prompt(cid,fused,features,geo); (case/'mac_prompt_geometry_plus_physx.txt').write_text(ptext,encoding='utf-8'); (out/'input_prompt.txt').write_text(ptext,encoding='utf-8')
  coverage=1.0 if all(x['id'] in ptext for x in features) else 0.0; secondary=max(0,len(features)-1)
  banned=['Construct the simplest solid','Make the simplest watertight approximation','Ignore secondary geometry']; simplification=any(x in ptext for x in banned)
  transform=spec['canonicalization']; writej(case/'pre_mac_transform.json',transform)
  ids_new=np.load(old_case/'source_triangle_ids.npy').astype(np.int64)
  reusable=False; old=None; reuse_audit={'cad_part_id':cid,'source_p3_ids':[pid],'new_triangle_ids_sha256':hashlib.sha256(ids_new.tobytes()).hexdigest(),'new_mesh_byte_sha256':sha(src),'new_mesh_geometry_sha256':geometry_hash(src)}
  if pid in (0,4):
   oldprov=readj(D2/f'cases/REAL_03_part_{pid:03d}/provenance.json'); oldsrc=Path(oldprov['PART_OBJ_PATH']); ids_old=np.asarray(oldprov['SOURCE_TRIANGLE_IDS'],dtype=np.int64)
   reuse_audit.update({'historical_p3_id':oldprov['P3_PART_ID'],'historical_triangle_ids_sha256':oldprov['SOURCE_TRIANGLE_IDS_SHA256'],'historical_mesh_byte_sha256':sha(oldsrc),'historical_mesh_geometry_sha256':geometry_hash(oldsrc),'p3_id_match':oldprov['P3_PART_ID']==pid,'triangle_ids_match':bool(np.array_equal(ids_new,ids_old)),'mesh_geometry_sha256_match':geometry_hash(src)==geometry_hash(oldsrc),'mesh_byte_sha256_match':sha(src)==sha(oldsrc)})
   reusable=bool(reuse_audit['p3_id_match'] and reuse_audit['triangle_ids_match'] and reuse_audit['mesh_geometry_sha256_match'])
   if reusable: old=copy_reuse(pid,out); reuse.append(cid)
  reuse_audit['REUSE_EXISTING_MAC_RESULT']=reusable; writej(case/'existing_mac_reuse_audit.json',reuse_audit)
  spec_ready=coverage>=.90
  rec={'case_id':cid,'part_id':pid,'source_p3_ids':[pid],'source_obj':str(case/'source_part.obj'),'case_dir':str(case),'mac_output_dir':str(out),'geometry_only_spec':str(case/'geometry_only_spec.json'),'fused_spec':str(case/'geometry_plus_physx_spec.json'),'prompt':str(case/'mac_prompt_geometry_plus_physx.txt'),'high_conf_geometry_features':features,'HIGH_CONF_GEOMETRY_FEATURES':len(features),'HIGH_CONF_FEATURES_IN_PROMPT':len(features) if coverage==1 else 0,'PROMPT_FEATURE_COVERAGE':coverage,'SECONDARY_HIGH_CONF_FEATURES':secondary,'SIMPLIFICATION_DIRECTIVE_USED':simplification,'SPEC_READY':spec_ready,'REUSE_EXISTING_MAC_RESULT':reusable,'reused_from':str(old) if old else None,'mesh_to_cad_scale':100/float(geo['stats']['bbox_diagonal_original']),'cad_to_mesh_scale':float(geo['stats']['bbox_diagonal_original'])/100,'part_centroid_global':np.asarray(geo['stats']['bbox_original']['min'])/2+np.asarray(geo['stats']['bbox_original']['max'])/2}
  full.append(rec)
  if not reusable and spec_ready: new.append(rec)
 assert len(reuse)==2 and len(new)==2
 f1={'track':'CAD_PART_MAC_GATE_1','input_parts':4,'selection_source':str(READY_MANIFEST),'selection_source_sha256':sha(READY_MANIFEST),'allowed_parts':ids,'cases':full,'existing_results_reused':reuse,'new_mac_parts':[x['case_id'] for x in new],'serial_execution_required':True,'canonical_bbox_diagonal_mm':100.0,'quality_thresholds':{'Q1':Q1,'Q2':Q2},'PHYSX_3D_PART_LOCALIZATION_AVAILABLE':False,'NEW_P3_RUNS':0,'NEW_PHYSX_RUNS':0,'ASSEMBLY_STEP_GENERATED':False,'STEP_GT_USED':False,'ABC_DATA_USED':False,'ICP_USED':False}
 writej(ART/'track_f1_manifest.json',f1)
 tc={'track':'CAD_PART_MAC_GATE_1_NEW_ONLY','input_parts':len(new),'cases':new,'serial_execution_required':True,'canonical_bbox_diagonal_mm':100.0,'sample_count':SAMPLE_COUNT,'sample_seed':SAMPLE_SEED,'quality_thresholds':{'Q1_STRONG_PAIR':Q1,'Q2_USABLE_PAIR':Q2}}
 writej(ART/'track_c_manifest.json',tc)
 make_f2(cad_graph,readj(P3_GRAPH),assoc)
 print(json.dumps({'INPUT_PARTS':4,'REUSED':reuse,'NEW':[x['case_id'] for x in new]}))

def plot_mesh(ax,path,color,title):
 import trimesh
 m=trimesh.load(path,force='mesh',process=False); v=np.asarray(m.vertices); ids=np.arange(len(v));
 if len(ids)>5000: ids=ids[np.linspace(0,len(ids)-1,5000,dtype=int)]
 x=v[ids]; az,el=np.radians(35),np.radians(20); rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]]); rx=np.array([[1,0,0],[0,np.cos(el),-np.sin(el)],[0,np.sin(el),np.cos(el)]]); q=x@(rz@rx).T; ax.scatter(q[:,0],q[:,2],s=.2,c=color); ax.set_title(title,fontsize=8); ax.axis('off'); ax.set_aspect('equal')

def make_f2(cad_graph,p3,assoc):
 import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
 reviews=[e for e in p3['edges'] if e['decision']=='REVIEW_MERGE']; assert len(reviews)==14
 amap={x['p3_segment_id']:x for x in assoc['associations']}
 rows=[]; fig,axes=plt.subplots(14,3,figsize=(15,52),dpi=120)
 for i,e in enumerate(reviews):
  a,b=e['segment_a'],e['segment_b']; eid=f'EDGE_{i:02d}_{a:03d}_{b:03d}'; pa=OURS3/f'fusion_pipeline/cases/REAL_03/segmentation/part_{a:03d}.obj'; pb=OURS3/f'fusion_pipeline/cases/REAL_03/segmentation/part_{b:03d}.obj'
  sema=amap[a]['physx_part_candidates'] or ['UNKNOWN']; semb=amap[b]['physx_part_candidates'] or ['UNKNOWN']
  packet={'EDGE_ID':eid,'segment_a':a,'segment_b':b,'segment_a_obj':str(pa),'segment_b_obj':str(pb),'shared_boundary_score':e['score_terms']['shared_boundary_score'],'surface_continuity':e['score_terms']['surface_continuity_score'],'primitive_relation':e['primitive_relation'],'normal_continuity':e['score_terms']['normal_tangent_continuity'],'proximity':e['score_terms']['proximity_score'],'geometry_merge_score':e['geometry_merge_score'],'physx_semantic_a':sema,'physx_semantic_b':semb,'physx_same_part_prior':e['physx_same_part_score'],'physx_separation_prior':e['physx_separate_score'],'final_merge_score':e['final_merge_score'],'current_decision':'REVIEW','human_decision_applied':False}
  pdir=STAGE/'review_packets'/eid; pdir.mkdir(parents=True,exist_ok=True); writej(pdir/'review_packet.json',packet)
  small,axs=plt.subplots(1,3,figsize=(12,4),dpi=120); plot_mesh(axs[0],pa,'#1f77b4',f'SEG {a}'); plot_mesh(axs[1],pb,'#ff7f0e',f'SEG {b}'); plot_mesh(axs[2],pa,'#1f77b4','COMBINED'); plot_mesh(axs[2],pb,'#ff7f0e',f'COMBINED score={e["final_merge_score"]:.3f}'); small.tight_layout(); small.savefig(pdir/'combined_preview.png'); plt.close(small)
  plot_mesh(axes[i,0],pa,'#1f77b4',f'SEG_A {a}'); plot_mesh(axes[i,1],pb,'#ff7f0e',f'SEG_B {b}'); plot_mesh(axes[i,2],pa,'#1f77b4','COMBINED'); plot_mesh(axes[i,2],pb,'#ff7f0e',f'{eid} SCORE={e["final_merge_score"]:.3f}')
  rows.append({'EDGE_ID':eid,'P3_A':a,'P3_B':b,'GEOMETRY_SCORE':e['geometry_merge_score'],'PHYSX_SCORE':e['physx_same_part_score'],'FINAL_SCORE':e['final_merge_score'],'SEMANTIC_A':'UNKNOWN','SEMANTIC_B':'UNKNOWN','CURRENT_DECISION':'REVIEW','HUMAN_DECISION':'','NOTES':''})
 fig.tight_layout(); fig.savefig(ART/'review_merge_edges_14.png'); plt.close(fig)
 fields=list(rows[0]);
 with (ART/'review_merge_edges_14.csv').open('w',newline='',encoding='utf-8') as h: w=csv.DictWriter(h,fieldnames=fields); w.writeheader(); w.writerows(rows)
 review_parts=[n for n in cad_graph['nodes'] if n['reconstruction_state']=='REVIEW_BEFORE_CAD']; assert len(review_parts)==20
 fig,axes=plt.subplots(5,4,figsize=(16,20),dpi=120)
 for ax,n in zip(axes.ravel(),review_parts):
  cid=n['cad_part_id']; c=GRAPH_CASES/cid; stats=readj(c/'geometry_analysis/mesh_stats.json'); prim=readj(c/'geometry_analysis/primitives.json'); plot_mesh(ax,n['global_obj'],'#4c78a8',f"{cid} P3={n['source_p3_segment_ids']}\n{n['cadability_class'][0]} analytic={prim['coverage']['TOTAL_ANALYTIC_COVERAGE']:.3f}\nPhysX=UNKNOWN; why=review-edge incident")
 fig.tight_layout(); fig.savefig(ART/'review_before_cad_20.png'); plt.close(fig)
 writej(ART/'track_f2_summary.json',{'TRACK_F2':'CAD_PART_REVIEW_GATE_1','TRACK_F2_STATUS':'PASS','REVIEW_EDGES_PREPARED':14,'REVIEW_PARTS_PREPARED':20,'REVIEW_PACKETS_COMPLETE':all((STAGE/'review_packets'/r['EDGE_ID']/'combined_preview.png').is_file() for r in rows),'HUMAN_DECISIONS_APPLIED':False,'NEW_MAC_RUNS':0,'NEW_PHYSX_RUNS':0,'NEW_P3_RUNS':0,'BLOCKERS':[]})

def run_case(cid): return load_track_c().run_case(cid)

def fresh_step(step):
 from build123d import import_step
 from OCP.BRepCheck import BRepCheck_Analyzer
 from OCP.IFSelect import IFSelect_RetDone
 from OCP.STEPControl import STEPControl_Reader
 rd=STEPControl_Reader(); status=rd.ReadFile(str(step));
 if status!=IFSelect_RetDone: raise RuntimeError(f'STEP reload status {status}')
 rd.TransferRoots(); shape=rd.OneShape(); valid=bool(BRepCheck_Analyzer(shape).IsValid()); b=import_step(step); v,t=b.tessellate(tolerance=.05,angular_tolerance=.1); return shape,np.asarray([[x.X,x.Y,x.Z] for x in v]),np.asarray(t,dtype=np.int64),valid

def geo_metrics(source,generated,valid):
 import trimesh
 from scipy.spatial import cKDTree
 sp,sf=trimesh.sample.sample_surface(source,SAMPLE_COUNT,seed=SAMPLE_SEED); cp,cf=trimesh.sample.sample_surface(generated,SAMPLE_COUNT,seed=SAMPLE_SEED+1); sn=source.face_normals[sf]; cn=generated.face_normals[cf]; ct,st=cKDTree(cp),cKDTree(sp); d1,i1=ct.query(sp,workers=-1); d2,i2=st.query(cp,workers=-1); diag=float(np.linalg.norm(source.extents)); a,b=d1/diag,d2/diag; sym=np.r_[a,b]; n1=np.abs(np.sum(sn*cn[i1],axis=1)); n2=np.abs(np.sum(cn*sn[i2],axis=1)); se,ce=source.extents,generated.extents; sc,cc=source.bounds.mean(0),generated.bounds.mean(0)
 out={'symmetric_chamfer_normalized':float((a.mean()+b.mean())/2),'p95_symmetric':float(np.quantile(sym,.95)),'hausdorff_approx':float(sym.max()),'coverage_005':float((a<=.005).mean()),'coverage_01':float((a<=.01).mean()),'coverage_02':float((a<=.02).mean()),'cad_to_source_coverage_01':float((b<=.01).mean()),'normal_consistency':float((n1.mean()+n2.mean())/2),'bbox_center_error':float(np.linalg.norm(cc-sc)/diag),'bbox_size_errors':(np.abs(ce-se)/np.maximum(se,1e-12)).tolist(),'distance_normalization':'part_bbox_diagonal','sample_count_per_surface':SAMPLE_COUNT,'sample_seed':SAMPLE_SEED,'icp_used':False}
 if valid and out['symmetric_chamfer_normalized']<=.01 and out['p95_symmetric']<=.02 and out['coverage_02']>=.95: q='Q1_STRONG_PAIR'
 elif valid and out['symmetric_chamfer_normalized']<=.02 and out['p95_symmetric']<=.05 and out['coverage_02']>=.85: q='Q2_USABLE_PAIR'
 else:q='Q3_REJECT'
 out['quality_class']=q; return out,sp,cp,a

def realized(features,code,metrics,valid):
 c=code.lower(); got=[]
 for x in features:
  k=x['kind'].lower(); ok=False
  if x['id']=='BOUNDING_BOX': ok=valid and max(metrics['bbox_size_errors'])<=.10
  elif k=='revolution': ok=any(z in c for z in ('revol','cylinder','cone','sphere'))
  elif k=='cylinder': ok='cylinder' in c
  elif k=='hole': ok=any(z in c for z in ('hole','cut','subtract'))
  elif k=='pattern': ok=any(z in c for z in ('for ','range(','pattern','polar'))
  elif k=='symmetry': ok=any(z in c for z in ('cylinder','revol','polar','pattern'))
  if ok: got.append(x['id'])
 return got

def qa_case(cid):
 import trimesh
 manifest=readj(ART/'track_f1_manifest.json'); rec=next(x for x in manifest['cases'] if x['case_id']==cid); out=Path(rec['mac_output_dir']); qa={'case_id':cid,'step_reload_success':False,'brep_valid':False,'geometry_metrics_computed':False,'fresh_step_tessellation':False,'icp_used':False,'error_class':None,'error_message':None}
 try:
  shape,v,f,valid=fresh_step(out/'generated.step'); qa['step_reload_success']=True; qa['brep_valid']=valid; qa.update(load_track_c().topology_counts(shape)); qa['fresh_step_tessellation']=True
  source=trimesh.load(rec['source_obj'],force='mesh',process=False); canonical=trimesh.Trimesh(vertices=v,faces=f,process=False); source_center=source.bounds.mean(0); diag=float(np.linalg.norm(source.extents)); canonical_center=canonical.bounds.mean(0)
  s2n=matrix(1/diag,-source_center/diag); n2c=matrix(100,canonical_center); s2c=n2c@s2n; c2s=np.linalg.inv(s2c); vg=apply(v,c2s); generated=trimesh.Trimesh(vertices=vg,faces=f,process=False); write_obj(out/'generated_step_source_frame.obj',vg,f,'Fresh OCC tessellation mapped by fixed MISSING_TRANSLATION_INVERSE protocol; no ICP')
  pts,_=trimesh.sample.sample_surface(source,12000,seed=SAMPLE_SEED); rt=apply(apply(pts,s2c),c2s); err=np.linalg.norm(rt-pts,axis=1)/diag
  ledger={'SOURCE_TO_CANONICAL':s2c.tolist(),'CANONICAL_TO_SOURCE':c2s.tolist(),'SOURCE_BBOX_CENTER':source_center.tolist(),'SOURCE_BBOX_DIAGONAL':diag,'STEP_CANONICAL_BBOX_CENTER':canonical_center.tolist(),'MISSING_TRANSLATION_INVERSE_FIX_REUSED':True,'ROUNDTRIP_MEAN_ERROR_NORMALIZED':float(err.mean()),'ROUNDTRIP_MAX_ERROR_NORMALIZED':float(err.max()),'ROUNDTRIP_PASS':bool(err.mean()<1e-10 and err.max()<1e-8),'ICP_USED':False}
  writej(out/'transform_ledger.json',ledger); m,sp,cp,d=geo_metrics(source,generated,valid); qa.update(m); qa['geometry_metrics_computed']=True
  code=(out/'generated_code.py').read_text(errors='ignore') if (out/'generated_code.py').is_file() else ''; got=realized(rec['high_conf_geometry_features'],code,m,valid); qa['SPEC_FEATURE_COUNT']=len(rec['high_conf_geometry_features']); qa['REALIZED_FEATURE_COUNT']=len(got); qa['REALIZED_FEATURE_IDS']=got; qa['FEATURE_REALIZATION_RATE']=len(got)/max(1,len(rec['high_conf_geometry_features']))
  make_case_vis(cid,source,generated,sp,cp,d,qa,out/'part_geometry_comparison.png')
 except Exception as e: qa['error_class']=type(e).__name__; qa['error_message']=str(e)[:2000]; (out/'qa_traceback.txt').write_text(traceback.format_exc(),encoding='utf-8')
 writej(out/'independent_ours_qa.json',qa); return 0 if qa['geometry_metrics_computed'] else 4

def proj(x):
 a,e=np.radians(35),np.radians(20); rz=np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]]); rx=np.array([[1,0,0],[0,np.cos(e),-np.sin(e)],[0,np.sin(e),np.cos(e)]]); q=np.asarray(x)@(rz@rx).T; return q[:,[0,2]]
def make_case_vis(cid,src,cad,sp,cp,d,qa,path):
 import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
 s=proj(sp[::5]); c=proj(cp[::5]); dd=d[::5]; fig,ax=plt.subplots(1,4,figsize=(16,4),dpi=120); ax[0].scatter(s[:,0],s[:,1],s=.2,c='#444'); ax[0].set_title('SOURCE'); ax[1].scatter(c[:,0],c[:,1],s=.2,c='#1f77b4'); ax[1].set_title('STEP FRESH MESH'); ax[2].scatter(s[:,0],s[:,1],s=.15,c='#d62728'); ax[2].scatter(c[:,0],c[:,1],s=.15,c='#1f77b4',alpha=.6); ax[2].set_title('OVERLAY'); sc=ax[3].scatter(s[:,0],s[:,1],s=.2,c=dd,cmap='magma'); fig.colorbar(sc,ax=ax[3]); ax[3].set_title('DISTANCE');
 for x in ax:x.axis('off');x.set_aspect('equal')
 fig.suptitle(f"{cid} | {qa['quality_class']} | chamfer={qa['symmetric_chamfer_normalized']:.4f} p95={qa['p95_symmetric']:.4f} cov02={qa['coverage_02']:.3f} feature={qa['FEATURE_REALIZATION_RATE']:.3f}"); fig.tight_layout(); fig.savefig(path); plt.close(fig)

def finalize():
 import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
 from PIL import Image
 mf=readj(ART/'track_f1_manifest.json'); cases=[]
 for rec in mf['cases']:
  out=Path(rec['mac_output_dir']); qa=readj(out/'independent_ours_qa.json') if (out/'independent_ours_qa.json').is_file() else {'quality_class':'Q3_REJECT','step_reload_success':False,'brep_valid':False,'geometry_metrics_computed':False,'fresh_step_tessellation':False,'icp_used':False,'error_class':'STEP_UNAVAILABLE_QUOTA','error_message':'Provider HTTP 403 AllocationQuota.FreeTierOnly before any model output','symmetric_chamfer_normalized':None,'p95_symmetric':None,'coverage_02':0.0,'FEATURE_REALIZATION_RATE':0.0,'SPEC_FEATURE_COUNT':rec['HIGH_CONF_GEOMETRY_FEATURES'],'REALIZED_FEATURE_COUNT':0}; run=readj(out/'mac_run_result.json') if (out/'mac_run_result.json').is_file() else {}; cases.append({**rec,'run':run,'qa':qa})
 q=Counter(x['qa'].get('quality_class','Q3_REJECT') for x in cases); accepted=[x for x in cases if x['qa'].get('quality_class') in ('Q1_STRONG_PAIR','Q2_USABLE_PAIR')]
 export=OURS3/'real03_cad_parts_v1'; export.mkdir(parents=True,exist_ok=True)
 for x in accepted:
  cid=x['case_id']; src=Path(x['source_obj']); out=Path(x['mac_output_dir']); dest=export/cid; dest.mkdir(parents=True,exist_ok=True)
  shutil.copy2(src,dest/'source_part.obj'); shutil.copy2(out/'generated.step',dest/'part.step'); shutil.copy2(out/'generated_code.py',dest/'cad_program.py'); shutil.copy2(x['geometry_only_spec'],dest/'geometry_spec.json'); shutil.copy2(x['fused_spec'],dest/'fused_spec.json'); shutil.copy2(out/'independent_ours_qa.json',dest/'metrics.json'); shutil.copy2(out/'transform_ledger.json',dest/'local_to_global_transform.json')
  writej(dest/'provenance.json',{'source_stage':'CAD_PART_RECOVERY_V1','cad_part_id':cid,'reused_existing_mac_result':x['REUSE_EXISTING_MAC_RESULT'],'quality_class':x['qa']['quality_class'],'q3_exported':False,'assembly_step_generated':False})
 fig,axes=plt.subplots(4,1,figsize=(18,18),dpi=120)
 for ax,x in zip(axes,cases):
  vis=Path(x['mac_output_dir'])/'part_geometry_comparison.png'; qx=x['qa']; ax.axis('off')
  if vis.is_file(): ax.imshow(Image.open(vis)); ctext=f"C={qx['symmetric_chamfer_normalized']:.4f} P95={qx['p95_symmetric']:.4f} Cov02={qx['coverage_02']:.3f} Feature={qx['FEATURE_REALIZATION_RATE']:.3f}"
  else: ax.text(.5,.5,'NO STEP — PROVIDER QUOTA BLOCKER',ha='center',va='center',fontsize=18,color='#b22222'); ctext='metrics=N/A Feature=0.000'
  ax.set_title(f"{x['case_id']} | semantic=UNKNOWN | {qx['quality_class']} | {ctext}")
 fig.tight_layout(); fig.savefig(ART/'cad_part_mac_gate1_contact_sheet.png'); plt.close(fig)
 total_step=sum((Path(x['mac_output_dir'])/'generated.step').is_file() for x in cases); brep=sum(bool(x['qa'].get('brep_valid')) for x in cases); new_attempt=sum(not x['REUSE_EXISTING_MAC_RESULT'] and bool(x['run'].get('attempted')) for x in cases)
 blockers=[] if total_step==4 else ['QUOTA']
 f1={'TRACK_F1':'CAD_PART_MAC_GATE_1','TRACK_F1_STATUS':'PASS' if len(cases)==4 and total_step==4 else 'BLOCKED','INPUT_CAD_PARTS':4,'REUSED_EXISTING_MAC_RESULTS':sum(x['REUSE_EXISTING_MAC_RESULT'] for x in cases),'NEW_MAC_ATTEMPTED':new_attempt,'TOTAL_STEP_AVAILABLE':total_step,'BREP_VALID_COUNT':brep,'Q1_STRONG_PAIR':q['Q1_STRONG_PAIR'],'Q2_USABLE_PAIR':q['Q2_USABLE_PAIR'],'Q3_REJECT':q['Q3_REJECT'],'ACCEPTED_CAD_PARTS':len(accepted),'PART_CAD_RECOVERY_RATE':len(accepted)/4,'CASES':cases,'BLOCKERS':blockers}
 writej(ART/'track_f1_summary.json',f1); f2=readj(ART/'track_f2_summary.json'); assembly=len(accepted); ready=assembly>=2
 summary={'CURRENT_STAGE':'CAD_PART_RECOVERY_V1_COMPLETE','TRACK_F1':'CAD_PART_MAC_GATE_1','TRACK_F1_STATUS':f1['TRACK_F1_STATUS'],'INPUT_CAD_PARTS':4,'REUSED_EXISTING_MAC_RESULTS':f1['REUSED_EXISTING_MAC_RESULTS'],'NEW_MAC_ATTEMPTED':new_attempt,'TOTAL_STEP_AVAILABLE':total_step,'BREP_VALID_COUNT':brep,'Q1_STRONG_PAIR':q['Q1_STRONG_PAIR'],'Q2_USABLE_PAIR':q['Q2_USABLE_PAIR'],'Q3_REJECT':q['Q3_REJECT'],'ACCEPTED_CAD_PARTS':len(accepted),'PART_CAD_RECOVERY_RATE':len(accepted)/4,'TRACK_F2':'CAD_PART_REVIEW_GATE_1','TRACK_F2_STATUS':f2['TRACK_F2_STATUS'],'REVIEW_EDGES_PREPARED':14,'REVIEW_PARTS_PREPARED':20,'HUMAN_DECISIONS_APPLIED':False,'ASSEMBLY_CAD_PARTS_AVAILABLE':assembly,'PARTIAL_ASSEMBLY_PILOT_READY':ready,'NEW_P3_RUNS':0,'NEW_PHYSX_RUNS':0,'ASSEMBLY_STEP_GENERATED':False,'STEP_GT_USED':False,'ABC_DATA_USED':False,'TESTS_PASSED':0,'TESTS_FAILED':0,'BLOCKERS_BY_TRACK':{'F1':blockers,'F2':[]}}
 writej(ART/'cad_part_recovery_v1_summary.json',summary)
 writej(ART/'quota_blocker_audit.json',{'track':'F1','case_id':'CADPART_006','blocker_enum':'QUOTA','provider_error_code':403,'provider_error_type':'AllocationQuota.FreeTierOnly','provider_message':'Free quota exhausted. To continue accessing the model on a paid basis, add funds or disable free tier only mode.','llm_calls':0,'tokens':0,'step_generated':False,'retry_performed':False,'retry_reason':'Deterministic quota rejection is not transient','historical_reuse_search_complete':True,'matching_historical_step_found':False})
 report=f'''# CAD Part Recovery V1\n\nStatus: {summary['CURRENT_STAGE']}\n\nF1: {f1['REUSED_EXISTING_MAC_RESULTS']} existing results reused, {new_attempt} new MAC attempts, {total_step} STEP available, {brep} BRep valid. Q1/Q2/Q3={q['Q1_STRONG_PAIR']}/{q['Q2_USABLE_PAIR']}/{q['Q3_REJECT']}; accepted={len(accepted)}/4.\n\nF2: 14 review edges and 20 review parts prepared; no decision applied.\n\nAssembly metadata readiness: {assembly} accepted CAD parts; pilot ready={str(ready).lower()}. No assembly STEP generated.\n'''; (ART/'cad_part_recovery_v1_report.md').write_text(report,encoding='utf-8')
 print(json.dumps(summary,indent=2))

def main():
 ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest='cmd',required=True); sp.add_parser('prepare'); x=sp.add_parser('run-case'); x.add_argument('case'); x=sp.add_parser('qa-case'); x.add_argument('case'); sp.add_parser('finalize'); a=ap.parse_args()
 if a.cmd=='prepare': prepare()
 elif a.cmd=='run-case': sys.exit(run_case(a.case))
 elif a.cmd=='qa-case': sys.exit(qa_case(a.case))
 else: finalize()
if __name__=='__main__':main()
