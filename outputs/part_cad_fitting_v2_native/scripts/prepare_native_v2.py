import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import json,shutil,hashlib,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
P=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');O=P/'part_cad_fitting_v2_native';R=P/'cad_render_v4';V=P/'part_cad_reject_repair_v3';A=P/'native_parametric_cad_audit_v1'
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(2**20),b''):h.update(b)
 return h.hexdigest()
def entry(p):s=p.stat();return str(p),{'sha256':sha(p),'size':s.st_size,'mtime_ns':s.st_mtime_ns}
roots=[P/x for x in ['p3_high_detail_mesh2cad_factory_v1_smoke20','part_cad_fitting_v2','part_cad_reject_repair_v3','part_cad_v3_assembly_visualizations','native_parametric_cad_audit_v1']]
def guard():
 with ThreadPoolExecutor(max_workers=4) as pool:return dict(pool.map(entry,[p for root in roots for p in root.rglob('*') if p.is_file()]))
if '--verify' in sys.argv:
 before=json.loads((O/'integrity/HISTORICAL_BEFORE.json').read_text());after=guard();bad=[p for p in before if before[p]!=after.get(p)];added=sorted(set(after)-set(before));r={'pass':not bad and not added,'protected_file_n':len(before),'changed_or_missing':bad,'added':added};dump(O/'integrity/READ_ONLY_GUARD.json',r);dump(R/'reports/READ_ONLY_GUARD.json',r);print(r);assert r['pass'];raise SystemExit
assert not (O/'manifests/cases.json').exists(),'Already prepared; do not overwrite'
for root in [O,R]:
 for sub in ['scripts','config','manifests','reports','integrity','logs']:(root/sub).mkdir(parents=True,exist_ok=True)
assert shutil.disk_usage(P).free>10*2**30
dump(O/'integrity/HISTORICAL_BEFORE.json',guard())
for name in ['v2_common.py','fit_logic.py','historical_fit.py','metric_runtime.py','cad_emit.py','v2_optimize.py','v3_geometry.py']:
 shutil.copyfile(V/'scripts'/name,O/'scripts'/name)
shutil.copyfile(A/'scripts/validate_native_parametric_cad.py',O/'scripts/validate_native_parametric_cad.py')
shutil.copyfile(V/'config/factory_config.json',O/'config/factory_config.json')
rows=json.loads((V/'manifests/cases.json').read_text());assert len(rows)==209
order={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}
def score(m):return 10*m['normalized_chamfer']+1-m['iou']+2*m['centroid_l2_error']+m['bbox_error']
for row in rows:
 d=O/'cases'/row['case_id'];old=V/'cases'/row['case_id'];orig=Path(row['v1_dir']);v1=json.loads((orig/'result.json').read_text());v3=json.loads((old/'result.json').read_text());choose1=(order[v1['status']],score(v1['metrics']))<(order[v3['v3_status']],score(v3['v3_metrics']));bd=orig if choose1 else old;version='V1' if choose1 else 'V3';metrics=v1['metrics'] if choose1 else v3['v3_metrics'];st=v1['status'] if choose1 else v3['v3_status']
 for sub in ['source','baseline','cad','metrics','candidates','diagnosis','optimization']:(d/sub).mkdir(parents=True,exist_ok=True)
 for name in ['part_local.ply','provenance.json','frozen_evaluation_points.npy','features_v2.json']:shutil.copyfile(old/'source'/name,d/'source'/name)
 for name in ['cad.py','cad.step','parameters.json']:shutil.copyfile(bd/'cad'/name,d/'baseline'/name);shutil.copyfile(bd/'cad'/name,d/'cad'/name)
 meshname='cad_mesh_from_reloaded_step.ply' if choose1 else 'cad_mesh.ply'
 for sub in ['baseline','cad']:shutil.copyfile(bd/'cad'/meshname,d/sub/'cad_mesh.ply')
 audit=json.loads((A/'cases'/version/row['case_id']/'audit.json').read_text());assert audit['cad_sha256']==sha(d/'baseline/cad.py') and audit['step_sha256']==sha(d/'baseline/cad.step')
 dump(d/'baseline/representation.json',audit);dump(d/'source/v1_result.json',v1);dump(d/'source/v3_result.json',v3);row.update(baseline_version=version,baseline_status=st,baseline_metrics=metrics,baseline_family=v1['cad_family'] if choose1 else v3.get('family',v3.get('v2_family',row['v1_family'])))
 dump(d/'metrics/metrics.json',metrics)
dump(O/'manifests/cases.json',rows);shutil.copyfile(V/'manifests/objects.json',O/'manifests/objects.json')
dump(O/'config/native_v2.json',{'task':'PART_CAD_FITTING_V2_NATIVE_AND_RENDER_V4','part_n':209,'major_n':153,'phase1':'original V1 NEAR_PASS 63 only','baseline_policy':'best original V1/current V3 status tier then unchanged score; historical gain separately attributed','workers':12,'max_candidates_including_baseline':8,'max_primitives':8,'max_booleans':6,'max_sketch_entities':96,'max_spline_controls_per_loop':20,'score':'10*NCD+(1-IoU)+2*centroid+bbox','evaluation':'unchanged 20000 sample points, original seed, IoU128, tessellation(0.001,0.05)','strict':{'iou_min':.9,'ncd_max':.01,'bbox_max':.03,'centroid_max':.02},'near_gate_for_reject_phase':{'min_original_near_to_strict':10,'min_additional_strict_vs_preserved_baseline':1,'max_status_damage':0},'threshold_is_operational_pause_rule_not_geometry_acceptance':True,'model_training':False,'p3_rerun':False})
print('PREPARED',len(rows),'NEAR',sum(r['v1_status']=='NEAR_PASS' for r in rows),flush=True)
