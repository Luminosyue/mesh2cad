from pathlib import Path
import os,subprocess,json
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');EXP=ROOT/'ours3/p1_airplane3_exact_overfit_v1'
assert not (EXP/'status.json').exists()
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES='1',PYTHONUNBUFFERED='1',TOKENIZERS_PARALLELISM='false')
with (EXP/'logs/train.log').open('w') as log:
 p=subprocess.Popen(['/usr/bin/python3','-u',str(EXP/'launch/a2_train.py')],stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,cwd=ROOT,env=env,start_new_session=True)
(EXP/'status.json').write_text(json.dumps({'state':'TRAINING','pid':p.pid,'gpu':1},indent=2));print('TRAIN_PID',p.pid)
