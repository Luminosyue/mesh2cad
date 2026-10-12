import json,hashlib,shutil
from pathlib import Path
P=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');V=P/'part_cad_fitting_v2';O=P/'part_cad_reject_repair_v3'
def dump(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
assert shutil.disk_usage(P).free>10*2**30
if (O/'manifests/cases.json').exists():raise SystemExit('Already prepared; resume, do not overwrite')
for k in ['scripts','config','manifests','integrity','logs','reports','tables','visualizations','cases']:(O/k).mkdir(parents=True,exist_ok=True)
guard={str(p):{'sha256':sha(p),'mtime_ns':p.stat().st_mtime_ns} for p in V.rglob('*') if p.is_file()}
dump(O/'integrity/V2_PROTECTED_BEFORE.json',guard)
for p in (V/'scripts').glob('*.py'):shutil.copyfile(p,O/'scripts'/p.name)
shutil.copyfile(V/'config/factory_config.json',O/'config/factory_config.json')
shutil.copyfile(V/'manifests/objects.json',O/'manifests/objects.json')
rows=json.loads((V/'manifests/cases.json').read_text())
for row in rows:
 old=V/'cases'/row['case_id'];r=json.loads((old/'result.json').read_text());row.update(v2_dir=str(old),v2_status=r['v2_status'],v2_score=r['v2_score'])
 d=O/'cases'/row['case_id']
 for k in ['source','baseline','cad','metrics','candidates','optimization','visualizations']:(d/k).mkdir(parents=True,exist_ok=True)
 for name in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:
  shutil.copyfile(old/'cad'/name,d/'baseline'/name)
  if r['v2_status']!='REJECT':shutil.copyfile(old/'cad'/name,d/'cad'/name)
 for name in ['part_local.ply','provenance.json','frozen_evaluation_points.npy']:shutil.copyfile(old/'source'/name,d/'source'/name)
 shutil.copyfile(old/'features/features_v2.json',d/'source/features_v2.json');shutil.copyfile(old/'result.json',d/'source/v2_result.json')
 if r['v2_status']!='REJECT':
  dump(d/'metrics/metrics.json',r['v2_metrics']);dump(d/'result.json',{'case_id':row['case_id'],'v2_status':r['v2_status'],'v3_status':r['v2_status'],'v2_metrics':r['v2_metrics'],'v3_metrics':r['v2_metrics'],'preserved':True,'attempts':[],'selected_candidate':0})
dump(O/'manifests/cases.json',rows)
dump(O/'config/v3.json',{'repair_cohort':'V2 REJECT only','reject_n':124,'workers':12,'max_candidates_including_baseline':8,'max_primitives':8,'max_booleans':6,'max_sketch_entities':96,'source_and_acceptance_protocol':'Unchanged source mesh, original seeds, 20000 points and IoU128','ranking':'STRICT then NEAR then REJECT, then fixed V2 weighted score; preserve V2 baseline within every case','proxy':'4000 frozen source points against analytic surfaces for proposal selection only','assembly':False,'training':False})
print('PREPARED',len(rows),'REJECT',sum(r['v2_status']=='REJECT' for r in rows),'V2_GUARDED',len(guard),flush=True)
