import os,json,time,sys,subprocess,hashlib,csv,shutil
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
names=json.loads((E/'reports/EXPERIMENT_CONTRACT.json').read_text())['priority_complete_objects']+['tank']
manifest=json.loads((O/'manifests/FULL20_OBJECT_MANIFEST.json').read_text())
blockers=json.loads((E/'reports/BLOCKERS.json').read_text())
def dump(p,x):
 q=p.with_suffix('.tmp');q.write_text(json.dumps(x,indent=2)+'\n');q.replace(p)
if os.environ.get('FULL20_GATE_WORKER')!='1':
 env=os.environ.copy();env['FULL20_GATE_WORKER']='1'
 with (E/'logs/generated_gate_watch.log').open('a') as f:p=subprocess.Popen([sys.executable,'-u',__file__],env=env,cwd=R,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
 dump(E/'logs/generated_gate_watch_process.json',dict(pid=p.pid));print(p.pid);sys.exit()
while True:
 status=[]
 for name in names:
  run=E/'runs'/name
  for folder in sorted(run.glob('free_*')):
   if not (folder/'SUMMARY.json').exists():continue
   result=E/'generated'/name/folder.name/'OBJECT_GATE.json'
   if result.exists():continue
   with (E/'logs'/f'{name}_{folder.name}_cad.log').open('a') as f:
    try:subprocess.run(['xvfb-run','-a','/usr/bin/python3',str(O/'code/generated_gate.py'),'attempt',str(folder)],stdout=f,stderr=f,timeout=18000,check=True)
    except Exception as error:
     result.parent.mkdir(parents=True,exist_ok=True);dump(result,dict(object=name,FULL_MODEL_ASSEMBLY_PASS=False,worker_error=str(error)))
  s=dict(object=name,training_status='QUEUED',free_exact_n=0,natural_eos_n=0,full_model_assembly_pass=False)
  for filename,key in [('TRAIN_STATUS.json','train'),('LATEST_CHECKPOINT.json','checkpoint'),('TRAIN_DONE.json','done'),('TRAIN_FAILED.json','failure')]:
   if (run/filename).exists():
    try:s[key]=json.loads((run/filename).read_text())
    except Exception:pass
  s['training_status']='FAILED' if 'failure' in s else 'DONE' if 'done' in s else 'TRAINING' if 'train' in s else 'QUEUED'
  gs=sorted((E/'generated'/name).glob('free_*/OBJECT_GATE.json'),key=lambda p:p.stat().st_mtime)
  if gs:
   g=json.loads(gs[-1].read_text());s.update(free_exact_n=g.get('free_exact_n',0),natural_eos_n=g.get('natural_eos_n',0),full_model_assembly_pass=g.get('FULL_MODEL_ASSEMBLY_PASS',False),cad_result=str(gs[-1]))
  status.append(s)
 for path,digest in json.loads((E/'reports/FROZEN_PART029_HASHES.json').read_text()).items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==digest
 success_n=sum(s['full_model_assembly_pass'] for s in status)
 dump(E/'reports/MODEL_LIVE_STATUS.json',dict(time=time.time(),objects=status,model_full_object_success_n=success_n,canonical_controls_are_not_model_success=True,frozen_part029_unchanged=True,full20_blocked_missing_inputs=50))
 (E/'tables').mkdir(exist_ok=True)
 table=[]
 for original in manifest:
  name=original['OBJECT_ID'];s=next((x for x in status if x['object']==name),{});bad=[x for x in blockers if x['object']==name and x['status'].startswith('BLOCKED')]
  table.append(dict(OBJECT_ID=name,PART_N=original['PART_N'],TRAIN_STATUS=s.get('training_status','NOT_LAUNCHED'),TRAIN_STEP=s.get('train',{}).get('step',0),FREE_EXACT_N=s.get('free_exact_n',0),NATURAL_EOS_N=s.get('natural_eos_n',0),FULL_MODEL_ASSEMBLY_PASS=s.get('full_model_assembly_pass',False),BLOCKED_PART_N=len(bad),FROZEN_REUSE_N=int(name=='tank'),CHECKPOINT=s.get('checkpoint',{}).get('path','')))
 with (E/'tables/FULL20_OBJECT_MODEL_RESULTS.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
 progress='Active objective: P1 full-sequence training + empty-target free generation\n\nFULL MODEL OBJECTS:\ncompleted '+str(success_n)+'/20\n\nEXPECTED PARTS:\n304 (254 X-Part meshes available; 50 missing inputs explicitly blocked)\n\nCANONICAL CONTROLS:\n7 complete objects; never counted as new model success.\n\nCURRENT:\n'+'\n'.join(s['object']+': '+s['training_status']+'; step='+str(s.get('train',{}).get('step',0))+'; free_exact='+str(s['free_exact_n'])+'; model_assembly='+str(s['full_model_assembly_pass']) for s in status)+'\n\nFAILED/BLOCKED PARTS:\n'+'\n'.join(x['object']+'/'+x['part']+': '+x.get('reason',x['status']) for x in blockers)+'\n'
 (E/'reports/PROGRESS.md').write_text(progress)
 old=O/'reports/PROGRESS.md';backup=O/'reports/CANONICAL_DATA_PREPARATION_PROGRESS.md'
 if not backup.exists() and old.exists():shutil.copy2(old,backup)
 old.write_text(progress)
 # Continue the other complete objects if a prior queue worker exits on a
 # single-object failure. Never restart an object with existing train results.
 queued=[s['object'] for s in status if s['training_status']=='QUEUED' and s['object']!='tank']
 qrecord=E/'logs/queue_gpu1.json'
 if queued and qrecord.exists():
  qpid=json.loads(qrecord.read_text())['pid'];cmd=Path('/proc')/str(qpid)/'cmdline'
  alive=cmd.exists() and b'launch_model.py' in cmd.read_bytes()
  if not alive:
   try:subprocess.run(['/usr/bin/python3',str(O/'code/launch_model.py'),'1',*queued],check=True,timeout=30)
   except Exception as error:print('QUEUE_RECOVERY_DEFERRED',str(error),flush=True)
 if all(s['training_status'] in ['DONE','FAILED'] for s in status):break
 time.sleep(30)
