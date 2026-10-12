from pathlib import Path
import os,json,time,subprocess
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');seen=set();active=[];start=time.time()
while not (E/'outcome.json').exists() and not (E/'failure.json').exists() and time.time()-start<14400:
 for p,g,tag,part in list(active):
  if p.poll() is not None:print('FINISH',tag,part,p.returncode,flush=True);active.remove((p,g,tag,part))
 s=json.loads((E/'status.json').read_text())
 if s['phase']=='evaluations':
  tag=f"checkpoint-{s['checkpoint']}"
  for gpu,prereq,part in [(0,'PART_005','PART_004'),(4,'PART_008','PART_007')]:
   if (tag,part) in seen or not (E/f'evaluations/{tag}/{prereq}/result.json').exists():continue
   seen.add((tag,part))
   if (E/f'evaluations/{tag}/{part}/result.json').exists():continue
   env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='4')
   with (E/f'logs/boost_{tag}_{part}.log').open('w') as f:p=subprocess.Popen(['/usr/bin/python3',str(E/'launch/a3_evaluate.py'),str(E/f'runs/quick/{tag}'),part,tag],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
   active.append((p,gpu,tag,part));print('START',gpu,tag,part,p.pid,flush=True)
 time.sleep(2)
for p,g,t,part in active:
 if p.poll() is None:p.terminate();p.wait()
(E/'control/boost_finished').touch()
