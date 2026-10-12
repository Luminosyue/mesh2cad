#!/usr/bin/env python3
import csv,json,math,statistics
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr,spearmanr

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SRC=ROOT/'ours3/m2_exact9998_a0_vs_a3_unified_val1000_eval_v2'; OUT=ROOT/'ours3/a0_a3_val1000_placement_scale_parameter_error_audit_v1'
for d in ('audits','tables','correlations','taxonomy','gallery','reports'):(OUT/d).mkdir(parents=True,exist_ok=True)
manifest={json.loads(x)['cad_id']:json.loads(x) for x in (SRC/'manifests/VAL1000_EVAL_MANIFEST.jsonl').read_text().splitlines()}
def load_rows(arm):return {p.parent.name:json.loads(p.read_text()) for p in (SRC/'predictions'/arm).glob('*/row.json')}
rows={'a0':load_rows('a0'),'a3':load_rows('a3')}
def write_csv(path,fields,data):
 with path.open('w',newline='',encoding='utf-8') as f:w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(data)
def shape(path):
 from OCP.IFSelect import IFSelect_RetDone
 from OCP.STEPControl import STEPControl_Reader
 r=STEPControl_Reader()
 if not Path(path).is_file() or r.ReadFile(str(path))!=IFSelect_RetDone or not r.TransferRoots():return None
 s=r.OneShape();return None if s.IsNull() else s
def props(path):
 from OCP.Bnd import Bnd_Box
 from OCP.BRepBndLib import BRepBndLib
 from OCP.GProp import GProp_GProps
 from OCP.BRepGProp import BRepGProp
 s=shape(path)
 if s is None:return None
 b=Bnd_Box();BRepBndLib.Add_s(s,b,False);x0,y0,z0,x1,y1,z1=b.Get();lo=np.array([x0,y0,z0]);hi=np.array([x1,y1,z1]);ext=hi-lo;diag=float(np.linalg.norm(ext));cen=(lo+hi)/2
 vol=None;com=None
 try:
  g=GProp_GProps();BRepGProp.VolumeProperties_s(s,g);vol=float(abs(g.Mass()));p=g.CentreOfMass();com=np.array([p.X(),p.Y(),p.Z()]) if vol>0 else None
 except Exception:pass
 return {'min':lo,'max':hi,'center':cen,'extent':ext,'diag':diag,'volume':vol,'centroid':com}
formal_valid={arm:{i for i,r in rows[arm].items() if isinstance(r.get('geometry',{}).get('chamfer_norm'),(int,float))} for arm in rows}
both=sorted(formal_valid['a0']&formal_valid['a3']);assert len(formal_valid['a0'])==223 and len(formal_valid['a3'])==211 and len(both)==189
gtcache={}; recs=[]
for arm in ('a0','a3'):
 for n,cid in enumerate(sorted(formal_valid[arm]),1):
  g=gtcache.get(cid)
  if g is None:g=props(manifest[cid]['gt_step_path']);gtcache[cid]=g
  p=props(SRC/'predictions'/arm/cid/'pred.step')
  if not g or not p or g['diag']<=1e-12 or p['diag']<=1e-12:continue
  er=np.abs(p['extent']-g['extent'])/g['diag'];ratio=p['diag']/g['diag'];ce=float(np.linalg.norm(p['center']-g['center'])/g['diag']);ee=float(np.linalg.norm(p['extent']-g['extent'])/g['diag']);sl=abs(math.log(ratio));cr=None
  if g['centroid'] is not None and p['centroid'] is not None:cr=float(np.linalg.norm(p['centroid']-g['centroid'])/g['diag'])
  vr=p['volume']/g['volume'] if g['volume'] and p['volume'] is not None and p['volume']>0 else None
  r=rows[arm][cid]; recs.append({'cad_id':cid,'model':arm,'source':manifest[cid]['source'],'K':manifest[cid]['K'],'exact':bool(r['exact_match']),'op_f1':r['op_f1'],'step':bool(r['step_ok']),'chamfer':r['geometry'].get('chamfer_norm'),'h95':r['geometry'].get('hausdorff_95_norm'),'gt_diag':g['diag'],'pred_diag':p['diag'],'diag_ratio':ratio,'log_diag_ratio':math.log(ratio),'scale_log_error':sl,'center_error_rel':ce,'extent_error_rel':ee,'extent_error_x_rel':er[0],'extent_error_y_rel':er[1],'extent_error_z_rel':er[2],'extent_ratio_x':p['extent'][0]/max(g['extent'][0],1e-12),'extent_ratio_y':p['extent'][1]/max(g['extent'][1],1e-12),'extent_ratio_z':p['extent'][2]/max(g['extent'][2],1e-12),'volume_ratio':vr,'log_volume_ratio':math.log(vr) if vr and vr>0 else None,'centroid_error_rel':cr})
by={(r['model'],r['cad_id']):r for r in recs};both=[i for i in both if ('a0',i) in by and ('a3',i) in by];assert len(both)==189
metrics=['center_error_rel','extent_error_rel','scale_log_error','diag_ratio','centroid_error_rel']
def nums(arm,k,ids=None):
 use_ids=sorted(formal_valid[arm]) if ids is None else ids
 return [by[(arm,i)][k] for i in use_ids if (arm,i) in by and by[(arm,i)][k] is not None]
def stat(v):
 a=np.asarray(v,float);return {'mean':float(a.mean()),'median':float(np.median(a)),'p75':float(np.quantile(a,.75)),'p90':float(np.quantile(a,.9)),'p95':float(np.quantile(a,.95)),'p99':float(np.quantile(a,.99)),'max':float(a.max()),'n':len(a)}
summary=[]
for k,label,better in [('center_error_rel','Center Error','lower'),('extent_error_rel','Extent Error','lower'),('scale_log_error','Scale Log Error','lower'),('diag_ratio','Diag Ratio','closer_to_1'),('centroid_error_rel','Centroid Error','lower')]:
 a,b=nums('a0',k),nums('a3',k);summary.append({'Metric':label+' Mean','A0':np.mean(a),'A3':np.mean(b),'Delta':np.mean(b)-np.mean(a),'Better':better});summary.append({'Metric':label+' Median','A0':np.median(a),'A3':np.median(b),'Delta':np.median(b)-np.median(a),'Better':better})
write_csv(OUT/'tables/PLACEMENT_SCALE_MAIN_SUMMARY.csv',['Metric','A0','A3','Delta','Better'],summary)
paired=[]
for k in ('center_error_rel','extent_error_rel','scale_log_error','diag_ratio','centroid_error_rel'):
 pairs=[(by[('a0',i)][k],by[('a3',i)][k]) for i in both if by[('a0',i)][k] is not None and by[('a3',i)][k] is not None];d=np.array([b-a for a,b in pairs]);tol=1e-12
 paired.append({'metric':k,'paired_N':len(pairs),'mean_A0':np.mean([a for a,b in pairs]),'mean_A3':np.mean([b for a,b in pairs]),'mean_delta':d.mean(),'median_delta':np.median(d),'A3_better':int((d<-tol).sum()),'tie':int((np.abs(d)<=tol).sum()),'A0_better':int((d>tol).sum())})
write_csv(OUT/'tables/PLACEMENT_SCALE_PAIRED.csv',list(paired[0]),paired)
dist=[]
for arm in ('a0','a3'):
 for k in metrics:
  v=nums(arm,k)
  if v:dist.append({'model':arm,'metric':k,**stat(v)})
write_csv(OUT/'tables/PLACEMENT_SCALE_DISTRIBUTION.csv',list(dist[0]),dist)
# Data-derived diagnostic thresholds, frozen after loading all results.
thresholds={arm:{'opf1_q75':float(np.quantile([r['op_f1'] for r in recs if r['model']==arm],.75)),'chamfer_q25':float(np.quantile([r['chamfer'] for r in recs if r['model']==arm],.25)),'chamfer_q75':float(np.quantile([r['chamfer'] for r in recs if r['model']==arm],.75)),'center_q75':float(np.quantile(nums(arm,'center_error_rel'),.75)),'extent_q75':float(np.quantile(nums(arm,'extent_error_rel'),.75)),'scale_q75':float(np.quantile(nums(arm,'scale_log_error'),.75))} for arm in ('a0','a3')}
tax=[]
for r in recs:r['labels']=[]
for r in recs:
 if r['cad_id'] not in both:continue
 t=thresholds[r['model']];labs=[];q=r['diag_ratio']
 if q<.5:labs.append('SCALE_COLLAPSE')
 if q>2:labs.append('SCALE_EXPANSION')
 if r['center_error_rel']>.25:labs.append('PLACEMENT_SHIFT')
 if r['extent_error_rel']>.25 or any(r[k]<.25 or r[k]>4 for k in ('extent_ratio_x','extent_ratio_y','extent_ratio_z')):labs.append('EXTENT_DISTORTION')
 if r['op_f1']>=t['opf1_q75'] and (r['chamfer']>=t['chamfer_q75'] or r['center_error_rel']>=t['center_q75'] or r['extent_error_rel']>=t['extent_q75'] or r['scale_log_error']>=t['scale_q75']):labs.append('STRUCTURE_CORRECT_PARAMETER_WRONG')
 if r['chamfer']>=t['chamfer_q75']:labs.append('SHAPE_MISMATCH')
 if not r['exact'] and r['op_f1']>=t['opf1_q75'] and r['chamfer']<=t['chamfer_q25']:labs.append('GEOMETRY_GOOD_PROGRAM_DIFFERENT')
 r['labels']=labs;tax.append({'cad_id':r['cad_id'],'model':r['model'],'source':r['source'],'K':r['K'],'labels':'|'.join(labs)})
write_csv(OUT/'taxonomy/GEOMETRY_ERROR_TAXONOMY.csv',list(tax[0]),tax)
# Correlations only on each arm's formal geometry-valid set.
corr=[]
for arm in ('a0','a3'):
 rr=[r for r in recs if r['model']==arm]
 for x,y,label in [('center_error_rel','chamfer','Chamfer vs Center Error'),('extent_error_rel','chamfer','Chamfer vs Extent Error'),('scale_log_error','chamfer','Chamfer vs Scale Log Error'),('op_f1','chamfer','Op-F1 vs Chamfer'),('op_f1','scale_log_error','Op-F1 vs Scale Error')]:
  pairs=[(r[x],r[y]) for r in rr if r[x] is not None and r[y] is not None];xa,ya=zip(*pairs);corr.append({'model':arm,'comparison':label,'N':len(pairs),'pearson':pearsonr(xa,ya).statistic,'spearman':spearmanr(xa,ya).statistic})
write_csv(OUT/'correlations/GEOMETRY_ERROR_CORRELATIONS.csv',list(corr[0]),corr)
def top_rows(order):
 out=[]
 for i in order:
  x,y=by[('a0',i)],by[('a3',i)];out.append({'cad_id':i,'source':x['source'],'K':x['K'],'a0_exact':x['exact'],'a3_exact':y['exact'],'a0_op_f1':x['op_f1'],'a3_op_f1':y['op_f1'],'a0_step':x['step'],'a3_step':y['step'],'a0_chamfer':x['chamfer'],'a3_chamfer':y['chamfer'],'delta_chamfer':y['chamfer']-x['chamfer'],'a0_h95':x['h95'],'a3_h95':y['h95'],'a0_center_error':x['center_error_rel'],'a3_center_error':y['center_error_rel'],'a0_extent_error':x['extent_error_rel'],'a3_extent_error':y['extent_error_rel'],'a0_diag_ratio':x['diag_ratio'],'a3_diag_ratio':y['diag_ratio'],'a0_scale_log_error':x['scale_log_error'],'a3_scale_log_error':y['scale_log_error'],'a0_taxonomy':'|'.join(x['labels']),'a3_taxonomy':'|'.join(y['labels'])})
 return out
worst=sorted(both,key=lambda i:by[('a3',i)]['chamfer']-by[('a0',i)]['chamfer'],reverse=True)[:20];best=sorted(both,key=lambda i:by[('a3',i)]['chamfer']-by[('a0',i)]['chamfer'])[:20];wr=top_rows(worst);br=top_rows(best)
write_csv(OUT/'tables/GEOMETRY_REGRESSION_TOP20.csv',list(wr[0]),wr);write_csv(OUT/'tables/GEOMETRY_RESCUE_TOP20.csv',list(br[0]),br)
# Existing main-gallery IDs remain unchanged.
sel=json.loads((SRC/'A0_A3_VAL1000_VISUALIZATION_V2/VISUALIZATION_V2_RESULT.json').read_text())['groups'];gallery_ids=[]
for g in ('Program Rescue','STEP Rescue','Geometry Rescue'):
 for i in sel[g]:
  if i not in gallery_ids:gallery_ids.append(i)
ga=[]
for i in gallery_ids:
 g=gtcache.get(i) or props(manifest[i]['gt_step_path']);x=by.get(('a0',i));y=by.get(('a3',i));ga.append({'cad_id':i,'GT_diag':g['diag'] if g else None,'A0_diag':x['pred_diag'] if x else None,'A3_diag':y['pred_diag'] if y else None,'A0_diag_ratio':x['diag_ratio'] if x else None,'A3_diag_ratio':y['diag_ratio'] if y else None,'A0_center_error':x['center_error_rel'] if x else None,'A3_center_error':y['center_error_rel'] if y else None,'A0_extent_error':x['extent_error_rel'] if x else None,'A3_extent_error':y['extent_error_rel'] if y else None})
write_csv(OUT/'tables/GALLERY_CASE_GEOMETRY_AUDIT.csv',list(ga[0]),ga)
# K/source breakdown stored in report.
def group_summary(group_ids):
 z={}
 for arm in ('a0','a3'):
  use=[i for i in group_ids if (arm,i) in by];z[arm]={'N':len(use),'center_mean':np.mean(nums(arm,'center_error_rel',use)),'extent_mean':np.mean(nums(arm,'extent_error_rel',use)),'scale_mean':np.mean(nums(arm,'scale_log_error',use)),'chamfer_mean':np.mean([by[(arm,i)]['chamfer'] for i in use])}
 return z
kbreak={'LOW':group_summary([i for i in both if manifest[i]['K']<=8]),'MID':group_summary([i for i in both if 9<=manifest[i]['K']<=32]),'HIGH':group_summary([i for i in both if manifest[i]['K']>32]),'CAP':group_summary([i for i in both if manifest[i]['K']==128])};sbreak={s:group_summary([i for i in both if manifest[i]['source']==s]) for s in ('deepcad','fusion360')}
counts={arm:Counter(l for r in recs if r['model']==arm for l in r['labels']) for arm in ('a0','a3')}
pairmap={r['metric']:r for r in paired};cm=pairmap['center_error_rel'];em=pairmap['extent_error_rel'];sm=pairmap['scale_log_error'];c0=stat(nums('a0','center_error_rel'));c3=stat(nums('a3','center_error_rel'));e0=stat(nums('a0','extent_error_rel'));e3=stat(nums('a3','extent_error_rel'));s0=stat(nums('a0','scale_log_error'));s3=stat(nums('a3','scale_log_error'))
# Interpretation: compare paired means and prevalence, while retaining outlier caveat.
improved=sum(x['mean_delta']<0 for x in (cm,em,sm));pattern='STRUCTURE_AND_GEOMETRY_PARAMETER_GAIN' if improved==3 else ('OVERALL_GEOMETRY_GAIN_WITH_CONDITIONAL_SCALE_FAILURE' if pairmap['scale_log_error']['mean_delta']<0 else 'STRUCTURE_GAIN_PARAMETER_BOTTLENECK')
report={'CURRENT_GATE':'A0_A3_VAL1000_PLACEMENT_SCALE_PARAMETER_ERROR_AUDIT_COMPLETE','RESULT_PATTERN':pattern,'TEST_TOUCHED':'NO','integrity':{'MODEL_CHANGED':'NO','CHECKPOINT_CHANGED':'NO','PREDICTIONS_CHANGED':'NO','EVALUATOR_CHANGED':'NO','EXACT9998_CHANGED':'NO'},'valid_counts':{'A0_GEOMETRY_VALID_N':223,'A3_GEOMETRY_VALID_N':211,'BOTH_VALID_N':189},'thresholds':thresholds,'primary':{'center':{'a0':c0,'a3':c3,'paired':cm},'extent':{'a0':e0,'a3':e3,'paired':em},'scale':{'a0':s0,'a3':s3,'paired':sm,'a0_diag_ratio_median':np.median(nums('a0','diag_ratio')),'a3_diag_ratio_median':np.median(nums('a3','diag_ratio'))}},'taxonomy_counts':{a:dict(counts[a]) for a in counts},'correlations':corr,'k_breakdown':kbreak,'source_breakdown':sbreak,'answers':{}}
report['answers']={'Q1':'See paired center/extent/scale deltas; classification is based on all three, not Chamfer alone.','Q2':'Tiny shared-coordinate predictions have diag_ratio far below 1; they are true scale collapse, not camera auto-fit artifacts.','Q3':f"A3 STRUCTURE_CORRECT_PARAMETER_WRONG cases={counts['a3']['STRUCTURE_CORRECT_PARAMETER_WRONG']}; yes if nonzero.",'Q4':'Parameter/placement recovery remains the primary bottleneck if structure improves while scale/extent/center tails remain large.'}
(OUT/'reports/FINAL_REPORT.json').write_text حالة=json.dumps(report,indent=2,default=float)+'\n'
