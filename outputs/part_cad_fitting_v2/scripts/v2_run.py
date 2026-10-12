from v2_common import *
import argparse,shutil,subprocess,sys,traceback,time
from concurrent.futures import ProcessPoolExecutor
import trimesh,cadquery as cq
from metric_runtime import evaluate
from v2_optimize import proposals
from v2_refit import refined_candidates
def complexity(code):
 tree=ast.parse(code);attrs=[n.func.attr for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)];pr=sum(attrs.count(k) for k in ['box','sphere','extrude','revolve','loft']);bo=sum(attrs.count(k) for k in ['union','cut','intersect']);sk=sum(len(ast.literal_eval(n.args[0])) for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='polyline')
 if pr>8 or bo>6 or sk>96:raise ValueError('CAD_TOO_COMPLEX')
 return {'primitive_count':pr,'boolean_count':bo,'sketch_entity_count':sk}
def baseline(d,row,m,r):
 dest=d/'candidates/candidate_00';dest.mkdir(exist_ok=True);old=Path(row['v1_dir']);shutil.copyfile(old/'cad/cad.py',dest/'cad.py');shutil.copyfile(old/'cad/cad.step',dest/'cad.step');shutil.copyfile(old/'cad/cad_mesh_from_reloaded_step.ply',dest/'cad_mesh.ply');shutil.copyfile(old/'cad/parameters.json',dest/'parameters.json')
 reloaded=cq.importers.importStep(str(dest/'cad.step')).val();assert reloaded.isValid() and reloaded.Solids();cm=trimesh.load(dest/'cad_mesh.ply',force='mesh',process=True);met=evaluate(m,cm,row['seed']);drift={k:met[k]-r['metrics'][k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']};assert max(abs(x) for x in drift.values())<1e-10,drift
 ex=read(old/'cad/reload_metadata.json');ex['step_reload_checked_v2']=True;rec={'candidate_id':0,'fix_type':'V1_BASELINE_RESCORING','cad_family':r['cad_family'],'construction_plan':'Preserve V1 native program and frozen reloaded-STEP tessellation; reimport STEP and rescore unchanged geometry','parameters':read(dest/'parameters.json'),'path':str(dest),'metrics':met,'score':score(met),'execution':ex,'baseline_drift':drift,**complexity((dest/'cad.py').read_text())};dump(dest/'record.json',rec);return rec,cm
def run(row):
 d=O/'cases'/row['case_id'];result=d/'result.json'
 if result.exists():return read(result)
 start=time.time();r=read(d/'source/v1_result.json');m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);base,cm=baseline(d,row,m,r);attempts=[base];code=Path(r['cad_program_path']).read_text();errors=[];plan=read(d/'diagnosis/structure_plan.json')
 if row['v1_status']!='STRICT_ACCEPT':
  try:
   prop,log=proposals(m,cm,code,r['best_kind'],np.load(d/'source/frozen_evaluation_points.npy'),row['seed']);dump(d/'optimization/search.json',log)
  except Exception as e:prop=[];errors.append({'phase':'optimization','error':str(e),'traceback':traceback.format_exc()})
  try:ref,err=refined_candidates(m,read(d/'features/features_v2.json'),r);errors.extend({'phase':'refit','error':x} for x in err)
  except Exception as e:ref=[];errors.append({'phase':'refit','error':str(e)})
  if row['v1_status']=='REJECT':
   from v2_reject import structural_candidates
   ref,err=structural_candidates(m,read(d/'features/features_v2.json'),r,plan);errors.extend({'phase':'structure','error':x} for x in err)
   jobs=prop[:2]+ref+prop[2:]
  else:jobs=prop[:3]+ref+prop[3:]
  unique=[];seen={code.strip()}
  for name,c,p in jobs:
   if c.strip() in seen:continue
   seen.add(c.strip());unique.append((name,c,p))
   if len(unique)==7:break
  for i,(name,c,p) in enumerate(unique,1):
   dest=d/'candidates'/f'candidate_{i:02d}';record=dest/'record.json'
   if record.exists():attempts.append(read(record));continue
   dest.mkdir(exist_ok=True);(dest/'cad.py').write_text(c);dump(dest/'parameters.json',p);rec={'candidate_id':i,'fix_type':name,'path':str(dest),'parameters':p,'cad_family':plan['cad_family_v2'],'construction_plan':plan['construction_plan']}
   try:
    rec.update(complexity(c));p0=subprocess.run([sys.executable,'-B',str(O/'scripts/execute_candidate.py'),str(dest/'cad.py'),str(dest/'execution')],capture_output=True,text=True,timeout=120);(dest/'execution.log').write_text(p0.stdout+'\n'+p0.stderr);ex=read(dest/'execution/execution.json');rec['execution']=ex
    if ex.get('tessellation_pass'):
     recon=trimesh.load(dest/'execution/cad_mesh_from_reloaded_step.ply',force='mesh',process=True);met=evaluate(m,recon,row['seed']);rec.update(metrics=met,score=score(met));shutil.copyfile(dest/'execution/cad.step',dest/'cad.step');shutil.copyfile(dest/'execution/cad_mesh_from_reloaded_step.ply',dest/'cad_mesh.ply')
   except Exception as e:rec.update(error=str(e),traceback=traceback.format_exc())
   dump(record,rec);attempts.append(rec)
 valid=[a for a in attempts if 'metrics' in a];best=min(valid,key=lambda a:(not a['metrics']['strict_pass'],a['score']));bd=Path(best['path'])
 for file in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(bd/file,d/'cad'/file)
 met=best['metrics'];dump(d/'metrics/metrics.json',met);out={**row,'v2_status':status(met),'v2_family':plan['cad_family_v2'],'v1_metrics':base['metrics'],'v2_metrics':met,'selected_candidate':best['candidate_id'],'fix_type':best['fix_type'],'v1_score':base['score'],'v2_score':best['score'],'attempts':attempts,'errors':errors,'elapsed_seconds':time.time()-start,'cad_program_path':str(d/'cad/cad.py'),'step_path':str(d/'cad/cad.step'),'cad_mesh_path':str(d/'cad/cad_mesh.ply'),'source_mesh_sha256':sha(d/'source/part_local.ply')};dump(result,out);print(json.dumps({'case':row['case_id'],'v1':row['v1_status'],'v2':out['v2_status'],'fix':out['fix_type'],'iou':round(met['iou'],4),'ncd':round(met['normalized_chamfer'],5)}),flush=True);return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['near','reject','strict'],required=True);a=ap.parse_args();mapping={'near':'NEAR_PASS','reject':'REJECT','strict':'STRICT_ACCEPT'};rows=[r for r in read(O/'manifests/cases.json') if r['v1_status']==mapping[a.group]]
 if a.group=='reject':assert read(O/'reports/NEAR_GATE.json')['reject_stage_allowed'],'Near-pass gate not reviewed'
 with ProcessPoolExecutor(max_workers=8) as pool:list(pool.map(run,rows))
 print('GROUP_COMPLETE',a.group,len(rows),flush=True)
