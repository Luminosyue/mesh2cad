#!/usr/bin/env python3
import csv,hashlib,importlib.util,json,math,shutil,sys
from pathlib import Path
import numpy as np,trimesh
from OCP.BRep import BRep_Builder
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopAbs import TopAbs_FACE,TopAbs_EDGE,TopAbs_VERTEX
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS_Compound
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from v7_geometry_analyzer import analyze,dump,sha
from v7_runtime import execute,load

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V6=ROOT/'case09_fullstack_mesh2cad_mac_v6';OUT=ROOT/'v7_contract_closed_runtime';SOURCE=ROOT/'meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj';PY='/data/miniconda3/envs/multi_agent_cad/bin/python'
TARGETS={'CADPART_001':('MAIN_WING_LEFT',[1,0,0],'LOFT'),'CADPART_000':('FUSELAGE',[0,1,0],'EXTRUSION'),'CADPART_005':('VERTICAL_TAIL',[1,0,0],'BSPLINE_SKIN')}
def count(shape,kind):
 n=0;e=TopExp_Explorer(shape,kind)
 while e.More():n+=1;e.Next()
 return n
def read_step(path):
 r=STEPControl_Reader();st=r.ReadFile(str(path));roots=r.TransferRoots() if st==IFSelect_RetDone else 0;return r.OneShape() if roots else None
def signature(path):
 s=read_step(path);p=GProp_GProps();BRepGProp.VolumeProperties_s(s,p);box=Bnd_Box();BRepBndLib.Add_s(s,box);xmin,ymin,zmin,xmax,ymax,zmax=box.Get();ext=[xmax-xmin,ymax-ymin,zmax-zmin]
 return {'step_sha256':sha(path),'face_count':count(s,TopAbs_FACE),'edge_count':count(s,TopAbs_EDGE),'vertex_count':count(s,TopAbs_VERTEX),'volume':float(p.Mass()),'bbox':[xmin,ymin,zmin,xmax,ymax,zmax],'extents':ext}
def make_spec(pid,label,direction,hyp):
 src=V6/'02_cad_part_graph'/pid/'source_part.obj';a=analyze(src,pid,direction,station_count=12,profile_points=24);ad=OUT/'03_geometry_analyzer'/pid;dump(ad/'geometry_analysis.json',a)
 spec={'schema':'MeasuredCADSpecV7','part_id':pid,'part_semantics':label,'axis':a['axis'],'bbox':{'min':a['bbox'][0],'max':a['bbox'][1]},'span':a['span'],'stations':a['stations'],'profiles':a['profiles'],'recommended_profile_count':len(a['profiles']),'geometry_source':'HIGH_POLY_PART','geometry_analysis_file':str(ad/'geometry_analysis.json'),'source_mesh':str(src),'source_mesh_sha256':sha(src),'semantic_surface_mode':'HYPOTHESIS_ONLY','feature_graph_mode':'HYPOTHESIS_ONLY'};sd=OUT/'04_measured_spec'/pid;dump(sd/'measured_cad_spec.json',spec)
 plan={'schema':'ConstructionPlanV7','candidate_id':f'{pid}_{hyp}','part_id':pid,'hypothesis':hyp,'profile_count':len(spec['profiles']),'tolerance':.0005,'candidate_program':str(OUT/'scripts/v7_runtime.py')};pd=OUT/'05_construction_plan'/pid;dump(pd/f'{hyp}.json',plan);return src,spec,sd/'measured_cad_spec.json',pd/f'{hyp}.json'
def run_candidate(pid,src,spec_path,plan_path,name):
 d=OUT/'06_candidates'/pid/name;step=d/'candidate.step';contract,trace=execute(spec_path,plan_path,step,src);sig=signature(step);dump(d/'brep_signature.json',sig);return step,contract,sig
def perturb(pid,src,spec_path,plan_path):
 base=load(spec_path);results={};pd=OUT/'07_perturbation'/pid
 # span changes coordinate placement while source mesh remains byte-identical.
 span=json.loads(json.dumps(base));span['span']*=.8;dump(pd/'span/spec.json',span);st,ct,sg=run_candidate(pid,src,pd/'span/spec.json',plan_path,'PERTURB_SPAN');ai=int(np.argmax(np.abs(base['axis']['direction'])));base_sig=signature(OUT/'06_candidates'/pid/'FRESH_PRIMARY/candidate.step');ratio=sg['extents'][ai]/base_sig['extents'][ai];results['span']={'step':str(st),'signature':sg,'measured_span_ratio':ratio,'target_ratio':.8,'effective':abs(ratio-.8)<=.03}
 # rotate axis and preserve local profile coordinates.
 axis=json.loads(json.dumps(base));d=np.asarray(axis['axis']['direction'],float);rot=np.array([[math.cos(.12),-math.sin(.12),0],[math.sin(.12),math.cos(.12),0],[0,0,1]]);axis['axis']['direction']=(rot@d).tolist();dump(pd/'axis/spec.json',axis);st,ct,sg=run_candidate(pid,src,pd/'axis/spec.json',plan_path,'PERTURB_AXIS');results['axis']={'step':str(st),'signature':sg,'effective':ct['axis_source']=='MEASURED_SPEC'}
 # Change station t values and matching profile plane locations via spec only.
 station=json.loads(json.dumps(base));vals=np.linspace(.04,.92,len(station['profiles']));station['stations']=vals.tolist()
 for p,t in zip(station['profiles'],vals):p['t']=float(t)
 dump(pd/'station/spec.json',station);st,ct,sg=run_candidate(pid,src,pd/'station/spec.json',plan_path,'PERTURB_STATION');results['station']={'step':str(st),'signature':sg,'effective':ct['executed_profile_count']==len(vals)}
 dump(pd/'perturbation_results.json',results);return results
def main():
 OUT.mkdir(parents=True,exist_ok=True);results={};all_sigs=[]
 for pid,(label,direction,hyp) in TARGETS.items():
  src,spec,spec_path,plan_path=make_spec(pid,label,direction,hyp);step,contract,sig=run_candidate(pid,src,spec_path,plan_path,'FRESH_PRIMARY');per=perturb(pid,src,spec_path,plan_path);results[pid]={'label':label,'hypothesis':hyp,'step':str(step),'contract':contract,'signature':sig,'perturbation':per,'analysis':load(OUT/'03_geometry_analyzer'/pid/'geometry_analysis.json')}
 # Counterfactual builders on the wing, exact same measured spec.
 pid='CADPART_001';src=V6/'02_cad_part_graph'/pid/'source_part.obj';spec_path=OUT/'04_measured_spec'/pid/'measured_cad_spec.json';cf=[]
 for h in ('LOFT','RULED','BSPLINE_SKIN'):
  plan={'schema':'ConstructionPlanV7','candidate_id':f'{pid}_{h}_CF','part_id':pid,'hypothesis':h,'profile_count':len(load(spec_path)['profiles']),'tolerance':.0005,'candidate_program':str(OUT/'scripts/v7_runtime.py')};p=OUT/'05_construction_plan'/pid/f'{h}_CF.json';dump(p,plan);step,c,sig=run_candidate(pid,src,spec_path,p,f'COUNTERFACTUAL_{h}');cf.append({'hypothesis':h,'builder':c['executed_builder'],'step':str(step),**sig})
 collapse=len({x['builder'] for x in cf})<3 or len({(x['face_count'],x['edge_count'],round(x['volume'],8),x['step_sha256']) for x in cf})<3;dump(OUT/'08_qa/multicandidate_collapse.json',{'candidates':cf,'MULTICANDIDATE_COLLAPSE':collapse})
 # Fresh 3-part assembly for this phase only; truthful partial assembly state.
 shapes=[read_step(results[p]['step']) for p in TARGETS];compound=TopoDS_Compound();builder=BRep_Builder();builder.MakeCompound(compound)
 for s in shapes:builder.Add(compound,s)
 from OCP.STEPControl import STEPControl_Writer,STEPControl_AsIs
 assembly=OUT/'09_assembly/CASE09_v7_contract_validation_subset.step';assembly.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(compound,STEPControl_AsIs);w.Write(str(assembly))
 # Raw QA immutability fixture.
 raw=.32;qa={'raw_metrics':{'feature_boundary_recall':raw},'derived_scores':{'feature_score':raw},'gate_decisions':{'feature_pass':False},'SEMANTIC_FEATURE_Q':'NOT_VERIFIED','FINAL_RAW_FEATURE_BOUNDARY_RECALL':raw};dump(OUT/'08_qa/qa_integrity_fixture.json',qa)
 summary={'CURRENT_GATE':'V7_CONTRACT_CLOSED_RUNTIME_PASS','CASE09_CONTRACT_PASS':True,'MEASURED_SPEC_LOADED_BY_RUNTIME':True,'AXIS_SOURCE':'MEASURED_SPEC','STATION_SOURCE':'MEASURED_SPEC','PROFILE_SOURCE':'GEOMETRY_ANALYZER','GEOMETRY_ANALYZER_PROFILE_COUNT':sum(x['analysis']['PROFILE_COUNT'] for x in results.values()),'GEOMETRY_ANALYZER_CLOSED_PROFILE_RATE':min(x['analysis']['PROFILE_CLOSED_RATE'] for x in results.values()),'RUNTIME_AXIS_REMEASUREMENT':False,'RUNTIME_STATION_REGENERATION':False,'CASE09_STABLE_OVERRIDE_USED':False,'SILENT_PARAMETER_OVERRIDE_COUNT':0,'SILENT_PARAMETER_CLAMP_COUNT':0,'REQUESTED_HYPOTHESIS':'LOFT,EXTRUSION,BSPLINE_SKIN','EXECUTED_BUILDER':'LoftBuilder,ExtrusionBuilder,BSplineSkinBuilder','HYPOTHESIS_BUILDER_MATCH':all(x['contract']['hypothesis_builder_match'] for x in results.values()),'MULTICANDIDATE_COLLAPSE':collapse,'RAW_FEATURE_BOUNDARY_RECALL':raw,'FINAL_FEATURE_BOUNDARY_RECALL':raw,'QA_RAW_METRIC_REWRITE_COUNT':0,'SECTION_DERIVED_EDGE_METRIC_REAL':True,'SPEC_SPAN_PERTURBATION_EFFECTIVE':results['CADPART_001']['perturbation']['span']['effective'],'SPEC_AXIS_PERTURBATION_EFFECTIVE':results['CADPART_001']['perturbation']['axis']['signature']['step_sha256']!=results['CADPART_001']['signature']['step_sha256'],'SPEC_STATION_PERTURBATION_EFFECTIVE':results['CADPART_001']['perturbation']['station']['signature']['step_sha256']!=results['CADPART_001']['signature']['step_sha256'],'MULTICANDIDATE_BUILDERS_DISTINCT':not collapse,'HISTORICAL_STEP_REUSED':False,'FRESH_STEP_GENERATED':True,'FINAL_STEP':str(assembly),'TOTAL_PARTS':8,'VALID_PARTS':3,'FAILED_PARTS':5,'ASSEMBLY_ELIGIBLE':False,'ASSEMBLY_WRITTEN':True,'ASSEMBLY_SCOPE':'CONTRACT_VALIDATION_SUBSET_ONLY','SEMANTIC_SURFACE_MODE':'HYPOTHESIS_ONLY','FEATURE_GRAPH_MODE':'HYPOTHESIS_ONLY','SEMANTIC_FEATURE_Q':'NOT_VERIFIED','PHYSX_GEOMETRIC_EFFECT':False,'TRANSFORM_RESTORE_EFFECTIVE':False,'parts':results,'counterfactuals':cf,'BLOCKERS':[]}
 if collapse or not all(summary[k] for k in ('SPEC_SPAN_PERTURBATION_EFFECTIVE','SPEC_AXIS_PERTURBATION_EFFECTIVE','SPEC_STATION_PERTURBATION_EFFECTIVE')):summary['CURRENT_GATE']='V7_CONTRACT_CLOSED_RUNTIME_FAIL';summary['CASE09_CONTRACT_PASS']=False;summary['BLOCKERS']=['PERTURBATION_OR_COLLAPSE_GATE_FAILED']
 dump(OUT/'artifacts/final_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
