from pathlib import Path
import os,sys,json,time,subprocess
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');parts=[f'PART_{i:03d}' for i in range(9)];milestones=[10,20,30,40,60,80,100,150,200,300,400,500];start=time.time();budget=14400;trainer=None;children=[]
def read(p):return json.loads(p.read_text())
def save(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);t=p.with_suffix(p.suffix+'.tmp');t.write_text(json.dumps(x,indent=2));t.replace(p)
def spawn(script,args,gpu,log):
 env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='4')
 with (E/'logs'/log).open('w') as f:p=subprocess.Popen(['/usr/bin/python3',str(E/'launch'/script),*map(str,args)],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 children.append(p);return p
def check_budget():
 if time.time()-start>budget:raise RuntimeError('4-hour total wall budget exhausted')
def status(phase,**kw):save(E/'status.json',dict(phase=phase,elapsed_seconds=time.time()-start,trainer_pid=trainer.pid if trainer else None,**kw))
def batch(script,step,kind):
 ckpt=E/f'runs/quick/checkpoint-{step}';tag=f'checkpoint-{step}';pending=parts.copy();active=[]
 while pending or active:
  check_budget()
  for p,part,gpu in list(active):
   if p.poll() is not None:
    assert p.returncode==0,(script,part,p.returncode)
    active.remove((p,part,gpu))
  for gpu in [1,3]:
   if pending and not any(g==gpu for _,_,g in active):
    part=pending.pop(0);p=spawn(script,[ckpt,part,tag],gpu,f'{kind}_{tag}_{part}.log');active.append((p,part,gpu))
  status(kind,checkpoint=step,active=[{'part':a,'gpu':g,'pid':p.pid} for p,a,g in active],pending=pending)
  time.sleep(2)
 root=E/kind/tag;rows=[read(root/p/('summary.json' if kind=='scans' else 'result.json')) for p in parts]
 if kind=='scans':summary={'step':step,'checkpoint':str(ckpt),'errors':[r['TOKEN_ERRORS'] for r in rows],'total_tf_errors':sum(r['TOKEN_ERRORS'] for r in rows),'zero_parts':sum(r['TOKEN_ERRORS']==0 for r in rows)}
 else:summary={'step':step,'checkpoint':str(ckpt),'exact_n':sum(r['SEQUENCE_EXACT_MATCH'] for r in rows),'gate_n':sum(r['PART_GATE_PASS'] for r in rows),'cad_step_n':sum(r['CAD_EXECUTION_PASS'] and r['STEP_READBACK_PASS'] for r in rows),'tf_errors':sum(r['TOKEN_ERRORS'] for r in rows)}
 save(root/'summary.json',summary);print(kind,summary,flush=True);return summary
def ready(step):
 while not (E/f'control/checkpoint-{step}.ready').exists():
  check_budget()
  assert trainer.poll() is None,('training exited',trainer.returncode)
  status('TRAINING',target=step);time.sleep(2)
def train_until(step):(E/'control/train_until').write_text(str(step))
try:
 assert read(E/'audits/data_gate.json')['PASS']
 train_until(10);trainer=spawn('a3_train.py',[],2,'train.log');trajectory=[];first_tf=None;first_exact=None;best=None;confirmation=None;stable=False;scanned=set();index=0
 while index<len(milestones):
  step=milestones[index];ready(step)
  scan=batch('a3_scan.py',step,'scans');scanned.add(step)
  row=dict(scan,free_exact_n=None);trajectory.append(row);save(E/'trajectory.json',trajectory)
  if scan['zero_parts']==9 and first_tf is None:first_tf=step
  if (scan['zero_parts']==9 or (step==500 and scan['zero_parts']>=8)) and (first_exact is None or step==confirmation):
   # Continue only to a nearby confirmation save while first candidate decodes.
   if first_exact is None:
    options=[m for m in milestones if 50<=m-step<=100];confirmation=options[0] if options else None
    if confirmation:train_until(confirmation)
   ev=batch('a3_evaluate.py',step,'evaluations');row['free_exact_n']=ev['exact_n'];save(E/'trajectory.json',trajectory)
   rank=lambda x:(x['exact_n'],x['cad_step_n'],-x['tf_errors'],-x['step'])
   if best is None or rank(ev)>rank(best):best=ev;save(E/'best_checkpoint.json',best)
   if ev['gate_n']==9:
    if first_exact is None:
     first_exact=step;save(E/'first_exact.json',ev)
     if confirmation is None:break
    elif 50<=step-first_exact<=100:
     stable=True;break
  if first_exact is not None and confirmation is not None and step>=confirmation:break
  index+=1
  if index<len(milestones):train_until(max(milestones[index],confirmation or 0) if first_exact else milestones[index])
 (E/'control/stop_after_stable').touch()
 trainer.wait(timeout=180)
 save(E/'outcome.json',{'P1_A3_GATE':'PASS' if first_exact else 'FAIL','FIRST_9_OF_9_TF_ZERO_CHECKPOINT':first_tf,'FIRST_9_OF_9_EXACT_CHECKPOINT':first_exact,'EXACT_MEMORIZATION_STABLE':stable,'best':best,'elapsed_seconds':time.time()-start,'training_returncode':trainer.returncode})
 status('COMPLETE');print('COMPLETE',read(E/'outcome.json'),flush=True)
except Exception as exc:
 save(E/'failure.json',{'error':repr(exc),'elapsed_seconds':time.time()-start});(E/'control/stop_after_stable').touch()
 if trainer and trainer.poll() is None:
  try:trainer.wait(timeout=120)
  except subprocess.TimeoutExpired:trainer.terminate()
 for p in children:
  if p is not trainer and p.poll() is None:p.terminate()
 status('STOPPED_WITH_EVIDENCE',error=repr(exc));raise
