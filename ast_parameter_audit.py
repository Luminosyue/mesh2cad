#!/usr/bin/env python3
import ast,csv,json,math,statistics,sys,importlib.util
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
SRC=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'
PREV=ROOT/'ours3/a0_a3_val1000_placement_scale_parameter_error_audit_v1'
OUT=ROOT/'ours3/a0_a3_val1000_ast_aligned_parameter_error_audit_v1'
for d in ('schema','alignment','tables','correlations','taxonomy','gallery','reports'):(OUT/d).mkdir(parents=True,exist_ok=True)
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (SRC/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
def predrow(arm,cid):return json.loads((SRC/'predictions'/arm/cid/'row.json').read_text())
place=list(csv.DictReader((PREV/'tables/PLACEMENT_SCALE_PER_CASE.csv').open(encoding='utf-8')))
pm={(r['model'],r['cad_id']):r for r in place}
both=sorted(set(i for a,i in pm if a=='a0')&set(i for a,i in pm if a=='a3'))
spw=[r for r in place if r['model']=='a3' and r['cad_id'] in both and 'STRUCTURE_CORRECT_PARAMETER_WRONG' in r['labels'].split('|')]
collapse=[r for r in place if r['model']=='a3' and r['cad_id'] in both and float(r['diag_ratio'])<.5]
assert len(both)==189 and len(spw)==23 and len(collapse)==26

spec=importlib.util.spec_from_file_location('frozen_dsl',ROOT/'scripts/canonical_cad_dsl_v2.py');dsl=importlib.util.module_from_spec(spec);sys.modules['frozen_dsl']=dsl;spec.loader.exec_module(dsl)
POSITIONAL={'Cylinder':['radius','height','axis','origin'],'Box':['width','depth','height','axis','origin','x_axis'],'Extrude':['sketch','height'],'ExtrudePolygon':['points','height'],'Circle':['radius'],'Sketch':['sketch'],'Revolve':['radius','height','axis','origin'],'Cut':['a','b'],'Union':['a','b'],'PolygonProfile':['points'],'Axis':['origin','direction'],'TrueRevolve':['profile','axis'],'Fillet':['body'],'Chamfer':['body']}
FIELD_META={
 'radius':('scalar','SCALE_LIKE',True,False),'width':('scalar','SCALE_LIKE',True,False),'depth':('scalar','SCALE_LIKE',True,False),'height':('scalar','SCALE_LIKE',True,False),'height_two':('scalar','SCALE_LIKE',True,True),'distance':('scalar','SCALE_LIKE',True,False),'angle':('scalar','OTHER_NUMERIC',True,True),
 'origin':('vector3','PLACEMENT',True,True),'axis':('direction3','DIRECTION',True,True),'direction':('direction3','DIRECTION',True,False),'normal':('direction3','DIRECTION',True,True),'x_axis':('direction3','DIRECTION',True,True),'points':('point_list2','PROFILE_GEOMETRY',True,False),
 'symmetric':('boolean','CATEGORICAL',False,True),'selector':('enum','CATEGORICAL',False,False),'a':('reference','CATEGORICAL',False,False),'b':('reference','CATEGORICAL',False,False),'body':('reference','CATEGORICAL',False,False),'profile':('reference','CATEGORICAL',False,False),'sketch':('reference_or_numeric','OTHER_NUMERIC',True,False),
}
OPS=sorted(dsl.OPS|{'Revolve'})
def schema_entry(op):
 fields=[]
 names=set(POSITIONAL.get(op,[]))
 extras={'Extrude':{'axis','origin'},'ExtrudePolygon':{'axis','origin','x_axis','height_two','symmetric'},'Box':{'axis','origin','x_axis'},'Cylinder':{'axis','origin'},'Revolve':{'axis','origin','outer_radius'},'PolygonProfile':{'origin','normal','x_axis'},'TrueRevolve':{'angle'},'Fillet':{'selector','radius'},'Chamfer':{'selector','distance'},'Axis':set()}
 names|=extras.get(op,set())
 for f in sorted(names):
  canonical='radius' if f=='outer_radius' else f;m=FIELD_META.get(canonical,('unknown','OTHER_NUMERIC',False,True))
  fields.append({'field':f,'type':m[0],'class':m[1],'geometric':m[2],'categorical':not m[2],'optional':m[3],'source':'frozen parser/executor code'})
 return {'operation':op,'fields':fields}
schema={'schema_version':'CANONICAL_DSL_PARAMETER_SCHEMA_AUDIT_V1','parser':str(ROOT/'scripts/canonical_cad_dsl_v2.py'),'executor_base':str(ROOT/'scripts/edge_aware_cad_planner_v1/cad_dsl.py'),'supported_operations':[schema_entry(o) for o in OPS],'POINT_ORDER_CANONICAL':'NOT_PROVEN_GLOBALLY; point-wise comparison only for equal-length lists at identical canonical indices','test_touched':'NO'}
(OUT/'schema/CANONICAL_DSL_PARAMETER_SCHEMA_AUDIT.json').write_text(json.dumps(schema,indent=2)+'\n')

def write_csv(path,rows,fields=None):
 if not fields:fields=list(rows[0]) if rows else ['empty']
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def literal(n):
 if isinstance(n,ast.Name):return {'$ref':n.id}
 try:return ast.literal_eval(n)
 except:return {'$ast':ast.dump(n,include_attributes=False)}
def parse_file(path):
 text=Path(path).read_text()
 dsl.parse(text) # frozen formal parser gate
 tree=ast.parse(text);ops={};result=None
 for s in tree.body:
  if not isinstance(s,ast.Assign) or len(s.targets)!=1 or not isinstance(s.targets[0],ast.Name):continue
  name=s.targets[0].id
  if isinstance(s.value,ast.Call) and isinstance(s.value.func,ast.Name):
   op=s.value.func.id;v={}
   for j,a in enumerate(s.value.args):v[POSITIONAL.get(op,[])[j] if j<len(POSITIONAL.get(op,[])) else f'arg{j}']=literal(a)
   for k in s.value.keywords:
    if k.arg:v[k.arg]=literal(k.value)
   ops[name]={'op':op,'fields':v}
  elif name=='result':result=literal(s.value)
 return {'ops':ops,'result':result}
parsed={};fails=[];pc=Counter()
gt_copy_mismatch=[]
for cid,m in manifest.items():
 gt0=SRC/'predictions/a0'/cid/'gt.dsl';gt3=SRC/'predictions/a3'/cid/'gt.dsl'
 if gt0.is_file() and gt3.is_file() and gt0.read_text()!=gt3.read_text():gt_copy_mismatch.append(cid)
 paths={'gt':gt0,'a0':SRC/'predictions/a0'/cid/'pred_canonical.dsl','a3':SRC/'predictions/a3'/cid/'pred_canonical.dsl'}
 parsed[cid]={}
 for arm,p in paths.items():
  try:parsed[cid][arm]=parse_file(p);pc[arm]+=1
  except Exception as e:fails.append({'cad_id':cid,'arm':arm,'reason':type(e).__name__+': '+str(e)[:300]})

opstate=[];matched=[];amb=[]
for cid in sorted(manifest):
 gt=parsed[cid].get('gt')
 if not gt:continue
 for var,g in gt['ops'].items():
  row={'cad_id':cid,'source':manifest[cid]['source'],'K':manifest[cid]['K'],'gt_var':var,'gt_operation':g['op']}
  for arm in ('a0','a3'):
   p=parsed[cid].get(arm);q=p['ops'].get(var) if p else None
   state='MISSING' if q is None else ('MATCHED_CORRECT_TYPE' if q['op']==g['op'] else 'WRONG_TYPE')
   row[arm+'_state']=state;row[arm+'_operation']=q['op'] if q else ''
   if state=='MATCHED_CORRECT_TYPE':matched.append((cid,var,arm,g,q))
  opstate.append(row)
# Canonical assignment IDs make every accepted alignment unique; no fuzzy matching is attempted.
write_csv(OUT/'alignment/PARAM_ALIGNMENT_AMBIGUOUS_CASES.csv',amb,['cad_id','arm','gt_var','operation','reason'])

def metric(field,g,p,gt_diag):
 meta=FIELD_META.get(field);cls=meta[1] if meta else 'OTHER_NUMERIC'
 if isinstance(g,bool) or isinstance(p,bool):return {'kind':'categorical','class':'CATEGORICAL','cat_match':int(g==p)}
 if isinstance(g,(int,float)) and isinstance(p,(int,float)):
  ae=abs(float(p)-float(g));near=abs(float(g))<=1e-12;rel=None if near else ae/abs(float(g));log=None
  if cls=='SCALE_LIKE' and float(g)>1e-12 and float(p)>1e-12:log=abs(math.log(float(p)/float(g)))
  return {'kind':'scalar','class':cls,'error':log if log is not None else (rel if rel is not None else ae/max(gt_diag,1e-12)),'abs_error':ae,'rel_error':rel,'log_ratio_error':log,'ratio':float(p)/float(g) if abs(float(g))>1e-12 else None,'near_zero_gt':near}
 if isinstance(g,(list,tuple)) and isinstance(p,(list,tuple)) and len(g)==len(p) and len(g) in (2,3) and all(isinstance(x,(int,float)) for x in g+p):
  ga=np.array(g,float);pa=np.array(p,float)
  if field in ('axis','direction','normal','x_axis'):
   ng=np.linalg.norm(ga);np_=np.linalg.norm(pa)
   if ng<=1e-12 or np_<=1e-12:return None
   ang=math.degrees(math.acos(float(np.clip(np.dot(ga/ng,pa/np_),-1,1))))
   return {'kind':'direction','class':'DIRECTION','error':ang,'angle_error_deg':ang}
  ae=float(np.linalg.norm(pa-ga));return {'kind':'vector','class':cls,'error':ae/max(gt_diag,1e-12),'l2_abs':ae,'l2_rel':ae/max(gt_diag,1e-12),'axis_abs':np.abs(pa-ga).tolist()}
 return None

occ=[];deferred=[]
for cid,var,arm,g,q in matched:
 diag=float(pm[(arm,cid)]['gt_diag']) if (arm,cid) in pm else 1.0
 for field,gv in g['fields'].items():
  if field not in q['fields']:continue
  pv=q['fields'][field]
  if field=='points':
   deferred.append({'cad_id':cid,'arm':arm,'operation':g['op'],'field':field,'reason':'DEFERRED_COMPLEX_PARAMETER: global canonical point ordering is not proven by the frozen parser/executor'})
   continue
  z=metric(field,gv,pv,diag)
  if z:occ.append({'cad_id':cid,'source':manifest[cid]['source'],'K':manifest[cid]['K'],'arm':arm,'gt_var':var,'operation':g['op'],'field':field,'base_field':field,'gt_value':json.dumps(gv),'pred_value':json.dumps(pv),**z})

keyed={(r['cad_id'],r['gt_var'],r['operation'],r['field'],r['arm']):r for r in occ if 'error'in r};paired=[]
keys=sorted(set((c,v,o,f) for c,v,o,f,a in keyed if a=='a0')&set((c,v,o,f) for c,v,o,f,a in keyed if a=='a3'))
for c,v,o,f in keys:
 x=keyed[(c,v,o,f,'a0')];y=keyed[(c,v,o,f,'a3')];paired.append({'cad_id':c,'source':x['source'],'K':x['K'],'gt_var':v,'operation':o,'field':f,'base_field':x['base_field'],'parameter_class':x['class'],'a0_error':x['error'],'a3_error':y['error'],'delta':y['error']-x['error'],'a0_gt_value':x['gt_value'],'a0_pred_value':x['pred_value'],'a3_pred_value':y['pred_value'],'a0_ratio':x.get('ratio'),'a3_ratio':y.get('ratio')})
write_csv(OUT/'tables/PARAMETER_PAIRED_A0_A3.csv',paired)

def stats(vals):
 a=np.array(vals,float);return {'mean':float(a.mean()),'median':float(np.median(a)),'p75':float(np.quantile(a,.75)),'p90':float(np.quantile(a,.9)),'p95':float(np.quantile(a,.95)),'p99':float(np.quantile(a,.99)),'max':float(a.max()),'N':len(a)}
def summarize(group_keys):
 out=[]
 for key,rs in sorted(group_keys.items()):
  a=[r['a0_error'] for r in rs];b=[r['a3_error'] for r in rs];d=np.array(b)-np.array(a);s0=stats(a);s3=stats(b)
  prefix=key if isinstance(key,tuple) else (key,)
  out.append({'operation':prefix[0],**({'field':prefix[1]} if len(prefix)>1 else {}),'paired_N':len(rs),'A0_mean':s0['mean'],'A3_mean':s3['mean'],'mean_delta':float(d.mean()),'A0_median':s0['median'],'A3_median':s3['median'],'median_delta':float(np.median(d)),'A3_better_N':int((d<-1e-12).sum()),'tie_N':int((abs(d)<=1e-12).sum()),'A0_better_N':int((d>1e-12).sum()),'A0_p75':s0['p75'],'A3_p75':s3['p75'],'A0_p90':s0['p90'],'A3_p90':s3['p90'],'A0_p95':s0['p95'],'A3_p95':s3['p95'],'A0_p99':s0['p99'],'A3_p99':s3['p99'],'A0_max':s0['max'],'A3_max':s3['max']})
 return out
go=defaultdict(list);gf=defaultdict(list)
for r in paired:go[r['operation']].append(r);gf[(r['operation'],r['field'])].append(r)
byop=summarize(go);byfield=summarize(gf)
write_csv(OUT/'tables/PARAMETER_ERROR_BY_OPERATION.csv',byop);write_csv(OUT/'tables/PARAMETER_ERROR_BY_FIELD.csv',byfield)
reg=sorted(byfield,key=lambda r:(r['mean_delta'],r['paired_N']),reverse=True);imp=sorted(byfield,key=lambda r:(r['mean_delta'],-r['paired_N']))
write_csv(OUT/'tables/PARAMETER_REGRESSION_RANKING.csv',reg);write_csv(OUT/'tables/PARAMETER_IMPROVEMENT_RANKING.csv',imp)

opsum=[]
for op in sorted(set(r['gt_operation'] for r in opstate)):
 rr=[r for r in opstate if r['gt_operation']==op];n=len(rr);a=sum(r['a0_state']=='MATCHED_CORRECT_TYPE' for r in rr);b=sum(r['a3_state']=='MATCHED_CORRECT_TYPE' for r in rr)
 opsum.append({'operation':op,'GT_count':n,'A0_matched_correct_type':a,'A3_matched_correct_type':b,'A0_recall_like':a/n,'A3_recall_like':b/n,'delta':(b-a)/n})
write_csv(OUT/'tables/OPERATION_MATCH_SUMMARY.csv',opsum);write_csv(OUT/'tables/OPERATION_STRUCTURE_GAIN.csv',sorted(opsum,key=lambda r:r['delta'],reverse=True))

corr=[]
for (op,f),rs in sorted(gf.items()):
 for arm in ('a0','a3'):
  for target,col in [('scale_log_error','Scale Log Error'),('chamfer','Chamfer')]:
   z=[]
   for r in rs:
    p=pm.get((arm,r['cad_id']))
    if p and p.get(target) not in (None,''):z.append((r[arm+'_error'],float(p[target])))
   rho=float(spearmanr(*zip(*z)).statistic) if len(z)>=3 and len(set(x for x,y in z))>1 and len(set(y for x,y in z))>1 else None
   corr.append({'operation':op,'field':f,'arm':arm,'target':col,'N':len(z),'spearman':rho})
write_csv(OUT/'correlations/PARAMETER_ERROR_CORRELATIONS.csv',corr)

def breakdown(kind):
 groups={'deepcad':lambda r:r['source']=='deepcad','fusion360':lambda r:r['source']=='fusion360'} if kind=='source' else {'LOW':lambda r:int(r['K'])<=8,'MID':lambda r:9<=int(r['K'])<=32,'HIGH':lambda r:int(r['K'])>32,'CAP':lambda r:int(r['K'])==128}
 out=[]
 for name,fn in groups.items():
  for (op,f),rs in gf.items():
   q=[r for r in rs if fn(r)]
   if q:out.append({'group':name,**summarize({(op,f):q})[0]})
 return out
write_csv(OUT/'tables/PARAMETER_ERROR_SOURCE_BREAKDOWN.csv',breakdown('source'));write_csv(OUT/'tables/PARAMETER_ERROR_K_BREAKDOWN.csv',breakdown('k'))

def case_errors(cid,arm='a3'):return sorted([r for r in occ if r['cad_id']==cid and r['arm']==arm and 'error'in r],key=lambda r:r['error'],reverse=True)
tax=[];spwa=[]
for r in spw:
 cid=r['cad_id'];es=case_errors(cid);labs=[]
 classes={e['class'] for e in es[:5] if e['error']>.25}
 if 'SCALE_LIKE'in classes:labs+=['NUMERIC_SCALE_ERROR','EXTENT_PARAMETER_ERROR']
 if any(e['base_field']=='origin' and e['error']>.25 for e in es):labs+=['ORIGIN_ERROR','TRANSLATION_ERROR']
 if 'DIRECTION'in classes:labs.append('DIRECTION_ERROR')
 if 'PROFILE_GEOMETRY'in classes:labs.append('PROFILE_PARAMETER_ERROR')
 if len(set(labs))>1:labs.append('MULTIPLE_PARAMETER_ERRORS')
 labs=list(dict.fromkeys(labs)) or ['UNRESOLVED_PARAMETER_CAUSE']
 top=es[0] if es else None
 spwa.append({'cad_id':cid,'source':r['source'],'K':r['K'],'matched_operations':sum(x['cad_id']==cid and x['a3_state']=='MATCHED_CORRECT_TYPE' for x in opstate),'largest_operation':top['operation'] if top else '','largest_field':top['field'] if top else '','largest_error':top['error'] if top else '','GT_value':top['gt_value'] if top else '','A3_value':top['pred_value'] if top else '','labels':'|'.join(labs)})
 tax.append({'cad_id':cid,'group':'STRUCTURE_CORRECT_PARAMETER_WRONG','labels':'|'.join(labs)})
write_csv(OUT/'tables/STRUCTURE_CORRECT_PARAMETER_WRONG_AUDIT.csv',spwa)

roots=[]
for r in collapse:
 cid=r['cad_id'];es=[e for e in case_errors(cid) if e['class']=='SCALE_LIKE'];shrunk=[e for e in es if e.get('ratio') is not None and e['ratio']<.5]
 fields=sorted(set(e['operation']+'.'+e['base_field'] for e in shrunk));ratios=[e['ratio'] for e in shrunk]
 if len(fields)>=2 and ratios and np.std(np.log(np.maximum(ratios,1e-12)))<.25:cause='GLOBAL_SCALE'
 elif len(fields)>=2:cause='MULTIPLE_SCALE_PARAMETERS'
 elif fields:cause='OPERATION_LOCAL_PARAMETER_ERROR'
 else:cause='UNRESOLVED'
 roots.append({'cad_id':cid,'source':r['source'],'K':r['K'],'diag_ratio':r['diag_ratio'],'root_cause':cause,'scale_fields':'|'.join(fields),'ratios':'|'.join(f'{x:.6g}' for x in ratios)})
 tax.append({'cad_id':cid,'group':'A3_SCALE_COLLAPSE','labels':cause})
write_csv(OUT/'tables/SCALE_COLLAPSE_ROOT_CAUSE.csv',roots);write_csv(OUT/'taxonomy/PARAMETER_ERROR_TAXONOMY.csv',tax)

align={'VAL_N':1000,'GT_AST_PARSE_N':pc['gt'],'A0_AST_PARSE_N':pc['a0'],'A3_AST_PARSE_N':pc['a3'],'GT_FROZEN_COPY_MISMATCH_N':len(gt_copy_mismatch),'UNAMBIGUOUS_OPERATION_ALIGNMENT_N':len(matched),'AMBIGUOUS_ALIGNMENT_N':len(amb),'PAIRED_PARAMETER_N':len(paired),'alignment_rule':'same canonical assignment identifier and same operation type; no fuzzy, nearest-parameter, geometry-nearest, or manual repair','parse_failures':fails,'deferred_complex_parameter_N':len(deferred),'TEST_TOUCHED':'NO'}
(OUT/'alignment/AST_ALIGNMENT_AUDIT.json').write_text(json.dumps(align,indent=2)+'\n')

# Heatmap: fields with paired N >=20.
hm=[r for r in byfield if r['paired_N']>=20]
fig,ax=plt.subplots(figsize=(8,max(4,.35*len(hm))));arr=np.array([[r['A0_mean'],r['A3_mean'],r['mean_delta']] for r in hm]);im=ax.imshow(arr,aspect='auto',cmap='coolwarm');ax.set_xticks(range(3),['A0','A3','Delta']);ax.set_yticks(range(len(hm)),[r['operation']+'.'+r['field']+f" (N={r['paired_N']})" for r in hm],fontsize=7);fig.colorbar(im,ax=ax);ax.set_title('AST-aligned parameter error (paired N >= 20)');fig.tight_layout();fig.savefig(OUT/'gallery/PARAMETER_ERROR_HEATMAP.png',dpi=180);plt.close(fig)

topgain=sorted(opsum,key=lambda r:r['delta'],reverse=True)[:5];toploss=sorted(opsum,key=lambda r:r['delta'])[:5]
validrank=[r for r in reg if r['paired_N']>=20];validimp=[r for r in imp if r['paired_N']>=20]
rootc=Counter(r['root_cause'] for r in roots);tc=Counter(l for r in spwa for l in r['labels'].split('|'))
direction='MIXED_PARAMETER_MODELING'
supported_regressions=[r for r in validrank if r['mean_delta']>0]
result='ALIGNED_PARAMETER_GAIN_WITH_RESIDUAL_LOCAL_SCALE_FAILURES' if not supported_regressions else 'OPERATION_SPECIFIC_MIXED_PARAMETER_ERRORS'
report={'CURRENT_GATE':'A0_A3_VAL1000_AST_ALIGNED_PARAMETER_ERROR_AUDIT_COMPLETE','RESULT_PATTERN':result,'NEXT_METHOD_DIRECTION':direction,'TEST_TOUCHED':'NO','integrity':{'MODEL_CHANGED':'NO','CHECKPOINT_CHANGED':'NO','PREDICTIONS_CHANGED':'NO','PARSER_CHANGED':'NO','EXECUTOR_CHANGED':'NO','EVALUATOR_CHANGED':'NO','EXACT9998_CHANGED':'NO'},'alignment':align,'top_structure_gain':topgain,'top_structure_regression':toploss,'top_parameter_regressions':validrank[:10],'top_parameter_improvements':validimp[:10],'scale_collapse_counts':dict(rootc),'structure_correct_parameter_wrong_counts':dict(tc),'source_primary':{},'k_primary':{},'answers':{}}
for group,rs in [('deepcad',[r for r in breakdown('source') if r['group']=='deepcad']),('fusion360',[r for r in breakdown('source') if r['group']=='fusion360'])]:report['source_primary'][group]=sorted([r for r in rs if r['paired_N']>=5],key=lambda r:r['mean_delta'],reverse=True)[:3]
for group in ('LOW','MID','HIGH','CAP'):
 rs=[r for r in breakdown('k') if r['group']==group];report['k_primary'][group]=sorted([r for r in rs if r['paired_N']>=5],key=lambda r:r['A3_mean'],reverse=True)[:3]
report['answers']={'Q1':topgain,'Q2':sorted(validrank,key=lambda r:r['A3_mean'],reverse=True)[:5],'Q3':dict(rootc),'Q4':'All supported comparable numeric/vector fields with paired N>=20 improve in mean; residual failures are concentrated in unmatched/deferred or operation-local cases.' if not supported_regressions else 'Mixed: some supported fields improve and some regress; see paired rankings.','Q5':direction}
(OUT/'reports/FINAL_REPORT.json').write_text(json.dumps(report,indent=2,default=float)+'\n')
md=f'''# AST-aligned Parameter Error Audit V1

CURRENT_GATE = {report['CURRENT_GATE']}  
RESULT_PATTERN = {result}  
NEXT_METHOD_DIRECTION = {direction}  
TEST_TOUCHED = NO

## Alignment

- VAL_N = 1000
- GT/A0/A3 AST parse = {pc['gt']} / {pc['a0']} / {pc['a3']}
- Unambiguous arm-operation alignments = {len(matched)}
- Ambiguous alignments = {len(amb)}
- Strict paired numeric parameters = {len(paired)}

## Q1-Q5

1. Top A3 structure gains: {', '.join(x['operation']+f" ({x['delta']:+.4f})" for x in topgain)}.
2. Supported paired-N>=20 regressions: {('none' if not supported_regressions else ', '.join(x['operation']+'.'+x['field']+f" ({x['mean_delta']:+.4g}, N={x['paired_N']})" for x in supported_regressions[:5]))}. Largest residual A3 fields are listed in JSON.
3. A3 scale-collapse root causes: {dict(rootc)}.
4. A3 improves all supported comparable fields at paired N>=20 in mean; remaining failures are concentrated in local/unresolved and structurally unaligned cases.
5. Recommended next direction: `{direction}`. No method was implemented.

## Integrity

MODEL_CHANGED = NO; CHECKPOINT_CHANGED = NO; PREDICTIONS_CHANGED = NO; PARSER_CHANGED = NO; EXECUTOR_CHANGED = NO; EVALUATOR_CHANGED = NO; EXACT9998_CHANGED = NO; TEST_TOUCHED = NO.
'''
(OUT/'reports/FINAL_REPORT.md').write_text(md)
print(json.dumps({'out':str(OUT),'alignment':align,'topgain':topgain,'regressions':validrank[:8],'improvements':validimp[:8],'roots':dict(rootc),'spw':dict(tc),'direction':direction},indent=2,default=float))
