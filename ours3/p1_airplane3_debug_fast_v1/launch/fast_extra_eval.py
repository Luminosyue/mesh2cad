from pathlib import Path
import subprocess,json,time,os
E=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/p1_airplane3_debug_fast_v1');started=time.time();child=None
try:
 for step in [60,150]:
  ready=E/f'control/checkpoint-{step}.ready'
  while not ready.exists():
   status=json.loads((E/'status.json').read_text())
   if status['phase'] in ['COMPLETE','STOPPED_WITH_EVIDENCE'] or time.time()-started>3000:raise RuntimeError('Training ended without scheduled checkpoint or evaluation budget elapsed')
   time.sleep(2)
  env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='5';env['PYTHONUNBUFFERED']='1'
  with (E/f'logs/extra_checkpoint-{step}_PART_005.log').open('w') as log:
   child=subprocess.Popen(['/usr/bin/python3',str(E/'launch/fast_evaluate.py'),str(E/f'runs/quick/checkpoint-{step}'),'PART_005',f'checkpoint-{step}'],env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
  (E/'control/extra_eval_active.json').write_text(json.dumps({'pid':child.pid,'step':step,'gpu':5}))
  code=child.wait(timeout=max(1,3300-(time.time()-started)));assert code==0,code
finally:
 if child and child.poll() is None:child.terminate();child.wait(timeout=30)
 subprocess.run(['/usr/bin/python3',str(E/'launch/fast_gpu_lease.py'),'restore'],check=True)
