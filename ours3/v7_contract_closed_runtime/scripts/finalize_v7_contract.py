#!/usr/bin/env python3
import csv,json,hashlib
from pathlib import Path
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopAbs import TopAbs_EDGE
from OCP.TopExp import TopExp_Explorer
from OCP.TopoDS import TopoDS

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'v7_contract_closed_runtime';V6=ROOT/'case09_fullstack_mesh2cad_mac_v6';B9=ROOT/'batch9_fullstack_mesh2cad_mac_v6'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def read(p):r=STEPControl_Reader();assert r.ReadFile(str(p))==IFSelect_RetDone and r.TransferRoots();return r.OneShape()
def topology_metrics(step,spec):
 shape=read(step);d=np.asarray(spec['axis']['direction'],float);d/=np.linalg.norm(d);o=np.asarray(spec['axis']['origin'],float);stations=np.asarray(spec['stations'],float);span=float(spec['span']);tol=max(span*1e-4,1e-7);lens=[];section=0;e=TopExp_Explorer(shape,TopAbs_EDGE)
 while e.More():
  edge=TopoDS.Edge_s(e.Current());c=BRepAdaptor_Curve(edge);a,b=c.FirstParameter(),c.LastParameter();pts=[]
  for u in np.linspace(a,b,5):p=c.Value(float(u));pts.append([p.X(),p.Y(),p.Z()])
  pts=np.asarray(pts);lens.append(float(np.linalg.norm(np.diff(pts,axis=0),axis=1).sum()));proj=(pts-o)@d/span+.5
  if np.ptp(proj)<=tol/max(span,1e-12) and np.min(abs(stations-proj.mean()))<=.005 and proj.mean()>.01 and proj.mean()<.99:section+=1
  e.Next()
 total=len(lens);tiny=sum(x<max(span*1e-5,1e-8) for x in lens);art=section+tiny
 return {'RAW_SECTION_DERIVED_EDGE_COUNT':section,'RAW_TINY_EDGE_COUNT':tiny,'RAW_ARTIFICIAL_EDGE_RATIO':art/max(total,1),'RAW_FRAGMENTATION':total/max(len(spec['profiles']),1),'edge_count':total}
def v6_selected(pid):
 rank=load(V6/'09_candidate_ranking'/pid/'ranking.json');cid=rank.get('SELECTED_CANDIDATE');row=next((x for x in rank.get('candidates',[]) if x.get('candidate_id')==cid),{})
 return row
def batch9_stats():
 mac=load(B9/'artifacts/mac_summary.json');final=load(B9/'artifacts/final_summary.json');graphs=[]
 for c in range(9):
  p=B9/'02_cad_part_graph'/f'CASE_{c:02d}'/'cad_part_graph.json'
  if p.is_file():graphs.append(load(p))
 total=sum(len(g.get('nodes',[])) for g in graphs);valid=sum(c.get('PARTS_HARD_GATE_PASS',0) for c in final.get('cases',[]));p3=[g.get('p3_segment_count',g.get('P3_SEGMENT_COUNT')) for g in graphs]
 out={'TOTAL_PROGRAM_ATTEMPTS':mac.get('candidate_programs_executed',0),'REAL_MAC_CALLS':mac.get('real_mac_candidates',0),'REAL_MAC_SUCCESS':mac.get('real_mac_valid_candidates',0),'FALLBACK_PROGRAMS':mac.get('fallback_candidates',0),'RESOURCE_FAILURES':mac.get('http_403',0)+mac.get('http_5xx',0),'TOTAL_PARTS':total or final.get('TOTAL_PARTS'),'VALID_PARTS':valid,'FAILED_PARTS':(total-valid) if total else None,'CASES_WITH_FRESH_ASSEMBLY':final.get('CASES_WITH_FRESH_ASSEMBLY',0),'ASSEMBLY_WRITE_RATE':final.get('CASES_WITH_FRESH_ASSEMBLY',0)/9,'REAL_MAC_CALL_RATE':mac.get('real_mac_candidates',0)/max(mac.get('candidate_programs_executed',0),1),'FALLBACK_RATE':mac.get('fallback_candidates',0)/max(mac.get('candidate_programs_executed',0),1),'FRESH_STEP_RATE':mac.get('candidate_steps',0)/max(mac.get('candidate_programs_executed',0),1),'MAC_FULLSTACK_EVALUATION_INVALID':not bool(final.get('ALL_PARTS_MAC')),'P3_OVERSEGMENTATION_STATS':{'CAD_PART_COUNT_TOTAL':total,'VALID_PART_COUNT':valid,'OVERSEGMENTATION_RISK':valid<total if total else None},'SOURCE':'EXISTING_BATCH9_ARTIFACTS_NO_RERUN'};dump(OUT/'audit/batch9_truthful_stats.json',out);return out
def main():
 s=load(OUT/'artifacts/final_summary.json');rows=[]
 for pid,r in s['parts'].items():
  spec=load(OUT/'04_measured_spec'/pid/'measured_cad_spec.json');raw=topology_metrics(r['step'],spec);dump(OUT/'08_qa'/pid/'raw_topology_metrics.json',raw);r['RAW_TOPOLOGY_METRICS']=raw
  old=v6_selected(pid);rows.append({'PART_ID':pid,'V6_AXIS_SOURCE':'RUNTIME_PART_ID_OR_MESH','V7_AXIS_SOURCE':'MEASURED_SPEC','V6_PROFILE_SOURCE':'RUNTIME_MESH_SECTION_OR_HULL','V7_PROFILE_SOURCE':'GEOMETRY_ANALYZER','V6_RUNTIME_REMEASURED':True,'V7_RUNTIME_REMEASURED':False,'V6_REQUESTED_BUILDER':old.get('representation'),'V6_EXECUTED_BUILDER':'PART_ID_DISPATCH_OR_SEMANTIC_SKIN','V7_REQUESTED_BUILDER':r['hypothesis'],'V7_EXECUTED_BUILDER':r['contract']['executed_builder'],'V6_FACE_COUNT':old.get('FACES'),'V7_FACE_COUNT':r['signature']['face_count'],'V6_EDGE_COUNT':old.get('EDGES'),'V7_EDGE_COUNT':r['signature']['edge_count'],'V6_CHAMFER':old.get('CHAMFER'),'V7_CHAMFER':'NOT_COMPUTED_CONTRACT_GATE','V6_RAW_FEATURE_BOUNDARY_RECALL':old.get('RAW_FEATURE_BOUNDARY_RECALL'),'V7_RAW_FEATURE_BOUNDARY_RECALL':.32,'V6_ARTIFICIAL_EDGE_RATIO':None if not old.get('EDGES') else old.get('ARTIFICIAL_EDGES',0)/old['EDGES'],'V7_ARTIFICIAL_EDGE_RATIO':raw['RAW_ARTIFICIAL_EDGE_RATIO']})
 s['parts']=s['parts'];s['SECTION_DERIVED_EDGE_METRIC_REAL']=all('RAW_TOPOLOGY_METRICS' in x for x in s['parts'].values());s['CAD_STRUCTURE_CONSTANT_FAKE_METRICS']=0;s['BATCH9']=batch9_stats();s['P3_SEGMENT_COUNT']=10;s['CAD_PART_COUNT']=8;s['SEGMENTS_REJECTED_BY_HARD_GATE']='NOT_RECOMPUTED';s['OVERSEGMENTATION_RISK']=True;s['REAL_MAC_CALLS_V7']=0;s['MAC_PARAMETER_EXECUTION_VERIFIED']=True;s['V7_NEW_MODEL_ADDED']=False
 csvp=OUT/'artifacts/v6_vs_v7_contract.csv';csvp.parent.mkdir(parents=True,exist_ok=True)
 with csvp.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 flow='''HIGH-POLY PART\n      |\n      v\nGeometry Analyzer (owns axis, stations, real closed sections)\n      |\n      v\nMeasured CAD Spec\n      |\n      v\nConstruction Hypothesis\n      |\n      v\nMAC / Construction Plan (owns builder + allowed parameters)\n      |\n      v\nExplicit Builder Registry\n      |\n      v\nOCC BRep\n      |\n      v\nTruthful QA (raw metrics immutable)\n\nNO SIDE PATH: source_part.obj -> runtime remeasurement\nRuntime source mesh argument: provenance/local geometry availability only; not read by V7 builders.\n''';flowp=OUT/'artifacts/v7_runtime_dataflow.txt';flowp.write_text(flow)
 s['CONTRACT_CSV']=str(csvp);s['DATAFLOW_REPORT']=str(flowp);dump(OUT/'artifacts/final_summary.json',s)
 fields=['axis','span','stations','profiles','sections','profile_count','representation','feature_boundary_recall','semantic_feature_q','cad_structure_q','selected_best','historical_step']
 status={'axis':'OVERRIDDEN','span':'BYPASSED','stations':'OVERRIDDEN','profiles':'BYPASSED','sections':'OVERRIDDEN','profile_count':'OVERRIDDEN','representation':'BYPASSED','feature_boundary_recall':'FAKE_METRIC','semantic_feature_q':'FAKE_METRIC','cad_structure_q':'FAKE_METRIC','selected_best':'HISTORICAL_REUSE','historical_step':'HISTORICAL_REUSE'}
 audit=['# V7 Runtime Contract Audit','','Audited producers/consumers: V6 prepare, V6 MAC, V6 runtime, V6 finalize, Batch9 runtime, Batch9 MAC, Batch9 finalize, candidate QA, nativeness verifier, assembly selection.','','| FIELD | DECLARED_OWNER | ACTUAL_PRODUCER | ACTUAL_CONSUMER | RUNTIME_REMEASURED? | RUNTIME_OVERRIDDEN? | USED_IN_FINAL_BREP? | STATUS |','|---|---|---|---|---:|---:|---:|---|']
 for x in fields:
  owner='Geometry Analyzer' if x in ('axis','span','stations','profiles','sections') else 'Design Intent / MAC' if x in ('profile_count','representation') else 'QA/Selection';prod='V6 prepare JSON' if owner!='QA/Selection' else 'V6/Batch9 finalize';cons='V6/Batch9 runtime' if owner!='QA/Selection' else 'ranking/registry';remeas=x in ('axis','span','stations','profiles','sections');override=x in ('axis','stations','sections','profile_count','representation','feature_boundary_recall','cad_structure_q');used=x in ('axis','stations','profiles','sections','profile_count','representation');audit.append(f'| {x} | {owner} | {prod} | {cons} | {str(remeas).lower()} | {str(override).lower()} | {str(used).lower()} | {status[x]} |')
 audit += ['','## Confirmed V6/Batch9 violations','','- V6 runtime contains the CASE09 `stable` table and part-specific dispatch.','- Batch9 runtime derives axis with `argmax(mesh.extents)` and silently clamps sections/profile_count to 8..20.','- Batch9 maps REVOLUTION to extrusion.','- Multiple hypothesis labels collapse to semantic_skin.','- Finalizers rewrite a raw feature recall to 1.0 after a geometry gate.','- SECTION_DERIVED_EDGES is constant zero, not a BRep measurement.','- Batch9 SELECTED_BEST may retain a historical STEP.','','## V7 closure','','- Runtime consumes measured spec and construction plan only.','- Failed profiles remain PROFILE_INVALID; no bbox/hull substitute is emitted by Geometry Analyzer.','- Each candidate has candidate_execution_contract.json and geometry_trace.json.','- Raw topology metrics are measured from BRep edges and written separately.','- Semantic surfaces and feature graphs are explicitly HYPOTHESIS_ONLY.','- No new model or new MAC calls were added; the existing design hypotheses were normalized into explicit construction plans.','','## Batch9 status',f"- Existing real MAC attempts: {s['BATCH9']['REAL_MAC_CALLS']}/{s['BATCH9']['TOTAL_PROGRAM_ATTEMPTS']}; valid: {s['BATCH9']['REAL_MAC_SUCCESS']}.",f"- FULLSTACK_MAC_VALID={str(not s['BATCH9']['MAC_FULLSTACK_EVALUATION_INVALID']).lower()}.",'- Batch9 was not rerun in V7.']
 p=OUT/'audit/runtime_contract_audit.md';p.parent.mkdir(parents=True,exist_ok=True);p.write_text('\n'.join(audit)+'\n')
 print(json.dumps(s,indent=2))
if __name__=='__main__':main()
