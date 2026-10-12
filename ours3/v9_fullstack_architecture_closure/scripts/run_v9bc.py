#!/usr/bin/env python3
import json,sys
from pathlib import Path
import numpy as np
from OCP.TopAbs import TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'v9_fullstack_architecture_closure';sys.path.insert(0,str(OUT))
from surface_primitives.fitters import fit_general_bspline
from wireframe.surface_wireframe import build_surface_wireframe
from topology.qa import topology_qa
from surface_primitives.primitive_selector import fit_primitive_bank
from wireframe.wireframe_graph import build_wireframe as build_v8_wireframe
from topology.global_topology_builder import build_topology
import trimesh
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def faces(shape):
 out=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():out.append(TopoDS.Face_s(ex.Current()));ex.Next()
 return out
parts={}
# MAIN_WING: V8 shared-edge builder is freshly re-executed from the source mesh and fitted planes.
source=ROOT/'case09_aircraft_end2end_cad_v1/02_cad_part_graph/CADPART_001/source_part.obj';mesh=trimesh.load(source,force='mesh',process=False);bank=fit_primitive_bank(mesh,'CADPART_001',source);v8wf=build_v8_wireframe(bank);shape,qa,_=build_topology(bank,v8wf);mf=faces(shape);ms=[(f'MW_SURF_{i:02d}',bank['selected_primitives'][i]['surface_id'],face) for i,face in enumerate(mf)];mwire=build_surface_wireframe('CADPART_001','MAIN_WING',ms,[1,0,0]);mqa=topology_qa('CADPART_001',mf,expected_shared=12,result_type='SOLID');mqa.update({k:qa[k] for k in ('surface_intersection_used','shared_occ_edge_count','duplicate_coincident_edge_count','brep_valid')});mqa['actual_shared_occ_edge_count']=qa['shared_occ_edge_count'];parts['CADPART_001']={'role':'MAIN_WING','wireframe':mwire,'topology':mqa,'wireframe_consumed_by_topology':True}
# FUSELAGE and VERTICAL_TAIL: execute every measured open-chain track into a real BSpline face.
for pid,role,axis in [('CADPART_000','FUSELAGE',[0,1,0]),('CADPART_005','VERTICAL_TAIL',[1,0,0])]:
 spec=json.loads((ROOT/'v7b_profile_type_aware_open_shell_reconstruction/04_measured_spec'/pid/'measured_cad_spec.json').read_text());surfaces=[]
 for i,(track_id,track) in enumerate(sorted(spec['open_chain_tracks'].items())):
  result=fit_general_bspline([x['resampled_points_3d'] for x in track]);surfaces.append((f'{pid}_SURF_{i:02d}',f'{pid}_GENERAL_BSPLINE_{track_id}',result['occ_shape']))
 wf=build_surface_wireframe(pid,role,surfaces,axis);fs=[x[2] for x in surfaces];tqa=topology_qa(pid,fs,expected_shared=1,result_type='FACE_SET');parts[pid]={'role':role,'wireframe':wf,'topology':tqa,'wireframe_consumed_by_topology':False,'shared_topology_blocker':'INDEPENDENT_MEASURED_TRACKS_HAVE_NONCOINCIDENT_BOUNDARIES'}
for pid,row in parts.items():dump(OUT/'V9B_SURFACE_AWARE_SEMANTIC_WIREFRAME'/pid/'wireframe.json',row['wireframe']);dump(OUT/'V9C_GLOBAL_TRIMMED_BREP_TOPOLOGY'/pid/'topology_qa.json',row['topology'])
summary={'CURRENT_GATE_V9B':'V9B_SURFACE_AWARE_SEMANTIC_WIREFRAME_PARTIAL','CURRENT_GATE_V9C':'V9C_GLOBAL_TRIMMED_BREP_TOPOLOGY_PARTIAL','MAIN_WING_WIREFRAME_EXECUTED':True,'FUSELAGE_WIREFRAME_EXECUTED':True,'VERTICAL_TAIL_WIREFRAME_EXECUTED':True,'MESH_TRIANGLE_EDGE_IMPORT_COUNT':0,'PROFILE_SAMPLE_DESIGN_EDGE_COUNT':0,'REAL_DESIGN_EDGE_COUNT':sum(x['wireframe']['real_design_edge_count'] for x in parts.values()),'SEMANTIC_SURFACE_COUNT':sum(x['wireframe']['semantic_surface_count'] for x in parts.values()),'WIRE_FRAME_DEPENDENCY_PASS':False,'MAIN_WING_GLOBAL_TOPOLOGY_PASS':parts['CADPART_001']['topology']['actual_shared_occ_edge_count']>0,'FUSELAGE_GLOBAL_TOPOLOGY_PASS':False,'VERTICAL_TAIL_GLOBAL_TOPOLOGY_PASS':False,'SHARED_OCC_EDGE_COUNT':sum(x['topology']['actual_shared_occ_edge_count'] for x in parts.values()),'PCURVE_EDGE_COUNT':sum(x['topology']['pcurve_count'] for x in parts.values()),'TRIMMED_FACE_COUNT':sum(x['topology']['trimmed_face_count'] for x in parts.values()),'FUSELAGE_RESULT_TYPE':'FACE_SET','VERTICAL_TAIL_RESULT_TYPE':'FACE_SET','parts':parts,'BLOCKERS':['FUSELAGE_COMMON_BOUNDARY_CONTROL_NET_NOT_CONSTRUCTED','VERTICAL_TAIL_COMMON_BOUNDARY_CONTROL_NET_NOT_CONSTRUCTED','V9B_FUSELAGE_TAIL_WIREFRAME_NOT_CONSUMED_BY_SHARED_TOPOLOGY']};dump(OUT/'artifacts/v9bc_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='parts'},indent=2))

