from structure_common import *
import shutil,collections,sys
from concurrent.futures import ThreadPoolExecutor
def protected():
 roots=[O.parent/x for x in ['p3_high_detail_mesh2cad_factory_v1_smoke20','part_cad_fitting_v2','part_cad_reject_repair_v3','part_cad_v3_assembly_visualizations','native_parametric_cad_audit_v1','part_cad_fitting_v2_native','cad_render_v4']]
 def entry(p):
  s=p.stat();return str(p),{'size':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':sha(p)}
 with ThreadPoolExecutor(max_workers=4) as pool:return dict(pool.map(entry,[p for root in roots for p in root.rglob('*') if p.is_file()]))
def select(rows,n):
 selected=[];seen={k:set() for k in ['family','failure_pattern','object_id','size_class']}
 rows=sorted(rows,key=lambda r:(distance(r['metrics']),r['case_id']))
 for r in rows:r['failure_pattern']=failure(r['metrics'])
 while len(selected)<n:
  available=[r for r in rows if r not in selected]
  # Half closest cases, half deterministic stratified coverage. No random choice.
  if len(selected)<n//2:r=available[0]
  else:r=max(available,key=lambda r:(sum(r[k] not in seen[k] for k in seen),-distance(r['metrics'])))
  selected.append(r)
  for k in seen:seen[k].add(r[k])
 return selected
if __name__=='__main__':
 if '--verify' in sys.argv:
  before=read(O/'integrity/HISTORICAL_BEFORE.json');after=protected();bad=[p for p in before if after.get(p)!=before[p]];added=sorted(set(after)-set(before));r={'pass':not bad and not added,'protected_file_n':len(before),'changed_or_missing':bad,'added':added};dump(O/'integrity/READ_ONLY_GUARD.json',r);print(r);assert r['pass'];raise SystemExit
 assert not (O/'manifests/all_parts.json').exists()
 for s in ['integrity','manifests','cases','tables','reports','visualizations','logs','runtime']:(O/s).mkdir(parents=True,exist_ok=True)
 dump(O/'integrity/HISTORICAL_BEFORE.json',protected());rows=all_rows();assert collections.Counter(r['status'] for r in rows)=={'STRICT_ACCEPT':17,'NEAR_PASS':76,'REJECT':116}
 near=[r for r in rows if r['status']=='NEAR_PASS'];ns=select(near,20);used={r['case_id'] for r in ns}
 es=select([r for r in rows if r['family']=='D_EXTRUDE_WITH_CUTS' and r['case_id'] not in used and r['status']!='STRICT_ACCEPT'],15);used|={r['case_id'] for r in es}
 ss=select([r for r in rows if r['family']=='A_SIMPLE_PRIMITIVE' and r['case_id'] not in used and r['status']!='STRICT_ACCEPT'],10)
 subset=[]
 for cohort,group in [('NEAR',ns),('EXTRUDE_CUT',es),('SIMPLE',ss)]:
  for row in group:
   r=dict(row,cohort=cohort,selection_reason='half nearest to strict then uncovered family/failure/object/size; deterministic',strict_distance=distance(row['metrics']));subset.append(r)
   old=V/'cases'/r['case_id'];d=O/'cases'/r['case_id']
   for s in ['source','baseline','rounds','final']:(d/s).mkdir(parents=True,exist_ok=True)
   for p in (old/'source').iterdir():
    if p.name in ['part_local.ply','provenance.json','frozen_evaluation_points.npy','features_v2.json']:shutil.copyfile(p,d/'source'/p.name)
   for p in (old/'cad').iterdir():
    if p.is_file():shutil.copyfile(p,d/'baseline'/p.name)
   dump(d/'baseline/metrics.json',r['metrics']);dump(d/'row.json',r)
 dump(O/'manifests/all_parts.json',rows);dump(O/'manifests/subset.json',subset);table('diagnosis_subset_manifest.csv',subset)
 gates=[{'case_id':r['case_id'],'family':r['family'],'failure_pattern':failure(r['metrics']),'failed_gates':failed(r['metrics']),**{k:r['metrics'][k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']}} for r in near];table('near_gate_failure_breakdown.csv',gates)
 dump(O/'config/structure.json',{'workers':12,'max_rounds':3,'max_candidates_per_round':4,'max_new_features':3,'max_primitives':10,'max_boolean_ops':8,'strict':{'iou':.9,'ncd':.01,'bbox':.03,'centroid':.02},'accept':{'delta_iou':.02,'delta_ncd':-.002,'or_new_strict':True},'significant':{'delta_iou':.05,'delta_ncd':-.003,'or_status_improved':True},'expansion_gate':{'new_strict':8,'or_near_significant_fraction':.3},'residual_connectivity':6,'min_proposal_component_voxels':16,'min_component_fit_precision':.65,'max_residual_fraction_for_local_model':.35,'no_reassembly':True,'no_scale':True,'no_new_source_sampling':True,'selection_frozen':True,'evaluation':'frozen source samples, same CAD seed and sample count; IoU128 existing majority scanfill; existing evaluation tessellation .001/.05; serialize/reload mesh before metrics'})
 print(json.dumps({'subset':len(subset),'near_failure':dict(collections.Counter(x['failure_pattern'] for x in gates)),'families':dict(collections.Counter(r['family'] for r in rows))}),flush=True)
