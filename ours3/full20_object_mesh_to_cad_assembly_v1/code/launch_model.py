import os,json,subprocess,sys,time
from pathlib import Path
R=Path('/data/home/cuiyuehan/project/mesh2cad');O=R/'ours3/full20_object_mesh_to_cad_assembly_v1';E=O/'model_v1'
PY=Path('/data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python')
gpu=sys.argv[1];names=sys.argv[2:];logs=E/'logs';logs.mkdir(parents=True,exist_ok=True)
env=os.environ.copy();env.update(CUDA_VISIBLE_DEVICES=gpu,OMP_NUM_THREADS='4',OPENBLAS_NUM_THREADS='4',MKL_NUM_THREADS='4',TOKENIZERS_PARALLELISM='false',DISABLE_VERSION_CHECK='1',HF_DATASETS_CACHE='/var/tmp/cuiyuehan_full20_p1_v3_20260925/hf_cache',TRITON_CACHE_DIR='/var/tmp/cuiyuehan_full20_p1_v3_20260925/triton_cache')
if os.environ.get('FULL20_WORKER')!='1':
 used=int(subprocess.check_output(['nvidia-smi',f'--id={gpu}','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).strip());assert used<1000,f'GPU {gpu} now occupied: {used} MiB'
 env['FULL20_WORKER']='1'
 with (logs/f'queue_gpu{gpu}.log').open('a') as log:
  p=subprocess.Popen([str(PY),'-u',__file__,gpu,*names],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 (logs/f'queue_gpu{gpu}.json').write_text(json.dumps(dict(pid=p.pid,gpu=gpu,objects=names,started=time.time()),indent=2));print(p.pid)
else:
 for name in names:
  with (logs/f'{name}_train.log').open('a') as log:
   p=subprocess.Popen([str(PY),'-u',str(O/'code/train_model.py'),name],cwd=R,env=env,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
   (logs/f'{name}_process.json').write_text(json.dumps(dict(pid=p.pid,gpu=gpu,object=name,started=time.time()),indent=2));code=p.wait()
  print(json.dumps(dict(object=name,exit_code=code,time=time.time())),flush=True)
  if code!=0:break
