from v2_common import *
from native_geometry import family,profile_types,FAMILIES
import csv,collections,shutil
def table(name,rows,fields=None):
 p=O/'tables'/name;p.parent.mkdir(exist_ok=True)
 if fields is None:fields=list(dict.fromkeys(k for r in rows for k in r))
 with p.open('w',newline='') as f:
  w=csv.DictWriter(f,fields,extrasaction='ignore');w.writeheader()
  for r in rows:w.writerow({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items() if k in fields})
def final_results():
 rows=read(O/'manifests/cases.json');results=[]
 for row in rows:
  d=O/'cases'/row['case_id'];p=d/'result.json'
  if p.exists():r=read(p)
  else:
   code=(d/'baseline/cad.py').read_text();r={**row,'status':row['baseline_status'],'metrics':row['baseline_metrics'],'score':score(row['baseline_metrics']),'family':family(code),'profile_types':profile_types(code),'fix_type':'PRESERVED_'+row['baseline_version']+'_NOT_REFIT_THIS_PHASE','selected_candidate':0,'attempts':[],'fitting_performed':False,'new_strict_vs_baseline':False};dump(d/'result_inherited.json',r);shutil.copyfile(d/'baseline/representation.json',d/'cad/representation.json')
  results.append(r)
 return results
def compile_reports():
 rows=final_results();near=[r for r in rows if r['v1_status']=='NEAR_PASS'];gate=read(O/'reports/NEAR_GATE.json');comp=[];diag=[];validation=[];candidate_rows=[]
 for r in rows:
  d=O/'cases'/r['case_id'];old=read(d/'source/v1_result.json');m0=old['metrics'];m=r['metrics'];c0=(Path(r['v1_dir'])/'cad/cad.py').read_text();originaltypes=profile_types(c0);rep=read(d/'cad/representation.json');newscore=score(m);oldscore=score(m0);statusdamage={'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}[r['status']]>{'STRICT_ACCEPT':0,'NEAR_PASS':1,'REJECT':2}[r['v1_status']]
  rec={'object_id':r['object_id'],'part_id':r['part_id'],'case_id':r['case_id'],'size_class':r['size_class'],'V1_family':old['cad_family'],'V2_family':r['family'],'family_changed':family(c0)!=r['family'],'V1_profile_type':originaltypes,'V2_profile_type':r['profile_types'],'V1_NCD':m0['normalized_chamfer'],'V2_NCD':m['normalized_chamfer'],'V1_IoU':m0['iou'],'V2_IoU':m['iou'],'V1_bbox':m0['bbox_error'],'V2_bbox':m['bbox_error'],'V1_centroid':m0['centroid_l2_error'],'V2_centroid':m['centroid_l2_error'],'V1_status':r['v1_status'],'V2_status':r['status'],'V3_preserved_baseline_status':r['baseline_status'],'delta_NCD':m['normalized_chamfer']-m0['normalized_chamfer'],'delta_IoU':m['iou']-m0['iou'],'delta_score':newscore-oldscore,'delta_score_vs_preserved_baseline':newscore-score(r['baseline_metrics']),'fix_type':r['fix_type'],'fitting_performed':r['fitting_performed'],'new_strict_vs_baseline':r['new_strict_vs_baseline'],'strict_rescue':r['v1_status']!='STRICT_ACCEPT' and r['status']=='STRICT_ACCEPT','strict_damage':r['v1_status']=='STRICT_ACCEPT' and r['status']!='STRICT_ACCEPT','status_damage':statusdamage,'comparison':'IMPROVED' if newscore<oldscore-1e-10 else 'WORSE' if newscore>oldscore+1e-10 else 'UNCHANGED','step_path':str(d/'cad/cad.step'),'cad_path':str(d/'cad/cad.py')};comp.append(rec)
  rec['delta_NCD_vs_preserved_baseline']=m['normalized_chamfer']-r['baseline_metrics']['normalized_chamfer'];rec['delta_IoU_vs_preserved_baseline']=m['iou']-r['baseline_metrics']['iou']
  local=[a for a in r['attempts'] if a['kind']=='BASELINE_LOCAL_REFINEMENT' and 'metrics' in a];control=local[0] if local else None;is_profile=r['fix_type'].startswith(('PROFILE_','STABLE_SECTION_','MEASURED_'))
  rec['parameter_only_control_status']=control['status'] if control else 'NOT_AVAILABLE';rec['profile_upgrade_strict_rescue']=bool(is_profile and r['new_strict_vs_baseline'] and control and control['status']!='STRICT_ACCEPT');rec['delta_NCD_vs_parameter_only']=m['normalized_chamfer']-control['metrics']['normalized_chamfer'] if control and is_profile else None;rec['delta_IoU_vs_parameter_only']=m['iou']-control['metrics']['iou'] if control and is_profile else None
  diagnosis=read(d/'diagnosis/diagnosis.json') if (d/'diagnosis/diagnosis.json').exists() else {'primary_failure':'NOT_REFIT_THIS_PHASE','secondary_failures':[],'strict_failed_by':failed(m0),'reason':'Preserved baseline; reject recovery depends on Near gate'}
  diag.append({'case_id':r['case_id'],'V1_status':r['v1_status'],'V1_NCD':m0['normalized_chamfer'],'V1_IOU':m0['iou'],'V1_BBOX_ERROR':m0['bbox_error'],'V1_CENTROID_ERROR':m0['centroid_l2_error'],**diagnosis})
  validation.append({'case_id':r['case_id'],'classification':rep['classification'],'self_contained':rep['self_contained'],'mesh_wrapper_detected':rep['mesh_wrapper_detected'],'isolated_reexecution_pass':rep['isolated_reexecution_pass'],'code_step_correspondence_pass':rep['code_step_correspondence_pass'],'cad_sha256':sha(d/'cad/cad.py'),'step_sha256':sha(d/'cad/cad.step'),'representation_source':'NEW_CANDIDATE_VALIDATION' if r.get('selected_candidate',0) else 'PRIOR_AUDIT_HASH_VERIFIED','hash_match':sha(d/'cad/cad.py')==rep['cad_sha256'] and sha(d/'cad/cad.step')==rep['step_sha256']})
  for a in r['attempts']:candidate_rows.append({'case_id':r['case_id'],'candidate_id':a.get('candidate_id'),'kind':a['kind'],'representation_pass':'metrics' in a,'geometry_evaluated':'metrics' in a,'status':a.get('status'),'score':a.get('score'),'error':a.get('error'),'path':a['path']})
 assert len(comp)==209 and all(r['hash_match'] for r in validation)
 table('part_v1_v2_comparison.csv',comp);table('profile_parameter_control_comparison.csv',[r for r in comp if r['delta_NCD_vs_parameter_only'] is not None],list(comp[0]));table('near_pass_diagnosis.csv',[r for r in diag if r['V1_status']=='NEAR_PASS']);table('reject_diagnosis.csv',[r for r in diag if r['V1_status']=='REJECT']);table('near_pass_rescue_v2.csv',[r for r in comp if r['V1_status']=='NEAR_PASS']);table('representation_validation_v2.csv',validation);table('all_candidates.csv',candidate_rows)
 for st,name in [('STRICT_ACCEPT','strict_accept_v2.csv'),('NEAR_PASS','near_pass_v2.csv'),('REJECT','reject_v2.csv')]:table(name,[r for r in comp if r['V2_status']==st],list(comp[0]))
 families=[]
 for f in FAMILIES:
  cohort=[r for r in comp if r['V2_family']==f];n=len(cohort);strict=sum(r['V2_status']=='STRICT_ACCEPT' for r in cohort);families.append({'family':f,'part_n':n,'strict_n':strict,'strict_rate':strict/n if n else None,'note':'N/A if no selected candidates in family'})
 table('family_success_v2.csv',families)
 upgrades=[]
 for label,typ in [('ARC','ARC'),('CIRCLE','CIRCLE'),('ELLIPSE','ELLIPSE'),('BSPLINE','BSPLINE'),('COMPOSITE','COMPOSITE_PROFILE')]:
  cohort=[r for r in comp if 'POLYLINE' in r['V1_profile_type'] and typ in r['V2_profile_type'] and r['fix_type'].startswith(('PROFILE_','STABLE_SECTION_','MEASURED_'))]
  upgrades.append({'upgrade':'POLYLINE_TO_'+label,'selected_part_n':len(cohort),'mean_delta_NCD':float(np.mean([r['delta_NCD'] for r in cohort])) if cohort else None,'mean_delta_IoU':float(np.mean([r['delta_IoU'] for r in cohort])) if cohort else None,'mean_delta_NCD_vs_preserved_baseline':float(np.mean([r['delta_NCD_vs_preserved_baseline'] for r in cohort])) if cohort else None,'mean_delta_IoU_vs_preserved_baseline':float(np.mean([r['delta_IoU_vs_preserved_baseline'] for r in cohort])) if cohort else None,'strict_rescue_n':sum(r['strict_rescue'] for r in cohort),'additional_strict_vs_baseline_n':sum(r['new_strict_vs_baseline'] for r in cohort),'case_ids':[r['case_id'] for r in cohort],'counts_can_overlap_for_mixed_profiles':True,'attribution':'curve reconstruction plus local optimization, not a profile-only causal ablation'})
 for u in upgrades:
  ids=set(u['case_ids']);cohort=[r for r in comp if r['case_id'] in ids];u['controlled_profile_strict_rescue_n']=sum(r['profile_upgrade_strict_rescue'] for r in cohort)
 table('profile_upgrade_summary.csv',upgrades)
 counts=collections.Counter(r['status'] for r in rows);major=sum(r['size_class']=='MAJOR_PART' and r['status']=='STRICT_ACCEPT' for r in rows);assert sum(r['size_class']=='MAJOR_PART' for r in rows)==153
 newstrict=sum(r['new_strict_vs_baseline'] for r in rows);fitted=sum(r['fitting_performed'] for r in rows);damage=sum(r['strict_damage'] for r in comp);passed=sum(r['classification']=='A_NATIVE_PARAMETRIC' for r in validation)
 summary={'TOTAL_PART_N':209,'MAJOR_PART_N':153,'NATIVE_REPRESENTATION_PASS_N':passed,'SELF_CONTAINED_N':sum(r['self_contained'] for r in validation),'V1_STRICT_N':4,'V1_NEAR_N':63,'V1_REJECT_N':142,'near':gate,'profile_upgrades':upgrades,'CAD_PARSE_PASS_N':209,'CAD_EXECUTE_PASS_N':sum(r['isolated_reexecution_pass'] for r in validation),'STEP_RELOAD_PASS_N':sum(r['code_step_correspondence_pass'] for r in validation),'STRICT_ACCEPT_N':counts['STRICT_ACCEPT'],'NEAR_PASS_N':counts['NEAR_PASS'],'REJECT_N':counts['REJECT'],'STRICT_ACCEPT_RATE':counts['STRICT_ACCEPT']/209,'MAJOR_PART_STRICT_N':major,'MAJOR_PART_STRICT_RATE':major/153,'NCD_MEDIAN_V1':float(np.median([r['V1_NCD'] for r in comp])),'NCD_MEDIAN_V2':float(np.median([r['V2_NCD'] for r in comp])),'IOU_MEDIAN_V1':float(np.median([r['V1_IoU'] for r in comp])),'IOU_MEDIAN_V2':float(np.median([r['V2_IoU'] for r in comp])),'CENTROID_MEDIAN_V1':float(np.median([r['V1_centroid'] for r in comp])),'CENTROID_MEDIAN_V2':float(np.median([r['V2_centroid'] for r in comp])),'IMPROVED_N':sum(r['comparison']=='IMPROVED' for r in comp),'UNCHANGED_N':sum(r['comparison']=='UNCHANGED' for r in comp),'WORSE_N':sum(r['comparison']=='WORSE' for r in comp),'STRICT_RESCUE_N':sum(r['strict_rescue'] for r in comp),'STRICT_DAMAGE_N':damage,'NEW_STRICT_VS_PRESERVED_BASELINE_N':newstrict,'FITTED_THIS_ROUND_N':fitted,'candidate_n':len(candidate_rows),'candidate_geometry_evaluated_n':sum(r['geometry_evaluated'] for r in candidate_rows),'family_success':families,'FREEFORM_UNSUPPORTED_N':sum(r['family']=='J_FREEFORM_UNSUPPORTED' for r in rows),'REPRESENTATION_GATE':'PASS' if passed==209 else 'FAIL','PART_GEOMETRY_GATE':'PASS' if major/153>=.3 and counts['STRICT_ACCEPT']>=20 else 'FAIL','CAN_START_REASSEMBLY_V2':major/153>=.3,'CAN_SCALE_TO_100_OBJECTS':False,'PRIMARY_REMAINING_BLOCKER':'Major-part geometry fidelity and unsupported/missing geometric detail','NEXT_ALLOWED_STAGE':'REASSEMBLY_V2_REVIEW' if major/153>=.3 else 'TARGETED_PROFILE_AND_STRUCTURE_DIAGNOSIS','strict_thresholds_unchanged':True,'class_first_ranking_can_increase_weighted_score':True,'baseline_attribution':'V1 paired metrics include historical V2/V3 gains; NEW_STRICT_VS_PRESERVED_BASELINE separates this round'}
 summary['PROFILE_UPGRADE_STRICT_RESCUE_N']=sum(r['profile_upgrade_strict_rescue'] for r in comp)
 dump(O/'reports/SUMMARY.json',summary)
 neartext=f'''# Near-pass rescue

Original V1 cohort: 63. Final Strict: {gate['near_to_strict_n']}; Near: {gate['near_still_near_n']}; Reject: {gate['near_to_reject_n']}. Rescue rate: {gate['rescue_rate']:.2%}. Of the Strict outcomes, {gate['inherited_baseline_strict_n']} were already Strict in the preserved baseline and {gate['new_strict_vs_baseline_n']} are additional this round. Do not attribute inherited improvements to new curve fitting.

The original strict failures and geometry-supported hypotheses are in near_pass_diagnosis.csv and each case's diagnosis JSON. Polyline approximation is a hypothesis until candidate comparison supports it. Multi-section stability uses 20/35/50/65/80% closed sections; open or inconsistent sections are explicitly recorded rather than fabricated. Missing holes/slots/fillets are unconfirmed unless measured topology supports them.

Pause policy fixed before fitting: >=10 original Near-to-Strict, >=1 additional Strict beyond preserved baseline, zero Near-to-Reject. Decision: {gate['decision']}. Reject recovery allowed: {gate['reject_stage_allowed']}.

Baseline remains a ranked candidate, so unsupported/invalid smooth fits cannot replace a better valid structure. Every new finalist is independently checked as native CAD before full geometry evaluation. Profile recognition uses least-squares + seeded RANSAC circle, ellipse fitting, rounded rectangle/slot model and line/arc segmentation; a periodic spline with at most 16 interpolation points is allowed only after analytic models fail. Full geometric metrics, not visual smoothness, determine selection.
'''
 (O/'reports/NEAR_PASS_RESCUE_REPORT.md').write_text(neartext)
 profiletext=f'''# Profile reconstruction

V1 selected programs using polyline: {sum('POLYLINE' in r['V1_profile_type'] for r in comp)}. Final programs using polyline: {sum('POLYLINE' in r['V2_profile_type'] for r in comp)}.

{json.dumps(upgrades,indent=2)}

Counts describe selected new profile reconstructions, not every attempted curve or inherited historical improvement. Mixed profiles can belong to multiple rows. Each row includes mean V1 paired metric changes and a separate additional-strict count against the preserved baseline. New fitting attribution and full candidate evidence are available in all_candidates.csv and optimization logs.

Circle/ellipse/arc parameters are solved from numeric contours. Curves are not guessed by the assistant. Composite fitting logs angular coverage/residuals and tangent discontinuities; real corners are retained. Multi-section extraction preserves observed inner loops as cuts. Existing protrusions/boolean structures are retained in Near candidates. This bounded implementation does not claim reliable automatic blind-hole, fillet/chamfer or arbitrary CSG discovery; unconfirmed features remain diagnosis items. Unsupported open-section/freeform parts keep explicitly rejected baselines, rather than being relabeled successful.

Parameter fitting uses local coordinate descent over radial scale, extrusion depth when valid, center and small orientation changes. Revolved curves use similarity transforms to preserve circles/arcs. Proxy objective prioritizes NCD and IoU48 and includes centroid/bbox penalties. Final acceptance always uses unchanged IoU128, 20000-point NCD and original seeds after native code -> STEP -> reload. Display tessellation never enters evaluation.
'''
 profiletext+=f'\nControlled profile contribution: {summary["PROFILE_UPGRADE_STRICT_RESCUE_N"]} additional Strict cases have a selected profile reconstruction while both preserved baseline and same-round parameter-only refinement remain non-Strict. See profile_parameter_control_comparison.csv. This is an empirical matched-optimizer comparison, not a claim that all paired V1 improvement is caused by profile type alone.\n'
 (O/'reports/PROFILE_RECONSTRUCTION_REPORT.md').write_text(profiletext)
 text=f'''# PART_CAD_FITTING_V2_NATIVE

Same 20 objects / 209 parts / 153 major parts. This output name follows the task; it is a new experiment after historical V2/V3, not an overwrite of them. Original V1 (4/63/142) is the requested paired comparison. Preserved strongest V1/V3 baseline retains prior gains; this round's extra gains are separately labeled.

Final: {counts['STRICT_ACCEPT']} Strict / {counts['NEAR_PASS']} Near / {counts['REJECT']} Reject. Major Strict: {major}/153 ({major/153:.2%}). Additional Strict this round: {newstrict}. Parts actually refit: {fitted}. Strict damage: {damage}.

Representation/self-contained/STEP validation pass: {passed}/209. Every newly accepted candidate is checked by the copied independent validator, extended only to count compact arc and spline entities; no geometry thresholds changed. Existing baseline validations are reused only after exact source-code/STEP hash matching. New representation failures cannot reach geometric ranking. Candidate failures and roundtrip discrepancies are retained in logs.

Metrics: NCD median {summary['NCD_MEDIAN_V1']:.6f} -> {summary['NCD_MEDIAN_V2']:.6f}; IoU {summary['IOU_MEDIAN_V1']:.6f} -> {summary['IOU_MEDIAN_V2']:.6f}; centroid {summary['CENTROID_MEDIAN_V1']:.6f} -> {summary['CENTROID_MEDIAN_V2']:.6f}. Weighted score improved/unchanged/worse: {summary['IMPROVED_N']}/{summary['UNCHANGED_N']}/{summary['WORSE_N']}. Ranking prioritizes class then loss, so class promotion can worsen the combined score; individual deltas remain visible.

No P3 rerun, source change, case-specific hardcode, model training, threshold relaxation or assembly optimization. There is no claim that smooth-looking CAD implies source fidelity. Successful geometric training candidates still require the original strict thresholds plus valid representation.

Required tables, source evidence, selected native code/STEP/metrics, candidate logs and profile fitting parameters accompany this report. Render V4 is in ../cad_render_v4/ and deliberately renders unchanged historical V3 STEP, not these newly fitted shapes, to isolate display changes.

Implementation limits: reliable general fillet/chamfer and blind-hole inference is not implemented; no features are invented in their absence. Family search on Reject uses measured revolve/loft hypotheses and preserved baselines under <=8 candidates, <=8 primitive features and <=6 booleans. No unrestricted high-detail freeform solver is claimed. Zero FREEFORM_UNSUPPORTED classifications means no case was conclusively reclassified into that semantic category, not that all freeform geometry is solved.
'''
 (O/'reports/PART_CAD_FITTING_V2_NATIVE_REPORT.md').write_text(text)
 decision=f'''# Next stage decision

REPRESENTATION_GATE = {summary['REPRESENTATION_GATE']}
PART_GEOMETRY_GATE = {summary['PART_GEOMETRY_GATE']}
CAN_START_REASSEMBLY_V2 = {'YES' if summary['CAN_START_REASSEMBLY_V2'] else 'NO'}
CAN_SCALE_TO_100_OBJECTS = NO
NEXT_ALLOWED_STAGE = {summary['NEXT_ALLOWED_STAGE']}

Operational geometry readiness requires at least 20 Strict and major-part Strict >=30%; neither this decision nor the target relaxes per-part strict criteria. Scale100 is prohibited this round even if part targets pass; object reassembly quality has not been improved or evaluated here. Remaining blocker: {summary['PRIMARY_REMAINING_BLOCKER']}.

Near-stage pause gate: {gate}. If blocked, 142 Reject were not refit; their retained results remain in the 209 paired table with fitting_performed=false. Review profile/family/parameter evidence before a further recovery round.
''';(O/'reports/NEXT_STAGE_DECISION.md').write_text(decision);print(json.dumps(summary,indent=2))
if __name__=='__main__':compile_reports()
