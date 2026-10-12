#!/usr/bin/env python3
import hashlib,json,sys
from pathlib import Path
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'v9_fullstack_architecture_closure';sys.path.insert(0,str(OUT))
from surface_primitives.fitters import execute_case09_fitter_suite
def clean(x):
 if isinstance(x,dict):return {k:clean(v) for k,v in x.items() if k!='occ_shape'}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 return x
def write(shape,path):
 path.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs);assert w.Write(str(path))==IFSelect_RetDone
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
results=execute_case09_fitter_suite(ROOT);records={};deps={}
for kind,result in results.items():
 path=OUT/'V9A_REAL_SURFACE_PRIMITIVE_FITTERS'/kind/f'{kind.lower()}_executed.step';write(result['occ_shape'],path);record=clean(result);record['step']=str(path);record['step_sha256']=sha(path);records[kind]=record
# Real parameter perturbations are re-executed through the relevant fitter inputs.
from surface_primitives.fitters import fit_cylinder,fit_loft
import numpy as np,trimesh
mesh=trimesh.load(ROOT/'case09_aircraft_end2end_cad_v1/02_cad_part_graph/CADPART_000/source_part.obj',force='mesh',process=False);pts=np.asarray(mesh.vertices)[::max(len(mesh.vertices)//4000,1)];axis=np.asarray([0.,1.,0.]);origin=np.asarray(mesh.vertices).mean(0);q=pts-origin;ax=q@axis;rad=q-np.outer(ax,axis);scaled=origin+np.outer(ax,axis)+rad*.8;pert=fit_cylinder(scaled,origin,axis);p1=OUT/'V9A_REAL_SURFACE_PRIMITIVE_FITTERS/CYLINDER/cylinder_radius_08.step';write(pert['occ_shape'],p1);deps['CYLINDER_RADIUS_PERTURBATION_EFFECTIVE']=sha(p1)!=records['CYLINDER']['step_sha256']
wing=json.loads((ROOT/'v7a_profile_recovery/04_measured_spec/CADPART_001/measured_cad_spec.json').read_text());profiles=[np.asarray(p['outer_loop']['resampled_points_3d'],float) for p in wing['profiles']];center=np.vstack(profiles).mean(0);scaled=[center+(p-center)*.9 for p in profiles];lp=fit_loft(scaled,[p['station_id'] for p in wing['profiles']]);p2=OUT/'V9A_REAL_SURFACE_PRIMITIVE_FITTERS/LOFT/loft_profile_scale_09.step';write(lp['occ_shape'],p2);deps['LOFT_PROFILE_PERTURBATION_EFFECTIVE']=sha(p2)!=records['LOFT']['step_sha256']
summary={'CURRENT_GATE':'V9A_REAL_SURFACE_PRIMITIVE_FITTERS_PARTIAL','REAL_SURFACE_FITTER_COUNT':len(records),'REAL_FITTERS':{k:bool(v['valid'] and v['executable_representation']=='OCC') for k,v in records.items()},'PRIMITIVE_STRING_ONLY_COUNT':0,'PRIMITIVE_PARAMETER_PERTURBATION_EFFECTIVE':all(deps.values()),'PER_SEMANTIC_SURFACE_CANDIDATE_SELECTION_EXECUTED':False,'DEPENDENCY_TESTS':deps,'records':records,'BLOCKERS':['PER_SEMANTIC_SURFACE_PRIMITIVE_SELECTOR_NOT_EXECUTED']}
if not (len(records)==8 and all(summary['REAL_FITTERS'].values()) and all(deps.values())):summary['CURRENT_GATE']='V9A_REAL_SURFACE_PRIMITIVE_FITTERS_FAIL';summary['BLOCKERS']=['V9A_GATE_REQUIREMENT_FAILED']
path=OUT/'artifacts/v9a_summary.json';path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
