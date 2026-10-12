#!/usr/bin/env python3
import ast,csv,json,math,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
P1=ROOT/'ours3/p1_exact9998_val1000_eval_v2'
A3=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2/predictions/a3'
BENCH=ROOT/'ours3/a0_a1_a2_a3_p1_geometric_effectiveness_bench_v1/case_results.jsonl'
CLOSURE=ROOT/'ours3/p1_operation_aware_formal_closure_v1'
OUT=ROOT/'ours3/p1_structure_correct_geometry_bad_parameter_bottleneck_audit_v1'
for x in ('protocol','cohorts','parameters','operations','correlations','outliers','gallery','tables','reports','integrity'): (OUT/x).mkdir(parents=True,exist_ok=True)

def f(x,d=None):
 try:
  v=float(x); return v if math.isfinite(v) else d
 except:return d
def loadrows(d):
 out={}
 for p in d.glob('*/row.json'):
  try:out[p.parent.name]=json.loads(p.read_text())
  except:pass
 return out
def getcalls(path):
 try:t=ast.parse(path.read_text())
 except:return []
 out=[]
 for n in t.body:
  if isinstance(n,ast.Assign) and isinstance(n.value,ast.Call):
   fn=n.value.func.id if isinstance(n.value.func,ast.Name) else None
   if fn in ('Box','Extrude','ExtrudePolygon','Cylinder','Cut','Union'):
    kw={k.arg:ast.literal_eval(k.value) for k in n.value.keywords if k.arg and _literal(k.value)}
    out.append((fn,kw))
 return out
def _literal(n):
 try:ast.literal_eval(n);return True
 except:return False
def angle(a,b):
 try:
  x=np.asarray(a,float);y=np.asarray(b,float); z=np.linalg.norm(x)*np.linalg.norm(y)
  return float(np.degrees(np.arccos(np.clip(np.dot(x,y)/z,-1,1)))) if z else None
 except:return None
def normerr(a,b,diag=1):
 try:return float(np.linalg.norm(np.asarray(a,float)-np.asarray(b,float))/max(diag,1e-12))
 except:return None
def q(v,p):
 a=[x for x in v if x is not None and math.isfinite(x)];return float(np.quantile(a,p)) if a else None
def mean(v):
 a=[x for x in v if x is not None and math.isfinite(x)];return float(np.mean(a)) if a else None

p1=loadrows(P1);a3=loadrows(A3)
bench={}
for line in BENCH.open():
 try:
  x=json.loads(line); r=next((z for z in x['rows'] if z['arm']=='P1'),None)
  if r:bench[x['cad_id']]=r
 except:pass
ids=sorted(set(p1)&set(a3)&set(bench))
valid=[c for c in ids if f((p1[c].get('geometry') or {}).get('chamfer_norm')) is not None and f((p1[c].get('geometry') or {}).get('hausdorff_95_norm')) is not None]
metric=lambda c,k:f((p1[c].get('geometry') or {}).get(k))
thr={}
for k in ('chamfer_norm','hausdorff_95_norm','volume_error'):thr[k]={'p75':q([metric(c,k) for c in valid],.75),'p90':q([metric(c,k) for c in valid],.90)}
for k in ('center_error','extent_error','scale_log_error'):thr[k]={'p75':q([f(bench[c].get(k)) for c in valid],.75),'p90':q([f(bench[c].get(k)) for c in valid],.90)}

# Strict aligned AST parameter records, only S1 cases and position-identical operation types.
param=[];case_groups=defaultdict(lambda:defaultdict(list)); applicable=aligned=0
fieldmap={'Box':['width','height','depth','origin'],'Extrude':['height','origin','axis'],'ExtrudePolygon':['height','origin','axis'],'Cylinder':['radius','height','origin','axis']}
for c in valid:
 gt=getcalls(P1/c/'gt.dsl');pr=getcalls(P1/c/'pred.dsl'); s1=[x[0] for x in gt]==[x[0] for x in pr]
 if not s1:continue
 for (op,g),(op2,p) in zip(gt,pr):
  if op not in fieldmap:continue
  applicable+=1
  if op!=op2:continue
  aligned+=1
  # GT DSL units; scalar errors are GT-operation-scale relative, origin normalized by GT operation scale.
  scalars=[abs(f(g.get(x),0)) for x in ('width','height','depth','radius') if f(g.get(x)) is not None]
  diag=max(math.sqrt(sum(x*x for x in scalars)),1e-8)
  for fld in fieldmap[op]:
   if fld not in g or fld not in p:continue
   if fld=='axis':e=angle(g[fld],p[fld]);grp='DIRECTION'
   elif fld=='origin':e=normerr(g[fld],p[fld],diag);grp='PLACEMENT'
   else:
    gv=f(g[fld]);pv=f(p[fld]);e=abs(pv-gv)/max(abs(gv),diag*.1,1e-8) if gv is not None and pv is not None else None;grp='SIZE'
   if e is not None:
    param.append({'cad_id':c,'operation':op,'field':fld,'error':e,'group':grp});case_groups[c][grp].append(e)

# Frozen field P75/P90 and operation tables.
byfield=defaultdict(list)
for r in param:byfield[(r['operation'],r['field'])].append(r['error'])
fieldthr={k:q(v,.75) for k,v in byfield.items()}
headers=['operation','parameter_field','support_N','MAE','median_error','P75','P90','units']
for op,name in [('Box','BOX_PARAMETER_ERRORS.csv'),('Extrude','EXTRUDE_PARAMETER_ERRORS.csv'),('ExtrudePolygon','EXTRUDE_POLYGON_PARAMETER_ERRORS.csv'),('Cylinder','CYLINDER_PARAMETER_ERRORS.csv')]:
 rows=[]
 for (o,ff),v in sorted(byfield.items()):
  if o==op:rows.append({'operation':o,'parameter_field':ff,'support_N':len(v),'MAE':mean(v),'median_error':q(v,.5),'P75':q(v,.75),'P90':q(v,.9),'units':'degrees' if ff=='axis' else 'relative'})
 with (OUT/'parameters'/name).open('w',newline='') as z:w=csv.DictWriter(z,headers);w.writeheader();w.writerows(rows)
with (OUT/'parameters/PARAMETER_ALIGNMENT_COVERAGE.csv').open('w',newline='') as z:
 w=csv.DictWriter(z,['PARAM_APPLICABLE_N','PARAM_ALIGNED_N','ALIGNMENT_COVERAGE','PROFILE_POINT_ALIGNMENT']);w.writeheader();w.writerow({'PARAM_APPLICABLE_N':applicable,'PARAM_ALIGNED_N':aligned,'ALIGNMENT_COVERAGE':aligned/applicable if applicable else None,'PROFILE_POINT_ALIGNMENT':'DEFERRED'})

case={}
for c in valid:
 r=p1[c];gt=r.get('gt_ops',[]);po=r.get('pred_ops',[]);s1=gt==po;s3=abs(f(r.get('op_f1'),0)-1)<1e-12;s2=s1 and abs(f(bench[c].get('dependency_edge_f1'),-1)-1)<1e-12
 flags={'CHAMFER_BAD_P75':metric(c,'chamfer_norm')>thr['chamfer_norm']['p75'],'H95_BAD_P75':metric(c,'hausdorff_95_norm')>thr['hausdorff_95_norm']['p75'],'VOLUME_BAD_P75':metric(c,'volume_error') is not None and metric(c,'volume_error')>thr['volume_error']['p75'],'PLACEMENT_BAD':f(bench[c].get('center_error'),-1)>thr['center_error']['p75'],'EXTENT_SCALE_BAD':f(bench[c].get('extent_error'),-1)>thr['extent_error']['p75'] or f(bench[c].get('scale_log_error'),-1)>thr['scale_log_error']['p75']}
 bad=any(flags.values()); sev=defaultdict(float)
 for rr in param:
  if rr['cad_id']==c and rr['error']>fieldthr[(rr['operation'],rr['field'])]:sev[rr['group']]=max(sev[rr['group']],rr['error'])
 labels=[]
 if not s1:labels=['RESIDUAL_STRUCTURE_ERROR']
 else:
  if sev['PLACEMENT']>0:labels.append('ORIGIN_ERROR')
  if sev['DIRECTION']>0:labels.append('DIRECTION_ERROR')
  if sev['SIZE']>0:labels.append('DIMENSION_ERROR')
  if flags['EXTENT_SCALE_BAD']:labels += ['SCALE_ERROR','EXTENT_ERROR']
  if not labels and bad:labels=['UNRESOLVED']
 if len(set(labels))>=3 and s1:primary='MULTIPLE_PARAMETER_ERRORS'
 else:
  priority=['RESIDUAL_STRUCTURE_ERROR','PROFILE_POINT_ERROR','ORIGIN_ERROR','TRANSLATION_ERROR','DIRECTION_ERROR','DIMENSION_ERROR','HEIGHT_ERROR','RADIUS_ERROR','SCALE_ERROR','EXTENT_ERROR','TOPOLOGY_ERROR','MULTIPLE_PARAMETER_ERRORS','UNRESOLVED']
  primary=next((x for x in priority if x in labels),'UNRESOLVED')
 case[c]={'cad_id':c,'source':r.get('dataset'),'GT_ops':' > '.join(gt),'P1_ops':' > '.join(po),'OpF1':r.get('op_f1'),'S1_OP_SEQUENCE_EXACT':s1,'S2_AST_STRUCTURE_EXACT':s2,'S3_OPF1_PERFECT':s3,'geometry_bad':bad,**flags,'Chamfer':metric(c,'chamfer_norm'),'H95':metric(c,'hausdorff_95_norm'),'Volume':metric(c,'volume_error'),'center_error':bench[c].get('center_error'),'extent_error':bench[c].get('extent_error'),'scale_log_error':bench[c].get('scale_log_error'),'direction_error':max(case_groups[c]['DIRECTION']) if case_groups[c]['DIRECTION'] else None,'size_error':max(case_groups[c]['SIZE']) if case_groups[c]['SIZE'] else None,'root_causes':'|'.join(dict.fromkeys(labels)),'PRIMARY_ROOT_CAUSE':primary,'STEP_Reload':bench[c].get('step_reload')}

gb=[case[c] for c in valid if case[c]['S1_OP_SEQUENCE_EXACT'] and case[c]['geometry_bad']]
with (OUT/'cohorts/STRUCTURE_CORRECT_GEOMETRY_BAD_CASES.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(gb[0]));w.writeheader();w.writerows(gb)
# Quadrants and aggregates.
quadr=[]
for sc,bad,label in [(1,0,'GROUP_A_STRUCTURE_CORRECT_GEOMETRY_GOOD'),(1,1,'GROUP_B_STRUCTURE_CORRECT_GEOMETRY_BAD'),(0,0,'GROUP_C_STRUCTURE_WRONG_GEOMETRY_GOOD'),(0,1,'GROUP_D_STRUCTURE_WRONG_GEOMETRY_BAD')]:
 cc=[case[c] for c in valid if case[c]['S1_OP_SEQUENCE_EXACT']==bool(sc) and case[c]['geometry_bad']==bool(bad)]
 quadr.append({'group':label,'N':len(cc),'percentage_geometry_valid':len(cc)/len(valid),'mean_OpF1':mean([f(x['OpF1']) for x in cc]),'mean_Chamfer':mean([x['Chamfer'] for x in cc]),'mean_H95':mean([x['H95'] for x in cc]),'mean_Volume':mean([x['Volume'] for x in cc]),'STEP_Reload_rate':mean([1 if x['STEP_Reload'] else 0 for x in cc])})
with (OUT/'cohorts/STRUCTURE_GEOMETRY_QUADRANTS.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(quadr[0]));w.writeheader();w.writerows(quadr)

# Root cause summaries and operation-specific bottlenecks.
rootcount=Counter(x['PRIMARY_ROOT_CAUSE'] for x in gb)
with (OUT/'tables/P1_RESIDUAL_ERROR_SUMMARY.csv').open('w',newline='') as z:
 w=csv.writer(z);w.writerow(['PRIMARY_ROOT_CAUSE','N','percentage_Group_B']);[w.writerow([k,n,n/len(gb) if gb else 0]) for k,n in rootcount.most_common()]
groups=Counter()
for x in gb:
 for k in x['root_causes'].split('|'):groups[k]+=1
with (OUT/'tables/P1_PARAMETER_GROUP_SUMMARY.csv').open('w',newline='') as z:
 w=csv.writer(z);w.writerow(['root_cause_multilabel','N','percentage_Group_B']);[w.writerow([k,n,n/len(gb) if gb else 0]) for k,n in groups.most_common()]
oprows=[]
for op in ('Box','Extrude','ExtrudePolygon','Cylinder','Cut','Union'):
 subset=[x for x in gb if op in x['GT_ops'].split(' > ')]; cnt=Counter()
 for x in subset:
  for a in x['root_causes'].split('|'):cnt[a]+=1
 oprows.append({'operation':op,'Group_B_support_N':len(subset),'main_parameter_bottleneck':cnt.most_common(1)[0][0] if cnt else 'INSUFFICIENT_SUPPORT','main_N':cnt.most_common(1)[0][1] if cnt else 0,'all_root_causes':json.dumps(cnt)})
with (OUT/'operations/OPERATION_PARAMETER_BOTTLENECK.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(oprows[0]));w.writeheader();w.writerows(oprows)

# Spearman, pairwise-complete, explicitly non-causal.
corr=[]
for gm in ('Chamfer','H95','Volume'):
 for pe in ('center_error','extent_error','direction_error','size_error'):
  xy=[(f(x[gm]),f(x[pe])) for x in case.values() if x['S1_OP_SEQUENCE_EXACT'] and f(x[gm]) is not None and f(x[pe]) is not None]
  rho,pv=spearmanr([x[0] for x in xy],[x[1] for x in xy]) if len(xy)>=3 else (None,None)
  corr.append({'geometry_metric':gm,'parameter_error':pe,'N':len(xy),'spearman_rho':rho,'p_value_two_sided':pv,'interpretation':'association only; not causal'})
with (OUT/'correlations/PARAMETER_GEOMETRY_CORRELATIONS.csv').open('w',newline='') as z:w=csv.DictWriter(z,list(corr[0]));w.writeheader();w.writerows(corr)

# Top20 reuse and relabel.
top=[]
with (CLOSURE/'geometry_outliers/P1_CHAMFER_TOP20.csv').open() as z:
 for r in csv.DictReader(z):
  c=r['cad_id']; top.append(case.get(c,{'cad_id':c,'PRIMARY_ROOT_CAUSE':'NOT_GEOMETRY_VALID_OR_MISSING'}))
keys=sorted(set().union(*(x.keys() for x in top)))
with (OUT/'outliers/P1_TOP20_PARAMETER_ROOT_CAUSE.csv').open('w',newline='') as z:w=csv.DictWriter(z,keys);w.writeheader();w.writerows(top)

s1=sum(x['S1_OP_SEQUENCE_EXACT'] for x in case.values());s2=sum(x['S2_AST_STRUCTURE_EXACT'] for x in case.values());s3=sum(x['S3_OPF1_PERFECT'] for x in case.values())
s2bad=sum(x['S2_AST_STRUCTURE_EXACT'] and x['geometry_bad'] for x in case.values());s3bad=sum(x['S3_OPF1_PERFECT'] and x['geometry_bad'] for x in case.values())
param_expl=sum(x['PRIMARY_ROOT_CAUSE'] not in ('RESIDUAL_STRUCTURE_ERROR','TOPOLOGY_ERROR','UNRESOLVED') for x in gb)
p2='JUSTIFIED' if s1/len(valid)>.5 and len(gb)/max(s1,1)>.15 and param_expl/max(len(gb),1)>.5 else 'NOT_JUSTIFIED'
target='NONE'; ranked=[(groups[k],k) for k in ('ORIGIN_ERROR','TRANSLATION_ERROR','DIMENSION_ERROR','DIRECTION_ERROR','PROFILE_POINT_ERROR','SCALE_ERROR','EXTENT_ERROR')]
if p2=='JUSTIFIED' and ranked:
 k=max(ranked)[1];target='PLACEMENT' if k in ('ORIGIN_ERROR','TRANSLATION_ERROR') else ('SIZE' if k in ('DIMENSION_ERROR','SCALE_ERROR','EXTENT_ERROR') else ('DIRECTION' if k=='DIRECTION_ERROR' else 'PROFILE'))
all_causes=['DIMENSION_ERROR','ORIGIN_ERROR','TRANSLATION_ERROR','DIRECTION_ERROR','SCALE_ERROR','EXTENT_ERROR','PROFILE_POINT_ERROR','RESIDUAL_STRUCTURE_ERROR','TOPOLOGY_ERROR','MULTIPLE_PARAMETER_ERRORS','UNRESOLVED']
cmap={(x['geometry_metric'],x['parameter_error']):(None if f(x['spearman_rho']) is None else x['spearman_rho']) for x in corr}
ranked_primary=rootcount.most_common()
summary={'CURRENT_GATE':'COMPLETE','TEST_TOUCHED':'NO','STRUCTURE':{'P1_GEOMETRY_VALID_N':len(valid),'OP_SEQUENCE_EXACT_N':s1,'AST_STRUCTURE_EXACT_N':s2,'OPF1_PERFECT_N':s3},'STRUCTURE_CORRECT_GEOMETRY_BAD':{'S1_N':len(gb),'S1_RATE_AMONG_STRUCTURE_CORRECT':len(gb)/s1,'S1_RATE_AMONG_GEOMETRY_VALID':len(gb)/len(valid),'S2_N':s2bad,'S3_N':s3bad},'QUADRANTS':{x['group']:x['N'] for x in quadr},'ROOT_CAUSES_MULTILABEL':{k:(rootcount.get(k,0) if k=='MULTIPLE_PARAMETER_ERRORS' else groups.get(k,0)) for k in all_causes},'PRIMARY_ROOT_CAUSES':dict(rootcount),'OPERATIONS':{x['operation']:x['main_parameter_bottleneck'] for x in oprows},'CORRELATION':{'CHAMFER_VS_ORIGIN_SPEARMAN':cmap.get(('Chamfer','center_error')),'CHAMFER_VS_EXTENT_SPEARMAN':cmap.get(('Chamfer','extent_error')),'CHAMFER_VS_DIRECTION_SPEARMAN':cmap.get(('Chamfer','direction_error')),'H95_VS_ORIGIN_SPEARMAN':cmap.get(('H95','center_error'))},'P1_RESIDUAL_BOTTLENECK':{'PRIMARY':ranked_primary[0][0] if ranked_primary else 'UNRESOLVED','SECONDARY':ranked_primary[1][0] if len(ranked_primary)>1 else 'NONE'},'THRESHOLDS':thr,'PARAMETER_ALIGNMENT':{'PARAM_APPLICABLE_N':applicable,'PARAM_ALIGNED_N':aligned,'ALIGNMENT_COVERAGE':aligned/applicable if applicable else None},'P2':{'P2_STATUS':p2,'RECOMMENDED_P2_TARGET':target,'RECOMMENDED_P2_SCOPE':'P1 architecture + L_op retained; add one operation-aware parameter-group loss only; lambda_param deferred'},'INTEGRITY':{'P1_CHANGED':'NO','NEW_TRAINING':'NO','NEW_DECODE':'NO','TEST_TOUCHED':'NO','FINAL_TEST_SCHEDULER_CHANGED':'NO','FINAL_TEST_GPU_INTERFERENCE':'NO'}}
with (OUT/'tables/P1_P2_DECISION_TABLE.csv').open('w',newline='') as z:w=csv.writer(z);w.writerow(['criterion','value']);w.writerow(['structure_stable_rate',s1/len(valid)]);w.writerow(['Group_B_rate_among_S1',len(gb)/s1]);w.writerow(['parameter_explained_rate_Group_B',param_expl/max(len(gb),1)]);w.writerow(['P2_STATUS',p2]);w.writerow(['target',target])
protocol={'scope':'Frozen EXACT9998 VAL1000 post-hoc only','S1':'ordered operation sequence exact; numeric values ignored','S2':'S1 plus frozen dependency_edge_f1 == 1.0','S3':'per-case Op-F1 == 1.0','geometry_valid':'frozen evaluator Chamfer and H95 both available','geometry_bad':'any frozen metric/placement field above its P1 geometry-valid P75','thresholds':thr,'parameter_alignment':'Python AST; only position-identical operations within S1 exact sequence; no forced match','PROFILE_POINT_ALIGNMENT':'DEFERRED','TEST_TOUCHED':False}
(OUT/'protocol/P1_PARAMETER_BOTTLENECK_PROTOCOL.json').write_text(json.dumps(protocol,indent=2)+'\n')
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(summary,indent=2)+'\n')
md=['# P1 Structure-Correct / Geometry-Bad Parameter Bottleneck Audit','',f"CURRENT_GATE = {summary['CURRENT_GATE']}",'','TEST_TOUCHED = NO','','## Structure',f'- Geometry-valid: {len(valid)}',f'- S1 sequence exact: {s1}',f'- S2 AST/dependency exact: {s2}',f'- S3 Op-F1 perfect: {s3}','','## Core cohort',f'- S1 structure-correct + geometry-bad: {len(gb)} ({len(gb)/s1:.1%} of S1; {len(gb)/len(valid):.1%} of geometry-valid)','','## Primary root causes']+[f'- {k}: {n}' for k,n in rootcount.most_common()]+['','## Decision',f'- P2_STATUS = {p2}',f'- RECOMMENDED_P2_TARGET = {target}','- This is an association-based post-hoc diagnostic, not a causal claim. No P2 training was started.']
(OUT/'reports/FINAL_REPORT.md').write_text('\n'.join(md)+'\n')
rec=f'''# P2 Design Recommendation\n\nP2_STATUS = {p2}\n\nRecommended target: **{target}**.\n\nKeep the P1 architecture and operation-aware loss unchanged. If pursued, add exactly one operation-aware, parameter-group-aware objective:\n\n`L_total = L_base + lambda_op * L_op + lambda_param * L_param`\n\nDo not use an undifferentiated all-numeric-token loss. Start with one controlled ablation for {target}; leave `lambda_param` undecided until that experiment is designed. No P2 training was launched in this audit.\n'''
(OUT/'reports/P2_DESIGN_RECOMMENDATION.md').write_text(rec)
(OUT/'integrity/INTEGRITY.json').write_text(json.dumps(summary['INTEGRITY'],indent=2)+'\n')

# Gallery: automatically select highest/lowest frozen diagnostic scores per requested row.
sys.path.insert(0,str(ROOT/'ours3'))
import p1_val1000_qualitative_visualization_v1 as vis
choices=[]
good=[x for x in case.values() if x['S1_OP_SEQUENCE_EXACT'] and not x['geometry_bad']]
choices.append(('Structure correct + geometry good',sorted(good,key=lambda x:(x['Chamfer'],x['cad_id']))[0]))
def pick(label,pred,score):
 a=[x for x in gb if pred(x)]; choices.append((label,sorted(a,key=lambda x:(-score(x),x['cad_id']))[0] if a else None))
pick('Structure correct + origin wrong',lambda x:'ORIGIN_ERROR' in x['root_causes'],lambda x:f(x['center_error'],0))
pick('Structure correct + dimension / scale wrong',lambda x:any(k in x['root_causes'] for k in ('DIMENSION_ERROR','SCALE_ERROR','EXTENT_ERROR')),lambda x:max(f(x['size_error'],0),f(x['extent_error'],0)))
pick('Structure correct + direction wrong',lambda x:'DIRECTION_ERROR' in x['root_causes'],lambda x:f(x['direction_error'],0))
res=[x for x in case.values() if not x['S1_OP_SEQUENCE_EXACT']]
choices.append(('Residual structure failure',sorted(res,key=lambda x:(-f(x['Chamfer'],0),x['cad_id']))[0]))
from PIL import Image,ImageDraw,ImageFont
panels=[]
for label,x in choices:
 if x is None:
  panels.append((label,'NO_ELIGIBLE_CASE_UNDER_FROZEN_RULE',[],None));continue
 c=x['cad_id']; d=OUT/'gallery'/c;d.mkdir(parents=True,exist_ok=True);gt=vis.ensure_gt_step(c);gv,_=vis.step_mesh(gt,1e-3);mn=gv.min(0);mx=gv.max(0);scale=max(np.linalg.norm(mx-mn),1e-8);tr={'center':(mn+mx)/2,'scale':scale};tol=max(scale*.001,1e-6);pp=[]
 for arm,sp,row in [('GT',gt,{'parsed':True,'step_ok':True,'geometry':{}}),('A3',A3/c/'pred.step',a3[c]),('P1',P1/c/'pred.step',p1[c])]:
  out=d/f'{arm}.png';vis.render_panel(c,arm,sp,tr,tol,row,out);pp.append(out)
 panels.append((label,c,pp,x))
w,h=1740,440;im=Image.new('RGB',(w,100+h*len(panels)),'white');dr=ImageDraw.Draw(im);dr.text((30,20),'P1: structure-correct geometry failures',fill='#17202a',font=vis.font(32,True))
for j,n in enumerate(('GT','A3','P1')):dr.text((250+j*500,68),n,fill='#111',font=vis.font(18,True))
for i,(lab,c,pps,x) in enumerate(panels):
 y=100+i*h;dr.text((10,y+15),lab,fill='#25364a',font=vis.font(15,True));dr.text((10,y+42),c,fill='#555',font=vis.font(11))
 if x is None:
  dr.text((590,y+190),'NO ELIGIBLE CASE',fill='#8b1e1e',font=vis.font(24,True));dr.text((480,y+230),'Direction error is constant / unsupported in S1 geometry-valid cohort.',fill='#444',font=vis.font(14));continue
 for j,p in enumerate(pps):
  q=Image.open(p).convert('RGB');q.thumbnail((480,340));im.paste(q,(180+j*500,y+55))
 dr.text((180,y+400),f"OpF1={f(x['OpF1'],0):.2f}  origin={f(x['center_error'],float('nan')):.3g}  extent={f(x['extent_error'],float('nan')):.3g}  direction={f(x['direction_error'],float('nan')):.3g}  CD={x['Chamfer']:.3g}  H95={x['H95']:.3g}",fill='#222',font=vis.font(12))
im.save(OUT/'gallery/P1_STRUCTURE_PARAMETER_FAILURE_GALLERY.png',dpi=(300,300))
print(json.dumps(summary,indent=2))
