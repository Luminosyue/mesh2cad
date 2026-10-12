#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil
from pathlib import Path
import numpy as np
import trimesh

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'batch_part_to_cad_recovery_v2'
TARGETS=['CASE_00','CASE_02','CASE_03','CASE_04','CASE_05','CASE_08','CASE_09']
MANIFEST=ROOT/'batch_real_mesh2cad_v1/manifest/batch_10_case_manifest.json'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(d),indent=2,sort_keys=True)+'\n')
def clean(v):
 if isinstance(v,dict):return {str(k):clean(x) for k,x in v.items()}
 if isinstance(v,(list,tuple)):return [clean(x) for x in v]
 if isinstance(v,np.ndarray):return v.tolist()
 if isinstance(v,np.generic):return v.item()
 if isinstance(v,Path):return str(v)
 if isinstance(v,float) and not np.isfinite(v):return None
 return v

def boundary_loop_count(mesh):
 edges=np.sort(np.asarray(mesh.edges).reshape((-1,2)),axis=1);u,c=np.unique(edges,axis=0,return_counts=True);b=u[c==1]
 if not len(b):return 0,len(b)
 try:return len(trimesh.graph.connected_components(b,nodes=np.unique(b),min_len=1)),len(b)
 except Exception:return None,len(b)

def analyze(mesh,case_id,part_id):
 v=np.asarray(mesh.vertices,float); ext=np.asarray(mesh.extents,float); center=v.mean(0);cov=np.cov(v-center,rowvar=False);vals,axes=np.linalg.eigh(cov);order=np.argsort(vals)[::-1];vals=vals[order];axes=axes[:,order]
 normals=np.asarray(mesh.face_normals,float); areas=np.asarray(mesh.area_faces,float); total=max(float(areas.sum()),1e-12)
 # Area support close to the six PCA-aligned plane normal directions.
 support=[]
 for i in range(3):support.append(float(areas[np.abs(normals@axes[:,i])>=np.cos(np.deg2rad(10))].sum()/total))
 angles=np.degrees(np.asarray(mesh.face_adjacency_angles,float));sharp=int(np.sum(angles>=30))
 loops,boundary_edges=boundary_loop_count(mesh)
 radial=float(min(ext[1],ext[2])/max(ext[1],ext[2],1e-12));elong=float(ext.max()/max(np.partition(ext,-2)[-2],1e-12))
 plane_regions=[{'axis':int(i),'normal':axes[:,i].tolist(),'area_support_ratio':support[i]} for i in range(3) if support[i]>=.01]
 cyl={'axis':axes[:,int(np.argmax(ext))].tolist(),'radial_extent_similarity':radial,'elongation':elong,'confidence':float(max(0,min(1,radial*(elong-1))))}
 return {
  'schema':'BATCH_V2_GEOMETRY_ANALYSIS_V1','case_id':case_id,'part_id':part_id,
  'measurements':{'bbox_min':mesh.bounds[0].tolist(),'bbox_max':mesh.bounds[1].tolist(),'extents':ext.tolist(),'centroid':center.tolist(),'surface_area':float(mesh.area),'volume':float(abs(mesh.volume)) if mesh.is_volume else None,'triangle_count':len(mesh.faces)},
  'plane':{'regions':plane_regions,'area_support_ratio_max':max(support)},'cylinder':cyl,'axis':{'principal_axes':axes.tolist(),'eigenvalues':vals.tolist()},
  'profile':{'available':True,'basis':'PCA_BOUNDARY_PROJECTION'},'loop':{'boundary_loop_count':loops,'boundary_edge_count':boundary_edges},
  'extrusion_hypothesis':{'enabled':bool(max(support)>=.25),'confidence':max(support)},'revolution_hypothesis':{'enabled':bool(cyl['confidence']>=.45),'confidence':cyl['confidence']},
  'loft_hypothesis':{'enabled':False,'reason':'NO_ORDERED_SEMANTIC_SECTION_SET'},'sweep_hypothesis':{'enabled':False,'reason':'NO_MEASURED_PATH_PROFILE_PAIR'},
  'holes':{'candidates':loops if loops else 0,'semantic_confirmed':False},'slots':{'candidates':0,'semantic_confirmed':False},
  'sharp_curves':{'edge_count_ge_30deg':sharp,'adjacency_edge_count':len(angles)},'symmetry':{'bbox_centered_axes':[0,1,2],'type':'MEASURED_BBOX_HYPOTHESIS_ONLY'},
  'freeform_regions':{'present':bool(max(support)<.5),'count':1 if max(support)<.5 else 0},'raw_mesh_used_by_analyzer':True,
 }

def feature_graph(a):
 types=['PLANE_REGION','CYLINDER_REGION','PROFILE','LOOP','EXTRUSION','REVOLUTION','LOFT','SWEEP','HOLE','SLOT','CUT','PATTERN','FREEFORM_REGION']
 enabled={
  'PLANE_REGION':bool(a['plane']['regions']),'CYLINDER_REGION':a['cylinder']['confidence']>=.45,'PROFILE':True,'LOOP':bool(a['loop']['boundary_loop_count']),
  'EXTRUSION':a['extrusion_hypothesis']['enabled'],'REVOLUTION':a['revolution_hypothesis']['enabled'],'LOFT':False,'SWEEP':False,'HOLE':False,'SLOT':False,'CUT':False,'PATTERN':False,'FREEFORM_REGION':a['freeform_regions']['present']}
 return {'schema':'CAD_FEATURE_GRAPH_V2','case_id':a['case_id'],'part_id':a['part_id'],'source':'GEOMETRY_ANALYZER_MEASUREMENTS','raw_mesh_included':False,
         'feature_vocabulary':types,'nodes':[{'id':f'F{i:03d}','type':t,'enabled':bool(enabled[t]),'measurement_ref':t.lower()} for i,t in enumerate(types)],'edges':[],'geometry_analysis_digest':hashlib.sha256(json.dumps(clean(a),sort_keys=True).encode()).hexdigest()}

def main():
 for d in ['cases','metrics','artifacts','scripts','logs','tests','manifest']: (OUT/d).mkdir(parents=True,exist_ok=True)
 frozen=json.loads(MANIFEST.read_text());rows={x['BATCH_CASE_ID']:x for x in frozen['cases']};inventory={'schema':'BATCH_PART_TO_CAD_RECOVERY_V2_INPUTS','frozen_manifest':str(MANIFEST),'cases':{}}
 case09_summary=json.loads((ROOT/'case09_aircraft_end2end_cad_v1/metrics/summary.json').read_text())
 historical={
  'CASE_00':ROOT/'negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step',
  'CASE_02':ROOT/'batch_real_mesh2cad_v1/cases/CASE_02/cad_recovery/reconstructed.step',
  'CASE_03':ROOT/'batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step',
  'CASE_04':ROOT/'feature_preserving_compact_cad_v2/case04/v2_feature_preserving.step',
  'CASE_05':ROOT/'case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step',
  'CASE_08':ROOT/'batch_real_mesh2cad_v1/cases/CASE_08/cad_recovery/reconstructed.step',
  'CASE_09':ROOT/'case09_aircraft_end2end_cad_v1/07_assembly/CASE09_aircraft_final.step'}
 for cid in TARGETS:
  row=rows[cid];source=Path(row['SOURCE_OBJ_PATH']);actual=sha(source)
  if actual!=row['SOURCE_SHA256']:raise RuntimeError(f'{cid}: source SHA mismatch')
  mesh=trimesh.load(source,force='mesh',process=False);groups=[];reuse={}
  if cid=='CASE_00':
   tri_path=ROOT/'fusion_pipeline/cases/REAL_03/segmentation/triangle_part_id.npy';labels=np.load(tri_path);groups=[([int(x)],f'CADPART_{i:03d}') for i,x in enumerate(sorted(np.unique(labels[labels>=0])))]
   reuse={'mode':'REUSED_VALIDATED_P3','triangle_map':str(tri_path),'physx':str(ROOT/'physx_and_alignment_recovery_v1/track_e2')}
  elif cid=='CASE_05':
   tri_path=ROOT/'batch_real_mesh2cad_v1/cases/CASE_05/p3/triangle_part_id.npy';labels=np.load(tri_path);groups=[([int(x)],f'CADPART_{i:03d}') for i,x in enumerate(sorted(np.unique(labels[labels>=0])))]
   reuse={'mode':'REUSED_VALIDATED_P3_PHYSX_GRAPH','triangle_map':str(tri_path),'physx':str(ROOT/'batch_real_mesh2cad_v1/cases/CASE_05/physx_v1'),'part_graph':str(ROOT/'batch_real_mesh2cad_v1/cases/CASE_05/cad_part_graph/cad_part_graph_v1.json')}
  elif cid=='CASE_09':
   tri_path=ROOT/'case09_aircraft_end2end_cad_v1/01_part_discovery/p3/triangle_part_id.npy';labels=np.load(tri_path);groups=[(list(map(int,x['segments'])),x['part_id']) for x in case09_summary['part_qa']]
   reuse={'mode':'REUSED_VALIDATED_CASE09_P3_PHYSX_GRAPH','triangle_map':str(tri_path),'physx':str(ROOT/'case09_aircraft_end2end_cad_v1/01_part_discovery/physx'),'part_graph':str(ROOT/'case09_aircraft_end2end_cad_v1/02_cad_part_graph/cad_part_graph.json')}
  else:
   labels=None;groups=[(None,'CADPART_000')];reuse={'mode':'FROZEN_WHOLE_OBJECT_ROUTE','reason':'ORIGINAL_ROUTE_WHOLE_OBJECT_NO_P3_REQUIRED','physx':str(ROOT/f'batch_real_mesh2cad_v1/cases/{cid}/physx_v1')}
  if labels is not None and len(labels)!=len(mesh.faces):raise RuntimeError(f'{cid}: triangle count mismatch {len(labels)} != {len(mesh.faces)}')
  total=float(mesh.area);parts=[]
  for segs,pid in groups:
   if segs is None:sub=mesh;part_mesh=source;face_count=len(mesh.faces)
   else:
    ids=np.flatnonzero(np.isin(labels,segs));sub=mesh.submesh([ids],append=True,repair=False);part_mesh=OUT/'cases'/cid/'parts'/pid/'input/source_part.obj';part_mesh.parent.mkdir(parents=True,exist_ok=True);sub.export(part_mesh);face_count=len(ids)
   pdir=OUT/'cases'/cid/'parts'/pid/'input';pdir.mkdir(parents=True,exist_ok=True);ga=analyze(sub,cid,pid);fg=feature_graph(ga)
   spec={'schema':'MEASURED_CAD_SPEC_V2','case_id':cid,'part_id':pid,'source':'GEOMETRY_ANALYZER_ONLY','raw_mesh_included':False,'measurements':ga['measurements'],'principal_axes':ga['axis'],'feature_hypotheses':{k:ga[k] for k in ['extrusion_hypothesis','revolution_hypothesis','loft_hypothesis','sweep_hypothesis']}}
   dump(pdir/'geometry_analysis.json',ga);dump(pdir/'cad_feature_graph.json',fg);dump(pdir/'measured_cad_spec.json',spec)
   part={'part_id':pid,'segments':segs,'mesh':str(part_mesh),'mesh_sha256':sha(part_mesh),'triangle_count':face_count,'source_area':float(sub.area),'source_area_ratio':float(sub.area/total),'geometry_analysis':str(pdir/'geometry_analysis.json'),'cad_feature_graph':str(pdir/'cad_feature_graph.json'),'measured_cad_spec':str(pdir/'measured_cad_spec.json')}
   dump(pdir/'input_manifest.json',part);parts.append(part)
  coverage=sum(x['source_area_ratio'] for x in parts)
  entry={'case_id':cid,'source_obj':str(source),'source_sha256':actual,'source_triangle_count':len(mesh.faces),'source_bbox':mesh.bounds.tolist(),'router_class':row['ROUTER_CLASS'],'part_discovery_reuse':reuse,'cad_part_count':len(parts),'part_graph_coverage':coverage,'parts':parts,'historical_best':str(historical[cid]),'historical_best_sha256':sha(historical[cid])}
  if abs(coverage-1)>1e-8:raise RuntimeError(f'{cid}: part coverage {coverage}')
  dump(OUT/'cases'/cid/'input_manifest.json',entry);inventory['cases'][cid]=entry;print(cid,'PARTS',len(parts),'COVERAGE',coverage,flush=True)
 dump(OUT/'manifest/input_inventory.json',inventory);dump(OUT/'artifacts/old_outputs_frozen_hashes.json',{cid:{'path':str(p),'sha256':sha(p)} for cid,p in historical.items()})

if __name__=='__main__':main()
