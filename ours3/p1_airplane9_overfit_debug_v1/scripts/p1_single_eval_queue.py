from pathlib import Path
import os,json,time,subprocess
root=Path('/data/home/cuiyuehan/project/mesh2cad');debug=root/'ours3/p1_airplane9_overfit_debug_v1';single=root/'ours3/p1_single_airplane_part_overfit_v1'
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='6',PYTHONUNBUFFERED='1')
for step in [100,200,500,1000,2000]:
 ckpt=single/f'runs/quick/checkpoint-{step}';out=debug/f'single_checks/checkpoint-{step}'
 deadline=time.time()+3600
 while not (ckpt/'trainer_state.json').exists():
  if time.time()>deadline:raise RuntimeError('Checkpoint wait timed out: '+str(ckpt))
  time.sleep(10)
 with (debug/f'logs/single_{step}.log').open('w') as log:
  print('EVALUATING',step,flush=True)
  p=subprocess.run(['/usr/bin/python3','-u',str(debug/'scripts/p1_evaluate_debug.py'),'--checkpoint',str(ckpt),'--out',str(out),'--teacher'],stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,env=env)
 if p.returncode:raise RuntimeError(f'Evaluation {step} exited {p.returncode}')
 result=json.loads((out/'single_case_decode_diagnosis.json').read_text());print('DONE',step,json.dumps({k:v for k,v in result.items() if k!='geometry_metrics'}),flush=True)
print('ALL_SINGLE_CHECKPOINTS_DONE',flush=True)
