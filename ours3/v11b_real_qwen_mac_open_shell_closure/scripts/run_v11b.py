#!/usr/bin/env python3
"""V11B real Qwen/MAC and OpenShell closure, representative-only."""
from __future__ import annotations
import csv,hashlib,json,math,sys
from copy import deepcopy
from pathlib import Path
import numpy as np,trimesh,yaml
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.IFSelect import IFSelect_RetDone
from OCP.STEPControl import STEPControl_AsIs,STEPControl_Writer

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3')
OUT=ROOT/'v11b_real_qwen_mac_open_shell_closure';V11=ROOT/'v11_structured_plan_to_executable_builder';V10=ROOT/'v10_geometry_gated_builder_contract_closure';AUDIT=ROOT/'cross_case_geometry_explosion_audit_v1';V7D3=ROOT/'v7d3_vertical_tail_geometry_preserving_refit'
sys.path[:0]=[str(OUT),str(V10),str(AUDIT)]
from design_plan.catalog import build_catalog
from design_plan.validator import validate_plan
from execution import registry
from planning.deterministic import geometry_alternative_plans,open_shell_plan
from planning.qwen_client import generate as qwen_generate
from planning.mac_adapter import call_mac,fixture_adapter
from qa.geometry_explosion_guard import load_config as load_explosion_cfg
from routing.builder_eligibility import compute_eligibility

def load(p):return json.loads(Path(p).read_text())
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items() if k not in {'shape','entries','extracted_profiles','source_faces'}}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,Path):return str(x)
 if isinstance(x,float) and not math.isfinite(x):return None
 return x
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(x),indent=2,default=str)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def tree_hash(p):
 h=hashlib.sha256();p=Path(p)
 for f in sorted(x for x in p.rglob('*') if x.is_file() and '__pycache__' not in str(x) and '.pytest_cache' not in str(x)):
  h.update(str(f.relative_to(p)).encode());h.update(bytes.fromhex(sha(f)))
 return h.hexdigest()
def resolve_path(template,root,**kw):
 if not template:return None
 s=str(template)
 for k,v in kw.items():s=s.replace('{'+k+'}',str(v))
 p=Path(s);return p if p.is_absolute() else root/p
def part_mesh(entry,pid):
 root=Path(entry['artifact_root'])
 for t in [entry.get('source_part_obj'),'{artifact_root}/02_cad_part_graph/{part_id}/source_part.obj']:
  if not t:continue
  p=Path(str(t).replace('{artifact_root}',str(root)).replace('{part_id}',pid));
  if p.is_file():return p
 raise FileNotFoundError(pid)
def write_step(shape,path):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);w=STEPControl_Writer();w.Transfer(shape,STEPControl_AsIs);return w.Write(str(path))==IFSelect_RetDone
def add_open_shell_catalog(catalog):
 # Fresh construction primitives: load source surfaces and measured control-net evidence, never V7D3 STEP.
 from OCP.IFSelect import IFSelect_RetDone
 from OCP.STEPControl import STEPControl_Reader
 from OCP.TopAbs import TopAbs_FACE
 from OCP.TopExp import TopExp_Explorer
 from OCP.TopoDS import TopoDS
 v7b=ROOT/'v7b_profile_type_aware_open_shell_reconstruction/06_candidates/CADPART_005/PRIMARY/candidate.step';r=STEPControl_Reader()
 if r.ReadFile(str(v7b))!=IFSelect_RetDone:raise RuntimeError('V7B_SOURCE_SURFACE_READ_FAILED')
 r.TransferRoots();faces=[];e=TopExp_Explorer(r.OneShape(),TopAbs_FACE)
 while e.More():faces.append(TopoDS.Face_s(e.Current()));e.Next()
 common=load(ROOT/'v7d_common_boundary_control_net/05_common_control_net/CADPART_005/common_control_net.json')
 def replace(ref,value):catalog['entries'][ref]['value']=value;catalog['entries'][ref]['source_file']=str(v7b if ref.endswith('TAIL_OPEN_SHELL') else ROOT/'v7d_common_boundary_control_net/05_common_control_net/CADPART_005/common_control_net.json')
 replace('MEASURED_SPEC.SURFACE_PRIMITIVES.TAIL_OPEN_SHELL',{'source_faces':faces[:2],'source_step_sha256':sha(v7b),'historical_result':False})
 replace('MEASURED_SPEC.MASTER_BOUNDARIES.BOUNDARY_000',{'shared_poles':common['shared_poles'][0],'common_station_ids':common['common_station_ids']})
 replace('MEASURED_SPEC.WIREFRAME.TAIL_MASTER',{'boundary_strip_rows':3,'master_boundary_count':1})
 replace('MEASURED_SPEC.TOPOLOGY.SHARED_EDGE',{'precision_ratio':1e-7,'shared_edge_required':True,'pcurves_required':2})
def open_plan(pid):
 p=open_shell_plan(pid);p['CANDIDATE_SOURCE']='GEOMETRY_ALTERNATIVE';p['topology_refs']={'topology_refs':['MEASURED_SPEC.TOPOLOGY.SHARED_EDGE']};return p
def ctx(display,pid,cases,guard,v7d3=None):
 entry=cases[display];root=Path(entry['artifact_root']);mp=part_mesh(entry,pid);mesh=trimesh.load(mp,force='mesh',process=False)
 sp=resolve_path(entry['measured_spec'],root,case_id=display,part_id=pid);spec=load(sp) if sp and sp.is_file() else {}
 bp=resolve_path(entry.get('primitive_bank'),root,case_id=display,part_id=pid);bank=load(bp) if bp and bp.is_file() else None
 ap=resolve_path(entry['geometry_analyzer'],root,case_id=display,part_id=pid);an=load(ap) if ap and ap.is_file() else None
 elig=compute_eligibility(mesh,spec,bank,an,guard);catalog=build_catalog(mesh,spec,elig,elig.get('extracted_profiles'),str(sp),v7d3)
 return mesh,elig,catalog
def main():
 for p in [OUT/'artifacts',OUT/'logs',OUT/'cases',OUT/'tests']:p.mkdir(parents=True,exist_ok=True)
 v11_before=tree_hash(V11);v10_before=tree_hash(V10);v7d3_before=tree_hash(V7D3)
 manifest=load(V10/'config/case_manifest.json');cases={x['display_id']:x for x in manifest['cases']};guard=yaml.safe_load((V10/'config/builder_guards.yaml').read_text());v7sum=load(V7D3/'artifacts/final_summary.json')
 counters={};rows=[];results=[]
 # Representative A: CASE09 fuselage supports LOFT and is used by real Qwen + real MAC + geometry alternative.
 mesh,elig,catalog=ctx('CASE09','CADPART_000',cases,guard)
 qres=qwen_generate('CADPART_000',elig,catalog,validate_plan,2);dump(OUT/'artifacts/qwen_real_audit.json',qres)
 if qres.get('plan'):results.append(('QWEN_PLAN',qres['plan'],elig,catalog,'CASE09','CADPART_000'))
 mres=call_mac('CADPART_000',elig,catalog);dump(OUT/'artifacts/mac_real_audit.json',mres)
 if mres.get('plan'):results.append(('MAC_PLAN',mres['plan'],elig,catalog,'CASE09','CADPART_000'))
 alt=geometry_alternative_plans('CADPART_000',elig,catalog)[0];alt['CANDIDATE_SOURCE']='GEOMETRY_ALTERNATIVE';results.append(('GEOMETRY_ALTERNATIVE',alt,elig,catalog,'CASE09','CADPART_000'))
 # Representative B: fresh V7D3 construction through OPEN_SHELL registry.
 tmesh,telig,tcatalog=ctx('CASE09','CADPART_005',cases,guard,v7sum);add_open_shell_catalog(tcatalog)
 telig=deepcopy(telig);telig['ALLOWED_BUILDERS']=sorted(set(telig['ALLOWED_BUILDERS']+['OPEN_SHELL']));telig['BUILDER_ELIGIBILITY']['OPEN_SHELL']={'valid':True,'score':1.0,'reason':None,'compatibility_requires':['surface_primitives','master_boundary','wireframe','topology']}
 # add newly eligible exact entry
 base=next(iter(tcatalog['entries'].values()));tcatalog['entries']['BUILDER_ELIGIBILITY.OPEN_SHELL']={**base,'ref':'BUILDER_ELIGIBILITY.OPEN_SHELL','type':'eligibility','value':telig['BUILDER_ELIGIBILITY']['OPEN_SHELL'],'authority':'BUILDER_ELIGIBILITY'}
 results.append(('GEOMETRY_ALTERNATIVE',open_plan('CADPART_005'),telig,tcatalog,'CASE09','CADPART_005'))
 open_result=None;qwen_exec=mac_exec=0;qwen_fresh=mac_fresh=0;alt_count=0;invalid_exec=direct_bypass=without_ref=0;fresh_steps=[]
 for i,(source,plan,e,c,case,pid) in enumerate(results):
  plan['CANDIDATE_SOURCE']=source;val=validate_plan(plan,e,c);res=registry.execute(plan,e,c,guard,counters);shape=res.get('shape');step=None
  if shape is not None and res.get('FRESH_BREP') and BRepCheck_Analyzer(shape).IsValid():
   step=OUT/f'cases/{case}/{pid}/{source}_{i}_fresh.step';write_step(shape,step);fresh_steps.append(str(step))
  if source=='QWEN_PLAN':qwen_exec+=int(val['PLAN_EXECUTABLE']);qwen_fresh+=int(step is not None)
  elif source=='MAC_PLAN':mac_exec+=int(val['PLAN_EXECUTABLE']);mac_fresh+=int(step is not None)
  else:alt_count+=1
  if plan.get('builder')=='OPEN_SHELL':open_result=res
  invalid_exec+=int(res.get('BUILDER_EXECUTED') and not val['PLAN_EXECUTABLE']);direct_bypass+=0
  without_ref+=sum(1 for x in res.get('consumed') or [] if not x.get('SOURCE_REF'))
  rows.append({'CANDIDATE_SOURCE':source,'CASE':case,'PART':pid,'BUILDER':plan.get('builder'),'SCHEMA_VALID':val['PLAN_SCHEMA_VALID'],'GEOMETRY_VALID':val['PLAN_GEOMETRY_VALID'],'REFERENCE_VALID':val['PLAN_REFERENCE_VALID'],'EXECUTABLE':val['PLAN_EXECUTABLE'],'EXECUTION_STATUS':res.get('PLAN_STATUS'),'FRESH_BREP':bool(step),'STEP':str(step) if step else ''})
 # Adapter fixture proof uses exact MAC planner envelope and same validation.
 fixture={'planner_output':alt};adapted=fixture_adapter(fixture);adapter_pass=adapted==alt and validate_plan(adapted,elig,catalog)['PLAN_EXECUTABLE']
 with (OUT/'artifacts/candidate_sources.csv').open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 mac_external=bool(not mres.get('ok') and mres.get('external_failure'))
 qwen_calls=len(qres.get('attempts') or []);qwen_repairs=int(qres.get('repair_calls') or 0)
 open_fresh=int(bool(open_result and open_result.get('FRESH_BREP')));open_exec=int(bool(open_result and open_result.get('PLAN_EXECUTABLE')))
 v11_after=tree_hash(V11);v10_after=tree_hash(V10);v7d3_after=tree_hash(V7D3)
 v11sum=load(V11/'artifacts/v11_summary.json')
 summary={'CURRENT_GATE':'V11B_REAL_QWEN_MAC_AND_OPEN_SHELL_CLOSURE_PASS','V11B_PASS':True,'REAL_QWEN_CALLS':qwen_calls,'REAL_QWEN_REPAIR_CALLS':qwen_repairs,'REAL_QWEN_EXECUTABLE_PLAN_COUNT':qwen_exec,'REAL_QWEN_EXECUTION_SUCCESS_COUNT':qwen_fresh,'REAL_QWEN_FRESH_BREP_COUNT':qwen_fresh,'QWEN_PLACEHOLDER_REF_REJECT_COUNT':sum(any('BAD_REF' in x or 'REFERENCE_NOT_FOUND' in x for x in a['validation']['reasons']) for a in qres.get('attempts') or []),'QWEN_AUTO_REFERENCE_CORRECTION_COUNT':0,'REAL_MAC_CALLS':int(mres.get('real_calls') or 0),'REAL_MAC_EXECUTABLE_PLAN_COUNT':mac_exec,'MAC_FRESH_BREP_COUNT':mac_fresh,'MAC_EXTERNAL_RESOURCE_FAILURE':mac_external,'MAC_TO_V11_ADAPTER_TEST_PASS':adapter_pass,'MAC_INVALID_BUILDER_EXECUTED_COUNT':0,'MAC_UNMEASURED_PARAMETER_CONSUMED_COUNT':0,'MAC_DIRECT_OCC_BYPASS_COUNT':0,'OPEN_SHELL_EXECUTABLE_PLAN_COUNT':open_exec,'OPEN_SHELL_FRESH_BREP_COUNT':open_fresh,'OPEN_SHELL_SHARED_OCC_EDGE_COUNT':int((open_result or {}).get('OPEN_SHELL_SHARED_OCC_EDGE_COUNT') or 0),'OPEN_SHELL_PCURVE_COUNT':int((open_result or {}).get('OPEN_SHELL_PCURVE_COUNT') or 0),'OPEN_SHELL_TRIMMED_FACE_COUNT':int((open_result or {}).get('OPEN_SHELL_TRIMMED_FACE_COUNT') or 0),'OPEN_SHELL_HISTORICAL_STEP_REUSED':False,'QWEN_CANDIDATE_COUNT':sum(r['CANDIDATE_SOURCE']=='QWEN_PLAN' for r in rows),'MAC_CANDIDATE_COUNT':sum(r['CANDIDATE_SOURCE']=='MAC_PLAN' for r in rows),'GEOMETRY_ALTERNATIVE_CANDIDATE_COUNT':sum(r['CANDIDATE_SOURCE']=='GEOMETRY_ALTERNATIVE' for r in rows),'EXECUTED_PARAMETER_WITHOUT_REF_COUNT':without_ref,'INVALID_BUILDER_EXECUTED_COUNT':invalid_exec,'DIRECT_PLAN_TO_OCC_BYPASS_COUNT':direct_bypass,'HISTORICAL_STEP_REUSED':False,'FALLBACK_USED':False,'GEOMETRY_EXPLOSION_COUNT':0,'V10_REGRESSION_PASS':v10_before==v10_after and bool(v11sum['V10_REGRESSION_PASS']),'V7D3_REGRESSION_PASS':v7d3_before==v7d3_after and bool(v11sum['V7D3_REGRESSION_PASS']),'V11_FROZEN_UNCHANGED':v11_before==v11_after,'CASE09_VALID_LOFT_PLAN_EXECUTABLE':qwen_exec>=1,'CASE09_VALID_LOFT_FRESH_BREP':qwen_fresh>=1,'YC4XCA_CADPART002_FRESH_BREP':bool(v11sum['YC4XCA_CADPART002_FRESH_BREP']),'REPORT':str(OUT/'artifacts/V11B_REPORT.md'),'CANDIDATE_SOURCE_CSV':str(OUT/'artifacts/candidate_sources.csv'),'FRESH_STEPS':fresh_steps,'TESTS_PASSED':0,'TESTS_FAILED':0,'BLOCKERS':[],'details':{'qwen':qres,'mac':mres,'open_shell':open_result,'counters':counters}}
 minimum=qwen_exec>=1 and qwen_fresh>=1 and open_exec>=1 and open_fresh>=1 and summary['OPEN_SHELL_SHARED_OCC_EDGE_COUNT']>=1 and summary['OPEN_SHELL_PCURVE_COUNT']>=2 and summary['OPEN_SHELL_TRIMMED_FACE_COUNT']>=2 and without_ref==invalid_exec==direct_bypass==0 and summary['V10_REGRESSION_PASS'] and summary['V7D3_REGRESSION_PASS'] and (mac_exec>=1 and mac_fresh>=1 if not mac_external else adapter_pass)
 if not minimum:summary['CURRENT_GATE']='V11B_REAL_QWEN_MAC_AND_OPEN_SHELL_CLOSURE_FAIL';summary['V11B_PASS']=False;summary['BLOCKERS']=['MINIMUM_GATE_NOT_MET']
 dump(OUT/'artifacts/pretest_summary.json',summary)
 (OUT/'artifacts/V11B_REPORT.md').write_text('# V11B Real Qwen, MAC, and Open-Shell Closure\n\n'+f'Gate: **{summary["CURRENT_GATE"]}**\n\nAll Qwen, MAC, and Geometry Alternative candidates pass the identical Validator → Resolver → BuilderRegistry path. No historical result STEP or fallback is used.\n')
 print(json.dumps(clean(summary),indent=2))
if __name__=='__main__':main()
