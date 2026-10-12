from pathlib import Path
import os,sys,json,time,subprocess
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');OLD=E.parent/'p1_airplane3_exact_overfit_v1';parts=['PART_000','PART_001','PART_005'];start=json.loads((E/'control/run_clock.json').read_text())['start'];eval_used=0;active=[];errors=[]
def read(p):return json.loads(p.read_text())
def save(p,x):
 temp=p.with_suffix('.tmp');temp.write_text(json.dumps(x,indent=2));temp.replace(p)
def spawn(cmd,gpu,log):
 env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=str(gpu);env['PYTHONUNBUFFERED']='1'
 f=(E/'logs'/log).open('w');p=subprocess.Popen(['/usr/bin/python3',str(E/'launch'/cmd[0]),*cmd[1:]],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True);f.close();return p
def summarize(tag):
 rows=[read(E/f'evaluations/{tag}/{p}/result.json') for p in parts if (E/f'evaluations/{tag}/{p}/result.json').exists()]
 v={'tag':tag,'complete_case_n':len(rows),'exact_n':sum(r['SEQUENCE_EXACT_MATCH'] for r in rows),'cad_step_readback_n':sum(r['CAD_EXECUTION_PASS'] and r['STEP_READBACK_PASS'] for r in rows),'TF_errors':sum(r['TOKEN_ERRORS'] for r in rows),'gate_n':sum(r['PART_GATE_PASS'] for r in rows),'checkpoint':rows[0]['checkpoint'] if rows else None}
 if len(rows)==3:save(E/f'evaluations/{tag}/summary.json',v)
 allv=[read(p) for p in (E/'evaluations').glob('*/summary.json')];complete=[r for r in allv if r['complete_case_n']==3]
 if complete:save(E/'best_checkpoint.json',max(complete,key=lambda r:(r['exact_n'],r['cad_step_readback_n'],-r['TF_errors'])))
 return v
def status(phase):save(E/'status.json',{'phase':phase,'elapsed_seconds':time.time()-start,'active':[{'pid':j['p'].pid,'gpu':j['gpu'],'tag':j['tag'],'part':j['part']} for j in active],'errors':errors})
def poll():
 for j in list(active):
  code=j['p'].poll()
  if code is None:continue
  active.remove(j)
  if code:errors.append({'tag':j['tag'],'part':j['part'],'exit_code':code})
  v=summarize(j['tag']);print('EVAL_FINISHED',j['tag'],j['part'],code,v,flush=True)
def enqueue(tag,ckpt,p,gpu):
 proc=spawn(['fast_evaluate.py',str(ckpt),p,tag],gpu,f'{tag}_{p}.log');active.append({'p':proc,'gpu':gpu,'tag':tag,'part':p,'started':time.time()});print('EVAL_STARTED',tag,p,gpu,proc.pid,flush=True)
assert read(E/'diagnostics/path_gate.json')['PASS']
# Corrected baseline must finish before any additional optimizer update.
pending=[(p,g) for p,g in [('PART_001',1),('PART_005',3),('PART_000',1)] if not (E/f'evaluations/baseline_fixed/{p}/result.json').exists()];eval_start=time.time()
while pending or active:
 poll()
 for part,gpu in list(pending):
  if not any(j['gpu']==gpu for j in active):enqueue('baseline_fixed',OLD/'runs/quick/checkpoint-2000',part,gpu);pending.remove((part,gpu))
 status('CORRECTED_BASELINE')
 if time.time()-start>3600:errors.append({'reason':'free decode budget exhausted in baseline'});break
 time.sleep(2)
eval_used+=time.time()-eval_start
if active:
 for j in active:j['p'].terminate()
 for j in active:j['p'].wait()
 active=[]
if errors:status('STOPPED_WITH_EVIDENCE');sys.exit(2)
baseline=summarize('baseline_fixed')
if baseline['gate_n']==3:status('PASS_BASELINE');sys.exit(0)
trainer=spawn(['fast_train.py'],1,'train.log');print('TRAIN_STARTED',trainer.pid,flush=True);seen=set();pending=[];eval_start=time.time()
while trainer.poll() is None or active or pending:
 poll()
 for ready in sorted((E/'control').glob('checkpoint-*.ready'),key=lambda p:int(p.name.split('-')[1].split('.')[0])):
  step=int(ready.name.split('-')[1].split('.')[0]);tag=f'checkpoint-{step}'
  if step not in seen:
   seen.add(step);pending.extend((tag,E/f'runs/quick/checkpoint-{step}',p) for p in parts)
 for tag,ckpt,part in list(pending):
  gpu=3 if not any(j['gpu']==3 for j in active) else (1 if trainer.poll() is not None and not any(j['gpu']==1 for j in active) else None)
  if gpu is None:break
  enqueue(tag,ckpt,part,gpu);pending.remove((tag,ckpt,part))
 status('TRAIN_AND_EVALUATE')
 if (E/'best_checkpoint.json').exists() and read(E/'best_checkpoint.json')['gate_n']==3:
  (E/'control/stop_after_stable').touch()
  # Already started jobs finish; skip further candidates after a strict success.
  pending=[]
 if time.time()-start>3600:
  errors.append({'reason':'60 minute full evaluation wall budget exhausted','pending':[(t,p) for t,c,p in pending]});break
 time.sleep(2)
if trainer.poll() is None:
 (E/'control/stop_after_stable').touch()
 trainer.wait(timeout=120)
for j in active:j['p'].terminate()
for j in active:j['p'].wait()
active=[]
if trainer.returncode:errors.append({'training_exit_code':trainer.returncode})
status('COMPLETE' if not errors else 'STOPPED_WITH_EVIDENCE')
print('FAST_FINISHED',read(E/'best_checkpoint.json'),errors,flush=True)
