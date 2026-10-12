from pathlib import Path
import os,sys,json,time,subprocess,traceback,signal
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'
PARTS=['PART_000','PART_001','PART_005'];STEPS=[250,500,750,1000,1500,2000,2500,3000]
if (EXP/'control/schedule.json').exists():STEPS=json.loads((EXP/'control/schedule.json').read_text())
def save(path,data):
 t=path.with_name(path.name+'.tmp');t.write_text(json.dumps(data,indent=2));t.replace(path)
def alive(pid):
 try:
  os.kill(pid,0)
  return Path(f'/proc/{pid}/stat').read_text().split()[2]!='Z'
 except (ProcessLookupError,FileNotFoundError):return False
def evaluation_alive(pid,step,part):
 try:
  argv=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
  return alive(pid) and str(EXP/'launch/a2_runtime.py').encode() in argv and str(EXP/f'runs/quick/checkpoint-{step}').encode() in argv and part.encode() in argv
 except FileNotFoundError:return False
def main():
 active={};attempts={};job_gpus={};trainpid=json.loads((EXP/'status.json').read_text())['pid']
 class Adopted:
  def __init__(self,pid,step,part):self.pid=pid;self.step=step;self.part=part;self.returncode=None
  def poll(self):
   if evaluation_alive(self.pid,self.step,self.part):return None
   self.returncode='adopted-process-exited';return self.returncode
 if (EXP/'audits/orchestrator.json').exists():
  for job in json.loads((EXP/'audits/orchestrator.json').read_text())['active']:
   if evaluation_alive(job['pid'],job['step'],job['part']):
    key=(job['step'],job['part']);active[key]=(Adopted(job['pid'],job['step'],job['part']),open(os.devnull,'w'));attempts[key]=1;job_gpus[key]=str(job.get('gpu','1'))
 save(EXP/'control/orchestrator_pid.json',{'pid':os.getpid()})
 while True:
  for key,(p,log) in list(active.items()):
   if p.poll() is not None:
    log.close();print('FINISHED',key,'exit',p.returncode,flush=True);del active[key];job_gpus.pop(key,None)
  ready=[s for s in STEPS if (EXP/f'control/checkpoint-{s}.ready').exists()]
  summaries=[]
  for s in ready:
   rows=[]
   for part in PARTS:
    path=EXP/f'evaluations/checkpoint-{s}/{part}/result.json'
    if path.exists():rows.append(json.loads(path.read_text()))
   if len(rows)==3:
    summary={'checkpoint':f'checkpoint-{s}','step':s,'TRAIN_CASE_N':3,'SEQUENCE_EXACT_N':sum(r['SEQUENCE_EXACT_MATCH'] for r in rows),'PART_GATE_PASS_N':sum(r['PART_GATE_PASS'] for r in rows),'MEAN_TOKEN_ACC':sum(r['TOKEN_ACC_TEACHER_FORCED'] for r in rows)/3,'MIN_TOKEN_ACC':min(r['TOKEN_ACC_TEACHER_FORCED'] for r in rows),'EOS_ACC_ALL':all(r['EOS_ACC']==1 for r in rows),'P1_A2_GATE':'PASS' if all(r['PART_GATE_PASS'] for r in rows) else 'FAIL'}
    save(EXP/f'evaluations/checkpoint-{s}/summary.json',summary);summaries.append(summary)
  stable=next(((a,b) for a,b in zip(summaries,summaries[1:]) if a['P1_A2_GATE']==b['P1_A2_GATE']=='PASS' and STEPS.index(b['step'])==STEPS.index(a['step'])+1),None)
  if stable:save(EXP/'control/stop_after_stable',{'first':stable[0],'confirmation':stable[1]})
  try:train_argv=Path(f'/proc/{trainpid}/cmdline').read_bytes().split(b'\0')
  except FileNotFoundError:train_argv=[]
  training=alive(trainpid) and any(str(EXP/'launch'/name).encode() in train_argv for name in ['a2_train.py','a2_train_extension.py'])
  # Measured inference footprint is ~3.7 GiB; four plus 24 GiB training fit GPU 1.
  capacity=4 if training else 6
  cap={}
  if (EXP/'control/workers.json').exists():
   cap=json.loads((EXP/'control/workers.json').read_text());capacity=cap['training' if training else 'finished']
  pool=cap.get('gpu_pool',['1']);per_gpu=cap.get('workers_per_gpu',capacity)
  restored=json.loads((EXP/'audits/gpu_lease_restored.json').read_text()) if (EXP/'audits/gpu_lease_restored.json').exists() else []
  pool=[g for g in pool if all(str(r['gpu'])!=g for r in restored)]
  for key,(p,log) in active.items():
   try:
    if evaluation_alive(p.pid,key[0],key[1]):os.kill(p.pid,signal.SIGSTOP if training and cap.get('pause_during_training') else signal.SIGCONT)
   except ProcessLookupError:pass
  pending=[(s,p) for s in ready for p in PARTS if not (EXP/f'evaluations/checkpoint-{s}/{p}/result.json').exists() and (s,p) not in active and attempts.get((s,p),0)<2]
  pending.sort(key=lambda key:(-key[0],PARTS.index(key[1])))
  for key in pending[:max(0,capacity-len(active))]:
   s,part=key;attempts[key]=attempts.get(key,0)+1
   counts={g:sum(v==g for v in job_gpus.values()) for g in pool};gpu=min(pool,key=lambda g:counts[g])
   if counts[gpu]>=per_gpu:break
   env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=gpu,PYTHONUNBUFFERED='1',TOKENIZERS_PARALLELISM='false')
   log=(EXP/f'logs/eval_{s}_{part}_attempt{attempts[key]}_gpu{gpu}_{int(time.time())}.log').open('w')
   p=subprocess.Popen(['/usr/bin/python3','-u',str(EXP/'launch/a2_runtime.py'),'evaluate',str(EXP/f'runs/quick/checkpoint-{s}'),part],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,cwd=ROOT,env=env)
   active[key]=(p,log);job_gpus[key]=gpu;print('STARTED',key,'pid',p.pid,'gpu',gpu,flush=True)
  state={'training_alive':training,'train_pid':trainpid,'ready':ready,'summaries':summaries,'active':[{'step':k[0],'part':k[1],'pid':v[0].pid,'gpu':job_gpus[k]} for k,v in active.items()],'errors':[{'step':k[0],'part':k[1]} for k,n in attempts.items() if n>=2 and k not in active and not (EXP/f'evaluations/checkpoint-{k[0]}/{k[1]}/result.json').exists()],'stable':stable}
  save(EXP/'audits/orchestrator.json',state)
  status=json.loads((EXP/'status.json').read_text());status['state']='TRAINING' if training else 'EVALUATING';status['evaluation_gpus']=pool;save(EXP/'status.json',status)
  if not training and not pending and not state['errors'] and (EXP/'audits/gpu_lease_released.json').exists():
   for g in pool:
    if g in ['0','4','5'] and all(gpu!=g for gpu in job_gpus.values()):
     subprocess.run(['/usr/bin/python3',str(EXP/'launch/a2_gpu_lease.py'),'restore',g],check=True)
  if not training and not active and not pending:
   save(EXP/'control/evaluation_complete.json',state);status['state']='EVALUATED_PENDING_REPORT';save(EXP/'status.json',status);print('ALL_AVAILABLE_CHECKPOINTS_EVALUATED',flush=True);return
  time.sleep(10)
if __name__=='__main__':main()
