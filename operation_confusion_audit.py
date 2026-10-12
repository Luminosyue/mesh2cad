#!/usr/bin/env python3
import ast,csv,json,statistics
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');SRC=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2';ASTOUT=ROOT/'ours3/a0_a3_val1000_ast_aligned_parameter_error_audit_v1';PLOUT=ROOT/'ours3/a0_a3_val1000_placement_scale_parameter_error_audit_v1';OUT=ROOT/'ours3/a0_a3_val1000_operation_confusion_equivalence_audit_v1'
for d in ('alignment','confusion','tables','breakdown','gallery','reports'):(OUT/d).mkdir(parents=True,exist_ok=True)
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (SRC/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
def write(path,rows,fields=None):
 if fields is None:fields=list(rows[0]) if rows else ['empty']
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def rows(arm):return {p.parent.name:json.loads(p.read_text()) for p in (SRC/'predictions'/arm).glob('*/row.json')}
rr={'a0':rows('a0'),'a3':rows('a3')}
place=list(csv.DictReader((PLOUT/'tables/PLACEMENT_SCALE_PER_CASE.csv').open()));pm={(r['model'],r['cad_id']):r for r in place};both=sorted(set(i for a,i in pm if a=='a0')&set(i for a,i in pm if a=='a3'));assert len(both)==189
chvals=[float(pm[(a,i)]['chamfer']) for a in ('a0','a3') for i in both];low_thr=float(np.quantile(chvals,.25))

def lit(n):
 if isinstance(n,ast.Name):return {'$ref':n.id}
 try:return ast.literal_eval(n)
 except:return {'$ast':ast.dump(n,include_attributes=False)}
def parse(path):
 t=ast.parse(Path(path).read_text());ops={};result=None
 for s in t.body:
  if not isinstance(s,ast.Assign) or len(s.targets)!=1 or not isinstance(s.targets[0],ast.Name):continue
  name=s.targets[0].id
  if isinstance(s.value,ast.Call) and isinstance(s.value.func,ast.Name):ops[name]={'op':s.value.func.id,'args':[lit(x) for x in s.value.args],'kwargs':{x.arg:lit(x.value) for x in s.value.keywords if x.arg}}
  elif name=='result':result=lit(s.value)
 return {'ops':ops,'result':result}
P={};parsefail=[]
for cid in manifest:
 P[cid]={}
 for a,p in {'gt':SRC/'predictions/a0'/cid/'gt.dsl','a0':SRC/'predictions/a0'/cid/'pred_canonical.dsl','a3':SRC/'predictions/a3'/cid/'pred_canonical.dsl'}.items():
  try:P[cid][a]=parse(p)
  except Exception as e:parsefail.append({'cad_id':cid,'arm':a,'reason':type(e).__name__+': '+str(e)})

arms=[]
for cid in sorted(manifest):
 g=P[cid].get('gt')
 if not g:continue
 for var,go in g['ops'].items():
  for arm in ('a0','a3'):
   p=P[cid].get(arm);po=p['ops'].get(var) if p else None
   arms.append({'cad_id':cid,'source':manifest[cid]['source'],'K':manifest[cid]['K'],'arm':arm,'gt_var':var,'gt_type':go['op'],'pred_type':po['op'] if po else 'MISSING_OPERATION','status':'SAME_TYPE' if po and po['op']==go['op'] else ('WRONG_TYPE_SUBSTITUTION' if po else 'MISSING_OPERATION')})
write(OUT/'alignment/OPERATION_ARMS.csv',arms)
(OUT/'alignment/ALIGNMENT_REUSE_AUDIT.json').write_text(json.dumps({'source_ast_audit':str(ASTOUT),'rule':'same canonical assignment identifier; exact reuse of prior audit alignment semantics','ambiguous_alignment_N':0,'fuzzy_alignment':False,'parse_failures':parsefail,'low_geometry_error':{'definition':'Chamfer <= combined A0/A3 BOTH_VALID 25th percentile','threshold':low_thr,'diagnostic_only':True},'TEST_TOUCHED':'NO'},indent=2)+'\n')

types=sorted(set(x['gt_type'] for x in arms)|set(x['pred_type'] for x in arms));mats={}
for arm in ('a0','a3'):
 c=Counter((x['gt_type'],x['pred_type']) for x in arms if x['arm']==arm);out=[]
 for gt in sorted(set(x['gt_type'] for x in arms)):
  row={'GT_OPERATION':gt};row.update({p:c[(gt,p)] for p in types});out.append(row)
 mats[arm]=c;write(OUT/f'confusion/{arm.upper()}_OPERATION_CONFUSION_MATRIX.csv',out,['GT_OPERATION']+types)
delta=[]
for gt in sorted(set(x['gt_type'] for x in arms)):
 for p in types:delta.append({'GT_OPERATION':gt,'PRED_OPERATION':p,'A0_N':mats['a0'][(gt,p)],'A3_N':mats['a3'][(gt,p)],'DELTA_A3_MINUS_A0':mats['a3'][(gt,p)]-mats['a0'][(gt,p)]})
write(OUT/'confusion/A0_A3_OPERATION_CONFUSION_DELTA.csv',delta)

def geom(arm,cid):
 r=rr[arm][cid];g=r.get('geometry',{});ch=g.get('chamfer_norm');h=g.get('hausdorff_95_norm')
 return {'exact':bool(r.get('exact_match')),'op_f1':r.get('op_f1'),'step':bool(r.get('step_ok')),'chamfer':ch,'h95':h,'close':ch is not None and float(ch)<=low_thr}
def subs(arm):return [x|geom(arm,x['cad_id']) for x in arms if x['arm']==arm and x['status']=='WRONG_TYPE_SUBSTITUTION']
subsby={'a0':subs('a0'),'a3':subs('a3')}
def pair_stats(arm,gt,pt):
 z=[x for x in subsby[arm] if x['gt_type']==gt and x['pred_type']==pt];ch=[float(x['chamfer']) for x in z if x['chamfer'] is not None];h=[float(x['h95']) for x in z if x['h95'] is not None]
 return {'N':len(z),'STEP_valid_rate':sum(x[' prélstep'] if False else x['step'] for x in z)/len(z) if z else None,'Chamfer_mean':statistics.mean(ch) if ch else None,'Chamfer_median':statistics.median(ch) if ch else None,'H95_mean':statistics.mean(h) if h else None,'Exact_rate':sum(x['exact'] for x in z)/len(z) if z else None,'Op_F1_mean':statistics.mean(x['op_f1'] for x in z) if z else None,'Geometry_close_N':sum(x['close'] for x in z)}
rank=[]
for (gt,pt),n in Counter((x['gt_type'],x['pred_type']) for x in subsby['a3']).most_common():rank.append({'GT_type':gt,'Pred_type':pt,**pair_stats('a3',gt,pt)})
write(OUT/'tables/A3_OPERATION_SUBSTITUTION_RANKING.csv',rank)

summary=[]
for gt in sorted(set(x['gt_type'] for x in arms)):
 z={a:[x for x in arms if x['arm']==a and x['gt_type']==gt] for a in ('a0','a3')};d={'GT_operation':gt}
 for a in ('a0','a3'):
  n=len(z[a]);same=sum(x['status']=='SAME_TYPE' for x in z[a]);miss=sum(x['status']=='MISSING_OPERATION' for x in z[a]);cs=Counter(x['pred_type'] for x in z[a] if x['status']=='WRONG_TYPE_SUBSTITUTION');d.update({a+'_same_type_rate':same/n,a+'_top_substitution':cs.most_common(1)[0][0] if cs else '',a+'_top_substitution_N':cs.most_common(1)[0][1] if cs else 0,a+'_missing_rate':miss/n,a+'_substitution_rate':sum(cs.values())/n})
 summary.append(d)
write(OUT/'tables/OPERATION_CONFUSION_SUMMARY.csv',summary)

close=[]
for arm in ('a0','a3'):
 for x in subsby[arm]:
  if x['step'] and x['close']:close.append({k:x[k] for k in ('cad_id','source','K','arm','gt_type','pred_type','exact','op_f1','step','chamfer','h95')})
write(OUT/'tables/OPERATION_DIFFERENT_GEOMETRY_CLOSE.csv',close)

exactdiag=[]
for arm in ('a0','a3'):
 c=Counter()
 for cid,r in rr[arm].items():
  g=geom(arm,cid)
  cat='Exact=1' if g['exact'] else ('Exact=0 + geometry close' if g['step'] and g['close'] else ('Exact=0 + geometry poor' if g['step'] and g['chamfer'] is not None else 'Exact=0 + invalid'))
  c[cat]+=1
 for cat,n in c.items():exactdiag.append({'arm':arm,'category':cat,'N':n,'rate':n/1000})
write(OUT/'tables/EXACT_VS_GEOMETRY_DIAGNOSTIC.csv',exactdiag)

def case_audit(op,target):
 out=[]
 for cid in manifest:
  g=P[cid].get('gt');
  if not g:continue
  gv=[v for v,x in g['ops'].items() if x['op']==op]
  if not gv:continue
  row={'cad_id':cid,'source':manifest[cid]['source'],'K':manifest[cid]['K'],'GT_count':len(gv)}
  for a in ('a0','a3'):
   q=P[cid].get(a);pred=[q['ops'].get(v) if q else None for v in gv];row[a+'_matched']=sum(x is not None and x['op']==op for x in pred);row[a+'_substitute_types']='|'.join((x['op'] if x else 'MISSING_OPERATION') for x in pred);gg=geom(a,cid);row.update({a+'_Op_F1':gg['op_f1'],a+'_STEP':gg['step'],a+'_Chamfer':gg['chamfer'],a+'_H95':gg['h95']})
  out.append(row)
 write(OUT/'tables'/target,out);return out
boxaudit=case_audit('Box','BOX_REPRESENTATION_SHIFT_AUDIT.csv');cutaudit=case_audit('Cut','CUT_GAIN_SOURCE_AUDIT.csv');unionaudit=case_audit('Union','UNION_REGRESSION_AUDIT.csv')

# Reverse source of A3 predicted ExtrudePolygon/Extrude under the reused canonical-ID alignment.
rev=[]
for predop in ('ExtrudePolygon','Extrude'):
 c=Counter(x['gt_type'] for x in arms if x['arm']=='a3' and x['pred_type']==predop)
 for gt,n in c.most_common():rev.append({'A3_pred_operation':predop,'GT_operation':gt,'N':n,'is_true_GT_type':gt==predop})
write(OUT/'tables/EXTRUDEPOLYGON_GAIN_SOURCE_AUDIT.csv',rev)

# Cut gain source: compare per canonical GT Cut arm across A0 and A3.
cutgain=Counter()
for cid in manifest:
 g=P[cid].get('gt');p0=P[cid].get('a0');p3=P[cid].get('a3')
 if not g:continue
 for v,x in g['ops'].items():
  if x['op']!='Cut':continue
  s0='MISSING_OPERATION' if not p0 or v not in p0['ops'] else p0['ops'][v]['op'];s3='MISSING_OPERATION' if not p3 or v not in p3['ops'] else p3['ops'][v]['op']
  if s3=='Cut' and s0!='Cut':cutgain['A0_'+('MISSING' if s0=='MISSING_OPERATION' else 'WRONG_TYPE')+'_TO_A3_CORRECT_CUT']+=1

# Boolean commutative reorder only for same aligned Union calls with exactly reversed direct operands.
comm=0;tree_rearr=0
for cid in manifest:
 g=P[cid].get('gt');p=P[cid].get('a3')
 if not g or not p:continue
 for v,x in g['ops'].items():
  y=p['ops'].get(v)
  if x['op']=='Union' and y and y['op']=='Union':
   if len(x['args'])>=2 and len(y['args'])>=2 and x['args'][:2]==list(reversed(y['args'][:2])):comm+=1
   elif x['args']!=y['args']:tree_rearr+=1

catdef={'Primitive_or_profile_like':['Box','Cylinder','Circle','Sketch','PolygonProfile','Axis'],'Constructive_or_extrusion':['Extrude','ExtrudePolygon','Revolve','TrueRevolve','Fillet','Chamfer'],'Boolean':['Union','Cut'],'note':'Read-only diagnostic categories from actual frozen DSL operations; not a formal metric.'}
(OUT/'alignment/OPERATION_CATEGORY_DEFINITION.json').write_text(json.dumps(catdef,indent=2)+'\n')

def breakdown(grouping):
 groups={'DeepCAD':lambda x:x['source']=='deepcad','Fusion360':lambda x:x['source']=='fusion360'} if grouping=='source' else {'LOW':lambda x:int(x['K'])<=8,'MID':lambda x:9<=int(x['K'])<=32,'HIGH':lambda x:int(x['K'])>32,'CAP':lambda x:int(x['K'])==128}
 out=[]
 for name,fn in groups.items():
  for arm in ('a0','a3'):
   z=[x for x in arms if x['arm']==arm and fn(x)];n=len(z);out.append({'group':name,'arm':arm,'operation_arms_N':n,'same_type_rate':sum(x['status']=='SAME_TYPE' for x in z)/n if n else None,'substitution_rate':sum(x['status']=='WRONG_TYPE_SUBSTITUTION' for x in z)/n if n else None,'missing_rate':sum(x['status']=='MISSING_OPERATION' for x in z)/n if n else None,'geometry_close_substitution_N':sum(geom(arm,x['cad_id'])['close'] for x in z if x['status']=='WRONG_TYPE_SUBSTITUTION')})
 return out
write(OUT/'breakdown/SOURCE_OPERATION_SHIFT_BREAKDOWN.csv',breakdown('source'));write(OUT/'breakdown/K_OPERATION_SHIFT_BREAKDOWN.csv',breakdown('k'))

def op_counts(kind):
 out=[]
 for cid in manifest:
  row={'cad_id':cid,'source':manifest[cid]['source'],'K':manifest[cid]['K']}
  for a in ('gt','a0','a3'):row[a+'_operation_count']=len(P[cid][a]['ops']) if a in P[cid] else None
  out.append(row)
 return out
write(OUT/'tables/PROGRAM_OPERATION_COUNT.csv',op_counts('count'))

box=[x for x in summary if x['GT_operation']=='Box'][0];union=[x for x in summary if x['GT_operation']=='Union'][0];ep=[x for x in summary if x['GT_operation']=='ExtrudePolygon'][0];cut=[x for x in summary if x['GT_operation']=='Cut'][0]
boxsubs=[x for x in subsby['a3'] if x['gt_type']=='Box'];boxclose=sum(x['close'] and x['step'] for x in boxsubs);boxpoor=len(boxsubs)-boxclose;boxmissing=mats['a3'][('Box','MISSING_OPERATION')]
if boxclose>boxpoor+boxmissing:pattern='ALTERNATIVE_CONSTRUCTION_REPRESENTATION_SHIFT'
elif boxclose and (boxpoor or boxmissing):pattern='MIXED_REPRESENTATION_SHIFT_AND_STRUCTURE_ERROR'
elif len(boxsubs)<max(10,.02*sum(x['gt_type']=='Box' and x['arm']=='a3' for x in arms)):pattern='NO_MEANINGFUL_OPERATION_REPRESENTATION_SHIFT'
else:pattern='TRUE_OPERATION_STRUCTURE_REGRESSION'
nonexact={a:next((x['N'] for x in exactdiag if x['arm']==a and x['category']=='Exact=0 + geometry close'),0) for a in ('a0','a3')}
report={'CURRENT_GATE':'A0_A3_VAL1000_OPERATION_CONFUSION_EQUIVALENCE_AUDIT_COMPLETE','RESULT_PATTERN':pattern,'NEXT_PRIORITY':'BOTH' if len(close)>0 else 'KEEP_MIXED_PARAMETER_MODELING_PRIORITY','TEST_TOUCHED':'NO','diagnostic_low_geometry_error_threshold':low_thr,'integrity':{'MODEL_CHANGED':'NO','CHECKPOINT_CHANGED':'NO','PREDICTIONS_CHANGED':'NO','PARSER_CHANGED':'NO','EXECUTOR_CHANGED':'NO','EVALUATOR_CHANGED':'NO','EXACT_CHANGED':'NO','OP_F1_CHANGED':'NO','EXACT9998_CHANGED':'NO'},'BOX':{'GT_BOX_N':sum(x['gt_type']=='Box' and x['arm']=='a3' for x in arms),'A0_BOX_TO_BOX_RATE':box['a0_same_type_rate'],'A3_BOX_TO_BOX_RATE':box['a3_same_type_rate'],'A3_BOX_TO_EXTRUDEPOLYGON_N':mats['a3'][('Box','ExtrudePolygon')],'A3_BOX_TO_EXTRUDE_N':mats['a3'][('Box','Extrude')],'A3_BOX_TO_OTHER_N':sum(n for (g,p),n in mats['a3'].items() if g=='Box' and p not in ('Box','ExtrudePolygon','Extrude','MISSING_OPERATION')),'A3_BOX_MISSING_N':boxmissing,'BOX_SUBSTITUTION_STEP_RATE':sum(x['step'] for x in boxsubs)/len(boxsubs) if boxsubs else None,'BOX_SUBSTITUTION_CHAMFER_MEAN':statistics.mean(float(x['chamfer']) for x in boxsubs if x['chamfer'] is not None) if any(x['chamfer'] is not None for x in boxsubs) else None,'BOX_SUBSTITUTION_GEOMETRY_CLOSE_N':boxclose},'EXTRUDEPOLYGON':{'GT_EXTRUDEPOLYGON_N':sum(x['gt_type']=='ExtrudePolygon' and x['arm']=='a3' for x in arms),'A0_MATCH_RATE':ep['a0_same_type_rate'],'A3_MATCH_RATE':ep['a3_same_type_rate'],'A3_GAIN_FROM_TRUE_GT_EXTRUDEPOLYGON_N':mats['a3'][('ExtrudePolygon','ExtrudePolygon')]-mats['a0'][('ExtrudePolygon','ExtrudePolygon')],'A3_PRED_EXTRUDEPOLYGON_FROM_GT_BOX_N':mats['a3'][('Box','ExtrudePolygon')],'A3_PRED_EXTRUDEPOLYGON_FROM_OTHER_N':sum(n for (g,p),n in mats['a3'].items() if p=='ExtrudePolygon' and g not in ('ExtrudePolygon','Box'))},'CUT':{'GT_CUT_N':sum(x['gt_type']=='Cut' and x['arm']=='a3' for x in arms),'A0_MATCH_RATE':cut['a0_same_type_rate'],'A3_MATCH_RATE':cut['a3_same_type_rate'],'A3_CUT_GAIN_SOURCE':dict(cutgain)},'UNION':{'GT_UNION_N':sum(x['gt_type']=='Union' and x['arm']=='a3' for x in arms),'A0_MATCH_RATE':union['a0_same_type_rate'],'A3_MATCH_RATE':union['a3_same_type_rate'],'UNION_TRUE_REGRESSION_N':max(0,mats['a0'][('Union','Union')]-mats['a3'][('Union','Union')]),'UNION_ALTERNATIVE_CONSTRUCTION_N':sum(x['close'] and x['step'] for x in subsby['a3'] if x['gt_type']=='Union'),'BOOLEAN_TREE_REARRANGEMENT_N':tree_rearr,'COMMUTATIVE_REORDER_N':comm},'EQUIVALENCE_DIAGNOSTIC':{'OPERATION_DIFFERENT_STEP_VALID_N':sum(x['step'] for x in subsby['a3']),'OPERATION_DIFFERENT_GEOMETRY_CLOSE_N':sum(x['step'] and x['close'] for x in subsby['a3']),'NONEXACT_GEOMETRY_CLOSE_A0_N':nonexact['a0'],'NONEXACT_GEOMETRY_CLOSE_A3_N':nonexact['a3']},'top_substitutions':rank[:10],'answers':{}}
close_mismatch_n=sum(x['step'] and x['close'] for x in subsby['a3']);valid_mismatch_n=sum(x['step'] for x in subsby['a3'])
report['NEXT_PRIORITY']='ADD_SEMANTIC_EQUIVALENCE_ANALYSIS_PRIORITY' if close_mismatch_n>=max(10,.1*valid_mismatch_n) else 'KEEP_MIXED_PARAMETER_MODELING_PRIORITY'
report['answers']={'Q1':report['BOX'],'Q2':report['EXTRUDEPOLYGON'],'Q3':'Systematic only if mismatch+geometry-close prevalence is material; see counts and galleries.','Q4':{'A0':nonexact['a0'],'A3':nonexact['a3'],'threshold':low_thr},'Q5':report['NEXT_PRIORITY']}
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(report,indent=2,default=float)+'\n')
md=f'''# Operation Confusion and Near-Equivalence Audit V1

CURRENT_GATE = {report['CURRENT_GATE']}  
RESULT_PATTERN = {pattern}  
NEXT_PRIORITY = {report['NEXT_PRIORITY']}  
TEST_TOUCHED = NO

`LOW_GEOMETRY_ERROR` is diagnostic only: combined A0/A3 BOTH_VALID Chamfer <= 25th percentile = {low_thr:.8g}. It is not a CAD equivalence standard.

## Box

{json.dumps(report['BOX'],indent=2)}

## ExtrudePolygon

{json.dumps(report['EXTRUDEPOLYGON'],indent=2)}

## Cut / Union

{json.dumps(report['CUT'],indent=2)}

{json.dumps(report['UNION'],indent=2)}

## Diagnostic interpretation

{json.dumps(report['EQUIVALENCE_DIAGNOSTIC'],indent=2)}

Formal Exact, Op-F1, STEP, Chamfer and H95 are unchanged. No program equivalence is claimed; only geometry-close alternate constructions are diagnosed.
'''
(OUT/'reports/FINAL_REPORT.md').write_text(md)
print(json.dumps(report,indent=2,default=float))
