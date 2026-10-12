"""Normalize all new candidate metrics to the persisted evaluation mesh protocol.

Does not rerun fitting or change any candidate geometry. Initial evidence retained.
"""
from v2_common import *
from metric_runtime import evaluate
from run_part_cad_fitting_v2_native import near_gate
import trimesh,shutil,argparse
from concurrent.futures import ProcessPoolExecutor,as_completed
ORDER={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}
def run(row):
 d=O/'cases'/row['case_id'];rp=d/'result.json'
 if not rp.exists():return {'case_id':row['case_id'],'preserved':True}
 r=read(rp);m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);attempts=[];deltas=[];beforehash={str(p):sha(p) for p in (d/'candidates').glob('*/cad.step')};beforehash.update({str(p):sha(p) for p in (d/'candidates').glob('*/cad.py')})
 for old in r['attempts']:
  if not old.get('new_candidate') or 'metrics' not in old:attempts.append(old);continue
  dest=Path(old['path']);rec=read(dest/'record.json');rec['candidate_id']=old['candidate_id']
  if not rec.get('evaluation_mesh_serialized'):
   if not(dest/'record_before_serialized_evaluation.json').exists():shutil.copyfile(dest/'record.json',dest/'record_before_serialized_evaluation.json')
   cm=trimesh.load(dest/'cad_mesh.ply',force='mesh',process=True);metrics=evaluate(m,cm,row['seed']);delta={k:metrics[k]-rec['metrics'][k] for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']};deltas.append({'candidate_id':old['candidate_id'],'delta':delta,'status_before':rec['status'],'status_after':status(metrics)});rec.update(metrics=metrics,score=score(metrics),status=status(metrics),evaluation_mesh_serialized=True);dump(dest/'record.json',rec)
  attempts.append(rec)
 valid=[a for a in attempts if 'metrics' in a];best=min(valid,key=lambda a:(ORDER[a['status']],a['score']));bd=Path(best['path'])
 if not(d/'result_before_serialized_evaluation.json').exists():shutil.copyfile(rp,d/'result_before_serialized_evaluation.json')
 for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:shutil.copyfile(bd/f,d/'cad'/f)
 dump(d/'cad/representation.json',read(bd/'representation.json'));dump(d/'metrics/metrics.json',best['metrics']);before_status=r['status'];before_choice=r['selected_candidate'];r.update(status=best['status'],metrics=best['metrics'],score=best['score'],family=best['family'],profile_types=best['profile_types'],fix_type=best['kind'],selected_candidate=best['candidate_id'],attempts=attempts,new_strict_vs_baseline=best['status']=='STRICT_ACCEPT' and row['baseline_status']!='STRICT_ACCEPT',evaluation_mesh_serialized=True);dump(rp,r)
 assert all(sha(Path(p))==h for p,h in beforehash.items())
 evidence={'case_id':row['case_id'],'candidate_deltas':deltas,'candidate_geometry_unchanged':True,'selection_changed':before_choice!=best['candidate_id'],'status_before':before_status,'status_after':r['status']};dump(d/'optimization/serialized_evaluation_check.json',evidence);return evidence
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--phase',choices=['near','all'],default='all');a=ap.parse_args();rows=read(O/'manifests/cases.json');group=[r for r in rows if a.phase=='all' or r['v1_status']=='NEAR_PASS'];out=[]
 with ProcessPoolExecutor(max_workers=12) as pool:
  for f in as_completed([pool.submit(run,r) for r in group]):out.append(f.result())
 all_deltas=[x for r in out for x in r.get('candidate_deltas',[])];result={'pass':True,'case_n':len(group),'new_candidates_recomputed':len(all_deltas),'max_abs_metric_drift':{k:max([abs(x['delta'][k]) for x in all_deltas]+[0.]) for k in ['iou','normalized_chamfer','bbox_error','centroid_l2_error']},'candidate_class_changes':sum(x['status_before']!=x['status_after'] for x in all_deltas),'case_selection_changes':sum(x.get('selection_changed',False) for x in out),'case_status_changes':sum(x.get('status_before')!=x.get('status_after') for x in out if 'status_before' in x),'candidate_geometry_changed':False,'details':out};dump(O/'integrity'/('SERIALIZED_EVALUATION_'+a.phase.upper()+'.json'),result);near_gate(rows);print(json.dumps({k:v for k,v in result.items() if k!='details'},indent=2))
