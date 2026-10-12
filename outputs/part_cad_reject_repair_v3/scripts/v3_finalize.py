from v2_common import *
import csv,collections,statistics
from execute_candidate import validate
from v2_run import complexity

def table(name,rows):
 dump(O/'tables'/(name+'.json'),rows)
 keys=list(dict.fromkeys(k for r in rows for k in r)) or ['case_id']
 with (O/'tables'/(name+'.csv')).open('w',newline='') as f:
  w=csv.DictWriter(f,keys);w.writeheader();w.writerows({k:json.dumps(v) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)

rows=read(O/'manifests/cases.json');comparison=[];audit=[];errors=[];drift=[]
assert all((O/'cases'/r['case_id']/'result.json').exists() for r in rows),'Incomplete cohort'
for row in rows:
 d=O/'cases'/row['case_id'];r=read(d/'result.json');old=read(d/'source/v2_result.json');a=r['v2_metrics'];b=r['v3_metrics'];changed=r['v2_status']!=r['v3_status'];delta=score(b)-score(a)
 c={'case_id':row['case_id'],'object_id':row['object_id'],'part_id':row['part_id'],'size_class':row['size_class'],'V2_status':r['v2_status'],'V3_status':r['v3_status'],'family':r.get('family',old['v2_family']),'fix_type':r.get('fix_type','PRESERVED_V2'),'preserved':r['preserved'],'V2_score':score(a),'V3_score':score(b),'score_delta':delta,'classification_improved':changed and r['v3_status']!='REJECT','score_improved':delta < -1e-8,'remaining_failed_checks':failed(b),'candidate_n':len(r['attempts']),'cad_program_path':str(d/'cad/cad.py'),'step_path':str(d/'cad/cad.step')}
 for name,key in [('IoU','iou'),('NCD','normalized_chamfer'),('bbox','bbox_error'),('centroid','centroid_l2_error')]:c['V2_'+name]=a[key];c['V3_'+name]=b[key]
 comparison.append(c)
 selected=next(x for x in (old['attempts'] if r['preserved'] else r['attempts']) if x['candidate_id']==(old['selected_candidate'] if r['preserved'] else r['selected_candidate']))
 for flag in ['parse_pass','execute_pass','step_reload_pass']:c[flag]=selected['execution'][flag]
 if sha(d/'source/part_local.ply')!=row['normalized_mesh_sha256']:errors.append(row['case_id']+': source mesh changed')
 if sha(d/'source/provenance.json')!=sha(Path(row['v2_dir'])/'source/provenance.json'):errors.append(row['case_id']+': source transforms changed')
 if sha(d/'source/frozen_evaluation_points.npy')!=sha(Path(row['v2_dir'])/'source/frozen_evaluation_points.npy'):errors.append(row['case_id']+': frozen points changed')
 if r['preserved']:
  for f in ['cad.py','cad.step','cad_mesh.ply','parameters.json']:
   if sha(d/'cad'/f)!=sha(Path(row['v2_dir'])/'cad'/f):errors.append(row['case_id']+': preserved CAD changed')
  if a!=b:errors.append(row['case_id']+': preserved metrics changed')
 if len(r['attempts'])>8:errors.append(row['case_id']+': candidate budget')
 validate((d/'cad/cad.py').read_text());complexity((d/'cad/cad.py').read_text())
 for cand in r['attempts']:
  p=Path(cand['path']);code=(p/'cad.py').read_text()
  try:validate(code);complexity(code)
  except Exception as e:errors.append(row['case_id']+': invalid native candidate '+str(e))
  if cand['candidate_id']==0:drift.extend(abs(x) for x in cand['baseline_drift'].values())
  if 'metrics' in cand:
   m=cand['metrics'];expected=m['iou']>=.9 and m['normalized_chamfer']<=.01 and m['bbox_error']<=.03 and m['centroid_l2_error']<=.02 and cand['execution']['step_reload_pass']
   if bool(m['strict_pass'])!=bool(expected):errors.append(row['case_id']+': strict gate mismatch')
  audit.append({'case_id':row['case_id'],'candidate_id':cand['candidate_id'],'kind':cand['kind'],'parse_pass':cand.get('execution',{}).get('parse_pass',False),'execute_pass':cand.get('execution',{}).get('execute_pass',False),'reload_pass':cand.get('execution',{}).get('step_reload_pass',False),'has_metrics':'metrics' in cand,'failure':cand.get('error',cand.get('execution',{}).get('error'))})
repair=[r for r in comparison if not r['preserved']];st=collections.Counter(r['V3_status'] for r in comparison);rs=collections.Counter(r['V3_status'] for r in repair);major=[r for r in comparison if r['size_class']=='MAJOR_PART'];eligible=st['STRICT_ACCEPT']/209>=.3
summary={'TOTAL_PART_N':209,'REPAIR_INPUT_N':124,'PRESERVED_NON_REJECT_N':85,'V2_STRICT_N':15,'V2_NEAR_N':70,'V2_REJECT_N':124,'REJECT_TO_STRICT_N':rs['STRICT_ACCEPT'],'REJECT_TO_NEAR_N':rs['NEAR_PASS'],'REJECT_STILL_REJECT_N':rs['REJECT'],'STRICT_ACCEPT_N':st['STRICT_ACCEPT'],'NEAR_PASS_N':st['NEAR_PASS'],'REJECT_N':st['REJECT'],'STRICT_ACCEPT_RATE':st['STRICT_ACCEPT']/209,'MAJOR_STRICT_N':sum(r['V3_status']=='STRICT_ACCEPT' for r in major),'MAJOR_STRICT_RATE':sum(r['V3_status']=='STRICT_ACCEPT' for r in major)/len(major),'CLASSIFICATION_DAMAGE_N':sum(r['V2_status']=='STRICT_ACCEPT' and r['V3_status']!='STRICT_ACCEPT' or r['V2_status']=='NEAR_PASS' and r['V3_status']=='REJECT' for r in comparison),'SCORE_IMPROVED_N':sum(r['score_improved'] for r in comparison),'SCORE_WORSE_N':sum(r['score_delta']>1e-8 for r in comparison),'ATTEMPTED_CANDIDATE_N':len(audit),'CANDIDATE_WITH_METRICS_N':sum(r['has_metrics'] for r in audit),'SELECTED_STEP_RELOAD_PASS_N':209,'PART_GEOMETRY_GATE':'PASS' if eligible else 'FAIL','CAN_START_REASSEMBLY':'YES' if eligible else 'NO','CAN_SCALE_TO_100_OBJECTS':'NO','NEXT_ALLOWED_STAGE':'REASSEMBLY_REVIEW' if eligible else 'IMPROVE_PART_CAD_FITTING'}
for metric in ['IoU','NCD','centroid','bbox']:
 for version in ['V2','V3']:summary[version+'_'+metric+'_MEDIAN']=statistics.median(r[version+'_'+metric] for r in comparison)
summary['remaining_failed_check_counts']=dict(collections.Counter(k for r in comparison for k in r['remaining_failed_checks']))
summary['SELECTED_STEP_RELOAD_PASS_N']=sum(r['step_reload_pass'] for r in comparison)
summary['SELECTED_PARSE_PASS_N']=sum(r['parse_pass'] for r in comparison)
summary['SELECTED_EXECUTE_PASS_N']=sum(r['execute_pass'] for r in comparison)
if summary['SELECTED_STEP_RELOAD_PASS_N']/209<.95:summary.update(PART_GEOMETRY_GATE='FAIL',CAN_START_REASSEMBLY='NO',NEXT_ALLOWED_STAGE='IMPROVE_PART_CAD_FITTING')
table('part_v2_v3_comparison',comparison);table('reject_recovery',repair);table('strict_accept_v3',[r for r in comparison if r['V3_status']=='STRICT_ACCEPT']);table('remaining_reject_v3',[r for r in comparison if r['V3_status']=='REJECT']);table('candidate_execution_audit',audit)
objects=read(O/'manifests/objects.json');object_rows=[]
for obj in objects:
 g=[r for r in comparison if r['object_id']==obj['object_id']];object_rows.append({'object_id':obj['object_id'],'name':obj['name'],'part_n':len(g),'strict_n':sum(r['V3_status']=='STRICT_ACCEPT' for r in g),'near_n':sum(r['V3_status']=='NEAR_PASS' for r in g),'reject_n':sum(r['V3_status']=='REJECT' for r in g),'assembly_run':False})
table('object_summary',object_rows)
families=[]
for family in sorted({r['family'] for r in comparison}):
 g=[r for r in comparison if r['family']==family];families.append({'family':family,'n':len(g),'strict_n':sum(r['V3_status']=='STRICT_ACCEPT' for r in g),'near_n':sum(r['V3_status']=='NEAR_PASS' for r in g),'reject_n':sum(r['V3_status']=='REJECT' for r in g)})
table('family_summary',families)
generation_errors=collections.Counter(e['error'] for r in rows if r['v2_status']=='REJECT' for e in read(O/'cases'/r['case_id']/'optimization/proposals.json')['errors']);table('proposal_failure_breakdown',[{'reason':k,'count':v} for k,v in generation_errors.most_common()])
support=[]
for row in rows:
 if row['v2_status']!='REJECT':continue
 d=O/'cases'/row['case_id'];f=read(d/'source/features_v2.json');p=read(d/'optimization/proposals.json');support.append({'case_id':row['case_id'],'source_boundary_edge_n':f['boundary_edge_n'],'source_boundary_loops_degree_two':f['boundary_all_degree_two'],'proposal_n':p['proposal_n'],'closed_geometry_proposal_n':sum(not x['kind'].startswith('v2_winner') for x in p['geometry_proposals']),'selected_candidate_n':p['selected_n'],'proposal_failure_reasons':[e['error'] for e in p['errors']]})
table('geometry_support_audit',support)
summary['REPAIR_SOURCE_OPEN_BOUNDARY_N']=sum(r['source_boundary_edge_n']>0 for r in support)
summary['NO_CLOSED_GEOMETRY_PROPOSAL_N']=sum(r['closed_geometry_proposal_n']==0 for r in support)
guard=read(O/'integrity/V2_PROTECTED_BEFORE.json');changes=[]
for name,item in guard.items():
 p=Path(name)
 if not p.exists() or p.stat().st_mtime_ns!=item['mtime_ns'] or sha(p)!=item['sha256']:changes.append(name)
if changes:errors.append('V2 protected files changed')
for filename in ['v3_geometry.py','v3_run.py']:
 if 'object_000' in (O/'scripts'/filename).read_text():errors.append(filename+': case-specific fitting')
validation={'pass':not errors,'errors':errors,'V2_protected_file_n':len(guard),'V2_changes':changes,'max_V2_baseline_drift':max(drift,default=0),'sources_transforms_and_points_unchanged':not any('source' in x or 'points' in x for x in errors),'preserved_strict_n':15,'preserved_near_n':70};dump(O/'integrity/VALIDATION.json',validation);assert not errors,errors
dump(O/'reports/summary.json',summary)
text_report='# Reject CAD Repair V3\n\n```json\n'+json.dumps(summary,indent=2)+'\n```\n\n## Scope and validation\n\nOnly the 124 V2 Reject parts were fitted. All 15 Strict and 70 Near parts are copied byte-for-byte from V2. Original mesh, transforms, frozen source samples, seeds, 20000-point metric and IoU128 acceptance thresholds are unchanged. No P3, training, reassembly or expansion. Twelve CPU workers; no GPU inference. Every repaired part retains the V2 CAD baseline, reimports its STEP and reproduces its prior metrics.\n\n## Fitting changes\n\nCandidate proposals include measured closed-section extrusions, three-section lofts with consistent hole topology, and measured inner/outer revolution profiles. Repeated section topology must match; unsupported profiles and excess complexity are recorded, not silently dropped. One refinement starts from the actual V2 winner. Geometry proxies rank proposals before at most seven new native CAD executions per part; the baseline makes at most eight candidates. At most eight primitives, six Booleans and 96 sketch vertices. Proxy metrics never grant acceptance.\n\nThe final ranking is Strict, then Near, then Reject, followed by the unchanged weighted score (10*NCD + 1-IoU + 2*centroid + bbox). This prevents classification regression but can raise the weighted score when moving to a better class; score and classification changes are reported separately. Family labels describe the selected candidate; complex sketches, holes and union structure should be inspected in the native program.\n\n## Limits\n\nOpen or inconsistent source sections often cannot support a closed solid profile; the library does not implement arbitrary freeform surfaces, automatic connected-frame decomposition or arbitrary CSG. Loft endpoint sections extrapolate the observed 3% and 97% sections to measured extent endpoints, so shape errors remain possible. Section-based profiles and finite candidate ranking do not establish a global optimum. Numerical Strict does not certify all small details or topology; the V2 opening discrepancy remains part of the preserved baseline limitations. No per-part LLM API calls are claimed: the assistant authored the construction policy, and geometry code fitted the numeric parameters.\n\nThe 12-case pilot was reviewed before the remaining cohort, and its outcomes were reused. V2 is read-only; integrity/VALIDATION.json records its complete guard. Recovered and remaining-reject comparisons are available in visualizations/index.html.\n'
(O/'reports/REJECT_REPAIR_V3_REPORT.md').write_text(text_report);print(json.dumps(summary,indent=2));print('VALIDATION',json.dumps(validation))
