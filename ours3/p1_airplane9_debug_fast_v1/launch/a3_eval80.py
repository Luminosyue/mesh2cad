from pathlib import Path
import os,subprocess,time
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane9_debug_fast_v1');parts=[f'PART_{i:03d}' for i in range(9)];active=[];pending=parts.copy();gpuq=[0,1,3,4,5]
while pending or active:
 for p,g,part in list(active):
  if p.poll() is not None:print(part,p.returncode);active.remove((p,g,part))
 for g in gpuq:
  if not pending or any(x[1]==g for x in active):continue
  part=pending.pop(0);env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(g),PYTHONUNBUFFERED='1',OMP_NUM_THREADS='4',MKL_NUM_THREADS='1')
  with (E/'logs'/f'manual80_{part}.log').open('w') as f:p=subprocess.Popen(['/usr/bin/python3',str(E/'launch/a3_evaluate.py'),str(E/'runs/quick/checkpoint-80'),part,'checkpoint-80'],env=env,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
  active.append((p,g,part));print('START',part,g,p.pid)
 time.sleep(3)
print('DONE')
