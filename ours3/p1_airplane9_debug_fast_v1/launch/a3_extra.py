from pathlib import Path
import os,sys,json,time,subprocess
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');start=time.time();leased=False;seen=set();active=[]
def lease(mode):subprocess.run(['/usr/bin/python3',str(E/'launch/a3_gpu_lease.py'),mode],check=True)
try:
 while not (E/'outcome.json').exists() and not (E/'failure.json').exists() and time.time()-start<14400:
  for p,gpu,tag,part in list(active):
   if p.poll() is not None:
    print('EXTRA_DONE',gpu,tag,part,p.returncode,flush=True);active.remove((p,gpu,tag,part))
    assert p.returncode==0
  status=json.loads((E/'status.json').read_text())
  if status['phase']=='evaluations':
   if not leased:lease('release');leased=True
   step=status['checkpoint'];tag=f'checkpoint-{step}'
   for gpu,queue in [(0,['PART_005']), (4,['PART_008']), (5,['PART_003','PART_006'])]:
    if any(g==gpu for p,g,t,part in active):continue
    for part in queue:
     key=(tag,part)
     if key in seen or (E/f'evaluations/{tag}/{part}/result.json').exists():continue
     seen.add(key);env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='4')
     with (E/f'logs/extra_{tag}_{part}.log').open('w') as f:p=subprocess.Popen(['/usr/bin/python3',str(E/'launch/a3_evaluate.py'),str(E/f'runs/quick/{tag}'),part,tag],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
     active.append((p,gpu,tag,part));print('EXTRA_START',gpu,tag,part,p.pid,flush=True);break
  time.sleep(2)
finally:
 for p,g,t,part in active:
  if p.poll() is None:p.terminate()
 for p,g,t,part in active:
  try:p.wait(timeout=60)
  except subprocess.TimeoutExpired:p.kill();p.wait()
 if leased:lease('restore')
 (E/'control/extra_finished').touch()
