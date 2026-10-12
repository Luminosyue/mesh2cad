import os,sys,json,subprocess,time
from pathlib import Path
root=Path(__file__).resolve().parent
assert (root/'MANIFEST.json').exists()
smoke='--smoke' in sys.argv
jobs=[]
for method,gpu in [('cadrille',1),('cadrecode',3)]:
    env=os.environ.copy()
    env.update(CUDA_VISIBLE_DEVICES=str(gpu),OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4',TOKENIZERS_PARALLELISM='false',HF_HUB_OFFLINE='1',PARTS_BATCH_SIZE='12')
    if smoke:env['SMOKE']='1'
    log=root/f'{method}_{"smoke" if smoke else "full"}.log'
    with log.open('a') as f:
        p=subprocess.Popen(['/data/miniconda3/envs/cadrille/bin/python','-u',str(root/'run_inference.py'),method],cwd=root,env=env,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
    jobs.append(dict(method=method,gpu=gpu,pid=p.pid,log=str(log),started=time.time()))
file=root/('SMOKE_PROCESSES.json' if smoke else 'PROCESSES.json')
file.write_text(json.dumps(jobs,indent=2));print(file.read_text())
