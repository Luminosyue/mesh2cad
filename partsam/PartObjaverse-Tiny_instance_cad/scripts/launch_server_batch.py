from pathlib import Path
import os,subprocess,json
root=Path(__file__).resolve().parent.parent
env={**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1'}
with (root/'batch_run.log').open('a') as log:
    proc=subprocess.Popen(['/usr/bin/python3','-u',str(root/'scripts/server_batch_cad.py'),'--workers','24'],
                          stdout=log,stderr=subprocess.STDOUT,stdin=subprocess.DEVNULL,
                          cwd=root,env=env,start_new_session=True)
(root/'batch_pid.json').write_text(json.dumps({'pid':proc.pid,'output':str(root)}))
print('Started batch PID',proc.pid)
