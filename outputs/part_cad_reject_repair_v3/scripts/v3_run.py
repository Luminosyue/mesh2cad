from v2_common import *
import sys,time,shutil,subprocess,argparse,traceback
from concurrent.futures import ProcessPoolExecutor,as_completed
import trimesh,cadquery as cq
from metric_runtime import evaluate
from v2_run import complexity
from execute_candidate import validate
from v3_geometry import generate

def run(row):
 d=O/'cases'/row['case_id'];rp=d/'result.json'
 if rp.exists():return read(rp)
 assert shutil.disk_usage(O).free>5*2**30,'Disk reserve exhausted'
 started=time.time();old=read(d/'source/v2_result.json');row=dict(row,v2_family=old['v2_family']);m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);cm=trimesh.load(d/'baseline/cad_mesh.ply',force='mesh',process=True);code=(d/'baseline/cad.py').read_text();validate(code)
 baseline_path=d/'candidates/candidate_00';baseline_path.mkdir(exist_ok=True)
 if (baseline_path/'record.json').exists():base=read(baseline_path/'record.json')
 else:
  for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(d/'baseline'/f,baseline_path/f)
  shape=cq.importers.importStep(str(baseline_path/'cad.step')).val();assert shape.isValid() and shape.Solids();met=evaluate(m,cm,row['seed']);drift={k:met[k]-old['v2_metrics'][k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']};assert max(map(abs,drift.values()))<1e-10
  base={'candidate_id':0,'kind':'V2_BASELINE','path':str(baseline_path),'metrics':met,'score':score(met),'family':old['v2_family'],'parameters':read(d/'baseline/parameters.json'),'baseline_drift':drift,'execution':{'parse_pass':True,'execute_pass':True,'step_reload_pass':True,'v2_execution_inherited':True,'step_reimported_v3':True},**complexity(code)};dump(baseline_path/'record.json',base)
 plans=d/'optimization/proposals.json'
 if plans.exists():jobs=read(plans)['selected']
 else:
  jobs,trace=generate(row,m,cm,code,read(d/'source/features_v2.json'),np.load(d/'source/frozen_evaluation_points.npy'));dump(plans,{'selected':jobs,**trace})
 attempts=[base]
 for i,job in enumerate(jobs,1):
  dest=d/'candidates'/f'candidate_{i:02d}';dest.mkdir(exist_ok=True);record=dest/'record.json'
  if record.exists():attempts.append(read(record));continue
  (dest/'cad.py').write_text(job['code']);dump(dest/'parameters.json',job['parameters']);rec={k:v for k,v in job.items() if k!='code'};rec.update(candidate_id=i,path=str(dest))
  try:
   validate(job['code']);rec.update(complexity(job['code']))
   exdir=dest/'execution'
   if exdir.exists() and not (exdir/'execution.json').exists():exdir.rename(dest/('interrupted_execution_'+str(time.time_ns())))
   if not (exdir/'execution.json').exists():
    p=subprocess.run([sys.executable,'-B',str(O/'scripts/execute_candidate.py'),str(dest/'cad.py'),str(exdir)],capture_output=True,text=True,timeout=120);(dest/'execution.log').write_text(p.stdout+'\n'+p.stderr)
   ex=read(exdir/'execution.json');rec['execution']=ex
   if ex.get('tessellation_pass'):
    recon=trimesh.load(exdir/'cad_mesh_from_reloaded_step.ply',force='mesh',process=True);met=evaluate(m,recon,row['seed']);rec.update(metrics=met,score=score(met));shutil.copyfile(exdir/'cad.step',dest/'cad.step');shutil.copyfile(exdir/'cad_mesh_from_reloaded_step.ply',dest/'cad_mesh.ply')
  except Exception as e:rec.update(error=str(e),traceback=traceback.format_exc())
  dump(record,rec);attempts.append(rec)
 order={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2};valid=[x for x in attempts if 'metrics' in x];best=min(valid,key=lambda x:(order[status(x['metrics'])],x['score']));bd=Path(best['path'])
 for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(bd/f,d/'cad'/f)
 dump(d/'metrics/metrics.json',best['metrics']);out={'case_id':row['case_id'],'object_id':row['object_id'],'part_id':row['part_id'],'size_class':row['size_class'],'v2_status':'REJECT','v3_status':status(best['metrics']),'v2_metrics':base['metrics'],'v3_metrics':best['metrics'],'v2_score':base['score'],'v3_score':best['score'],'family':best['family'],'fix_type':best['kind'],'selected_candidate':best['candidate_id'],'attempts':attempts,'preserved':False,'source_sha256':sha(d/'source/part_local.ply'),'elapsed_seconds':time.time()-started};dump(rp,out)
 dump(d/'optimization/final_summary.json',{'initial_parameters':base['parameters'],'best_parameters':best['parameters'],'initial_score':base['score'],'best_score':best['score'],'optimization_steps':read(plans).get('local_search',{}).get('optimization_steps',0),'candidate_n':len(attempts),'selection_policy':'status tier then fixed V2 score','final_metrics_are_proxy':False})
 print(json.dumps({'case':row['case_id'],'status':out['v3_status'],'fix':out['fix_type'],'iou':round(best['metrics']['iou'],5),'ncd':round(best['metrics']['normalized_chamfer'],5),'seconds':round(out['elapsed_seconds'],1)}),flush=True);return out

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);ap.add_argument('--workers',type=int,default=12);a=ap.parse_args();rows=sorted([r for r in read(O/'manifests/cases.json') if r['v2_status']=='REJECT'],key=lambda r:r['v2_score']);rows=rows[:a.limit] if a.limit else rows
 failures=[]
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  tasks={pool.submit(run,r):r['case_id'] for r in rows}
  for f in as_completed(tasks):
   try:f.result()
   except Exception as e:failures.append({'case_id':tasks[f],'error':str(e),'traceback':traceback.format_exc()});print('CASE_FAILED',tasks[f],str(e),flush=True)
 dump(O/'logs'/('pilot_failures.json' if a.limit else 'run_failures.json'),failures);print('RUN_COMPLETE',len(rows),'FAILED',len(failures),flush=True)
 if failures:raise SystemExit(1)
