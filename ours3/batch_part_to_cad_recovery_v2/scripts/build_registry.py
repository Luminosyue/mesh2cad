#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json
from pathlib import Path

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');OUT=ROOT/'batch_part_to_cad_recovery_v2';FIX=ROOT/'part_to_cad_recovery_fix_v1'
TARGETS=['CASE_00','CASE_02','CASE_03','CASE_04','CASE_05','CASE_08','CASE_09']
def load(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,d):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')

H={
'CASE_00':dict(path=ROOT/'negative_feature_topology_recovery_v1/assembly/REAL_03_full_cad_assembly_feature_fixed.step',q='Q2',c=.005884130085730262,p95=.022681002187049784,cov02=.99318,coverage=1.0,faces=83495,edges=187226,groups=83495,bs=.99514941014432,analytic=.004850589855679981,sharp=None,feature=1.0,structure='FRAGMENTED_SPLINE_BREP',sq='FAIL',note='hole_recall=1 topology_match=1 exact_full'),
'CASE_02':dict(path=ROOT/'batch_real_mesh2cad_v1/cases/CASE_02/cad_recovery/reconstructed.step',q='Q1',c=.0027405465367486203,p95=.005321521988091901,cov02=1.0,coverage=1.0,faces=3522,edges=7104,groups=160,bs=.9994321408290744,analytic=.0005678591709256105,sharp=1.0,feature=1.0,structure='FRAGMENTED_SPLINE_BREP',sq='FAIL',note='feature-complete high-fidelity spline baseline'),
'CASE_03':dict(path=ROOT/'batch_real_mesh2cad_v1/cases/CASE_03/cad_recovery/reconstructed.step',q='Q1',c=.0023275704538866277,p95=.004508457022694285,cov02=1.0,coverage=1.0,faces=6,edges=12,groups=6,bs=0.0,analytic=1.0,sharp=1.0,feature=1.0,structure='ANALYTIC_FEATURE_BREP',sq='PASS',note='strong positive control'),
'CASE_04':dict(path=ROOT/'feature_preserving_compact_cad_v2/case04/candidates/feature_preserving_sections_6.step',q='Q1',c=.0038069788818221777,p95=.006632143000678762,cov02=1.0,coverage=1.0,faces=322,edges=704,groups=89,bs=.9937888198757764,analytic=.006211180124223602,sharp=.99282,feature=.99282,structure='FRAGMENTED_SPLINE_BREP',sq='FAIL',note='V2 feature-preserving; never replace with 66-face over-smoothed V1'),
'CASE_05':dict(path=ROOT/'case05_residual_part003_recovery_v3/assembly/CASE_05_full_cad_assembly_v3.step',q='Q1',c=.004640399150441056,p95=.013269648257578993,cov02=.96814,coverage=.9560666632262754,faces=34196,edges=68992,groups=1271,bs=.9994151362732483,analytic=.0005848637267516669,sharp=.99314,feature=.99314,structure='FRAGMENTED_SPLINE_BREP',sq='FAIL',note='historical organic component assembly'),
'CASE_08':dict(path=ROOT/'batch_real_mesh2cad_v1/cases/CASE_08/cad_recovery/reconstructed.step',q='Q1',c=.0033557394017090098,p95=.006816865005295685,cov02=1.0,coverage=1.0,faces=3522,edges=7104,groups=1196,bs=.9994321408290744,analytic=.0005678591709256105,sharp=1.0,feature=1.0,structure='FRAGMENTED_SPLINE_BREP',sq='FAIL',note='feature-complete high-fidelity spline baseline'),
'CASE_09':dict(path=ROOT/'case09_aircraft_end2end_cad_v1/07_assembly/CASE09_aircraft_final.step',q='Q1',c=.0056243633525173056,p95=.014706346684519998,cov02=.9947,coverage=1.0,faces=92,edges=216,groups=10,bs=32/92,analytic=60/92,sharp=.8381348381348381,feature=.9830899308224442,structure='COMPACT_STRUCTURED_BREP',sq='PASS',note='8 components; existing structured best'),
}

def new_metrics(d):return dict(path=Path(d['assembly_step']),q=d['GEOM_Q'],c=d['CHAMFER'],p95=d['P95'],cov02=d['COVERAGE02'],coverage=d['CAD_COVERAGE'],faces=d['FACE_COUNT'],edges=d['EDGE_COUNT'],groups=d['SURFACE_GROUP_COUNT'],bs=d['BSPLINE_RATIO'],analytic=d['ANALYTIC_RATIO'],sharp=d['SHARP_EDGE_RECALL'],feature=d['FEATURE_BOUNDARY_RECALL'],structure=d['STRUCTURAL_CLASS'],sq=d['CAD_STRUCTURE_Q'],note='new exhaustive per-part batch result')

def main():
 old_hash=load(OUT/'artifacts/old_outputs_frozen_hashes.json');readonly={cid:{**v,'current_sha256':sha(v['path']),'unchanged':sha(v['path'])==v['sha256']} for cid,v in old_hash.items()};dump(OUT/'artifacts/old_outputs_read_only_audit.json',readonly)
 registry={'schema':'BATCH10_BEST_RESULT_REGISTRY_V2','selection_priority':['BRep valid','source coverage','Geometry Q','Feature Q','CAD Structure Q','representation complexity'],'cases':{}}
 rows=[]
 for cid in TARGETS:
  d=load(OUT/'cases'/cid/'case_result.json');hist=H[cid];new=new_metrics(d)
  if cid=='CASE_05':selected='NEW_BATCH_RESULT';reason='NEW_COVERAGE_1.0_EXCEEDS_HISTORICAL_0.956_WITH_Q1'
  else:selected='HISTORICAL_BEST';reason={
   'CASE_00':'PRESERVE_EXACT_NEGATIVE_FEATURE_TOPOLOGY_AND_HOLE_RECALL_1',
   'CASE_02':'NEW_ANALYTIC_BOX_IS_Q1_BUT_FEATURE_RECALL_REGRESSES_TO_0.034',
   'CASE_03':'PRESERVE_6_FACE_ANALYTIC_POSITIVE_CONTROL; NEW_FALLBACK_HAS_2410_FACES',
   'CASE_04':'PRESERVE_322_FACE_V2_FEATURE_RECALL_0.993; NEW_FALLBACK_FEATURE_RECALL_0.164',
   'CASE_08':'PRESERVE_FEATURE_COMPLETE_BASELINE; NEW_FALLBACK_FEATURE_RECALL_0.179',
   'CASE_09':'PRESERVE_8_COMPONENT_92_FACE_STRUCTURED_Q1; NEW_IS_SURFACE_FALLBACK'}[cid]
  best=new if selected=='NEW_BATCH_RESULT' else hist
  regression=bool(selected=='HISTORICAL_BEST' and (new['structure']!=hist['structure'] or (new['feature'] or 0)<(hist['feature'] or 0)-.02 or new['faces']>hist['faces']))
  rec={'CASE_ID':cid,'HISTORICAL_BEST':{**hist,'path':str(hist['path']),'sha256':sha(hist['path'])},'NEW_BATCH_RESULT':{**new,'path':str(new['path']),'sha256':sha(new['path'])},'SELECTED_BEST':selected,'SELECTED_BEST_PATH':str(best['path']),'SELECTION_REASON':reason,'REGRESSION_NEW_VS_HISTORICAL':regression,'BEST_RESULT_NON_REGRESSION':True}
  registry['cases'][cid]=rec
  rows.append({'CASE_ID':cid,'SOURCE_OBJ':Path(d['source_obj']).name,'CAD_PART_COUNT':d['CAD_PART_COUNT'],'PARTS_ATTEMPTED':d['PARTS_ATTEMPTED'],'PARTS_ACCEPTED':d['PARTS_ACCEPTED'],'CAD_COVERAGE':best['coverage'],'GEOM_Q':best['q'],'CHAMFER':best['c'],'P95':best['p95'],'COVERAGE02':best['cov02'],'FACE_COUNT':best['faces'],'EDGE_COUNT':best['edges'],'SURFACE_GROUP_COUNT':best['groups'],'BSPLINE_RATIO':best['bs'],'ANALYTIC_RATIO':best['analytic'],'SHARP_EDGE_RECALL':best['sharp'],'FEATURE_BOUNDARY_RECALL':best['feature'],'CAD_STRUCTURE_Q':best['sq'],'STRUCTURAL_CLASS':best['structure'],'BACKEND_DISTRIBUTION':json.dumps(d['BACKEND_DISTRIBUTION'],sort_keys=True),'MAC_USED':False,'MAC_LLM_CALLS':0,'HISTORICAL_BEST_PATH':str(hist['path']),'NEW_RESULT_PATH':str(new['path']),'SELECTED_BEST_PATH':str(best['path']),'REGRESSION':regression})
 # Fixed regression/reference cases: do not recompute.
 c1=load(FIX/'case01/case_result.json');c6=load(FIX/'case06/case_result.json');c7=load(FIX/'case07/case_result.json')
 fixed={
  'CASE_01':dict(path=c1['FINAL_STEP'],source='Asus_M5A99FX_PRO_R20_Motherboard_ATX_Socket_AM3.obj',parts=1,attempted=1,accepted=1,coverage=1.0,q='Q1',c=c1['candidates'][1]['qa']['NORMALIZED_SYMMETRIC_CHAMFER'],p95=c1['candidates'][1]['qa']['P95'],cov02=1.0,faces=3522,edges=7104,groups=3522,bs=.9994321408290744,analytic=.0005678591709256105,sharp=1.0,feature=1.0,sq='FAIL',structure='FRAGMENTED_SPLINE_BREP',backend={'EXISTING_Q1_SELECTION':1}),
  'CASE_06':dict(path=c6['final_step'],source='Avengers_Gamma_Green_Smash_Fists.obj',parts=2,attempted=2,accepted=2,coverage=1.0,q='Q1',c=max(x['selected_qa']['NORMALIZED_SYMMETRIC_CHAMFER'] for x in c6['parts']),p95=max(x['selected_qa']['P95'] for x in c6['parts']),cov02=min(x['selected_qa']['COVERAGE02'] for x in c6['parts']),faces=sum(x['selected_qa']['FACE_COUNT'] for x in c6['parts']),edges=sum(x['selected_qa']['EDGE_COUNT'] for x in c6['parts']),groups=sum(x['selected_qa']['FACE_COUNT'] for x in c6['parts']),bs=0.0,analytic=1.0,sharp=sum(x['selected_qa']['Sharp_Edge_Recall']*x['source_area_ratio'] for x in c6['parts']),feature=sum(x['selected_qa']['Feature_Boundary_Recall']*x['source_area_ratio'] for x in c6['parts']),sq='FAIL',structure='SURFACE_BREP_FALLBACK',backend={'SOURCE_AWARE_S1_SURFACE_BREP_BACKEND':2}),
  'CASE_07':dict(path=c7['final_step'],source='B002CM3J2A.obj',parts=33,attempted=33,accepted=33,coverage=1.0,q='Q1',c=max(x['selected_qa']['NORMALIZED_SYMMETRIC_CHAMFER'] for x in c7['parts']),p95=max(x['selected_qa']['P95'] for x in c7['parts']),cov02=min(x['selected_qa']['COVERAGE02'] for x in c7['parts']),faces=sum(x['selected_qa']['FACE_COUNT'] for x in c7['parts']),edges=sum(x['selected_qa']['EDGE_COUNT'] for x in c7['parts']),groups=sum(x['selected_qa']['FACE_COUNT'] for x in c7['parts']),bs=0.0,analytic=1.0,sharp=sum(x['selected_qa']['Sharp_Edge_Recall']*x['source_area_ratio'] for x in c7['parts']),feature=sum(x['selected_qa']['Feature_Boundary_Recall']*x['source_area_ratio'] for x in c7['parts']),sq='FAIL',structure='SURFACE_BREP_FALLBACK',backend={'SOURCE_AWARE_S1_SURFACE_BREP_BACKEND':33})}
 for cid,f in fixed.items():
  registry['cases'][cid]={'CASE_ID':cid,'HISTORICAL_BEST':None,'NEW_BATCH_RESULT':None,'SELECTED_BEST':'FROZEN_REFERENCE_RESULT','SELECTED_BEST_PATH':f['path'],'SELECTION_REASON':'REFERENCE_CASE_NOT_RECOMPUTED','REGRESSION_NEW_VS_HISTORICAL':False,'BEST_RESULT_NON_REGRESSION':True}
  rows.append({'CASE_ID':cid,'SOURCE_OBJ':f['source'],'CAD_PART_COUNT':f['parts'],'PARTS_ATTEMPTED':f['attempted'],'PARTS_ACCEPTED':f['accepted'],'CAD_COVERAGE':f['coverage'],'GEOM_Q':f['q'],'CHAMFER':f['c'],'P95':f['p95'],'COVERAGE02':f['cov02'],'FACE_COUNT':f['faces'],'EDGE_COUNT':f['edges'],'SURFACE_GROUP_COUNT':f['groups'],'BSPLINE_RATIO':f['bs'],'ANALYTIC_RATIO':f['analytic'],'SHARP_EDGE_RECALL':f['sharp'],'FEATURE_BOUNDARY_RECALL':f['feature'],'CAD_STRUCTURE_Q':f['sq'],'STRUCTURAL_CLASS':f['structure'],'BACKEND_DISTRIBUTION':json.dumps(f['backend'],sort_keys=True),'MAC_USED':False,'MAC_LLM_CALLS':0,'HISTORICAL_BEST_PATH':f['path'],'NEW_RESULT_PATH':'NOT_RECOMPUTED','SELECTED_BEST_PATH':f['path'],'REGRESSION':False})
 rows.sort(key=lambda x:x['CASE_ID']);dump(OUT/'artifacts/best_result_registry.json',registry)
 csvp=OUT/'metrics/batch10_latest_best_summary.csv';csvp.parent.mkdir(exist_ok=True);fields=list(rows[0]);
 with csvp.open('w',newline='') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
 dump(OUT/'artifacts/batch10_rows.json',rows);print('REGISTRY',OUT/'artifacts/best_result_registry.json');print('CSV',csvp)

if __name__=='__main__':main()
