import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
import json,csv,sys,runpy,traceback,subprocess,concurrent.futures,shutil,time
from pathlib import Path
import cadquery as cq
import pipeline as P
O=P.O;E=O/'model_v1';V=E/'resume_v1';V.mkdir(exist_ok=True)
BASE=Path('/var/tmp/cuiyuehan_full20_p1_v3_20260925/resume_labels');BASE.mkdir(exist_ok=True)
def save(p,x):P.dump(p,x)
def attempt(pid,idx):
 src=O/'objects/tank/cad_parts'/pid;dst=BASE/'tank'/pid/f'attempt_{idx}';dst.mkdir(parents=True,exist_ok=True)
 result=dict(part=pid,attempt=idx,PASS=False,original_ir_sha256=P.sha(src/'compact_ir_v3.v3'),q14_changed=False,normalization_changed=False)
 try:
  source=(src/'compiled_cadquery.py').read_text()
  if idx>=2:source=source.replace('shape=shape.clean()','shape=shape')
  if idx==3:
   old="shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()"
   new=old+"\n                if not shape.isValid():\n                    # Quantized periodic spline loft degeneracy: retry the same\n                    # section vertices as closed polygon wires; q/order unchanged.\n                    wires=[sketch_wire(q,z,False) for z,q in feature['sections']]\n                    shape=cq.Workplane('XY').newObject(wires).toPending().loft(ruled=feature.get('ruled',True),combine=False).val()"
   assert old in source;source=source.replace(old,new)
  source+='\n_resume_unhealed_build=build\ndef build():\n    shape=_resume_unhealed_build()\n    return shape.fix() if not shape.isValid() else shape\n'
  cp=dst/'compiled_cadquery.py';cp.write_text(source);s=runpy.run_path(str(cp))['build']()
  assert s.isValid() and s.Solids(),'REPAIRED_BREP_INVALID'
  sp=dst/'part.step';cq.exporters.export(s,str(sp));s=cq.importers.importStep(str(sp)).val();assert s.isValid() and s.Solids(),'READBACK_INVALID'
  raw=cq.importers.importStep(str(src/'raw.step')).val();m=P.compare(P.shapemesh(raw),P.shapemesh(s));m['VOLUME_ERROR']=abs(abs(raw.Volume())-abs(s.Volume()))/max(abs(raw.Volume()),1e-12)
  result.update(PASS=True,body_n=len(s.Solids()),raw_body_n=len(raw.Solids()),geometry=m,quality_gate=all(m[k]<=.02 for k in ['CD','BBOX_ERROR','CENTROID_ERROR']) and m['VOLUME_ERROR']<=.05,compiler=str(cp),step=str(sp))
 except Exception:result['error']=traceback.format_exc()
 result['action']={1:'OCCT shape healing, generated q and feature order unchanged',2:'Avoid problematic same-domain clean then OCCT healing',3:'For an invalid spline loft only, retry identical quantized section vertices as polygon wires, then OCCT healing'}[idx]
 save(dst/'REPAIR_RESULT.json',result);print(json.dumps(result),flush=True)
def audit():
 folder=O/'tank';folder.mkdir(exist_ok=True);rows=[]
 failed=json.loads((E/'reports/TANK_LABEL_BLOCKERS.json').read_text())
 for f in failed:
  pid=f['part'];d=O/'objects/tank/cad_parts'/pid;r=json.loads((d/'result.json').read_text());ir=d/'compact_ir_v3.v3';qm=d/'q14.json';parse=False;qok=False
  try:
   cid,q=P.v3['parse'](ir.read_text());meta=json.loads(qm.read_text());parse=True;qok=q==[x['q14'] for x in meta['parameters']] and all(0<=v<=16383 for v in q)
  except Exception:pass
  brep=bool(r.get('STEP_PASS'));repaired=[]
  for p in sorted((BASE/'tank'/pid).glob('attempt_*/REPAIR_RESULT.json')):repaired.append(json.loads(p.read_text()))
  passed=next((a for a in repaired if a['PASS']),None)
  row=dict(PART_ID=pid,FAILURE_STAGE='J. OTHER: RAW_VS_Q14_GEOMETRIC_QUALITY' if brep else 'G. CAD_EXEC_FAILURE: BREP_INVALID',RAW_CAD_AVAILABLE=bool(r.get('RAW_CAD_PASS')),Q14_STATUS='EXACT' if qok else 'FAIL',V3_STATUS='SERIALIZED' if ir.exists() else 'MISSING',PARSER_STATUS='PASS' if parse else 'FAIL',CAD_STATUS='PASS_WITH_QUALITY_WARNING' if brep else 'REPAIRED' if passed else 'BREP_INVALID',STEP_STATUS='PASS' if brep or passed else 'BLOCKED',TRANSFORM_STATUS='OBJECT_FRAME_AND_INVERSE_PRESENT',ERROR_MESSAGE=r['FAILURE_REASON'],RECOVERABLE='EXECUTION_READY_QUALITY_WARNING' if brep else 'REPAIRED' if passed else 'BOUNDED_ATTEMPTS_FAILED' if len(repaired)==3 else 'TARGETED_REPAIR_PENDING',REPAIR_ACTION='Keep original quality failure; separate execution pass from geometric quality' if brep else passed['action'] if passed else 'OCCT healing / same-domain fix / degenerate spline loft fallback',NEW_ATTEMPTS=len(repaired))
  rows.append(row)
 P.csvout(folder/'TANK_FAILED_LABEL_AUDIT.csv',rows);save(folder/'TANK_FAILED_LABEL_AUDIT.json',rows)
 return rows
def runpart(pid):
 for idx in [1,2,3]:
  f=BASE/'tank'/pid/f'attempt_{idx}/REPAIR_RESULT.json'
  if not f.exists():
   log=f.parent/'execution.log';log.parent.mkdir(parents=True,exist_ok=True)
   with log.open('a') as out:
    try:subprocess.run(['/usr/bin/python3',__file__,'attempt',pid,str(idx)],stdout=out,stderr=out,timeout=240,check=True)
    except Exception as e:save(f,dict(part=pid,attempt=idx,PASS=False,error=str(e),action='bounded repair process'))
  if json.loads(f.read_text())['PASS']:break
def run():
 rows=audit();pids=[r['PART_ID'] for r in rows if r['CAD_STATUS']=='BREP_INVALID']
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
  for result in pool.map(runpart,pids):pass
 rows=audit();save(V/'TANK_REPAIR_DONE.json',dict(rows=rows,completed=time.time(),new_authorization='RESUME_AND_FINISH_V1 explicitly authorizes another bounded targeted repair pass; prior artifacts retained',texture_reconstruction_out_of_scope=True));print('REPAIR_COMPLETE',flush=True)
if __name__=='__main__':
 if len(sys.argv)>1 and sys.argv[1]=='attempt':attempt(sys.argv[2],int(sys.argv[3]))
 elif len(sys.argv)>1 and sys.argv[1]=='audit':print(json.dumps(audit(),indent=2))
 elif os.environ.get('TANK_REPAIR_WORKER')=='1':run()
 else:
  env=os.environ.copy();env['TANK_REPAIR_WORKER']='1'
  with (V/'tank_repair.log').open('a') as out:p=subprocess.Popen(['/usr/bin/python3','-u',__file__],env=env,cwd=O/'code',stdout=out,stderr=out,stdin=subprocess.DEVNULL,start_new_session=True)
  save(V/'tank_repair_process.json',dict(pid=p.pid));print(p.pid)
