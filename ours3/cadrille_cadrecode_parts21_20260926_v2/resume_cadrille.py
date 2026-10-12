import os,subprocess,json,time
from pathlib import Path
root=Path(__file__).resolve().parent
jobs=[]
for shard,gpu in [(0,1),(1,3)]:
    env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',PARTS_BATCH_SIZE='12')
    with (root/f'cadrille_resume_{shard}.log').open('a') as f:
        p=subprocess.Popen(['/data/miniconda3/envs/cadrille/bin/python','-u',str(root/'run_inference.py'),'cadrille',str(shard),'2'],cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    jobs.append(dict(pid=p.pid,method='cadrille',shard=shard,gpu=gpu,started=time.time()))
(root/'CADRILLE_RESUME_PROCESSES.json').write_text(json.dumps(jobs,indent=2));print(json.dumps(jobs))
