#!/usr/bin/env python3
"""Read-only rare-type failure audit for DORA_FITTED_CURVE_DATASET_V1."""
from __future__ import annotations
import hashlib,json,sys
from collections import Counter,defaultdict
from pathlib import Path
import numpy as np
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');sys.path[:0]=[str(ROOT/'scripts')]
from dora_fitted_curve_dataset_v1 import sample_fit,gt_samples,graph_from_dora
BASE=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1'; COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'; OUT=ROOT/'ours3/dora_fitted_curve_dataset_v1_1/rare_type_recovery_audit_v3'
FT=('LINE','CIRCLE','ARC','ELLIPSE','BSPLINE'); CL=('MATCHED_1_TO_1','FRAGMENTED','PARTIAL','MERGED','UNMATCHED')
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def objverts(p):
 return np.asarray([[float(x) for x in q.split()[1:4]] for q in Path(p).read_text(errors='ignore').splitlines() if q.startswith('v ')],float)
def farr(f):
 q=dict(f)
 for k in ('origin','direction','center','normal','x_axis','y_axis','major_axis','minor_axis'):
  if k in q:q[k]=np.asarray(q[k],float)
 if q.get('type')=='BSPLINE':q['tck']=[np.asarray(q['tck'][0]),np.asarray(q['tck'][1]),int(q['tck'][2])]
 return q
def cause(f,c,gt_type):
 m=c.get('metrics',{}); typ=f['type']; cls=c['classification']
 if cls=='FRAGMENTED':return 'A_CHAIN_FRAGMENTATION'
 if cls=='MERGED':return 'B_CHAIN_MERGE'
 family='CIRCLE' if typ=='ARC' else typ
 if gt_type and family!=gt_type:return 'D_GT_TYPE_MAPPING'
 if f.get('normalized_residual',0)>0.005:return 'C_FITTING_ERROR'
 if m and m.get('tangent_compatibility',1)<.75:return 'G_TANGENT_MISMATCH'
 if m and min(m.get('coverage_d2g',1),m.get('coverage_g2d',1))<.85:return 'F_CORRESPONDENCE_COVERAGE'
 if m and max(m.get('d2g_mean_rel',0),m.get('g2d_mean_rel',0))>.008:return 'E_CORRESPONDENCE_DISTANCE'
 return 'H_TRUE_UNMATCHED' if cls=='UNMATCHED' else 'I_OTHER'
def choose(rows,n=15):
 # deterministic category coverage first, remaining hash order
 out=[];seen=set()
 for c in sorted(set(r['root_cause'] for r in rows)):
  z=sorted([r for r in rows if r['root_cause']==c],key=lambda r:hashlib.sha256((r['cad_id']+str(r['dora_curve_index'])).encode()).hexdigest())
  if z:out.append(z[0]);seen.add((z[0]['cad_id'],z[0]['dora_curve_index']))
 for r in sorted(rows,key=lambda r:hashlib.sha256((r['cad_id']+str(r['dora_curve_index'])).encode()).hexdigest()):
  if len(out)>=n:break
  if (r['cad_id'],r['dora_curve_index']) not in seen:out.append(r);seen.add((r['cad_id'],r['dora_curve_index']))
 return out[:n]
def render(row,paths,outp):
 import matplotlib;matplotlib.use('Agg');import matplotlib.pyplot as plt
 cad=row['cad_id']; cdir=BASE/'cad'/cad;fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves'];f=farr(fits[row['dora_curve_index']]);fp,_,_,_=sample_fit(f)
 z=np.load(paths['dora']);xyz,adj,edges=graph_from_dora(z);ch=np.load(cdir/'dora/chains.npz');off=ch['offsets'];ids=ch['vertex_indices_flat'][off[row['dora_chain_id']]:off[row['dora_chain_id']+1]];chain=np.asarray([xyz[int(i)] for i in ids])
 _,gts=gt_samples(paths['step']);g=next((x for x in gts if x['gt_id']==row['gt_curve_id']),None);gp=np.asarray(g['points']) if g else np.zeros((0,3));mesh=objverts(paths['obj']);cen=mesh.mean(0);_,_,vh=np.linalg.svd(mesh-cen,full_matrices=False);P=lambda x:(x-cen)@vh[:2].T
 fig,ax=plt.subplots(figsize=(6,6));mm=P(mesh);ax.scatter(mm[::max(1,len(mm)//5000),0],mm[::max(1,len(mm)//5000),1],s=.15,c='.7',label='mesh');q=P(chain);ax.plot(q[:,0],q[:,1],c='tab:red',lw=1,label='Dora chain');q=P(fp);ax.plot(q[:,0],q[:,1],c='tab:blue',lw=1.5,label='fitted curve');
 if len(gp):q=P(gp);ax.plot(q[:,0],q[:,1],c='tab:green',lw=1.5,label='nearest GT BRep')
 ax.set_title(f"{cad} | {row['fitted_type']} | {row['classification']} | {row['root_cause']}");ax.legend(fontsize=7);ax.set_aspect('equal');fig.tight_layout();fig.savefig(outp,dpi=180);plt.close(fig)
def main():
 OUT.mkdir(parents=True,exist_ok=False);co={r['cad_id']:r for r in [json.loads(x) for x in COHORT.read_text().splitlines() if x]}; table={t:{c:0 for c in CL} for t in FT};conf=defaultdict(lambda:Counter());rare=[]
 for cdir in sorted((BASE/'cad').iterdir()):
  cad=cdir.name; fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves'];corr=json.loads((cdir/'correspondence.json').read_text())['records'];gts=json.loads((cdir/'gt_brep_curves.json').read_text())['curves'];gtby={x['edge_id']:x for x in gts}
  for c in corr:
   i=int(c['dora_curve_index']);f=fits[i];gt=gtby.get(c['gt_curve_id']);gt_type=None if gt is None else ('BSPLINE' if gt['curve_type']=='BEZIER' else gt['curve_type']);table[f['type']][c['classification']]+=1
   if gt_type:conf[gt_type][f['type']]+=1
   if f['type'] in ('ELLIPSE','BSPLINE') and c['classification']!='MATCHED_1_TO_1':
    m=c.get('metrics',{});sp,_,_,_=sample_fit(farr(f));rare.append({'cad_id':cad,'dora_curve_index':i,'dora_chain_id':f['chain_id'],'fitted_type':f['type'],'gt_candidate_type':gt_type,'gt_curve_id':c.get('gt_curve_id'),'classification':c['classification'],'bidirectional_distance':{'dora_to_gt_mean_rel':m.get('d2g_mean_rel'),'gt_to_dora_mean_rel':m.get('g2d_mean_rel')},'coverage':{'dora_to_gt':m.get('coverage_d2g'),'gt_to_dora':m.get('coverage_g2d')},'tangent_compatibility':m.get('tangent_compatibility'),'dora_curve_length':f.get('curve_length'),'gt_curve_length':None if gt is None else gt.get('length'),'dora_bbox_extent':np.ptp(sp,axis=0).astype(float).tolist(),'fit_normalized_residual':f.get('normalized_residual'),'root_cause':cause(f,c,gt_type)})
 dump(OUT/'TYPE_CONDITIONED_FAILURE_TABLE.json',{'columns':['TOTAL_FITTED',*CL],'table':{t:{'TOTAL_FITTED':sum(table[t].values()),**table[t]} for t in FT}});dump(OUT/'GT_BY_FITTED_CONFUSION.json',{'rows':'GT_BRep_type','columns':'fitted_type','matrix':{k:{t:int(v[t]) for t in FT} for k,v in conf.items()}});(OUT/'RARE_TYPE_FAILURE_RECORDS.jsonl').write_text(''.join(json.dumps(x,sort_keys=True)+'\n' for x in rare));dump(OUT/'ROOT_CAUSE_COUNTS.json',dict(Counter(x['root_cause'] for x in rare)))
 can=[]
 for typ in ('ELLIPSE','BSPLINE'):can+=choose([r for r in rare if r['fitted_type']==typ],15)
 if len([x for x in can if x['fitted_type']=='ELLIPSE'])<15 or len([x for x in can if x['fitted_type']=='BSPLINE'])<15:raise RuntimeError('insufficient rare failure canaries')
 (OUT/'visual_canary').mkdir();records=[]
 for n,r in enumerate(can):
  a=co[r['cad_id']]['assets'];paths={'obj':Path(a['model_obj']['path']),'dora':Path(a['dora_salient_edges']['path']),'step':Path(a['model_step']['path'])};name=f"{n:02d}_{r['fitted_type']}_{r['cad_id']}_{r['dora_curve_index']}.png";render(r,paths,OUT/'visual_canary'/name);records.append({**r,'visualization':name})
 dump(OUT/'VISUAL_CANARY_MANIFEST.json',{'ellipse_failure_canaries':15,'bspline_failure_canaries':15,'records':records});dump(OUT/'AUDIT_FREEZE.json',{'CURRENT_GATE':'DORA_FITTED_CURVE_DATASET_V1_1_RARE_TYPE_RECOVERY_AUDIT_PASS','V1_MODIFIED':False,'TRAINING_STARTED':False,'DECODE_DEV50_PREDICTIONS_READ':False,'PILOT150_READ':False,'ANCHOR_EVAL100_READ':False,'OFFICIAL_TEST_READ':False,'rare_failures':len(rare),'visual_canaries':len(records),'next_action':'Targeted fix requires explicit root-cause review; V1.1 rebuild not started'})
if __name__=='__main__':main()
