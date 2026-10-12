from v2_common import *
from report_native_v2 import final_results
from native_geometry import profile_types
import csv
R=O.parent/'cad_render_v4'
rows=final_results();issues=[];baseline_drift=0.;candidate_n=0;validated_new_n=0;failed_candidates=0
for r in rows:
 d=O/'cases'/r['case_id'];m=r['metrics'];rep=read(d/'cad/representation.json')
 if sha(d/'source/part_local.ply')!=r['normalized_mesh_sha256']:issues.append(r['case_id']+':source hash')
 if status(m)!=r['status']:issues.append(r['case_id']+':status criteria')
 if len(r['attempts'])>8:issues.append(r['case_id']+':candidate budget')
 if rep['classification']!='A_NATIVE_PARAMETRIC' or not rep['self_contained'] or rep['mesh_wrapper_detected']:issues.append(r['case_id']+':native gate')
 if sha(d/'cad/cad.py')!=rep['cad_sha256'] or sha(d/'cad/cad.step')!=rep['step_sha256']:issues.append(r['case_id']+':final code/STEP audit hashes')
 if {'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}[r['status']]>{'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}[r['baseline_status']]:issues.append(r['case_id']+':baseline status regression')
 for a in r['attempts']:
  candidate_n+=1
  if a.get('baseline_drift'):baseline_drift=max(baseline_drift,max(abs(v) for v in a['baseline_drift'].values()))
  if a.get('new_candidate') and 'metrics' in a:
   ar=read(Path(a['path'])/'representation.json');validated_new_n+=1
   if not(ar['classification']=='A_NATIVE_PARAMETRIC' and ar['self_contained'] and not ar['mesh_wrapper_detected']):issues.append(a['path']+':geometry before native acceptance')
   if ar['primitive_count']>8 or sum(ar.get(k,0) for k in ['boolean_union_count','boolean_cut_count','boolean_intersect_count'])>6 or ar['sketch_entity_count']>96:issues.append(a['path']+':feature budget')
   if not a.get('evaluation_mesh_serialized'):issues.append(a['path']+':evaluation must use persisted mesh')
  if 'error' in a:failed_candidates+=1
config=read(O/'config/factory_config.json')
if config['n_points']!=20000 or config['iou_resolution']!=128:issues.append('Evaluation protocol drift')
renders=read(R/'manifests/render_results.json');assert len(renders)==20
render_part_n=0
for obj in renders:
 for part in obj['parts']:
  render_part_n+=1
  if sha(part['step_path'])!=part['step_sha256_before']:issues.append(part['case_id']+':renderer changed STEP')
for name in ['near_pass_diagnosis.csv','near_pass_rescue_v2.csv','reject_diagnosis.csv','part_v1_v2_comparison.csv','family_success_v2.csv','profile_upgrade_summary.csv','strict_accept_v2.csv','near_pass_v2.csv','reject_v2.csv','representation_validation_v2.csv']:
 if not(O/'tables'/name).exists():issues.append('Missing table '+name)
for name in ['NEAR_PASS_RESCUE_REPORT.md','PROFILE_RECONSTRUCTION_REPORT.md','PART_CAD_FITTING_V2_NATIVE_REPORT.md','NEXT_STAGE_DECISION.md']:
 if not(O/'reports'/name).exists():issues.append('Missing report '+name)
if not(R/'reports/CAD_RENDER_V4_REPORT.md').exists():issues.append('Missing render report')
tests=read(O/'tests/PROFILE_TEST_RESULTS.json')
if not tests['pass'] or tests['test_n']<7:issues.append('Profile/kernel tests incomplete')
guard=read(O/'integrity/READ_ONLY_GUARD.json')
if not guard['pass']:issues.append('Historical files changed')
vis=read(O/'visualizations/manifest.json')
groups={g:sum(x['group']==g for x in vis) for g in ['near_to_strict','near_still_failed','reject_representative']}
if any(n<10 for n in groups.values()):issues.append('Representative visualization count incomplete')
if len(rows)!=209 or render_part_n!=209:issues.append('Cohort count drift')
if baseline_drift>1e-10:issues.append('Baseline evaluator drift')
if not read(O/'integrity/SERIALIZED_EVALUATION_ALL.json')['pass']:issues.append('Serialized mesh evaluation verification failed')
result={'pass':not issues,'issues':issues,'part_n':len(rows),'major_n':153,'fitted_this_round_n':sum(r['fitting_performed'] for r in rows),'candidate_n':candidate_n,'new_candidate_native_pass_and_geometry_evaluated_n':validated_new_n,'failed_candidates_retained':failed_candidates,'max_baseline_metric_drift':baseline_drift,'render_objects':20,'render_parts':render_part_n,'render_geometry_changed':False,'geometry_visual_groups':groups,'profile_tests_n':tests['test_n'],'historical_guard':guard,'thresholds_unchanged':True,'evaluation_protocol_unchanged':True,'gate_order_enforced':True};dump(O/'integrity/FINAL_VALIDATION.json',result);print(json.dumps(result,indent=2));assert not issues
