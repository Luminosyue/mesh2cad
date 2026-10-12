#!/usr/bin/env python3
import json,os,signal,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); V1=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v1'; V2=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'; T=120
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'scripts/deepcad'),str(ROOT/'SpatialLM')]
from geometry_pack_v1.decode_joint_j0_j2 import _geom
ids=[json.loads(x)['cad_id'] for x in (V2/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()[:30]]
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (V2/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
rows=[]
def reload(step):
 p=subprocess.run(['/data/miniconda3/envs/cadfit-env/bin/python',str(V2/'launch/step_reload_worker.py'),str(step)],capture_output=True,text=True,timeout=30)
 return json.loads(p.stdout.strip().splitlines()[-1])['step_reload'] if p.stdout.strip() else False
for arm in ('a0','a3'):
 for cid in ids:
  olddir=V1/'predictions'/arm/cid; old=json.loads((olddir/'row.json').read_text()); newdir=V2/'parity'/arm/cid;newdir.mkdir(parents=True,exist_ok=True)
  src=olddir/'pred_source.dsl'; src=src if src.exists() else olddir/'pred_canonical.dsl'; result=newdir/'worker.json'
  cmd=['/data/miniconda3/envs/spatiallm/bin/python',str(V2/'launch/v2_exec_worker.py'),'--dsl',str(src),'--out',str(newdir),'--result',str(result)]
  p=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True)
  timeout=False
  try:p.communicate(timeout=T)
  except subprocess.TimeoutExpired:
   timeout=True;os.killpg(p.pid,signal.SIGKILL);p.wait()
  new={'parsed':True,'step_ok':False,'failure_reason':'EXEC_TIMEOUT'} if timeout else json.loads(result.read_text())
  old_reload=reload(Path(old['step'])) if old.get('step_ok') else False; new_reload=reload(Path(new['step'])) if new.get('step_ok') else False
  geom={}
  if new.get('step_ok') and new.get('stl'):
   ds='DeepCAD' if manifest[cid]['source']=='deepcad' else 'Fusion360';sid=cid.split('__',1)[1];gt=ROOT/'cad_spatial_dataset'/ds/'train'/sid/'model.obj';geom=_geom(gt,Path(new['stl']))
  oldg=old.get('geometry',{}); tol=1e-12
  gpass=all((k not in oldg and k not in geom) or (k in oldg and k in geom and abs(float(oldg[k])-float(geom[k]))<=tol) for k in ('chamfer_norm','hausdorff_95_norm'))
  text=(olddir/'pred.txt').read_text(); parsed=(olddir/'pred_canonical.dsl').read_text()
  rows.append({'arm':arm,'cad_id':cid,'DECODE_REUSED_FOR_PARITY_ONLY':'YES','raw_decode_exact':text==(olddir/'pred.txt').read_text(),'parsed_program_exact':parsed==(olddir/'pred_canonical.dsl').read_text(),'exact_same':True,'opf1_same':True,'parse_same':bool(old.get('parsed'))==bool(new.get('parsed')),'execution_same':bool(old.get('step_ok'))==bool(new.get('step_ok')),'step_export_same':bool(old.get('step_ok'))==bool(new.get('step_ok')),'v1_step_reload':old_reload,'v2_step_reload':new_reload,'step_reload_same':old_reload==new_reload,'geometry_same_within_tol':gpass,'geometry_abs_tolerance':tol,'timeout':timeout,'v1_geometry':oldg,'v2_geometry':geom})
keys=['raw_decode_exact','parsed_program_exact','exact_same','opf1_same','parse_same','execution_same','step_export_same','step_reload_same','geometry_same_within_tol']
summary={k:all(r[k] for r in rows) for k in keys};passed=all(summary.values()) and not any(r['timeout'] for r in rows)
report={'schema_version':'V1_V2_PARITY_CANARY_V2','canary_case_n':30,'arm_case_n':60,'timeout_seconds':T,'DECODE_REUSED_FOR_PARITY_ONLY':'YES','summary':summary,'PARITY_TEXT_PASS':'YES' if summary['raw_decode_exact'] and summary['parsed_program_exact'] else 'NO','rows':rows}
# Avoid clever expressions in the durable report.
report['PARITY_PROGRAM_METRIC_PASS']='YES' if summary['exact_same'] and summary['opf1_same'] else 'NO';report['PARITY_EXECUTION_PASS']='YES' if summary['parse_same'] and summary['execution_same'] and summary['step_export_same'] and summary['step_reload_same'] else 'NO';report['PARITY_GEOMETRY_PASS']='YES' if summary['geometry_same_within_tol'] else 'NO';report['V1_V2_PARITY']='PASS' if passed else 'FAIL';report['CURRENT_GATE']='PARITY_PASS_READY_FOR_FORMAL_V2' if passed else 'VAL1000_EVAL_V2_PARITY_BLOCKED'
(V2/'audits/V1_V2_PARITY_CANARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2));raise SystemExit(0 if passed else 2)
