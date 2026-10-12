import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,sys,traceback,collections,time
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,ThreadPoolExecutor,as_completed
from validate_native_parametric_cad import validate,dump,sha
P=Path('/data/home/cuiyuehan/project/mesh2cad/outputs')
O=P/'native_parametric_cad_audit_v1'
V=P/'part_cad_reject_repair_v3'
ROOTS=[P/x for x in ['p3_high_detail_mesh2cad_factory_v1_smoke20','part_cad_fitting_v2','part_cad_reject_repair_v3','part_cad_v3_assembly_visualizations']]
def entry(p):
 s=p.stat();return str(p),{'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'sha256':sha(p)}
def guard():
 files=sorted(p for root in ROOTS for p in root.rglob('*') if p.is_file())
 with ThreadPoolExecutor(max_workers=4) as pool:r=dict(pool.map(entry,files))
 return r
def job(task):
 version,row=task;d=Path(row['v1_dir']) if version=='V1' else V/'cases'/row['case_id'];out=O/'cases'/version/row['case_id'];out.mkdir(parents=True,exist_ok=True)
 try:
  r=validate(d/'cad/cad.py',d/'cad/cad.step',d/'source/part_local.ply',out)
  result=json.loads((d/'result.json').read_text());r.update(version=version,object_id=row['object_id'],part_id=row['part_id'],case_id=row['case_id'],previous_status=row['v1_status'],current_status=result.get('v3_status',result.get('status')),size_class=row['size_class'],candidate_metadata_path=str(d/'cad/parameters.json'),existing_metrics_path=str(d/'result.json'),metadata_presence={'parameters':'PRESENT' if (d/'cad/parameters.json').exists() else 'MISSING','result':'PRESENT'},selected_kind=result.get('best_kind',result.get('fix_type','see metadata')))
  dump(out/'audit.json',r);return {'version':version,'case_id':row['case_id'],'classification':r['classification'],'faces':r.get('step_face_count'),'isolated':r.get('isolated_reexecution_pass'),'error':None}
 except Exception as e:
  r={'version':version,'case_id':row['case_id'],'classification':'E_UNCERTAIN','error':str(e),'traceback':traceback.format_exc()};dump(out/'ERROR.json',r);return r
if __name__=='__main__':
 O.mkdir(exist_ok=True)
 if '--guard-after' in sys.argv:
  before=json.loads((O/'integrity/READ_ONLY_BEFORE.json').read_text());after=guard();changes=[k for k in before if before[k]!=after.get(k)];added=sorted(set(after)-set(before));r={'pass':not changes and not added,'protected_file_n':len(before),'bytes':sum(v['bytes'] for v in before.values()),'changed_or_missing':changes,'added':added,'roots':[str(p) for p in ROOTS]};dump(O/'integrity/READ_ONLY_GUARD.json',r);print(json.dumps(r));raise SystemExit(0 if r['pass'] else 1)
 if not (O/'integrity/READ_ONLY_BEFORE.json').exists():
  print('HASHING HISTORICAL FILES',flush=True);before=guard();dump(O/'integrity/READ_ONLY_BEFORE.json',before);print('PROTECTED',len(before),sum(v['bytes'] for v in before.values()),flush=True)
 rows=json.loads((V/'manifests/cases.json').read_text());assert len(rows)==209
 dump(O/'manifests/input_cases.json',rows)
 dump(O/'manifests/gate.json',{'current_gate':'CAD_REPRESENTATION_VALIDITY_NOT_VERIFIED','next_allowed_stage':'NATIVE_PARAMETRIC_CAD_AUDIT_V1','fitting_performed':False,'cohorts':['V1 original 209 primary','V3 current visualization 209 supplemental'],'workers':8})
 tasks=[(version,row) for version in ['V1','V3'] for row in rows if not (O/'cases'/version/row['case_id']/'audit.json').exists()]
 with ProcessPoolExecutor(max_workers=8) as pool:
  futures=[pool.submit(job,x) for x in tasks]
  for i,f in enumerate(as_completed(futures),1):print(i,len(tasks),json.dumps(f.result()),flush=True)
 print('AUDIT_EXECUTION_COMPLETE',flush=True)
