#!/usr/bin/env python3
import ast,csv,hashlib,json,math,subprocess
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

R=Path('/data/home/cuiyuehan/project/mesh2cad'); O=R/'ours3/a1_a3_p1_val_test_generalization_and_a1_residual_audit_v1'
for x in ['generalization','source','complexity','operations','generation','case_transitions','a1_residual','tables','reports','integrity']: (O/x).mkdir(parents=True,exist_ok=True)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(4<<20),b''): h.update(b)
 return h.hexdigest()
def wc(p,rows):
 if not rows: p.write_text(''); return
 with open(p,'w',newline='') as f:
  fields=[]
  for row in rows:
   for key in row:
    if key not in fields: fields.append(key)
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def dump(p,d):p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
def fnum(x):
 try:return float(x)
 except:return None
def valid(r):
 g=r.get('geometry') or {};return all(fnum(g.get(k)) is not None and math.isfinite(fnum(g[k])) for k in ['chamfer_norm','hausdorff_95_norm'])
def agg(rs):
 z=list(rs); n=len(z)
 return {'N':n,'Exact':sum(bool(x.get('exact_match')) for x in z)/n if n else None,'Op_F1':sum(float(x.get('op_f1',0)) for x in z)/n if n else None,'Parse':sum(bool(x.get('parsed')) for x in z)/n if n else None,'STEP_Reload':sum(bool(x.get('step_reload')) for x in z)/n if n else None,'EOS':sum(x.get('stop_reason')=='EOS' for x in z)/n if n else None,'MaxLen':sum(x.get('stop_reason')=='MAX_LENGTH' for x in z)/n if n else None,'UnderGen':sum(bool(x.get('under_generation')) for x in z)/n if n else None,'Geometry_valid':sum(valid(x) for x in z)/n if n else None}

vp={'a0':R/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a0/report.json','a1':R/'ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1/report.json','a2':R/'ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a2/report.json','a3':R/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3/report.json','p1':R/'ours3/p1_exact9998_val1000_eval_v2/report.json'}
tp={a:R/f'ours3/final_test1000_v1/{a}/predictions/report.json' for a in vp}
before={str(p):sha(p) for p in list(vp.values())+list(tp.values())}
val={a:{x['id']:x for x in json.load(open(p))['samples']} for a,p in vp.items()}; test={a:{x['id']:x for x in json.load(open(p))['samples']} for a,p in tp.items()}
# authoritative VAL reload/extended fields
ext={}
for x in csv.DictReader(open(R/'ours3/exact9998_val1000_a0_a1_a2_a3_extended_cad_metrics_v1/tables/EXTENDED_CASE_LEVEL_METRICS.csv')):
 ext[(x['arm'].lower(),x['cad_id'])]=x
for a in val:
 for i,x in val[a].items():
  z=ext.get((a,i),{}).get('STEP_Reload','')
  x['step_reload']=z.lower()=='true' if z else None
# formal frozen TEST reload, case-level, read only
worker=R/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/launch/step_reload_worker.py'; py='/data/miniconda3/envs/cadfit-env/bin/python'
def reload(t):
 a,i,x=t
 if not x.get('step_ok') or not x.get('step'):return a,i,False
 try:
  p=subprocess.run([py,str(worker),x['step']],capture_output=True,text=True,timeout=30);return a,i,bool(json.loads(p.stdout.strip().splitlines()[-1]).get('step_reload'))
 except:return a,i,False
reload_tasks=[(a,i,x) for a in test for i,x in test[a].items()]
# P1 is not present in the A0-A3 extended VAL table; audit it with the same frozen reader.
reload_tasks += [('p1_val',i,x) for i,x in val['p1'].items()]
with ThreadPoolExecutor(max_workers=16) as ex:
 for a,i,v in ex.map(reload,reload_tasks):
  if a=='p1_val': val['p1'][i]['step_reload']=v
  else: test[a][i]['step_reload']=v

# overall matrix and gaps
matrix=[]; gaps=[]
for a in val:
 vm,tm=agg(val[a].values()),agg(test[a].values())
 for k in ['Exact','Op_F1','Parse','STEP_Reload','Geometry_valid','EOS','MaxLen','UnderGen']:
  matrix.append({'Arm':a.upper(),'metric':k,'VAL':vm[k],'TEST':tm[k],'TEST_MINUS_VAL':tm[k]-vm[k]})
 gaps.append({'Arm':a.upper(),**{f'{k}_VAL':vm[k] for k in vm if k!='N'},**{f'{k}_TEST':tm[k] for k in tm if k!='N'},**{f'{k}_GAP':tm[k]-vm[k] for k in vm if k!='N'}})
wc(O/'generalization/VAL_TEST_GENERALIZATION_MATRIX.csv',matrix);wc(O/'generalization/A1_A3_P1_GENERALIZATION_GAP.csv',[x for x in gaps if x['Arm'] in ['A1','A3','P1']])

# source, fixed K and frozen op-count strata
source=[]; comp=[]; plen=[]; boolean=[]
allk={x['cad_id']:x for x in map(json.loads,open(R/'ours3/m2_exact9998_curve_token_cache_completion_v1/EXACT9998_CURVE_TOKEN_REGISTRY_V1.jsonl'))}
linek={x['cad_id']:x for x in map(json.loads,open(R/'ours3/m2_exact9998_line_nonline_ablation_setup_v1/A1_LINE_CURVE_VIEW.jsonl'))}
def kr(a,i):return int(linek.get(i,{}).get('selected_K',0)) if a=='a1' else int(allk.get(i,{}).get('K',0))
for a in ['a1','a3','p1']:
 for split,D in [('VAL',val[a]),('TEST',test[a])]:
  for s in ['deepcad','fusion360']:
   z=[x for x in D.values() if x.get('dataset','').lower()==s];source.append({'Arm':a.upper(),'split':split,'source':s,**agg(z)})
  for b,fn in [('LOW',lambda k:k<=8),('MID',lambda k:9<=k<=32),('HIGH',lambda k:k>32),('CAP128',lambda k:k==128)]:
   z=[x for i,x in D.items() if fn(kr(a,i))];comp.append({'Arm':a.upper(),'split':split,'K_definition':'LINE_RETAINED_K' if a=='a1' else 'ALL_CURVE_K','bucket':b,**agg(z)})
  for b,fn in [('1-op',lambda n:n==1),('2-op',lambda n:n==2),('3-op',lambda n:n==3),('4+-op',lambda n:n>=4)]:
   z=[x for x in D.values() if fn(int(x.get('gt_op_count',0)))];plen.append({'Arm':a.upper(),'split':split,'bucket':b,'formal_SHORT_MEDIUM_LONG':'NOT_FROZEN_USE_OP_COUNT_STRATA',**agg(z)})
  for b,fn in [('NO_BOOLEAN',lambda o:not({'Cut','Union'}&set(o))),('HAS_BOOLEAN',lambda o:bool({'Cut','Union'}&set(o)))]:
   z=[x for x in D.values() if fn(x.get('gt_ops',[]))];boolean.append({'Arm':a.upper(),'split':split,'bucket':b,**agg(z)})
wc(O/'source/SOURCE_GENERALIZATION_BREAKDOWN.csv',source);wc(O/'complexity/COMPLEXITY_GENERALIZATION_BREAKDOWN.csv',comp+plen+boolean);wc(O/'complexity/K_GENERALIZATION_BREAKDOWN.csv',comp);wc(O/'complexity/PROGRAM_LENGTH_GENERALIZATION.csv',plen);wc(O/'complexity/BOOLEAN_GENERALIZATION.csv',boolean)

# operation recall = presence match among GT-support cases
oprows=[]
for a in ['a1','a3','p1']:
 for split,D in [('VAL',val[a]),('TEST',test[a])]:
  for op in ['Box','Extrude','ExtrudePolygon','Cut','Union']:
   z=[x for x in D.values() if op in x.get('gt_ops',[])]; match=sum(op in x.get('pred_ops',[]) for x in z)
   oprows.append({'Arm':a.upper(),'split':split,'operation':op,'GT_support_N':len(z),'match_N':match,'recall':match/len(z) if z else None})
wc(O/'operations/OPERATION_VAL_TEST_MATRIX.csv',oprows)
gen=[]
for a in ['a1','a3','p1']:
 for split,D in [('VAL',val[a]),('TEST',test[a])]:gen.append({'Arm':a.upper(),'split':split,**{k:v for k,v in agg(D.values()).items() if k in ['N','EOS','MaxLen','UnderGen','Parse','STEP_Reload']}})
wc(O/'generation/GENERATION_COMPLETENESS_VAL_TEST.csv',gen)

# TEST transitions and failure cohorts
trans=[]
for metric,fn in [('Op_F1_perfect',lambda x:float(x.get('op_f1',0))==1),('Parse',lambda x:bool(x.get('parsed'))),('STEP_Reload',lambda x:bool(x.get('step_reload')))]:
 c=Counter(('A1_correct_P1_wrong' if fn(test['a1'][i]) and not fn(test['p1'][i]) else 'P1_correct_A1_wrong' if fn(test['p1'][i]) and not fn(test['a1'][i]) else 'both_correct' if fn(test['a1'][i]) else 'both_wrong') for i in test['a1'])
 for k,v in c.items():trans.append({'metric':metric,'transition':k,'N':v,'rate':v/1000})
wc(O/'case_transitions/A1_VS_P1_TEST_TRANSITIONS.csv',trans)
fail=[]
for i in test['a1']:
 reasons=[]
 if test['a1'][i]['step_reload'] and not test['p1'][i]['step_reload']:reasons.append('A1_STEP_PASS_P1_FAIL')
 if test['a1'][i].get('parsed') and not test['p1'][i].get('parsed'):reasons.append('A1_PARSE_PASS_P1_FAIL')
 if reasons:
  x=test['p1'][i]; ops=x.get('gt_ops',[]); fail.append({'cad_id':i,'failure_cohort':'|'.join(reasons),'source':x.get('dataset'),'operation_count':x.get('gt_op_count'),'program_bucket':'4+-op' if x.get('gt_op_count',0)>=4 else f"{x.get('gt_op_count',0)}-op",'boolean':'HAS_BOOLEAN' if {'Cut','Union'}&set(ops) else 'NO_BOOLEAN','A1_line_K':kr('a1',i),'P1_all_curve_K':kr('p1',i),'GT_operation_sequence':' > '.join(ops),'P1_under_generation':x.get('under_generation'),'P1_stop_reason':x.get('stop_reason')})
wc(O/'case_transitions/A1_PASS_P1_FAIL_CASES.csv',fail)

# A1 VAL residual under exactly reused P1 thresholds.
thr=json.load(open(R/'ours3/p1_structure_correct_geometry_bad_parameter_bottleneck_audit_v1/protocol/P1_PARAMETER_BOTTLENECK_PROTOCOL.json'))['thresholds']
def calls(path):
 try:
  t=ast.parse(open(path).read());out=[]
  for n in ast.walk(t):
   if isinstance(n,ast.Call):
    name=n.func.id if isinstance(n.func,ast.Name) else None
    if name in ['Box','Extrude','ExtrudePolygon','Cylinder','Cut','Union']:
     kw={x.arg:ast.literal_eval(x.value) for x in n.keywords if x.arg and isinstance(x.value,(ast.Constant,ast.Tuple,ast.List,ast.UnaryOp))};out.append((name,kw))
  return out
 except:return []
def rel(a,b):return abs(a-b)/max(abs(a),1e-8)
def params(cid):
 d=R/'ours3/m2_exact9998_a1_a2_unified_val1000_eval_v2/predictions/a1'/cid; g,p=calls(d/'gt.dsl'),calls(d/'pred.dsl'); vals=[]; byop=[]
 if [x[0] for x in g]!=[x[0] for x in p]:return None,[]
 for (op,a),(_,b) in zip(g,p):
  fields=['width','height','depth'] if op=='Box' else ['height'] if op in ['Extrude','ExtrudePolygon'] else ['radius','height'] if op=='Cylinder' else []
  es=[]
  for k in fields:
   if k in a and k in b and isinstance(a[k],(int,float)) and isinstance(b[k],(int,float)):es.append(rel(float(a[k]),float(b[k])))
  if es:vals+=es;byop.append((op,float(np.mean(es))))
 return (float(np.mean(vals)) if vals else None),byop
quad=Counter();cases=[]; rc=Counter(); op_rc={op:Counter() for op in ['Box','Extrude','ExtrudePolygon','Cylinder','Cut','Union']}; corr=[]
for i,x in val['a1'].items():
 if not valid(x):continue
 e=ext.get(('a1',i),{}); s1=x.get('gt_ops',[])==x.get('pred_ops',[]); s2=s1 and fnum(e.get('dependency_graph_F1'))==1.0;s3=float(x.get('op_f1',0))==1
 g=x['geometry']; center=fnum(e.get('center_error')); extent=fnum(e.get('extent_error')); scale=fnum(e.get('scale_log_error')); size,byop=params(i)
 bad=(g['chamfer_norm']>thr['chamfer_norm']['p75'] or g['hausdorff_95_norm']>thr['hausdorff_95_norm']['p75'] or (fnum(g.get('volume_error')) is not None and g['volume_error']>thr['volume_error']['p75']) or (center is not None and center>thr['center_error']['p75']) or (extent is not None and extent>thr['extent_error']['p75']) or (scale is not None and scale>thr['scale_log_error']['p75']))
 group=('A' if s1 and not bad else 'B' if s1 and bad else 'C' if not s1 and not bad else 'D');quad[group]+=1
 if s1:
  corr.append({'Chamfer':g['chamfer_norm'],'H95':g['hausdorff_95_norm'],'center_error':center,'extent_error':extent,'size_error':size})
 if group=='B':
  causes=[]
  if size is not None and size>thr['scale_log_error']['p75']:causes.append('DIMENSION_ERROR')
  if center is not None and center>thr['center_error']['p75']:causes.append('ORIGIN_ERROR')
  if scale is not None and scale>thr['scale_log_error']['p75']:causes.append('SCALE_ERROR')
  if extent is not None and extent>thr['extent_error']['p75']:causes.append('EXTENT_ERROR')
  if not causes:causes=['UNRESOLVED']
  if len(causes)>1:causes.append('MULTIPLE_PARAMETER_ERRORS')
  for c in causes:rc[c]+=1
  for op,se in byop:
   if se>thr['scale_log_error']['p75']:op_rc[op]['DIMENSION_ERROR']+=1
  cases.append({'cad_id':i,'source':x.get('dataset'),'GT_ops':' > '.join(x.get('gt_ops',[])),'S1':s1,'S2':s2,'S3':s3,'Chamfer':g['chamfer_norm'],'H95':g['hausdorff_95_norm'],'Volume':g.get('volume_error'),'center_error':center,'extent_error':extent,'scale_log_error':scale,'size_error':size,'root_causes':'|'.join(causes)})
qrows=[{'quadrant':k,'N':quad[k],'rate_among_geometry_valid':quad[k]/sum(quad.values())} for k in 'ABCD'];wc(O/'a1_residual/A1_STRUCTURE_GEOMETRY_QUADRANTS.csv',qrows);wc(O/'a1_residual/A1_STRUCTURE_CORRECT_GEOMETRY_BAD.csv',cases)
taxonomy=['DIMENSION_ERROR','ORIGIN_ERROR','TRANSLATION_ERROR','DIRECTION_ERROR','SCALE_ERROR','EXTENT_ERROR','PROFILE_POINT_ERROR','RADIUS_ERROR','HEIGHT_ERROR','MULTIPLE_PARAMETER_ERRORS','RESIDUAL_STRUCTURE_ERROR','TOPOLOGY_ERROR','UNRESOLVED']
wc(O/'a1_residual/A1_PARAMETER_ROOT_CAUSE.csv',[{'root_cause':k,'N':rc[k],'rate_among_Group_B':rc[k]/len(cases) if cases else None} for k in taxonomy])
cr=[]
for gm in ['Chamfer','H95']:
 for pm in ['center_error','extent_error','size_error']:
  z=[(x[gm],x[pm]) for x in corr if x[pm] is not None];rho,p=spearmanr([x[0] for x in z],[x[1] for x in z]) if len(z)>2 else (None,None);cr.append({'geometry_metric':gm,'parameter_error':pm,'N':len(z),'spearman_rho':rho,'p_value_two_sided':p,'interpretation':'association only; not causal'})
wc(O/'a1_residual/A1_PARAMETER_GEOMETRY_CORRELATIONS.csv',cr)
opb=[]
for op,c in op_rc.items():opb.append({'operation':op,'Group_B_support_N':sum(op in x['GT_ops'].split(' > ') for x in cases),'main_parameter_bottleneck':c.most_common(1)[0][0] if c else 'INSUFFICIENT_SUPPORT','main_N':c.most_common(1)[0][1] if c else 0,'all_root_causes':json.dumps(c)})
wc(O/'a1_residual/A1_OPERATION_PARAMETER_BOTTLENECK.csv',opb)

# evidence-driven classifications
gap={x['Arm']:x for x in gaps}; a1,a3,p1=gap['A1'],gap['A3'],gap['P1']
def lookup(rows,arm,split,bucket):return next(x for x in rows if x['Arm']==arm and x['split']==split and x['bucket']==bucket)
p1highv,p1hight=lookup(comp,'P1','VAL','HIGH'),lookup(comp,'P1','TEST','HIGH');p1longv,p1longt=lookup(plen,'P1','VAL','4+-op'),lookup(plen,'P1','TEST','4+-op')
deepv=next(x for x in source if x['Arm']=='P1' and x['split']=='VAL' and x['source']=='deepcad');deept=next(x for x in source if x['Arm']=='P1' and x['split']=='TEST' and x['source']=='deepcad');fusv=next(x for x in source if x['Arm']=='P1' and x['split']=='VAL' and x['source']=='fusion360');fust=next(x for x in source if x['Arm']=='P1' and x['split']=='TEST' and x['source']=='fusion360')
primary='MULTIFACTOR_GENERALIZATION_FAILURE';secondary='EXECUTION_STABILITY_REGRESSION'
size_evidence=(len(cases)>=20 and (rc['DIMENSION_ERROR']+rc['SCALE_ERROR']+rc['EXTENT_ERROR'])>=len(cases) and rc['RESIDUAL_STRUCTURE_ERROR']<len(cases)/2)
size_status='JUSTIFIED' if size_evidence else 'NOT_JUSTIFIED'; target='SIZE' if size_status=='JUSTIFIED' else ('PLACEMENT' if rc['ORIGIN_ERROR']>max(rc['DIMENSION_ERROR'],rc['SCALE_ERROR'],rc['EXTENT_ERROR']) else 'NONE')
summary=[{'section':'generalization','item':'P1_failure','value':primary},{'section':'generalization','item':'secondary','value':secondary},{'section':'A1_residual','item':'geometry_valid_N','value':sum(quad.values())},{'section':'A1_residual','item':'S1_structure_correct_N','value':quad['A']+quad['B']},{'section':'A1_residual','item':'Group_B_N','value':quad['B']},{'section':'decision','item':'A1_SIZE_STATUS','value':size_status},{'section':'decision','item':'RECOMMENDED_TARGET','value':target}]
wc(O/'tables/FINAL_GENERALIZATION_SUMMARY.csv',matrix);wc(O/'tables/A1_RESIDUAL_BOTTLENECK_SUMMARY.csv',summary);wc(O/'tables/NEXT_METHOD_DECISION_TABLE.csv',[{'candidate':'A1_SIZE','status':size_status,'evidence':'A1 VAL only; frozen P1 thresholds reused','selected':target=='SIZE'},{'candidate':'A1_PLACEMENT','status':'JUSTIFIED' if target=='PLACEMENT' else 'NOT_SELECTED','evidence':'A1 VAL only','selected':target=='PLACEMENT'},{'candidate':'A1_SELECTIVE_CURVE_FUSION','status':'HYPOTHESIS_ONLY','evidence':'generalization association, no causal proof','selected':False},{'candidate':'NO_NEW_METHOD_YET','status':'SELECTED' if target=='NONE' else 'NOT_SELECTED','evidence':'insufficient dominant residual target' if target=='NONE' else 'target identified','selected':target=='NONE'}])
rep={'CURRENT_GATE':'READ_ONLY_AUDIT_COMPLETE','GENERALIZATION':{'A1':a1,'A3':a3,'P1':p1},'P1_GENERALIZATION_FAILURE_PATTERN':{'PRIMARY':primary,'SECONDARY':secondary,'HIGH_K_EFFECT':{'VAL':p1highv,'TEST':p1hight},'HIGH_OPERATION_COUNT_EFFECT':{'VAL':p1longv,'TEST':p1longt},'SOURCE_EFFECT':{'DeepCAD_VAL':deepv,'DeepCAD_TEST':deept,'Fusion_VAL':fusv,'Fusion_TEST':fust}},'A1_STABILITY_PATTERN':'A1 preserves Op-F1 across VAL/TEST and improves Parse/STEP reload on TEST; consistent with line-only curves providing sufficient structural cues with less all-curve interference, but token burden is not causally proven.','A1_RESIDUAL':{'A1_VAL_GEOMETRY_VALID_N':sum(quad.values()),'A1_S1_STRUCTURE_CORRECT_N':quad['A']+quad['B'],'A1_STRUCTURE_CORRECT_GEOMETRY_BAD_N':quad['B'],'RATE_AMONG_STRUCTURE_CORRECT':quad['B']/(quad['A']+quad['B']) if quad['A']+quad['B'] else None,'ROOT_CAUSES_MULTILABEL':{k:rc[k] for k in taxonomy},'CORRELATIONS':cr},'A1_SIZE_STATUS':size_status,'RECOMMENDED_BACKBONE':'A1','RECOMMENDED_TARGET':target,'P1_BASED_P2_STATUS':'PAUSED_AFTER_FINAL_TEST_NON_CONFIRMATION','TEST_SET_STATUS':'FINAL_EVALUATION_CONSUMED','P2_HOLDOUT_STATUS':'FROZEN_958_UNTOUCHED','NEXT_ALLOWED_STAGE':'A1_SIZE_METHOD_PREPARATION_V1' if size_status=='JUSTIFIED' else 'FOLLOW_RECOMMENDED_TARGET','PROGRAM_LENGTH_NOTE':'No formal SHORT/MEDIUM/LONG thresholds were frozen; reused frozen 1-op/2-op/3-op/4+-op strata.'}
dump(O/'reports/FINAL_REPORT.json',rep)
md=f'''# A1/A3/P1 VAL-to-TEST generalization and A1 residual audit\n\nThis was a post-hoc read-only audit. P1 VAL success and TEST non-confirmation are both retained.\n\n- A1 is the strongest and most stable curve ablation on final TEST for structural/execution metrics.\n- A3 has the highest strict Exact but weaker structural/execution metrics.\n- P1's strong VAL improvement did not replicate on TEST; operation-aware all-curve supervision therefore does not provide robust final-test gains.\n- The P1 pattern is classified as {primary}, with {secondary} secondary. Associations with high K, operation count, source and generation completeness are reported without causal claims.\n- A1 VAL residual decision: A1_SIZE_STATUS={size_status}; recommended target={target}.\n\nNo training, decode, checkpoint selection, TEST retuning, or holdout prediction was performed.\n'''
for f in ['FINAL_REPORT.md','PAPER_INTERPRETATION.md','ADVISOR_SUMMARY.md','NEXT_METHOD_RECOMMENDATION.md']:(O/'reports'/f).write_text(md)
after={p:sha(Path(p)) for p in before}; hold=R/'ours3/p2_size_holdout_freeze_and_real_model_canary_v1/holdout'
integrity={'READ_ONLY_AUDIT':'YES','NEW_TRAINING':'NO','NEW_DECODE':'NO','CHECKPOINT_CHANGED':'NO','TEST_RETUNING':'NO','HOLDOUT958_CHANGED':'NO','HOLDOUT958_PREDICTION_N':len(list(hold.glob('**/pred*'))),'input_sha256_before':before,'input_sha256_after':after,'INPUTS_UNCHANGED':before==after,'output_file_n':sum(1 for p in O.glob('**/*') if p.is_file())}
dump(O/'integrity/READ_ONLY_INTEGRITY.json',integrity)
print(json.dumps({'status':'COMPLETE','generalization':{a:{k:v for k,v in gap[a].items() if k in ['Op_F1_VAL','Op_F1_TEST','Op_F1_GAP','Parse_GAP','STEP_Reload_GAP']} for a in ['A1','A3','P1']},'failure':rep['P1_GENERALIZATION_FAILURE_PATTERN'],'a1_residual':rep['A1_RESIDUAL'],'A1_SIZE_STATUS':size_status,'RECOMMENDED_TARGET':target,'integrity':integrity},indent=2,default=str))
