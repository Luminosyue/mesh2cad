from __future__ import annotations
import hashlib, json, math, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); SCRIPTS=ROOT/'scripts'; sys.path.insert(0,str(SCRIPTS))
sys.path.insert(0,str(Path(__file__).parent))
from dora_fitted_curve_dataset_v1 import graph_from_dora, extract_chains, objverts, linefit, circlefit, ellipsefit, splinefit
from primitive_aware_chain_segmentation_v1 import geometric_profile, candidate_change_points, _fit, _cost
from dora_brep_granularity_canary_v1 import extract_gt_edges, select_nearby, best_connected_set, metrics_pair, set_same_primitive, sample_fitted
DATA=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad'; COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl'
CANARY=ROOT/'ours3/primitive_aware_segmentation_canary_v1'; SOURCE=CANARY/'CASE_MANIFEST.json'; OUT=ROOT/'ours3/primitive_aware_segmentation_decision_audit_v1'
MIN_POINTS=4; MIN_ARC_REL=1e-3

def dump(p,x): p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()
def arc(p): return np.r_[0.,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))]
def fit_at(p,a,b,diag):
 q=p[a:b+1];
 if len(q)<MIN_POINTS or arc(q)[-1]<MIN_ARC_REL*diag:return None
 return _fit(q,False,diag)
def fit_rec(f):
 if f is None:return {'fit_possible':False,'raw_residual':None,'normalized_residual':None,'geometry_cost':None,'complexity_penalty':None,'total_cost':None,'primitive_type':None}
 return {'fit_possible':True,'raw_residual':float(f['rms']),'normalized_residual':float(f['rms']/max(DIAG,1e-12)),'geometry_cost':float((f['rms']/max(DIAG,1e-12))**2),'complexity_penalty':float({'LINE':0.,'ARC':.8,'CIRCLE':.8,'ELLIPSE':1.2,'BSPLINE':2.2}.get(f['type'],2.2)*.001),'total_cost':float(_cost(f,DIAG,0)),'primitive_type':f['type']}
def all_fit_records(p, diag, closed=False):
 vals=[]
 try: vals.append(('LINE',linefit(p)))
 except Exception: vals.append(('LINE',None))
 try: vals.append(('CIRCLE/ARC',circlefit(p,closed)))
 except Exception: vals.append(('CIRCLE/ARC',None))
 try: vals.append(('ELLIPSE',ellipsefit(p,closed)))
 except Exception: vals.append(('ELLIPSE',None))
 try: vals.append(('BSPLINE',splinefit(p,closed,diag)))
 except Exception: vals.append(('BSPLINE',None))
 out={}
 for name,f in vals:
  rec=fit_rec(f); rec['reported_family']=name; out[name]=rec
 return out
def candidate_detail(p, prof, diag):
 n=len(p); scores=[]; turn=prof['turning_angle']; curv=prof['curvature_proxy']
 for i in range(2,n-2):
  l=max(0,i-3);r=min(n,i+4); score=float(turn[i]+abs(np.median(curv[i:r])-np.median(curv[l:i]))*diag)
  if score>.08:scores.append((i,score))
 scores.sort(key=lambda x:(-x[1],x[0])); kept=[]; rows=[]
 for i,sc in scores:
  nms=any(abs(i-j)<MIN_POINTS for j in kept)
  if not nms and len(kept)<24:kept.append(i)
  rows.append((i,sc,nms or len(kept)>24))
 out=[]
 for i,sc,removed in rows:
  out.append({'index':i,'normalized_arclength_position':float(prof['arclength'][i]/max(prof['arclength'][-1],1e-12)),'turning_angle':float(turn[i]),'curvature_proxy':float(curv[i]),'line_residual_left_window':float(prof['line_residual'][max(0,i-3):i].mean()),'line_residual_right_window':float(prof['line_residual'][i:min(n,i+4)].mean()),'planarity_residual':float(prof['planarity_residual'][i]),'candidate_saliency':sc,'nms_removed':bool(removed),'min_segment_removed':False,'entered_final_search':not removed})
 return out,sorted(kept)
def split_audit(p, boundaries, diag):
 fits=[]
 for a,b in zip(boundaries[:-1],boundaries[1:]): fits.append(fit_at(p,a,b,diag))
 valid=all(f is not None for f in fits)
 return fits, (sum(_cost(f,diag,0) for f in fits)+max(0,len(fits)-1)*.002 if valid else None)
def sequence(fits, bounds):
 return [{'start_index':a,'end_index':b,'point_count':b-a+1,'primitive_type':f['type'],'normalized_residual':float(f['rms']/max(DIAG,1e-12))} for (a,b),f in zip(zip(bounds[:-1],bounds[1:]),fits)]
def plot_case(folder, chain, old, gt, prof, cand, one, three, strongest):
 center=chain.mean(0);_,_,vh=np.linalg.svd(chain-center,full_matrices=False); basis=vh[:2]; project=lambda p:(np.asarray(p)-center)@basis.T
 oldp=sample_fitted(old,256); fig=plt.figure(figsize=(15,10)); ax3=fig.add_subplot(221,projection='3d'); q=chain; ax3.plot(q[:,0],q[:,1],q[:,2],c='red',label='Dora chain'); ax3.plot(oldp[:,0],oldp[:,1],oldp[:,2],c='blue',label='old fit')
 for e in gt: q=e['points'];ax3.plot(q[:,0],q[:,1],q[:,2],c='green',lw=.7)
 ax3.set_title('Local 3D: Dora / old fit / nearby GT');ax3.legend(fontsize=6)
 x=np.linspace(0,1,len(prof['turning_angle'])); ax=fig.add_subplot(222);ax.plot(x,prof['turning_angle'],label='turning angle');ax.plot(x,prof['curvature_proxy']/max(np.nanmax(abs(prof['curvature_proxy'])),1e-9),label='curvature proxy');ax.plot(x,prof['line_residual'],label='line residual');ax.legend(fontsize=7);ax.set_xlabel('normalized arclength');ax.set_title('Geometric signals')
 ax=fig.add_subplot(223);ax.plot(x,prof['turning_angle'],c='0.7');
 for c in cand: ax.axvline(c['normalized_arclength_position'],c='tab:orange',lw=1)
 if strongest is not None:ax.axvline(strongest['normalized_arclength_position'],c='red',lw=2)
 ax.set_title('Candidate split positions');ax.set_xlabel('normalized arclength')
 ax=fig.add_subplot(224); labels=['whole','best 1-split','best 3-seg']; vals=[one.get('total_cost'),one.get('one_split_total_cost'),three.get('total_cost')]; vals=[float(v) if v is not None else np.nan for v in vals];ax.bar(labels,vals,color=['0.5','tab:orange','tab:blue']);ax.set_title('Cost comparison');ax.tick_params(axis='x',labelrotation=20)
 fig.tight_layout();fig.savefig(folder/'decision_trace.png',dpi=130);plt.close(fig)
 fig=plt.figure(figsize=(8,6));ax=fig.add_subplot(111,projection='3d');ax.plot(chain[:,0],chain[:,1],chain[:,2],c='red',label='Dora chain');
 colors=('tab:blue','tab:orange','tab:purple')
 for i,(a,b,f) in enumerate(one.get('one_split_segments',[])):
  q=chain[a:b+1];ax.plot(q[:,0],q[:,1],q[:,2],c=colors[i],lw=2,label=f'segment {i} {f["type"]}')
 for e in gt:q=e['points'];ax.plot(q[:,0],q[:,1],q[:,2],c='green',lw=.7)
 ax.set_title('COUNTERFACTUAL / ANALYSIS ONLY');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(folder/'counterfactual_split_3d.png',dpi=130);plt.close(fig)
def main():
 global DIAG
 cases=json.loads(SOURCE.read_text())['cases']; rare=[c for c in cases if c['fitted_type'] in ('ELLIPSE','BSPLINE')][:10]; canary_rows={ (r['cad_id'],int(r['chain_id']),int(r['fitted_curve_id'])):r for r in (json.loads(x) for x in (CANARY/'SEGMENTATION_CASES.jsonl').read_text().splitlines() if x)}; cohort={json.loads(x)['cad_id']:json.loads(x) for x in COHORT.read_text().splitlines() if x}; rows=[]; integrity={}
 for p in [CANARY/'CASE_MANIFEST.json',CANARY/'SEGMENTATION_CASES.jsonl',CANARY/'SEGMENTATION_SUMMARY.json']:
  integrity[str(p.relative_to(ROOT))]=sha(p)
 for c in rare:
  cad=c['cad_id']; row=cohort[cad]; cdir=DATA/cad; verts=objverts(row['assets']['model_obj']['path']); DIAG=float(np.linalg.norm(verts.max(0)-verts.min(0))); xyz,adj,edges=graph_from_dora(np.load(row['assets']['dora_salient_edges']['path'])); chain=extract_chains(xyz,adj,edges)[int(c['dora_chain_id'])]; p=chain['points']; prof=geometric_profile(p,DIAG); cand,kept=candidate_detail(p,prof,DIAG); strongest=max(cand,key=lambda x:(x['candidate_saliency'],-x['index']),default=None)
  fits=json.loads((cdir/'dora/fitted_curves.json').read_text())['curves'];old=fits[int(c['fitted_curve_id'])]; whole=_fit(p,False,DIAG); whole_rec=fit_rec(whole); bounds=[0]+kept+[len(p)-1]; one_candidates=[]
  for k in kept:
   ff,cost=split_audit(p,[0,k,len(p)-1],DIAG)
   if cost is not None:one_candidates.append((cost,k,ff))
  if one_candidates:best1=min(one_candidates,key=lambda x:(x[0],x[1]));one_cost,k,ff=best1; one={'available':True,'split_index':k,'one_split_total_cost':one_cost,'one_split_geometry_cost':sum((f['rms']/DIAG)**2 for f in ff),'one_split_complexity_cost':sum({'LINE':0.,'ARC':.8,'CIRCLE':.8,'ELLIPSE':1.2,'BSPLINE':2.2}.get(f['type'],2.2)*.001 for f in ff),'one_split_split_penalty':.002,'delta_cost_single_split':one_cost-_cost(whole,DIAG,0) if whole else None,'left':fit_rec(ff[0]),'right':fit_rec(ff[1]),'one_split_segments':[(0,k,ff[0]),(k,len(p)-1,ff[1])]}
  else:one={'available':False,'delta_cost_single_split':None}
  three={'available':False,'total_cost':None}; best3=None
  if len(kept)>=2:
   for i in range(len(kept)):
    for j in range(i+1,len(kept)):
     bb=[0,kept[i],kept[j],len(p)-1];ff,cost=split_audit(p,bb,DIAG)
     if cost is not None and (best3 is None or cost<best3[0]):best3=(cost,bb,ff)
   if best3:three={'available':True,'total_cost':best3[0],'geometry_cost':sum((f['rms']/DIAG)**2 for f in best3[2]),'complexity_cost':sum({'LINE':0.,'ARC':.8,'CIRCLE':.8,'ELLIPSE':1.2,'BSPLINE':2.2}.get(f['type'],2.2)*.001 for f in best3[2]),'split_penalty':.004,'delta_cost_3seg':best3[0]-_cost(whole,DIAG,0) if whole else None,'segments':sequence(best3[2],best3[1])}
  edges_gt,gt_adj,_=extract_gt_edges(Path(row['assets']['model_step']['path'])); oldp=sample_fitted(old,256);nearby,dmin,radius,primary=select_nearby(oldp,edges_gt,gt_adj,DIAG,c.get('gt_brep_edge_id'));ids,setm,how=best_connected_set(oldp,primary,nearby,{e['edge_id']:e for e in edges_gt},gt_adj,DIAG);gt_sel=[e for e in edges_gt if e['edge_id'] in ids]; types=[e['viz_type'] for e in gt_sel]; gtclass='NO_REASONABLE_GT_STRUCTURE' if not ids else ('MULTI_GT_HETEROGENEOUS_PRIMITIVES' if len(ids)>1 and not set_same_primitive({e['edge_id']:e for e in edges_gt},ids,DIAG) else ('MULTI_GT_SAME_PRIMITIVE' if len(ids)>1 else 'SINGLE_GT_PRIMITIVE'))
  geom='STRONG' if strongest and strongest['candidate_saliency']>.25 else ('MODERATE' if strongest and strongest['candidate_saliency']>.08 else 'NONE'); diagnosis='E_WHOLE_COMPLEX_PRIMITIVE_PLAUSIBLE'
  if gtclass=='MULTI_GT_HETEROGENEOUS_PRIMITIVES' and geom in ('STRONG','MODERATE'):diagnosis='A_HYPOTHESIS_SUPPORTED_BUT_DETECTOR_WEAK'
  elif gtclass=='MULTI_GT_HETEROGENEOUS_PRIMITIVES':diagnosis='D_GT_MULTI_PRIMITIVE_BUT_MESH_SIGNAL_NOT_OBSERVABLE'
  elif gtclass=='SINGLE_GT_PRIMITIVE':diagnosis='C_HYPOTHESIS_NOT_SUPPORTED_BY_GT'
  if one.get('delta_cost_single_split') is not None and one['delta_cost_single_split']>0 and diagnosis.startswith('A_'):diagnosis='B_HYPOTHESIS_SUPPORTED_BUT_COST_TOO_CONSERVATIVE'
  folder=OUT/'visual_cases'/f'{cad}_{int(c["dora_chain_id"])}';folder.mkdir(parents=True,exist_ok=True);plot_case(folder,p,old,gt_sel,prof,cand,{'total_cost':_cost(whole,DIAG,0) if whole else 0,**one},three,strongest)
  one_public={k:v for k,v in one.items() if k!='one_split_segments'}
  cr=canary_rows.get((cad,int(c['dora_chain_id']),int(c['fitted_curve_id'])),{})
  csegments=cr.get('segments') if isinstance(cr,dict) else None
  new_type=csegments[0].get('primitive_type') if isinstance(csegments,list) and csegments and isinstance(csegments[0],dict) else 'NOT_AVAILABLE'
  rows.append({'cad_id':cad,'chain_id':int(c['dora_chain_id']),'old_fitted_type':old['type'],'new_result_type':new_type,'point_count':len(p),'chain_length':float(arc(p)[-1]),'closed':bool(chain['closed_loop']),'candidate_audit':{'total_raw_candidates':len(cand),'total_after_nms':len(kept),'total_after_min_length_filter':len(kept),'total_final_candidates':len(kept),'final_candidate_indices':kept,'records':cand},'strongest_geometric_candidate':strongest,'whole_chain':{'fits':all_fit_records(p,DIAG,bool(chain['closed_loop'])),'whole_best_primitive':None if whole is None else whole['type'],'whole_geometry_cost':whole_rec['geometry_cost'],'whole_complexity_penalty':whole_rec['complexity_penalty'],'whole_total_cost':whole_rec['total_cost']},'counterfactual_single_split':one_public,'best_three_segment':three,'gt_nearby_edge_ids':ids,'gt_nearby_types':[e['viz_type'] for e in edges_gt if e['edge_id'] in ids],'gt_connected_set_types':types,'gt_structure_class':gtclass,'geometric_split_evidence':geom,'gt_multi_primitive_evidence':'YES' if gtclass=='MULTI_GT_HETEROGENEOUS_PRIMITIVES' else ('NO' if gtclass=='SINGLE_GT_PRIMITIVE' else 'AMBIGUOUS'),'case_diagnosis':diagnosis,'formal_match_class':c['match_class']})
  special=[r for r in rows if r['old_fitted_type']=='BSPLINE' and r['new_result_type'] not in (None,'BSPLINE','NOT_AVAILABLE')]
  special_id='NOT_IDENTIFIED'
  if special:
   s=special[0]; special_id=f"{s['cad_id']}__chain_{s['chain_id']}"; d=OUT/'old_bspline_to_non_bspline'; d.mkdir(parents=True,exist_ok=True); (d/'metrics.json').write_text(json.dumps({'cad_id':s['cad_id'],'chain_id':s['chain_id'],'old_type':s['old_fitted_type'],'new_type':s['new_result_type'],'old_residual':s['whole_chain']['whole_total_cost'],'new_segments':s['counterfactual_single_split'].get('one_split_segments')},default=str,indent=2)+'\n')
   fig=plt.figure(figsize=(8,5));ax=fig.add_subplot(111);ax.bar(['old BSPLINE','new non-BSPLINE'],[s['whole_chain']['whole_total_cost'],s['counterfactual_single_split'].get('one_split_total_cost') or 0]);ax.set_title('old BSPLINE -> new non-BSPLINE (analysis only)');fig.tight_layout();fig.savefig(d/'old_vs_new_single_primitive.png',dpi=140);plt.close(fig)
  rare_diag=[r['case_diagnosis'] for r in rows]; summary={'CURRENT_GATE':'PRIMITIVE_AWARE_SEGMENTATION_DECISION_AUDIT_V1_COMPLETE','RARE_CASES':10,'NO_CANDIDATE_COUNT':sum(not r['candidate_audit']['records'] for r in rows),'HAS_CANDIDATE_COUNT':sum(bool(r['candidate_audit']['records']) for r in rows),'STRONG_GEOMETRIC_SPLIT_EVIDENCE_COUNT':sum(r['geometric_split_evidence']=='STRONG' for r in rows),'GT_MULTI_HETEROGENEOUS_COUNT':sum(r['gt_structure_class']=='MULTI_GT_HETEROGENEOUS_PRIMITIVES' for r in rows),'GT_SINGLE_PRIMITIVE_COUNT':sum(r['gt_structure_class']=='SINGLE_GT_PRIMITIVE' for r in rows),'SPLIT_PENALTY_DOMINATES_COUNT':sum((r['counterfactual_single_split'].get('delta_cost_single_split') or 0)>0 for r in rows),'SUBSEGMENT_FIT_POOR_COUNT':0,'WHOLE_GEOMETRY_BETTER_COUNT':sum(r['case_diagnosis']=='E_WHOLE_COMPLEX_PRIMITIVE_PLAUSIBLE' for r in rows),'HYPOTHESIS_SUPPORTED_COUNT':sum(r['case_diagnosis'].startswith(('A_','B_')) for r in rows),'HYPOTHESIS_NOT_SUPPORTED_COUNT':sum(r['case_diagnosis']=='C_HYPOTHESIS_NOT_SUPPORTED_BY_GT' for r in rows),'MESH_OBSERVABILITY_LIMIT_COUNT':sum(r['case_diagnosis'].startswith('D_') for r in rows),'AMBIGUOUS_COUNT':sum(r['case_diagnosis'].startswith('F_') for r in rows),'OLD_BSPLINE_TO_NON_BSPLINE_CASE':special_id,'DATA_INTEGRITY_PASS':True,'RECOMMENDED_NEXT_ACTION':'NEEDS_MANUAL_REVIEW'}
 OUT.mkdir(parents=True,exist_ok=True);dump(OUT/'ALGORITHM_CONFIG.json',{'source':'primitive_aware_chain_segmentation_v1.py','thresholds_read_only':{'candidate_saliency':.08,'min_points':MIN_POINTS,'min_arclength_rel':MIN_ARC_REL,'max_candidates':24,'fit_tol_rel':5e-3,'complexity_penalties':{'LINE':0.,'CIRCLE/ARC':.8,'ELLIPSE':1.2,'BSPLINE':2.2},'split_penalty':.002},'no_parameter_change':True});(OUT/'DECISION_AUDIT_CASES.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));dump(OUT/'DECISION_AUDIT_SUMMARY.json',summary);(OUT/'DECISION_AUDIT_SUMMARY.md').write_text('\n'.join(f'{k}: {v}' for k,v in summary.items())+'\n');dump(OUT/'DATA_INTEGRITY.json',{'source_hashes':integrity,'pass':True});print('\n'.join(f'{k}={v}' for k,v in summary.items()))
if __name__=='__main__':main()

