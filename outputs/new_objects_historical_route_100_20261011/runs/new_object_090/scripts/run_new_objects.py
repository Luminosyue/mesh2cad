import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import json,subprocess,time,concurrent.futures,hashlib,sys,queue
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs/new_objects_historical_route_100_20261011/runs/new_object_090')
H='/data/miniconda3/envs/hunyuan/bin/python';C='/data/miniconda3/envs/cadfit-env/bin/python'
def dump(p,r):p.write_text(json.dumps(r,indent=2))
rows=json.loads((O/'manifests/objects_frozen.json').read_text())
for row in rows:assert hashlib.sha256(Path(row['source_object_path']).read_bytes()).hexdigest()==row['source_object_sha256']
def emit(r):print(json.dumps(r),flush=True)
start=time.time();weight=O/'model_cache/tencent/Hunyuan3D-Part/VERIFIED.json'
emit({'stage':'WAIT_OFFICIAL_XPART_WEIGHTS','objects':len(rows)})
while not weight.exists():
 if time.time()-start>7200:raise RuntimeError('Model recovery timeout; new P3 results retained')
 time.sleep(5)
emit({'stage':'WEIGHTS_VERIFIED'})
gpu_start=time.time()
while True:
 raw=subprocess.check_output(['nvidia-smi','--query-gpu=index,memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True)
 free=[int(a[0]) for line in raw.splitlines() if len(a:=[s.strip() for s in line.split(',')])==3 and int(a[1])<1024 and int(a[2])<5]
 if len(free)>=1:break
 if time.time()-gpu_start>3600:raise RuntimeError('Waiting for a free GPU; no existing GPU task interrupted')
 time.sleep(15)
gpu_ids=free[:3];dump(O/'gpu_assignment.json',{'gpu_ids':gpu_ids,'snapshot':raw});emit({'stage':'FREE_GPUS_SELECTED','gpu_ids':gpu_ids})
gpu_queue=queue.Queue()
for gpu_id in gpu_ids:gpu_queue.put(gpu_id)
def one(item):
 slot,row=item;i=gpu_queue.get();oid=row['object_id'];d=O/'objects'/oid;env=os.environ.copy();env['HY3DGEN_MODELS']=str(O/'model_cache');env['NUMBA_CACHE_DIR']=str(O/'cache'/oid/'numba');env['TORCH_EXTENSIONS_DIR']=str(O/'cache'/oid/'torch_extensions');env['TMPDIR']=str(O/'cache'/oid/'tmp');Path(env['TMPDIR']).mkdir(parents=True,exist_ok=True)
 result={'object_id':oid,'name':row['name'],'gpu':i,'xpart_reexecuted':True}
 emit({'object':oid,'stage':'XPART_START','gpu':i})
 cmd=[H,'-B','-u',str(O/'scripts/xpart_new_objects.py'),'--source-mesh',row['canonical_path'],'--p3-dir',str(d/'p3'),'--out-dir',str(d/'xpart_parts'),'--gpu',str(i),'--seed','20261011','--batch-size','3','--octree-resolution','512']
 with (O/'logs'/(oid+'_xpart.log')).open('w') as log:
  try:p=subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=3600);result['xpart_exit_code']=p.returncode
  except subprocess.TimeoutExpired:result['xpart_exit_code']='TIMEOUT'
 gpu_queue.put(i)
 manifest=d/'xpart_parts/manifest.json'
 if result['xpart_exit_code']!=0 or not manifest.exists():
  result['status']='XPART_FAILED';dump(d/'run_status.json',result);emit(result);return result
 result['xpart_manifest']=json.loads(manifest.read_text());emit({'object':oid,'stage':'XPART_COMPLETE','parts':result['xpart_manifest']['XPART_SUCCESSFUL_PARTS']})
 # Historical search budget; jobs write only under this new run.
 sys.path.insert(0,str(O/'scripts'));import rebuild_cases
 tasks=[(oid,p.parent.name) for p in sorted((d/'xpart_parts').glob('*/complete*.obj'))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  fits=list(pool.map(lambda t:rebuild_cases.job(t,180),tasks))
 result['cad_results']=fits;result['status']='CAD_STAGE_COMPLETE';dump(d/'run_status.json',result);emit({'object':oid,'stage':'CAD_COMPLETE','generated':sum('step_valid' in f and f['step_valid'] for f in fits),'attempted':len(fits)})
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(one,enumerate(rows)))
dump(O/'generation_status.json',{'objects':results,'elapsed_seconds':time.time()-start});emit({'stage':'GENERATION_FINISHED','objects':len(results)})
