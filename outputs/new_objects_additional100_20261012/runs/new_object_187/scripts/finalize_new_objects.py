from pathlib import Path
import subprocess,time,sys
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_additional100_20261012/runs/new_object_187')
start=time.time()
while not (O/'generation_status.json').exists():
 if time.time()-start>3600:raise RuntimeError('Generation not complete; retaining results')
 time.sleep(5)
for script in ['evaluate_new_objects.py','visualize_new_objects.py','package_new_objects.py']:
 print('START',script,flush=True)
 with (O/'logs'/(script+'.log')).open('w') as log:
  p=subprocess.Popen([sys.executable,'-B','-u',str(O/'scripts'/script)],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  for line in p.stdout:log.write(line);log.flush();print(line,end='',flush=True)
  rc=p.wait()
  if rc:raise RuntimeError(f'{script} failed: {rc}')
print('DELIVERY_READY',flush=True)
