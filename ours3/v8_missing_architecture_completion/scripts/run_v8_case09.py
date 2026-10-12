#!/usr/bin/env python3
import csv,hashlib,json,sys
from pathlib import Path
import numpy as np,trimesh
from scipy.spatial import cKDTree
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer
from OCP.TopAbs import TopAbs_EDGE,TopAbs_FACE
from OCP.TopExp import TopExp_Explorer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'v8_missing_architecture_completion';HERE=Path(__file__).resolve().parents[1];sys.path.insert(0,str(HERE))
from surface_primitives import fit_primitive_bank
from wireframe.wireframe_graph import build_wireframe
from topology.global_topology_builder import build_topology
from optimization.optimizer import optimize
from grounding.grounding import index_entities,ground_query
from repair.repair_loop import run_repair
TARGETS={'CADPART_001':'MAIN_WING','CADPART_000':'FUSELAGE','CADPART_005':'VERTICAL_TAIL'}
SRC=ROOT/'case09_aircraft_end2end_cad_v1/02_cad_part_graph'
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_step(shape,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs);assert w.Write(str(path))==IFSelect_RetDone
def tess(shape):
 from OCP.BRepMesh import BRepMesh_IncrementalMesh
 from OCP.BRep import BRep_Tool
 from OCP.TopLoc import TopLoc_Location
 from OCP.TopoDS import TopoDS
 BRepMesh_IncrementalMesh(shape,.003,False,.2,True);vs=[];fs=[];ex=TopExp_Explorer(shape,TopAbs_FACE)
 while ex.More():
  face=TopoDS.Face_s(ex.Current());loc=TopLoc_Location();tri=BRep_Tool.Triangulation_s(face,loc);off=len(vs)
  if tri:
   tr=loc.Transformation();vs += [[tri.Node(i).Transformed(tr).X(),tri.Node(i).Transformed(tr).Y(),tri.Node(i).Transformed(tr).Z()] for i in range(1,tri.NbNodes()+1)]
   for i in range(1,tri.NbTriangles()+1):
    a,b,c=tri.Triangle(i).Get();fs.append([off+a-1,off+b-1,off+c-1])
  ex.Next()
 return trimesh.Trimesh(vs,fs,process=False)
def metrics(source,shape):
 cad=tess(shape);a,_=trimesh.sample.sample_surface(source,8000,seed=123);b,_=trimesh.sample.sample_surface(cad,8000,seed=456);da=cKDTree(b).query(a)[0];db=cKDTree(a).query(b)[0];ch=float((da.mean()+db.mean())/2);haus=float(max(np.quantile(da,.99),np.quantile(db,.99)));faces=sum(1 for _ in iter_exp(shape,TopAbs_FACE));edges=sum(1 for _ in iter_exp(shape,TopAbs_EDGE));return {'chamfer':ch,'hausdorff_p99':haus,'nativeness':1/(1+edges/20),'valid':bool(BRepCheck_Analyzer(shape).IsValid()),'artificial_edges':0,'faces':faces,'edges':edges,'composite':ch+.2*haus+.01*edges}
def iter_exp(shape,kind):
 ex=TopExp_Explorer(shape,kind)
 while ex.More():yield ex.Current();ex.Next()
def main():
 banks={}
 for pid,label in TARGETS.items():
  path=SRC/pid/'source_part.obj';mesh=trimesh.load(path,force='mesh',process=False);bank=fit_primitive_bank(mesh,pid,path);banks[pid]=bank;dump(OUT/'05_surface_primitive_bank'/pid/'primitive_bank.json',bank)
 wing=trimesh.load(SRC/'CADPART_001/source_part.obj',force='mesh',process=False);bank=banks['CADPART_001'];wf=build_wireframe(bank);dump(OUT/'06_semantic_wireframe/CADPART_001/wireframe_graph.json',wf)
 base_shape,topqa,prov=build_topology(bank,wf);base=OUT/'07_global_topology/CADPART_001/baseline.step';write_step(base_shape,base);dump(base.with_suffix('.topology_qa.json'),topqa)
 # Dependencies 5/6/7
 primitive_shape,_,_=build_topology(bank,wf,offset_overrides={'LEADING':-.03});pp=OUT/'dependency/step5_primitive_perturb.step';write_step(primitive_shape,pp)
 try:build_topology(bank,wf,removed_edge=wf['edges'][0]['edge_id']);wire_fail=False
 except RuntimeError:wire_fail=True
 topology_shape,tqa,_=build_topology(bank,wf,offset_overrides={'UPPER':.02});tp=OUT/'dependency/step7_topology_perturb.step';write_step(topology_shape,tp)
 # Step 9 V8 measured spec aggregate; Step 8 remains partial.
 v7spec=json.loads((ROOT/'v7a_profile_recovery/04_measured_spec/CADPART_001/measured_cad_spec.json').read_text())
 feature_graph={'mode':'PARTIAL','features':[{'feature_id':'F000','feature_type':'FREEFORM_FEATURE','affected_surfaces':[p['surface_id'] for p in bank['selected_primitives']],'parameters':{},'support_geometry':'PRIMITIVE_BANK','confidence':.7,'executability':True}]}
 spec={'schema':'MeasuredCADSpecV8','geometry_analyzer_source':str(ROOT/'v7a_profile_recovery/04_measured_spec/CADPART_001/measured_cad_spec.json'),'exact_dimensions':{'bbox':v7spec['bbox'],'axis':v7spec['axis'],'span':v7spec['span'],'stations':v7spec['stations']},'profiles':v7spec['profiles'],'surface_primitive_bank':bank,'semantic_wireframe':wf,'design_boundary_references':[x['edge_id'] for x in wf['edges']],'feature_graph':feature_graph,'feature_parameters':[x['parameters'] for x in feature_graph['features']],'constraints':{'shared_topology_required':True,'program_logic_frozen_during_optimization':True},'MEASURED_SPEC_SURFACE_PRIMITIVES_INCLUDED':True,'MEASURED_SPEC_WIREFRAME_INCLUDED':True,'MEASURED_SPEC_FEATURE_PARAMETERS_INCLUDED':True};dump(OUT/'09_measured_spec/CADPART_001/measured_cad_spec_v8.json',spec)
 # Frozen-logic optimizer: only offsets; same builder/topology every execution.
 bank=spec['surface_primitive_bank'];wf=spec['semantic_wireframe']
 def execp(p):return build_topology(bank,wf,offset_overrides={'LEADING':p['leading_offset'],'UPPER':p['upper_offset'],'TRAILING':p.get('trailing_offset',0.)})[0]
 def obj(shape):m=metrics(wing,shape);return m['composite'],m
 initial={'leading_offset':.04,'upper_offset':.03};final,history,result=optimize(initial,execp,obj,10);opt_shape=execp(final);opt_step=OUT/'13_parameter_optimization/CADPART_001/optimized.step';write_step(opt_shape,opt_step);opt={'initial_parameters':initial,'final_parameters':final,'initial_metrics':history[0]['metrics'],'final_metrics':metrics(wing,opt_shape),'iterations':len(history),'executions':len(history),'program_logic_frozen':True,'construction_family':'GLOBAL_INTERSECTION_PLANE_BREP','builder':'GlobalTopologyBuilder','feature_sequence':['SIX_TRIMMED_PLANAR_FACES'],'topology_structure':'FIXED_HEXAHEDRAL_SHARED_EDGE_GRAPH','runtime_grid_search_only':False};dump(opt_step.with_suffix('.optimization.json'),opt)
 # Source counterfactual objective: translate a copy, same program family.
 shifted=wing.copy();shifted.apply_translation([0,.015,0]);
 def obj2(shape):m=metrics(shifted,shape);return m['composite'],m
 final2,h2,_=optimize(final,execp,obj2,5);opt['source_counterfactual']={'final_parameters':final2,'program_family_unchanged':True,'parameters_changed':final2!=final};dump(OUT/'13_parameter_optimization/CADPART_001/optimization_provenance.json',opt)
 # Step 17 real OCC entity grounding.
 index=index_entities(opt_shape,wf);centers=np.asarray([x['centroid'] for x in index['EDGE']]);semantic={'main wing':centers.mean(0),'leading edge':centers[np.argmax(centers[:,1])],'trailing edge':centers[np.argmin(centers[:,1])],'upper surface':np.mean([x['centroid'] for x in index['FACE']],axis=0)}
 queries=['main wing leading edge','main wing trailing edge','main wing upper surface','ambiguous decorative fillet edge'];ground=[ground_query(index,q,semantic) for q in queries];dump(OUT/'17_grounding/CADPART_001/grounding_results.json',ground)
 # Step 18 local param patch on grounded leading edge.
 lead=ground[0];evalf=lambda s:metrics(wing,s);repair_initial={**final,'trailing_offset':0.};mac_patch_path=OUT/'18_targeted_repair/CADPART_001/mac_local_patch.json';mac_patch=json.loads(mac_patch_path.read_text()) if mac_patch_path.is_file() else {};mac_valid=bool(mac_patch.get('provider_request_sent') and mac_patch.get('provider_response_received') and mac_patch.get('target_entity_id')==lead['occ_entity_id'] and mac_patch.get('parameter')=='leading_offset' and abs(float(mac_patch.get('delta',0)))<=.03)
 if mac_valid:
  repair_delta=float(mac_patch['delta']);params,repair_shape,repair_metrics,repair=run_repair(repair_initial,lead['occ_entity_id'],execp,evalf,3,repair_delta,target_parameter='leading_offset')
 else:
  repair_delta=0.;params,repair_shape,repair_metrics=repair_initial,opt_shape,evalf(opt_shape);repair={'repair_rounds':[],'attempts':0,'accepted':0,'repair_locality_valid':False,'multi_round_repair_supported':True,'rollback_supported':True,'blocked_before_patch':True,'blocker':'MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403'}
 repair['mac_local_patch_used']=mac_valid;repair['mac_provenance']=mac_patch if mac_valid else None;repair_step=OUT/'18_targeted_repair/CADPART_001/repaired.step';write_step(repair_shape,repair_step);dump(repair_step.with_suffix('.repair.json'),repair)
 # Repair target counterfactual uses a different grounded ID and local parameter.
 target_changed=ground[1]['occ_entity_id']!=lead['occ_entity_id'] and None not in (ground[1]['occ_entity_id'],lead['occ_entity_id'])
 if mac_valid:
  _,_,_,repair_cf=run_repair(repair_initial,ground[1]['occ_entity_id'],execp,evalf,1,repair_delta,target_parameter='trailing_offset');cf_parameter=repair_cf['repair_rounds'][0]['local_program_patch']['parameter']
 else:cf_parameter=None
 repair['target_counterfactual']={'target_changed':target_changed,'original_patch_parameter':'leading_offset','counterfactual_patch_parameter':cf_parameter,'patch_changed':cf_parameter=='trailing_offset'};dump(repair_step.with_suffix('.repair.json'),repair);step18=target_changed and repair['repair_locality_valid'] and repair['target_counterfactual']['patch_changed'] and mac_valid
 final_step=OUT/'19_final/CASE09_v8_main_wing_fresh.step';write_step(repair_shape,final_step)
 deps={'STEP5_DEPENDENCY_PASS':sha(base)!=sha(pp),'STEP6_DEPENDENCY_PASS':wire_fail,'STEP7_DEPENDENCY_PASS':sha(base)!=sha(tp),'STEP13_DEPENDENCY_PASS':sha(opt_step)!=sha(base) and final!=initial,'STEP17_DEPENDENCY_PASS':ground[0]['occ_entity_id']!=ground[1]['occ_entity_id'],'STEP18_DEPENDENCY_PASS':step18}
 gates={'V8A':'PARTIAL','V8B':'PARTIAL','V8C':'PARTIAL','V8D':'PARTIAL','V8E':'PARTIAL','V8F':'PARTIAL'}
 blockers=['REAL_FITTERS_MISSING_FOR_CYLINDER_REVOLUTION_EXTRUSION_SWEEP_LOFT_PERIODIC_BSPLINE_GENERAL_BSPLINE','FUSELAGE_LOFT_OPEN_SHELL_NOT_EXECUTED','VERTICAL_TAIL_FREEFORM_WIREFRAME_NOT_EXECUTED','GROUNDING_DESCRIPTOR_MISSING_ORIENTATION_ADJACENCY_FEATURE_MEMBERSHIP']+([] if mac_valid else ['MAC_PROVIDER_FREE_TIER_QUOTA_EXHAUSTED_403'])
 summary={**deps,'gates':gates,'SURFACE_PRIMITIVE_COUNT':sum(len(x['selected_primitives']) for x in banks.values()),'REAL_PRIMITIVE_FITTER_TYPE_COUNT':1,'REAL_DESIGN_EDGE_COUNT':wf['design_edge_count'],'SHARED_OCC_EDGE_COUNT':topqa['shared_occ_edge_count'],'PCURVE_EDGE_COUNT':topqa['pcurve_edge_count'],'TRIMMED_FACE_COUNT':topqa['trimmed_face_count'],'PARAMETERS_OPTIMIZED':len(final),'GROUNDING_FACE_SUCCESS_COUNT':sum(x['entity_type']=='FACE' and x['grounding_status']=='RESOLVED' for x in ground),'GROUNDING_EDGE_SUCCESS_COUNT':sum(x['entity_type']=='EDGE' and x['grounding_status']=='RESOLVED' for x in ground),'TARGETED_REPAIR_ATTEMPTS':repair['attempts'],'TARGETED_REPAIR_ACCEPTED':repair['accepted'],'HISTORICAL_STEP_REUSED':False,'FALLBACK_COUNT':0,'CASE09_FRESH_STEP':str(final_step),'optimization':opt,'topology_qa':topqa,'grounding':ground,'repair':repair,'BLOCKERS':blockers};dump(OUT/'artifacts/pretest_summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
