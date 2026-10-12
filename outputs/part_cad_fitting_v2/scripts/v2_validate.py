from v2_common import *
import trimesh,cadquery as cq
from metric_runtime import evaluate
from v2_run import complexity
from execute_candidate import validate as validate_native_program
rows=read(O/'manifests/cases.json');errors=[];deltas=[];count=0
for row in rows:
 d=O/'cases'/row['case_id'];p=d/'result.json'
 if not p.exists():errors.append(row['case_id']+':missing result');continue
 r=read(p);count+=len(r['attempts']);old=Path(row['v1_dir'])
 if sha(d/'source/part_local.ply')!=row['normalized_mesh_sha256'] or sha(old/'source/part_local.ply')!=row['normalized_mesh_sha256']:errors.append(row['case_id']+':source changed')
 v1p=read(d/'source/provenance.json');oldf=read(old/'features/features.json')
 for key in ['local_transform','world_transform','inverse_transform','local_to_original_object']:
  if v1p[key]!=oldf[key]:errors.append(row['case_id']+':transform changed')
 if len(r['attempts'])>8:errors.append(row['case_id']+':candidate cap')
 if r['v1_status']=='STRICT_ACCEPT' and r['v2_status']!='STRICT_ACCEPT':errors.append(row['case_id']+':strict damage')
 for c in r['attempts']:
  code=(Path(c['path'])/'cad.py').read_text()
  try:complexity(code);validate_native_program(code)
  except Exception as e:errors.append(row['case_id']+':'+str(e))
  if any(x in code for x in ['importStep','importBrep','makeShell','makeFromWires','vertices','faces','mesh','open(']):errors.append(row['case_id']+':non-native payload')
  if c['candidate_id']==0:deltas.extend(abs(v) for v in c['baseline_drift'].values())
  if 'metrics' in c and c['metrics']['strict_pass']:
   m=c['metrics']
   if not (m['iou']>=.9 and m['normalized_chamfer']<=.01 and m['bbox_error']<=.03 and m['centroid_l2_error']<=.02 and c['execution']['step_reload_pass']):errors.append(row['case_id']+':gate mismatch')
 initial=r['attempts'][0];best=next(x for x in r['attempts'] if x['candidate_id']==r['selected_candidate']);search=read(d/'optimization/search.json') if (d/'optimization/search.json').exists() else {}
 dump(d/'optimization/final_summary.json',{'initial_parameters':initial['parameters'],'best_parameters':best['parameters'],'initial_score':initial['score'],'best_score':best['score'],'optimization_steps':search.get('optimization_steps',0),'score_protocol':'Final unchanged IoU128/20000 point score; proxy trace is separate','selected_candidate':best['candidate_id']})
# Synthetic evaluator smoke tests are never added to the 209-case dataset.
box=trimesh.creation.box(extents=[1,.7,.5]);same=evaluate(box,box,20261006);shifted=box.copy();shifted.apply_translation([.10,0,0]);bad=evaluate(box,shifted,20261006)
if not (same['iou']==1 and same['bbox_error']==0 and same['centroid_l2_error']==0 and same['strict_pass'] and not bad['strict_pass'] and bad['bbox_error']>=.099):errors.append('synthetic evaluator invariance/translation test')
for name in ['v2_optimize.py','v2_refit.py','v2_reject.py','v2_run.py','v2_plan.py']:
 code=(O/'scripts'/name).read_text()
 if any('object_000' in line or 'part_00' in line for line in code.splitlines()):errors.append(name+':case-id-specific literal')
protected=read(O/'integrity/PROTECTED_BEFORE.json');changes=[]
for name,record in protected.items():
 p=Path(name)
 if not p.exists() or p.stat().st_mtime_ns!=record['mtime_ns'] or sha(p)!=record['sha256']:changes.append(name)
guard={'pass':not changes,'checked_files':len(protected),'changes':changes,'scope':'V1 Smoke20 files, its recorded prior protected inputs/results, two historical fitter scripts; authorized optimizer deletion was outside this guard and recorded separately'};dump(O/'integrity/READ_ONLY_GUARD.json',guard)
if changes:errors.append('historical guard')
out={'pass':not errors,'case_n':len(rows),'candidate_n':count,'max_baseline_metric_drift':max(deltas,default=None),'synthetic_evaluator_identity':same,'synthetic_evaluator_displacement':bad,'no_case_id_hardcode':not any('case-id' in x for x in errors),'errors':errors};dump(O/'integrity/VALIDATION.json',out);print(json.dumps({k:v for k,v in out.items() if not k.startswith('synthetic')},indent=2));assert not errors
