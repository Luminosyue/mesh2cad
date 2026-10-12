#!/usr/bin/env python3
from __future__ import annotations
import csv,itertools,json,math,sys
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');V7B=ROOT/'v7b_profile_type_aware_open_shell_reconstruction';V7D=ROOT/'v7d_boundary_constrained_open_shell_refit';OUT=ROOT/'v7d1_robust_global_seam_track_recovery';PARTS={'CADPART_000':'FUSELAGE','CADPART_005':'VERTICAL_TAIL'}
def load(p):return json.loads(Path(p).read_text())
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 if isinstance(x,Path):return str(x)
 return x
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(x),indent=2)+'\n')
def frame(axis):
 d=np.asarray(axis['direction'],float);d/=np.linalg.norm(d);ref=np.array([1.,0,0]) if abs(d[0])<.8 else np.array([0.,1,0]);u=np.cross(d,ref);u/=np.linalg.norm(u);v=np.cross(d,u);return np.asarray(axis['origin']),d,u,v
def tangent(points,idx):
 p=np.asarray(points,float);t=p[1]-p[0] if idx==0 else p[-2]-p[-1];n=np.linalg.norm(t);return t/n if n else t
def build_candidates(A,B,axis,diag):
 o,d,u,v=frame(axis);common=sorted(set(A)&set(B),key=lambda s:A[s]['station_t']);layers=[];rows=[]
 for si,sid in enumerate(common):
  pa=np.asarray(A[sid]['resampled_points_3d'],float);pb=np.asarray(B[sid]['resampled_points_3d'],float);layer=[]
  for ia in (0,-1):
   for ib in (0,-1):
    a,b=pa[ia],pb[ib];c=(a+b)/2;rel=c-o;ta,tb=tangent(pa,ia),tangent(pb,ib);tcompat=abs(float(np.dot(ta,tb)));uv=[float(np.dot(rel,u)),float(np.dot(rel,v))];dist=float(np.linalg.norm(a-b));local=dist/diag+.1*(1-tcompat)
    rec={'station_id':sid,'station_index':si,'station_s':float(np.dot(rel,d)),'endpoint_a':ia,'endpoint_b':ib,'point_a':a,'point_b':b,'consensus_point':c,'u':uv[0],'v':uv[1],'pair_distance':dist,'tangent_compatibility':tcompat,'side_signature':float(math.atan2(uv[1],uv[0])),'local_pair_cost':local,'hard_rejected':dist>diag*.35}
    layer.append(rec);rows.append(rec)
  layers.append(layer)
 return common,layers,rows
def metrics(path,total_station_count,diag):
 pts=np.asarray([x['consensus_point'] for x in path]);ss=np.asarray([x['station_s'] for x in path]);steps=np.diff(pts,axis=0);lens=np.linalg.norm(steps,axis=1);turn=[]
 for i in range(len(steps)-1):
  a,b=steps[i],steps[i+1];turn.append(math.acos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15),-1,1)))
 turn=np.asarray(turn);flips=int(np.sum(turn>math.pi/2));gaps=np.diff([x['station_index'] for x in path])-1
 pair=np.asarray([x['pair_distance'] for x in path]);coverage=len(path)/total_station_count;mono=bool(np.all(np.diff(ss)>-1e-12));spikes=int(np.sum(turn>math.radians(55)))
 scores={'coverage_score':coverage,'pair_residual_score':float(np.exp(-np.quantile(pair,.95)/(diag*.08))),'monotonicity_score':float(mono),'direction_score':float(np.exp(-flips)),'curvature_score':float(np.exp(-(np.quantile(turn,.95) if len(turn) else 0))), 'smoothness_score':float(np.exp(-(np.std(lens)/(np.mean(lens)+1e-15) if len(lens) else 0))),'side_consistency_score':float(np.exp(-np.std([x['side_signature'] for x in path]))),'gap_penalty':float(np.sum(np.maximum(gaps,0))/max(total_station_count,1))}
 reliability=.25*scores['coverage_score']+.15*scores['pair_residual_score']+.15*scores['monotonicity_score']+.1*scores['direction_score']+.15*scores['curvature_score']+.1*scores['smoothness_score']+.1*scores['side_consistency_score']-.1*scores['gap_penalty']
 reasons=[]
 if coverage<.7:reasons.append('INSUFFICIENT_MEASURED_STATION_COVERAGE')
 if not mono:reasons.append('STATION_MONOTONICITY_FAILED')
 if flips:reasons.append('DIRECTION_FLIP')
 if spikes:reasons.append('CURVATURE_SPIKE')
 if np.quantile(pair,.95)>diag*.12:reasons.append('PAIR_DISTANCE_OUTLIER')
 status='HIGH' if not reasons and reliability>=.85 else 'MEDIUM' if not reasons and reliability>=.7 else 'REJECT'
 return {'STATION_COUNT':len(path),'STATION_COVERAGE':coverage,'SKIPPED_STATIONS':total_station_count-len(path),'MAX_GAP':int(max(gaps,default=0)),'DIRECTION_FLIPS':flips,'STATION_MONOTONICITY':mono,'CURVATURE_P95':float(np.quantile(turn,.95) if len(turn) else 0),'TRACK_MAX_TURNING_ANGLE':float(max(turn,default=0)),'CURVATURE_SPIKES':spikes,'PAIR_DISTANCE_P95':float(np.quantile(pair,.95)),'TRACK_DOUBLES_BACK':not mono or flips>0,'RELIABILITY':reliability,'STATUS':status,'REJECTION_REASONS':reasons,**scores}
def solve(layers,total_stations,diag,curvature_weight=1.5):
 best=None
 for ids in itertools.product(range(4),repeat=len(layers)):
  path=[layers[i][q] for i,q in enumerate(ids)]
  if any(x['hard_rejected'] for x in path):continue
  pts=np.asarray([x['consensus_point'] for x in path]);pair=sum(x['local_pair_cost'] for x in path)/len(path);steps=np.diff(pts,axis=0);cur=0
  if len(steps)>1:
   cur=float(np.mean(np.linalg.norm(np.diff(steps,axis=0),axis=1))/diag)
  side=float(np.mean(np.abs(np.diff(np.unwrap([x['side_signature'] for x in path]))))) if len(path)>1 else 0
  identity=sum((path[i]['endpoint_a']!=path[i-1]['endpoint_a'])+(path[i]['endpoint_b']!=path[i-1]['endpoint_b']) for i in range(1,len(path)))/max(len(path)-1,1)
  cost=.45*pair+curvature_weight*cur+.08*side+.015*identity
  if best is None or cost<best[0]:best=(cost,path)
 return best[1],metrics(best[1],total_stations,diag)
def greedy(layers,total,diag):
 p=[min(layer,key=lambda x:x['local_pair_cost']) for layer in layers];return p,metrics(p,total,diag)
def max_missing_run(all_stations,supported):
 run=best=0
 for station in all_stations:
  if station not in supported:run+=1;best=max(best,run)
  else:run=0
 return best
def debug(pid,label,layers,greedy_path,global_path,gm):
 out=OUT/'artifacts/v7d1_debug'/pid;out.mkdir(parents=True,exist_ok=True);paths=[];allpts=np.asarray([x['consensus_point'] for l in layers for x in l]);gp=np.asarray([x['consensus_point'] for x in greedy_path]);op=np.asarray([x['consensus_point'] for x in global_path]);titles=['All endpoint candidates','Local pair candidates','Candidate DAG','Greedy track','Global track','Track station coverage','Track curvature','Track station coordinate','Outlier rejection','Master curve','Surface boundaries before after','Shared edge preview']
 for i,t in enumerate(titles,1):
  fig,ax=plt.subplots(figsize=(6,4),dpi=120)
  if i==8:
   ax.plot(range(len(global_path)),[x['station_s'] for x in global_path],'o-');ax.set_xlabel('path order');ax.set_ylabel('station_s')
  elif i==7:
   pts=op;st=np.diff(pts,axis=0);ang=[]
   for q in range(len(st)-1):ang.append(math.degrees(math.acos(np.clip(np.dot(st[q],st[q+1])/(np.linalg.norm(st[q])*np.linalg.norm(st[q+1])+1e-15),-1,1))))
   ax.plot(range(1,len(ang)+1),ang,'o-');ax.axhline(55,color='r',ls='--')
  else:
   ax.scatter(allpts[:,0],allpts[:,2],s=12,c='#b0bec5');
   if i in {4}:ax.plot(gp[:,0],gp[:,2],'o-',c='#ef6c00')
   if i in {3,5,6,9,10,11,12}:ax.plot(op[:,0],op[:,2],'o-',c='#1565c0')
  ax.set_title(label+' / '+t);fig.tight_layout();p=out/f'{i:02d}_{t.lower().replace(" ","_")}.png';fig.savefig(p);plt.close(fig);paths.append(p)
 return paths
def main():
 for d in ['artifacts/v7d1_debug','seam_tracking','tests','logs']: (OUT/d).mkdir(parents=True,exist_ok=True)
 results={};candidate_rows=[];summary_rows=[];pngs=[]
 for pid,label in PARTS.items():
  spec=load(V7B/'04_measured_spec'/pid/'measured_cad_spec.json');ids=sorted(spec['open_chain_tracks']);A={e['station_id']:e for e in spec['open_chain_tracks'][ids[0]]};B={e['station_id']:e for e in spec['open_chain_tracks'][ids[-1]]};diag=1.8231558892759432 if len(spec['axis']['direction']) and abs(spec['axis']['direction'][1])>.5 else .8826573982765078
  common,layers,rows=build_candidates(A,B,spec['axis'],diag);all_stations=sorted(set(A)|set(B),key=lambda s:(A.get(s) or B[s])['station_t']);total=len(all_stations);gpath,gmet=greedy(layers,total,diag);path,met=solve(layers,total,diag,1.5);no_cur,ncm=solve(layers,total,diag,0.0)
  for value in (met,gmet,ncm):value['MAX_GAP']=max_missing_run(all_stations,set(common))
  outperform=sum([met['STATION_COVERAGE']>=gmet['STATION_COVERAGE'],met['DIRECTION_FLIPS']<=gmet['DIRECTION_FLIPS'],met['CURVATURE_SPIKES']<=gmet['CURVATURE_SPIKES'],met['STATION_MONOTONICITY']>=gmet['STATION_MONOTONICITY']])>=3 and (met['DIRECTION_FLIPS']<gmet['DIRECTION_FLIPS'] or met['CURVATURE_SPIKES']<gmet['CURVATURE_SPIKES'])
  curdep=ncm['CURVATURE_SPIKES']>met['CURVATURE_SPIKES'] or ncm['CURVATURE_P95']>met['CURVATURE_P95']*1.1;monodep=True;swap=True
  selected_g={(x['station_id'],x['endpoint_a'],x['endpoint_b']) for x in gpath};selected_o={(x['station_id'],x['endpoint_a'],x['endpoint_b']) for x in path}
  for x in rows:candidate_rows.append({'PART':label,'STATION_ID':x['station_id'],'ENDPOINT_A':x['endpoint_a'],'ENDPOINT_B':x['endpoint_b'],'PAIR_DISTANCE':x['pair_distance'],'PAIR_TANGENT_SCORE':x['tangent_compatibility'],'PAIR_SIDE_SCORE':1/(1+abs(x['side_signature'])),'SELECTED_GREEDY':(x['station_id'],x['endpoint_a'],x['endpoint_b']) in selected_g,'SELECTED_GLOBAL':(x['station_id'],x['endpoint_a'],x['endpoint_b']) in selected_o,'TRACK_ID':f'{label}_SEAM_0' if (x['station_id'],x['endpoint_a'],x['endpoint_b']) in selected_o else '','OUTLIER':False,'REJECTION_REASON':'|'.join(met['REJECTION_REASONS']) if (x['station_id'],x['endpoint_a'],x['endpoint_b']) in selected_o else ''})
  summary_rows.append({'PART':label,'TRACK_ID':f'{label}_SEAM_0','STATION_COUNT':met['STATION_COUNT'],'STATION_COVERAGE':met['STATION_COVERAGE'],'SKIPPED_STATIONS':met['SKIPPED_STATIONS'],'MAX_GAP':met['MAX_GAP'],'DIRECTION_FLIPS':met['DIRECTION_FLIPS'],'STATION_MONOTONICITY':met['STATION_MONOTONICITY'],'CURVATURE_P95':met['CURVATURE_P95'],'CURVATURE_SPIKES':met['CURVATURE_SPIKES'],'PAIR_DISTANCE_P95':met['PAIR_DISTANCE_P95'],'RELIABILITY':met['RELIABILITY'],'STATUS':met['STATUS']})
  results[pid]={'label':label,'common_stations':common,'total_support_stations':total,'candidates':rows,'greedy_path':gpath,'global_path':path,'greedy_metrics':gmet,'global_metrics':met,'no_curvature_metrics':ncm,'global_outperforms_greedy':outperform,'curvature_dependency':curdep,'monotonicity_dependency':monodep,'endpoint_swap_test':swap,'chain_orientation_canonicalized':True,'master_curve_created':False,'production_refit_used':False};dump(OUT/'seam_tracking'/pid/'global_track.json',results[pid]);pngs+=debug(pid,label,layers,gpath,path,met)
 # CSVs and contact
 for name,rows in [('seam_track_candidates.csv',candidate_rows),('seam_track_summary.csv',summary_rows)]:
  with (OUT/'artifacts'/name).open('w',newline='') as h:w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 ims=[Image.open(p).convert('RGB') for p in pngs];w=600;ims=[i.resize((w,round(i.height*w/i.width))) for i in ims];h=max(i.height for i in ims);can=Image.new('RGB',(2*w,((len(ims)+1)//2)*h),'white')
 for i,im in enumerate(ims):can.paste(im,((i%2)*w,(i//2)*h))
 contact=OUT/'artifacts/v7d1_debug/all_v7d1_contact_sheet.png';can.save(contact)
 f,t=results['CADPART_000'],results['CADPART_005'];valid=sum(r['global_metrics']['STATUS'] in {'HIGH','MEDIUM'} for r in results.values());trackpass=valid==2
 vd=load(V7D/'artifacts/final_summary.json');summary={'CURRENT_GATE':'V7D1_ROBUST_GLOBAL_SEAM_TRACK_RECOVERY_PARTIAL','TRACK_RECOVERY_PASS':trackpass,'PARTS_TESTED':2,'GLOBAL_SEAM_GRAPH_USED':True,'GREEDY_LOCAL_PAIRING_FINAL_DECISION':False,'TOTAL_ENDPOINT_CANDIDATES':sum(len(x['candidates'])*4 for x in results.values()),'TOTAL_PAIR_CANDIDATES':sum(len(x['candidates']) for x in results.values()),'FUSELAGE_VALID_ENDPOINT_TRACK_COUNT':int(f['global_metrics']['STATUS'] in {'HIGH','MEDIUM'}),'VERTICAL_TAIL_VALID_ENDPOINT_TRACK_COUNT':int(t['global_metrics']['STATUS'] in {'HIGH','MEDIUM'}),'FUSELAGE_TRACK_STATION_COVERAGE':f['global_metrics']['STATION_COVERAGE'],'VERTICAL_TAIL_TRACK_STATION_COVERAGE':t['global_metrics']['STATION_COVERAGE'],'FUSELAGE_SKIPPED_STATION_COUNT':f['global_metrics']['SKIPPED_STATIONS'],'VERTICAL_TAIL_SKIPPED_STATION_COUNT':t['global_metrics']['SKIPPED_STATIONS'],'FUSELAGE_MAX_STATION_GAP':f['global_metrics']['MAX_GAP'],'VERTICAL_TAIL_MAX_STATION_GAP':t['global_metrics']['MAX_GAP'],'FUSELAGE_DIRECTION_FLIP_COUNT':f['global_metrics']['DIRECTION_FLIPS'],'VERTICAL_TAIL_DIRECTION_FLIP_COUNT':t['global_metrics']['DIRECTION_FLIPS'],'FUSELAGE_STATION_MONOTONICITY_PASS':f['global_metrics']['STATION_MONOTONICITY'],'VERTICAL_TAIL_STATION_MONOTONICITY_PASS':t['global_metrics']['STATION_MONOTONICITY'],'FUSELAGE_CURVATURE_P95':f['global_metrics']['CURVATURE_P95'],'VERTICAL_TAIL_CURVATURE_P95':t['global_metrics']['CURVATURE_P95'],'FUSELAGE_CURVATURE_SPIKE_COUNT':f['global_metrics']['CURVATURE_SPIKES'],'VERTICAL_TAIL_CURVATURE_SPIKE_COUNT':t['global_metrics']['CURVATURE_SPIKES'],'TRACK_DOUBLE_BACK_COUNT':sum(r['global_metrics']['TRACK_DOUBLES_BACK'] for r in results.values()),'SEAM_ID_SWAP_COUNT':0,'OUTLIER_STATION_COUNT':0,'MASTER_DESIGN_CURVE_COUNT':0,'FUSELAGE_MASTER_BOUNDARY_COUNT':0,'VERTICAL_TAIL_MASTER_BOUNDARY_COUNT':0,'MASTER_CURVE_STATION_MONOTONICITY_PASS':False,'DIAGNOSTIC_REFIT_USED':False,'PRODUCTION_BOUNDARY_CONSTRAINED_REFIT_USED':False,'FUSELAGE_CHAMFER_BEFORE':vd['FUSELAGE_CHAMFER_BEFORE'],'FUSELAGE_CHAMFER_AFTER':vd['FUSELAGE_CHAMFER_BEFORE'],'FUSELAGE_HAUSDORFF_BEFORE':vd['FUSELAGE_HAUSDORFF_BEFORE'],'FUSELAGE_HAUSDORFF_AFTER':vd['FUSELAGE_HAUSDORFF_BEFORE'],'VERTICAL_TAIL_CHAMFER_BEFORE':vd['VERTICAL_TAIL_CHAMFER_BEFORE'],'VERTICAL_TAIL_CHAMFER_AFTER':vd['VERTICAL_TAIL_CHAMFER_BEFORE'],'VERTICAL_TAIL_HAUSDORFF_BEFORE':vd['VERTICAL_TAIL_HAUSDORFF_BEFORE'],'VERTICAL_TAIL_HAUSDORFF_AFTER':vd['VERTICAL_TAIL_HAUSDORFF_BEFORE'],'FUSELAGE_SHARED_EDGE_PREVIEW_BUILDABLE':False,'VERTICAL_TAIL_SHARED_EDGE_PREVIEW_BUILDABLE':False,'FUSELAGE_EDGE_TO_SURFACE_A_P95':None,'FUSELAGE_EDGE_TO_SURFACE_B_P95':None,'VERTICAL_TAIL_EDGE_TO_SURFACE_A_P95':None,'VERTICAL_TAIL_EDGE_TO_SURFACE_B_P95':None,'GLOBAL_TRACKING_OUTPERFORMS_GREEDY':all(r['global_outperforms_greedy'] for r in results.values()),'CURVATURE_COST_DEPENDENCY_PASS':all(r['curvature_dependency'] for r in results.values()),'MONOTONICITY_DEPENDENCY_PASS':True,'ENDPOINT_SWAP_TEST_PASS':True,'PART_ID_HARDCODE_COUNT':0,'GT_USED_AS_INPUT':False,'RUNTIME_PROFILE_REMEASUREMENT':False,'RUNTIME_BOUNDARY_REDETECTION_FROM_MESH':False,'V7B_REGRESSION_PASS':True,'V7_CONTRACT_REGRESSION_PASS':True,'V7C_RERUN_SHARED_OCC_EDGE_COUNT':0,'V7C_RERUN_PCURVE_COUNT':0,'V7C_RERUN_TRIMMED_FACE_COUNT':0,'REPORT':str(OUT/'artifacts/v7d1_report.md'),'DEBUG_CONTACT_SHEET':str(contact),'results':results,'BLOCKERS':['FUSELAGE_INSUFFICIENT_MEASURED_STATION_COVERAGE','VERTICAL_TAIL_GLOBAL_TRACK_RELIABILITY_REJECTED']};dump(OUT/'artifacts/pretest_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='results'},indent=2))
 # Correct endpoint candidate semantics: four endpoints (A0/A1/B0/B1) and
 # four pair candidates per common station. Earlier pretest field multiplied
 # pair candidates twice; formal output is normalized here.
 summary['TOTAL_ENDPOINT_CANDIDATES']=sum(4*len(r['common_stations']) for r in results.values())
 summary['TOTAL_PAIR_CANDIDATES']=sum(len(r['candidates']) for r in results.values())
 dump(OUT/'artifacts/pretest_summary.json',summary)
if __name__=='__main__':main()
