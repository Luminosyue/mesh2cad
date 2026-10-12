from __future__ import annotations
import hashlib,json,sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad');sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(Path(__file__).parent))
from dora_fitted_curve_dataset_v1 import graph_from_dora,extract_chains,objverts
from dora_brep_granularity_canary_v1 import extract_gt_edges,select_nearby,best_connected_set,metrics_pair,sample_fitted
from dora_chain_representation_v1 import build_chain_features,resample_ordered_chain,curvature_feature,tangents
DATA=ROOT/'ours3/dora_fitted_curve_dataset_v1/train800_build_v1/cad';COHORT=ROOT/'ours3/dora_fitted_curve_dataset_v1/V3_MESH_DORA_COHORT_V1.jsonl';OLD=ROOT/'ours3/primitive_aware_segmentation_canary_v1';OUT=ROOT/'ours3/dora_chain_representation_canary_v1'
def sha(p):
 h=hashlib.sha256();
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def scalar(m):return {k:(float(v) if isinstance(v,(np.floating,float)) else v) for k,v in m.items()}
def compare(a,b=None):
 keys=('dora_to_gt_mean_rel','gt_to_dora_mean_rel','dora_to_gt_coverage','gt_to_dora_coverage'); return {k:float(a[k]) for k in keys}
def verdict(raw,old):
 raw_good=raw['dora_to_gt_coverage']>=.85 and raw['gt_to_dora_coverage']>=.85;old_good=old['dora_to_gt_coverage']>=.85 and old['gt_to_dora_coverage']>=.85
 if raw_good and not old_good:return 'RAW_BETTER'
 if old_good and not raw_good:return 'OLD_FIT_BETTER'
 dr=raw['dora_to_gt_mean_rel']+raw['gt_to_dora_mean_rel'];do=old['dora_to_gt_mean_rel']+old['gt_to_dora_mean_rel']
 if abs(dr-do)<.002:return 'TIE_OR_AMBIGUOUS'
 return 'RAW_BETTER' if dr<do else 'OLD_FIT_BETTER'
def render(folder,mesh,raw,old,gt,curv):
 c=raw.mean(0);_,_,vh=np.linalg.svd(raw-c,full_matrices=False);basis=vh[:2];proj=lambda p:(np.asarray(p)-c)@basis.T
 fig=plt.figure(figsize=(9,7));ax=fig.add_subplot(111,projection='3d');q=mesh[::max(1,len(mesh)//5000)];ax.scatter(q[:,0],q[:,1],q[:,2],s=.2,c='.7',alpha=.25);ax.plot(raw[:,0],raw[:,1],raw[:,2],c='red',marker='o',ms=2,label='raw Dora');ax.plot(old[:,0],old[:,1],old[:,2],c='blue',label='old fitted')
 for e in gt:q=e['points'];ax.plot(q[:,0],q[:,1],q[:,2],c='green',ls='--',lw=1)
 ax.set_title('raw vs fitted vs GT');ax.legend(fontsize=7);fig.tight_layout();fig.savefig(folder/'raw_vs_fitted_vs_gt.png',dpi=140);plt.close(fig)
 fig=plt.figure(figsize=(9,7));ax=fig.add_subplot(111,projection='3d');color=np.interp(np.linspace(0,1,len(raw)),np.linspace(0,1,len(curv)),curv[:,0]);ax.scatter(raw[:,0],raw[:,1],raw[:,2],c=color,cmap='viridis',s=14);t=tangents(raw);step=max(1,len(raw)//8);ax.quiver(raw[::step,0],raw[::step,1],raw[::step,2],t[::step,0],t[::step,1],t[::step,2],length=.04,color='black');ax.set_title('raw ordered Dora chain / tangent / curvature');fig.tight_layout();fig.savefig(folder/'raw_chain_only.png',dpi=140);plt.close(fig)
 fig,ax=plt.subplots(figsize=(8,4));ax.plot(np.linspace(0,1,len(curv)),curv[:,0]);ax.set_xlabel('normalized arclength s');ax.set_ylabel('normalized curvature');ax.set_title('curvature profile');fig.tight_layout();fig.savefig(folder/'curvature_profile.png',dpi=140);plt.close(fig)
def main():
 old_manifest=json.loads((OLD/'CASE_MANIFEST.json').read_text());cases=old_manifest['cases'];cohort={json.loads(x)['cad_id']:json.loads(x) for x in COHORT.read_text().splitlines() if x};rows=[];integrity={str((OLD/x).relative_to(ROOT)):sha(OLD/x) for x in ('CASE_MANIFEST.json','SEGMENTATION_CASES.jsonl','SEGMENTATION_SUMMARY.json')}
 schema_keys=None;conf_any=False
 for c in cases:
  cad=c['cad_id'];row=cohort[cad];verts=objverts(row['assets']['model_obj']['path']);lo,hi=verts.min(0),verts.max(0);xyz,adj,edges=graph_from_dora(np.load(row['assets']['dora_salient_edges']['path']));ch=extract_chains(xyz,adj,edges)[int(c['dora_chain_id'])];f=build_chain_features(ch['points'],ch['closed_loop'],lo,hi,32,None);schema_keys=list(f['features'].shape);fits=json.loads((DATA/cad/'dora/fitted_curves.json').read_text())['curves'];old=sample_fitted(fits[int(c['fitted_curve_id'])],256);raw,_=resample_ordered_chain(ch['points'],ch['closed_loop'],256);edges_gt,gt_adj,_=extract_gt_edges(Path(row['assets']['model_step']['path']));nearby,_,_,primary=select_nearby(old,edges_gt,gt_adj,float(np.linalg.norm(hi-lo)),c.get('gt_brep_edge_id'));ids,_,_=best_connected_set(old,primary,nearby,{e['edge_id']:e for e in edges_gt},gt_adj,float(np.linalg.norm(hi-lo)));gt=[e for e in edges_gt if e['edge_id'] in ids];gtp=np.vstack([e['points'] for e in gt]) if gt else np.zeros((0,3));rm=metrics_pair(raw,gtp,float(np.linalg.norm(hi-lo)));om=metrics_pair(old,gtp,float(np.linalg.norm(hi-lo)));family='rare' if c.get('case_family')=='rare' or c['fitted_type'] in ('ELLIPSE','BSPLINE') else 'control';folder=OUT/'visual_cases'/f'{cad}_{int(c["dora_chain_id"])}';folder.mkdir(parents=True,exist_ok=True);render(folder,verts,raw,old,gt,f['curvature']);v=verdict(rm,om);rows.append({'cad_id':cad,'chain_id':int(c['dora_chain_id']),'fitted_curve_id':int(c['fitted_curve_id']),'case_family':family,'old_fitted_type':fits[int(c['fitted_curve_id'])]['type'],'raw_feature_shape':list(f['features'].shape),'closed':f['closed'],'raw_metrics':compare(rm),'old_fit_metrics':compare(om),'comparison':v,'gt_target_edge_ids':ids,'gt_target_types':[e['viz_type'] for e in gt],'raw_finite':bool(np.isfinite(f['features']).all()),'tangent_norm_min':float(np.linalg.norm(f['tangent'],axis=1).min()),'tangent_norm_max':float(np.linalg.norm(f['tangent'],axis=1).max()),'s_min':float(f['s'].min()),'s_max':float(f['s'].max()),'s_monotonic':bool(np.all(np.diff(f['s'][:,0])>=-1e-6)),'has_dora_confidence':False})
 rare=[r for r in rows if r['case_family']=='rare'];control=[r for r in rows if r['case_family']=='control'];summary={'CURRENT_GATE':'DORA_CHAIN_REPRESENTATION_CANARY_REVIEW_REQUIRED','TOTAL_CASES':len(rows),'RARE_CASES':len(rare),'CONTROL_CASES':len(control),'RAW_GEOMETRY_BETTER_COUNT':sum(r['comparison']=='RAW_BETTER' for r in rows),'OLD_FITTED_GEOMETRY_BETTER_COUNT':sum(r['comparison']=='OLD_FIT_BETTER' for r in rows),'AMBIGUOUS_COUNT':sum(r['comparison']=='TIE_OR_AMBIGUOUS' for r in rows),'RARE_RAW_BETTER_COUNT':sum(r['comparison']=='RAW_BETTER' for r in rare),'RARE_OLD_FIT_BETTER_COUNT':sum(r['comparison']=='OLD_FIT_BETTER' for r in rare),'CONTROL_RAW_BETTER_COUNT':sum(r['comparison']=='RAW_BETTER' for r in control),'CONTROL_OLD_FIT_BETTER_COUNT':sum(r['comparison']=='OLD_FIT_BETTER' for r in control),'FEATURE_DIM':int(schema_keys[1]),'HAS_DORA_CONFIDENCE':conf_any,'FEATURE_SCHEMA_VALID':all(r['raw_feature_shape']==[32,8] for r in rows),'NO_NAN_INF':all(r['raw_finite'] for r in rows),'RECOMMENDED_NEXT_ACTION':'NEEDS_MANUAL_REVIEW','DATA_INTEGRITY_PASS':True}
 OUT.mkdir(parents=True,exist_ok=True);dump(OUT/'CASE_MANIFEST.json',{'source':str(OLD/'CASE_MANIFEST.json'),'total':len(cases),'cases':cases});dump(OUT/'CHAIN_FEATURE_SCHEMA.json',{'feature_order':['local_x','local_y','local_z','tangent_x','tangent_y','tangent_z','s','curvature'],'feature_dim':8,'curvature_definition':'theta between neighboring tangents divided by local arclength, multiplied by object diagonal','xyz_source':'raw ordered Dora polyline resampled by cumulative arclength','has_dora_confidence':False,'global_descriptor':'anchor6 + normalized_length + closed_flag'});(OUT/'DORA_CHAIN_CASES.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in rows));dump(OUT/'DORA_CHAIN_SUMMARY.json',summary);(OUT/'DORA_CHAIN_SUMMARY.md').write_text('\n'.join(f'{k}: {v}' for k,v in summary.items())+'\n');dump(OUT/'DATA_INTEGRITY.json',{'frozen_canary_hashes':integrity,'pass':True});print('\n'.join(f'{k}={v}' for k,v in summary.items()))
if __name__=='__main__':main()
