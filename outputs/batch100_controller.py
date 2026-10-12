import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
from pathlib import Path
import json,csv,hashlib,shutil,subprocess,time,concurrent.futures,threading,sys,traceback,fcntl,html
import numpy as np,trimesh
BASE=Path('/data/home/cuiyuehan/project/mesh2cad')
OLD=BASE/'outputs/new_objects_historical_route_20261011'
B=BASE/'outputs/new_objects_historical_route_100_20261011'
H='/data/miniconda3/envs/hunyuan/bin/python';C='/data/miniconda3/envs/cadfit-env/bin/python'
lock=threading.Lock()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_suffix(p.suffix+'.tmp');tmp.write_text(json.dumps(v,indent=2));tmp.replace(p)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,log,timeout=7200,env=None):
 with log.open('a') as f:
  p=subprocess.Popen(cmd,stdout=f,stderr=subprocess.STDOUT,env=env,start_new_session=True)
  try:rc=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   import signal
   os.killpg(p.pid,signal.SIGKILL);p.wait();raise RuntimeError('TIMEOUT '+str(cmd[:3]))
  if rc:raise RuntimeError('EXIT '+str(rc)+' '+str(log))
def status(row,stage,**extra):
 with lock:
  dump(B/'status'/f"{row['object_id']}.json",dict(object_id=row['object_id'],name=row['name'],stage=stage,time=time.time(),**extra))
  refresh()
 print(json.dumps({'object':row['object_id'],'stage':stage,**extra}),flush=True)
def refresh():
 states=[json.loads(p.read_text()) for p in sorted((B/'status').glob('*.json'))]
 completed=[r for r in states if r['stage']=='COMPLETE']
 report={'target_objects':100,'carried_completed_objects':3,'new_target':97,'new_completed':len(completed),'total_completed':3+len(completed),'new_failed':sum(r['stage']=='FAILED' for r in states),'objects':states,'updated':time.time()}
 initial=json.loads((OLD/'summary.json').read_text())
 for k in ['p3_part_n','cad_valid_n','strict_original_n','strict_completed_n']:report[k]=initial[k]+sum(r.get(k,0) for r in completed)
 dump(B/'progress.json',report)
 page='<meta charset="utf-8"><meta http-equiv="refresh" content="60"><title>100 个新物体生成进度</title><style>body{font:17px system-ui;max-width:1400px;margin:40px auto}td,th{padding:10px;border-bottom:1px solid #ddd}table{border-collapse:collapse}</style><h1>新数据扩展到 100 个物体</h1><p>已完成 %d / 100；新增失败 %d。已完成表示生成和评测结束，不表示全部零件严格合格。</p><p>沿用首批 3 个，再新增 97 个。P3 → X-Part → CadQuery；原始网格与补全网格分别评测。</p><table><tr><th>物体</th><th>阶段</th><th>有效 CAD</th><th>原始严格合格</th><th>补全严格合格</th></tr>'%(report['total_completed'],report['new_failed'])
 for r in states:
  oid=r['object_id'];link='runs/'+oid+'/visualizations/index.html'
  page+='<tr><td>'+('<a href="'+link+'">'+html.escape(r['name'])+'</a>' if r['stage']=='COMPLETE' else html.escape(r['name']))+'</td><td>'+r['stage']+'</td><td>'+str(r.get('cad_valid_n','—'))+'</td><td>'+str(r.get('strict_original_n','—'))+'</td><td>'+str(r.get('strict_completed_n','—'))+'</td></tr>'
 (B/'index.html').write_text(page+'</table>',encoding='utf-8')
def prepare():
 for n in ['status','logs','runs','manifests']:(B/n).mkdir(parents=True,exist_ok=True)
 if (B/'manifests/new97.json').exists():return json.loads((B/'manifests/new97.json').read_text())
 prev=json.loads((OLD/'manifests/objects_frozen.json').read_text());excluded={r['source_object_sha256'] for r in prev}
 historical=json.loads((BASE/'outputs/p3_high_detail_mesh2cad_factory_v1_smoke20/manifests/objects_frozen.json').read_text())
 for r in historical:excluded.add(r['source_object_sha256'])
 for r in csv.DictReader((BASE/'ours3/full20_object_mesh_to_cad_assembly_v1/manifests/FULL20_OBJECT_MANIFEST.csv').open()):
  p=Path(r['FULL_MESH_PATH'])
  if p.exists():excluded.add(sha(p))
 choices=[];rejected=[]
 # Fixed hash ordering avoids cherry-picking quality and alphabetical category bias.
 sources=sorted((BASE/'ours3/meshes').glob('*.obj'),key=lambda p:hashlib.sha256(('20261011:'+p.name).encode()).hexdigest())
 for p in sources:
  h=sha(p)
  if h in excluded:continue
  try:
   m=trimesh.load(p,force='mesh',process=True)
   if len(m.faces)<10 or not np.isfinite(m.vertices).all() or m.area<=0 or max(m.extents)<=1e-10:raise ValueError('Degenerate source')
   if len(m.faces)>1500000:raise ValueError('Over 1.5M source faces; bounded pilot resource limit')
   oid=f'new_object_{len(choices)+3:03d}';R=B/'runs'/oid;d=R/'objects'/oid
   for name in ['source','p3','assembly','xpart_parts']:(d/name).mkdir(parents=True,exist_ok=True)
   for name in ['scripts','config','manifests','logs','cache','visualizations']:(R/name).mkdir(parents=True,exist_ok=True)
   center=m.bounds.mean(0);scale=1/float(max(m.extents));T=np.eye(4);T[:3,:3]*=scale;T[:3,3]=-center*scale;m.apply_transform(T);m.export(d/'source/object_canonical.ply')
   row=dict(object_id=oid,name=p.stem,source_object_path=str(p),source_object_sha256=h,canonical_path=str(d/'source/object_canonical.ply'),object_transform=T.tolist(),inverse_object_transform=np.linalg.inv(T).tolist(),face_count=len(m.faces),new_vs_previous_two_20_object_batches=True,new_vs_first_three=True,source_dataset='existing_ours3_mesh_snapshot')
   dump(d/'source/provenance.json',row);dump(R/'manifests/objects_frozen.json',[row]);shutil.copy2(OLD/'config/smoke20.json',R/'config/smoke20.json')
   for folder in ['runtime','model_cache']:(R/folder).symlink_to(OLD/folder,target_is_directory=True)
   for src in (OLD/'scripts').glob('*.py'):
    text=src.read_text().replace(str(OLD),str(R))
    if src.name=='p3_smoke_segment.py':text=text.replace("os.environ['CUDA_VISIBLE_DEVICES']='3'","os.environ['CUDA_VISIBLE_DEVICES']=os.environ['BATCH_GPU']")
    if src.name=='evaluate_new_objects.py':text=text.replace("str(O.parent/'part_cad_fitting_v2_native/scripts')",repr(str(BASE/'outputs/part_cad_fitting_v2_native/scripts')))
    if src.name=='visualize_new_objects.py':
     text=text.replace('搅拌机、咖啡机、黑色餐椅。3 个源文件哈希均已排除此前两批 20 物体','本物体源文件哈希已排除旧两批及首批 3 个物体')
    (R/'scripts'/src.name).write_text(text)
   choices.append(row);excluded.add(h);dump(B/'manifests/preparation_progress.json',{'selected':len(choices),'last':oid})
  except Exception as e:rejected.append({'path':str(p),'error':str(e)});continue
  if len(choices)==97:break
 assert len(choices)==97,('Not enough unique valid objects',len(choices))
 dump(B/'manifests/new97.json',choices);dump(B/'manifests/carried3.json',prev);dump(B/'manifests/selection_rejections.json',rejected)
 dump(B/'manifests/all100.json',prev+choices)
 for row in choices:status(row,'QUEUED')
 return choices
def diskcheck(row):
 while shutil.disk_usage(B).free<60*2**30:
  status(row,'WAIT_DISK',reason='Less than 60 GiB free; waiting without deleting inputs/results');time.sleep(30)
def gpu_stage(row,gpu):
 R=B/'runs'/row['object_id'];d=R/'objects'/row['object_id'];env=os.environ.copy();env.update(BATCH_GPU=str(gpu),HY3DGEN_MODELS=str(OLD/'model_cache'),NUMBA_CACHE_DIR=str(R/'cache/numba'),TORCH_EXTENSIONS_DIR=str(R/'cache/torch_extensions'))
 diskcheck(row);assert sha(row['source_object_path'])==row['source_object_sha256']
 status(row,'P3',gpu=gpu)
 run([H,'-B','-u',str(R/'scripts/p3_smoke_segment.py'),'--limit','3'],R/'logs/p3.log',env=env)
 seg=json.loads((d/'p3/segmentation.json').read_text())
 if 'error' in seg:raise RuntimeError(seg['error'])
 pm=json.loads((d/'p3/parts_manifest.json').read_text());parts=pm['parts']
 dump(d/'p3/part_metadata.json',{'parts':[{'part_id':int(p['part_id'].split('_')[-1]),'path':p['part_mesh_path'],'p3_label':p['p3_label']} for p in parts]})
 status(row,'XPART',gpu=gpu,p3_parts=len(parts))
 if not (d/'xpart_parts/manifest.json').exists():run([H,'-B','-u',str(R/'scripts/xpart_new_objects.py'),'--source-mesh',row['canonical_path'],'--p3-dir',str(d/'p3'),'--out-dir',str(d/'xpart_parts'),'--gpu',str(gpu),'--seed','20261011','--batch-size','3','--octree-resolution','512'],R/'logs/xpart.log',env=env)
 status(row,'CAD_QUEUED',p3_parts=len(parts))
def cpu_stage(row):
 R=B/'runs'/row['object_id']
 try:
  diskcheck(row);status(row,'CAD')
  env=os.environ.copy();env.update(CAD_WORKERS='4',CAD_TIMEOUT='180')
  run([C,'-B','-u',str(R/'scripts/rebuild_cases.py'),'run',row['object_id']],R/'logs/cad.log',timeout=14400,env=env)
  status(row,'EVALUATION')
  run([C,'-B','-u',str(R/'scripts/evaluate_new_objects.py')],R/'logs/evaluation.log',timeout=7200)
  run([C,'-B','-u',str(R/'scripts/visualize_new_objects.py')],R/'logs/visualization.log',timeout=1800)
  s=json.loads((R/'summary.json').read_text());s['scope']='One new source object from frozen additional 97; excludes old two batches and first three.';dump(R/'summary.json',s)
  status(row,'COMPLETE',**{k:s[k] for k in ['p3_part_n','cad_valid_n','strict_original_n','strict_completed_n']})
 except Exception as e:status(row,'FAILED',error=str(e),traceback=traceback.format_exc())
def main():
 B.mkdir(parents=True,exist_ok=True);handle=(B/'controller.lock').open('w');fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
 rows=prepare()
 allrows=json.loads((B/'manifests/carried3.json').read_text())+rows
 assert len(allrows)==100 and len({r['source_object_sha256'] for r in allrows})==100
 dump(B/'manifests/all100.json',allrows)
 if '--prepare-only' in sys.argv:return
 # No third-party GPU processes are stopped. Check each GPU before each object.
 import queue
 q=queue.Queue()
 for row in rows:
  p=B/'status'/f"{row['object_id']}.json"
  if p.exists() and json.loads(p.read_text())['stage']=='COMPLETE':continue
  q.put(row)
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as cpu:
  futures=[]
  def worker(gpu):
   while True:
    try:row=q.get_nowait()
    except queue.Empty:return
    try:
     while True:
      raw=subprocess.check_output(['nvidia-smi',f'--id={gpu}','--query-gpu=memory.used,utilization.gpu','--format=csv,noheader,nounits'],text=True);mem,util=map(int,raw.strip().split(','))
      if mem<1024 and util<5:break
      status(row,'WAIT_GPU',gpu=gpu);time.sleep(30)
     gpu_stage(row,gpu);futures.append(cpu.submit(cpu_stage,row))
    except Exception as e:status(row,'FAILED',error=str(e),traceback=traceback.format_exc())
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(worker,[0,6]))
  for f in futures:f.result()
 refresh();print('BATCH_FINISHED',flush=True)
if __name__=='__main__':main()
