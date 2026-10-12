"""Only run after writing evidence-based budget_decision.json authorizing extension."""
from pathlib import Path
import json,os,subprocess,yaml,signal,time
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'
decision=json.loads((EXP/'audits/budget_decision.json').read_text());assert decision['EXTEND_AUTHORIZED_BY_METRICS']
source=decision['RESUME_STEP'];budget=decision['NEW_MAX_STEPS'];assert budget<=5000 and source in [3000,4000]
ckpt=EXP/f'runs/quick/checkpoint-{source}';assert (ckpt/'optimizer.pt').exists() and (ckpt/'scheduler.pt').exists()
# Free our evaluation contexts. Raw model tokens persist at each block boundary;
# evaluation resumes with an independent last-block replay exactness check.
manager=json.loads((EXP/'control/orchestrator_pid.json').read_text())['pid']
try:os.kill(manager,signal.SIGTERM)
except ProcessLookupError:pass
jobs=json.loads((EXP/'audits/orchestrator.json').read_text())['active'];terminated=[]
for job in jobs:
 pid=job['pid'];cmd=Path(f'/proc/{pid}/cmdline')
 if cmd.exists() and str(EXP/'launch/a2_runtime.py').encode() in cmd.read_bytes().split(b'\0'):
  os.kill(pid,signal.SIGCONT);os.kill(pid,signal.SIGTERM);terminated.append(job)
time.sleep(5)
for job in terminated:
 cmd=Path(f"/proc/{job['pid']}/cmdline")
 assert not cmd.exists() or not cmd.read_bytes(),'Evaluation process has not exited; do not start competing training'
(EXP/'audits/evaluation_boundary_pause.json').write_text(json.dumps(terminated,indent=2))
if (EXP/'control/evaluation_complete.json').exists():(EXP/'control/evaluation_complete.json').unlink()
cfg=yaml.safe_load((EXP/'configs/train.yaml').read_text());cfg.update(max_steps=budget,resume_from_checkpoint=str(ckpt))
(EXP/'configs/train_extension.yaml').write_text(yaml.safe_dump(cfg,sort_keys=False))
code=(EXP/'launch/a2_train.py').read_text()
anchor='    def save(name,obj):'
restore='''    prior=json.loads((EXP/'audits/exposure_checkpoint-RESUME_STEP.json').read_text())
    counts.update(prior['part_exposures']);block_counts.update(prior['block_exposures']);calls[0]=prior['microbatches']
    losses[:]=[json.loads(line)['last_scaled_loss'] for line in (EXP/'audits/training_steps.jsonl').read_text().splitlines()]
    started=time.time()-prior['elapsed_seconds']
'''.replace('RESUME_STEP',str(source))
code=code.replace(anchor,restore+anchor).replace("EXP/'configs/train.yaml'","EXP/'configs/train_extension.yaml'")
(EXP/'launch/a2_train_extension.py').write_text(code)
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',PYTHONUNBUFFERED='1',TOKENIZERS_PARALLELISM='false')
with (EXP/f'logs/train_extension_{source}_{budget}.log').open('w') as f:
 p=subprocess.Popen(['/usr/bin/python3','-u',str(EXP/'launch/a2_train_extension.py')],stdout=f,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,cwd=ROOT,env=env,start_new_session=True)
(EXP/'status.json').write_text(json.dumps({'state':'TRAINING_EXTENSION','pid':p.pid,'gpu':1,'resume_step':source,'max_steps':budget},indent=2))
schedule=[250,500,750,1000,1500,2000,2500,3000]+[s for s in [4000,5000] if s<=budget]
(EXP/'control/schedule.json').write_text(json.dumps(schedule))
print('EXTENSION_TRAIN_PID',p.pid)
