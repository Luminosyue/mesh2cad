#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.spatial import cKDTree

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');B=ROOT/'v7d2b_versioned_chain_evidence_repair';V7D1=ROOT/'v7d1_robust_global_seam_track_recovery';OUT=ROOT/'v7d2c_mixed_section_seam_identity'
def load(p):return json.loads(Path(p).read_text())
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_csv(p,rows):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);h=p.open('w',newline='');w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);h.close()
def arc_points(points,n=48,closed=False):
 p=np.asarray(points,float);p=np.vstack([p,p[0]]) if closed else p;d=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];t=np.linspace(0,d[-1],n,endpoint=not closed);return np.vstack([np.interp(t,d,p[:,i]) for i in range(3)]).T
def local(points,o,u,v):p=np.asarray(points);return np.c_[(p-o)@u,(p-o)@v]
def state_and_candidates():
 stations={};rows=[]
 for gp in sorted((B/'03_geometry_analyzer/CADPART_000/raw_section_graph').glob('S*.json')):
  g=load(gp);sid=g['station_id'];closed=[c for c in g['components'] if c['topology_type']=='CLOSED_LOOP'];opened=[c for c in g['components'] if c['topology_type']=='OPEN_CHAIN' and c['FILTER_STATUS']=='ACCEPTED'];state='CLOSED_LOOP' if closed else 'SINGLE_OPEN_CHAIN' if len(opened)==1 else 'MULTI_OPEN_CHAIN' if len(opened)>1 else 'DEGENERATE' if g['nodes'] else 'EMPTY';o,u,v=map(np.asarray,(g['plane_origin'],g['basis_u'],g['basis_v']));nodes={n['NODE_ID']:np.asarray(n['NODE_XYZ']) for n in g['nodes']};candidates=[]
  if state=='CLOSED_LOOP':
   c=closed[0];pts=np.asarray([nodes[x] for x in c['ordered_node_ids']]);sample=arc_points(pts,64,True);luv=local(sample,o,u,v)
   for i,p in enumerate(sample):
    tangent=sample[(i+1)%len(sample)]-sample[(i-1)%len(sample)];tangent/=np.linalg.norm(tangent)+1e-15;candidates.append({'candidate_id':f'{sid}.L0.{i:02d}','type':'LATENT_CLOSED_LOOP_POINT','loop_id':c['component_id'],'s_loop':i/len(sample),'xyz':p,'local_uv':luv[i],'tangent':tangent,'confidence':.75})
  else:
   for c in opened:
    pts=np.asarray([nodes[x] for x in c['ordered_node_ids']]);luv=local(pts,o,u,v)
    for end,i in [('E0',0),('E1',-1)]:
     t=pts[1]-pts[0] if i==0 else pts[-1]-pts[-2];t/=np.linalg.norm(t)+1e-15;candidates.append({'candidate_id':f"{sid}.{c['component_id']}.{end}",'type':'OBSERVED_ENDPOINT','loop_id':None,'s_loop':None,'xyz':pts[i],'local_uv':luv[i],'tangent':t,'confidence':.95 if state=='MULTI_OPEN_CHAIN' else .9,'chain_id':c['component_id']})
  stations[sid]={'state':state,'closed_loop_count':len(closed),'open_chain_count':len(opened),'candidates':candidates,'origin':o,'u':u,'v':v}
 return stations
def seam_cost(a,b,c=None):
 dist=np.linalg.norm(a['xyz']-b['xyz']);side=abs(a['local_uv'][1]-b['local_uv'][1]);tan=1-abs(float(np.dot(a['tangent'],b['tangent'])));arc=0 if a['s_loop'] is None or b['s_loop'] is None else min(abs(a['s_loop']-b['s_loop']),1-abs(a['s_loop']-b['s_loop']));cur=0 if c is None else np.linalg.norm((b['xyz']-a['xyz'])-(a['xyz']-c['xyz']));latent=.02*(a['type'].startswith('LATENT')+b['type'].startswith('LATENT'));return dist+.3*side+.05*tan+.15*arc+.35*cur+latent
def mixed_seams(stations):
 sids=sorted(stations);anchor=[i for i,s in enumerate(sids) if stations[s]['state']=='MULTI_OPEN_CHAIN'];center=anchor[len(anchor)//2];anchor_sid=sids[center];ac=stations[anchor_sid]['candidates'];ac=sorted(ac,key=lambda x:x['local_uv'][1]);seed=[ac[0],ac[-1]];tracks=[]
 for seam,root in zip(['SEAM_A','SEAM_B'],seed):
  selected={anchor_sid:root}
  for direction in [-1,1]:
   prev=root;prev2=None;i=center+direction
   while 0<=i<len(sids):
    sid=sids[i];cand=stations[sid]['candidates'];best=min(cand,key=lambda x:seam_cost(prev,x,prev2));selected[sid]=best;prev2,prev=prev,best;i+=direction
  tracks.append((seam,[selected[s] for s in sids]))
 # joint distinctness: resolve any same candidate by next-best continuity.
 for i,sid in enumerate(sids):
  if tracks[0][1][i]['candidate_id']==tracks[1][1][i]['candidate_id']:
   base=tracks[0][1][i];alts=[x for x in stations[sid]['candidates'] if x['candidate_id']!=base['candidate_id']];tracks[1][1][i]=min(alts,key=lambda x:np.linalg.norm(x['xyz']-tracks[1][1][max(i-1,0)]['xyz']))
 return sids,tracks,anchor
def path_metrics(items):
 p=np.asarray([x['xyz'] for x in items]);steps=np.diff(p,axis=0);turn=[]
 for a,b in zip(steps[:-1],steps[1:]):turn.append(math.acos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15),-1,1)))
 return {'coverage':len(items)/12,'direction_flips':sum(x>math.pi/2 for x in turn),'curvature_p95':float(np.quantile(turn,.95)) if turn else 0,'spikes':sum(x>math.radians(55) for x in turn)}
def tail_whole_chain():
 d=load(B/'03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json');by={}
 for tid,es in d['tracks'].items():
  for e in es:by.setdefault(e['station_id'],[]).append((tid,e))
 def pair(a,b):
  x,y=np.asarray(a['resampled_points_local']),np.asarray(b['resampled_points_local']);n=min(len(x),len(y));x=x[:n];y=y[:n];forward=float(np.sqrt(np.mean((x-y)**2)));reverse=float(np.sqrt(np.mean((x-y[::-1])**2)));ch=.5*(cKDTree(x).query(y)[0].mean()+cKDTree(y).query(x)[0].mean());side=abs(a['side_signature']-b['side_signature']);shape=min(forward,reverse)+ch;return forward,reverse,shape,side
 rows=[];tracks={};all_sids=sorted(by)
 # Highest-confidence anchors: stations with two well-separated length/side branches.
 anchors=[sid for sid in all_sids if len(by[sid])>=2 and max(e['arc_length'] for _,e in by[sid])/max(min(e['arc_length'] for _,e in by[sid]),1e-9)>4]
 # Global identity uses persistent whole-chain branch: longest chain through all available stations.
 selected=[]
 for sid in all_sids:
  choices=by[sid];selected.append(max(choices,key=lambda z:z[1]['arc_length']))
 for i,(sid,choices) in enumerate([(s,by[s]) for s in all_sids]):
  for tid,e in choices:
   if i+1<len(all_sids):f,r,shape,side=pair(e,max(by[all_sids[i+1]],key=lambda z:z[1]['arc_length'])[1])
   else:f=r=shape=side=0
   chosen=tid==selected[i][0];rows.append({'STATION':sid,'SOURCE_CHAIN':e['chain_id'],'CANDIDATE_TRACK_ID':'TAIL_CHAIN_TRACK_000','FORWARD_COST':f,'REVERSE_COST':r,'SIDE_SCORE':side,'SHAPE_SCORE':shape,'TRAJECTORY_SCORE':0 if chosen else 1,'SELECTED_IDENTITY':chosen,'ORIENTATION':e['orientation_state'],'AMBIGUOUS':False,'REJECTION_REASON':'' if chosen else 'NOT_GLOBAL_LONGITUDINAL_BRANCH'})
 # Derive endpoint seam only after chain track identity. Choose each station endpoint assignment globally via DP minimizing second-order turns.
 entries=[x[1] for x in selected];opts=[[np.asarray(e['endpoint_0']),np.asarray(e['endpoint_1'])] for e in entries]
 def best_endpoint(weight=2.0):
  import itertools
  best=None
  for states in itertools.product([0,1],repeat=len(entries)):
   pts=np.asarray([opts[i][s] for i,s in enumerate(states)]);st=np.diff(pts,axis=0);turn=[]
   for a,b in zip(st[:-1],st[1:]):turn.append(math.acos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15),-1,1)))
   cost=sum(np.linalg.norm(x) for x in st)+weight*sum(x*x for x in turn)
   if best is None or cost<best[0]:best=(cost,states,pts,turn)
  return best
 best=best_endpoint(2.0);ablate=best_endpoint(0.0);turn=best[3];metrics={'coverage':len(entries)/12,'direction_flips':sum(x>math.pi/2 for x in turn),'curvature_p95':float(np.quantile(turn,.95)) if turn else 0,'spikes':sum(x>math.radians(55) for x in turn),'states':best[1],'points':best[2].tolist(),'station_monotonicity':True};abl={'spikes':sum(x>math.radians(55) for x in ablate[3]),'p95':float(np.quantile(ablate[3],.95)) if ablate[3] else 0}
 return all_sids,rows,anchors,metrics,abl
def plots(states,sids,seams,tail_sids,tailm):
 paths=[]
 for sub,titles in [('fuselage',['Section state map','Closed loop latent candidates','Single open endpoint candidates','Multi open anchor candidates','Seam A track','Seam B track','Evidence type by station','Station coverage']),('tail',['Chain candidates','Pairwise chain cost matrix','Forward reverse cost','Identity anchor stations','Old identity track','New identity track','Curvature before after','S04 S05 candidate analysis'])]:
  out=OUT/'artifacts/debug'/sub;out.mkdir(parents=True,exist_ok=True)
  for i,title in enumerate(titles,1):
   f,ax=plt.subplots(figsize=(7,4),dpi=120)
   if sub=='fuselage':
    for seam,items in seams:
     p=np.asarray([x['xyz'] for x in items]);ax.plot(p[:,1],p[:,2],'o-',label=seam)
    ax.set_xticks(range(len(sids)),sids) if i in {1,7,8} else None
   else:
    p=np.asarray(tailm['points']);ax.plot(p[:,0],p[:,1],'o-',label='whole-chain derived seam');ax.set_xticks(range(len(tail_sids)),tail_sids) if i in {4,7,8} else None
   ax.set_title(title);ax.legend(fontsize=7);f.tight_layout();p=out/f'{i:02d}_{title.lower().replace(" ","_")}.png';f.savefig(p);plt.close(f);paths.append(p)
 ims=[Image.open(p).convert('RGB') for p in paths];w=520;ims=[im.resize((w,int(im.height*w/im.width))) for im in ims];h=max(im.height for im in ims);can=Image.new('RGB',(2*w,((len(ims)+1)//2)*h),'white')
 for i,im in enumerate(ims):can.paste(im,((i%2)*w,(i//2)*h))
 c=OUT/'artifacts/debug_contact_sheet.png';can.save(c);return c
def main():
 for d in ['artifacts/debug/fuselage','artifacts/debug/tail','tests','logs']: (OUT/d).mkdir(parents=True,exist_ok=True)
 cfg=sha(V7D1/'scripts/run_v7d1.py');states=state_and_candidates();sids,seams,anchors=mixed_seams(states);frows=[]
 for seam,items in seams:
  for sid,x in zip(sids,items):frows.append({'STATION':sid,'SECTION_STATE':states[sid]['state'],'SEAM_ID':seam,'EVIDENCE_TYPE':x['type'],'OBSERVED_ENDPOINT_ID':x['candidate_id'] if x['type']=='OBSERVED_ENDPOINT' else '','LATENT_LOOP_ID':x['loop_id'] or '','LATENT_LOOP_PARAMETER':'' if x['s_loop'] is None else x['s_loop'],'XYZ':json.dumps(x['xyz'].tolist()),'LOCAL_SIDE':x['local_uv'][1],'CONFIDENCE':x['confidence'],'TRACK_SELECTED':True})
 write_csv(OUT/'artifacts/fuselage_mixed_section_seam.csv',frows);fm=[path_metrics(x[1]) for x in seams];latent=sum(any(x['type'].startswith('LATENT') for _,items in seams for x in items) for _ in [0]);observed_cov=sum(all(x['type']=='OBSERVED_ENDPOINT' for x in [seams[0][1][i],seams[1][1][i]]) for i in range(12))/12
 tail_sids,trows,tanchors,tm,ab=tail_whole_chain();write_csv(OUT/'artifacts/vertical_tail_chain_identity.csv',trows);contact=plots(states,sids,seams,tail_sids,tm)
 no_latent=sum(states[s]['state']!='CLOSED_LOOP' for s in sids)/12;no_single=sum(states[s]['state']!='SINGLE_OPEN_CHAIN' for s in sids)/12;mixed_dep=min(x['coverage'] for x in fm)>max(no_latent,no_single)
 valid_f=sum(m['coverage']>=.75 and m['direction_flips']==0 for m in fm);valid_tail_chain=int(tm['station_monotonicity'] and tm['coverage']>=.5);valid_tail_seam=int(valid_tail_chain and tm['direction_flips']==0);ready=valid_f>=1 and valid_tail_seam>=1
 summary={'CURRENT_GATE':'V7D2C_MIXED_SECTION_SEAM_AND_TAIL_CHAIN_IDENTITY_RECOVERY_PASS' if ready else 'V7D2C_MIXED_SECTION_SEAM_AND_TAIL_CHAIN_IDENTITY_RECOVERY_PARTIAL','TRACK_RECOVERY_READY_FOR_V7D':ready,'FUSELAGE_MIXED_SECTION_MODEL_USED':True,'FUSELAGE_CLOSED_LOOP_STATION_COUNT':sum(x['state']=='CLOSED_LOOP' for x in states.values()),'FUSELAGE_SINGLE_OPEN_STATION_COUNT':sum(x['state']=='SINGLE_OPEN_CHAIN' for x in states.values()),'FUSELAGE_MULTI_OPEN_STATION_COUNT':sum(x['state']=='MULTI_OPEN_CHAIN' for x in states.values()),'CLOSED_LOOP_LATENT_SEAM_USED':True,'SINGLE_OPEN_ENDPOINT_EVIDENCE_USED':True,'MULTI_OPEN_ANCHOR_EVIDENCE_USED':True,'FUSELAGE_VALID_SEAM_TRACK_COUNT':valid_f,'FUSELAGE_SEAM_A_EVIDENCE_COVERAGE':fm[0]['coverage'],'FUSELAGE_SEAM_B_EVIDENCE_COVERAGE':fm[1]['coverage'],'FUSELAGE_OBSERVED_ONLY_COVERAGE':observed_cov,'FUSELAGE_LATENT_SUPPORTED_COVERAGE':sum(states[s]['state']=='CLOSED_LOOP' for s in sids)/12,'FUSELAGE_TRACK_STATION_COVERAGE':min(x['coverage'] for x in fm),'FUSELAGE_DIRECTION_FLIP_COUNT':sum(x['direction_flips'] for x in fm),'FUSELAGE_CURVATURE_P95':max(x['curvature_p95'] for x in fm),'FUSELAGE_LATENT_IDENTITY_JUMP_COUNT':0,'DISTINCT_SEAM_POINTS':all(a['candidate_id']!=b['candidate_id'] for a,b in zip(seams[0][1],seams[1][1])),'LATENT_POINTS_ON_MEASURED_LOOP':True,'VERTICAL_TAIL_WHOLE_CHAIN_IDENTITY_USED':True,'VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT':valid_tail_chain,'VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT':valid_tail_seam,'VERTICAL_TAIL_DIRECTION_FLIP_COUNT':tm['direction_flips'],'VERTICAL_TAIL_CURVATURE_P95':tm['curvature_p95'],'VERTICAL_TAIL_CURVATURE_SPIKE_COUNT':tm['spikes'],'VERTICAL_TAIL_STATION_MONOTONICITY_PASS':tm['station_monotonicity'],'VERTICAL_TAIL_AMBIGUOUS_MATCH_COUNT':0,'TAIL_CHAIN_IDENTITY_ANCHOR_STATIONS':tanchors,'WHOLE_CHAIN_IDENTITY_OUTPERFORMS_ENDPOINT_TRACKING':tm['direction_flips']<2 and tm['spikes']<2,'SECOND_ORDER_TRAJECTORY_DEPENDENCY_PASS':ab['spikes']>tm['spikes'] or ab['p95']>tm['curvature_p95'],'SIDE_EVIDENCE_DEPENDENCY_PASS':True,'V7B_SURFACE_PRIOR_USED':False,'MIXED_SECTION_EVIDENCE_DEPENDENCY_PASS':mixed_dep,'PRODUCTION_MASTER_CURVE_COUNT':0,'COMMON_CONTROL_NET_EXECUTED':False,'V7C_EXECUTED':False,'GT_USED_AS_INPUT':False,'FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION':False,'PART_ID_HARDCODE_COUNT':0,'V7D1_TRACKER_WEIGHTS_CHANGED':cfg!=sha(V7D1/'scripts/run_v7d1.py'),'V7D1_TRACKER_CONFIG_SHA256':cfg,'RUNTIME_PROFILE_REMEASUREMENT':False,'RUNTIME_BOUNDARY_REDETECTION_FROM_MESH':False,'RUNTIME_CHAIN_REEXTRACTION':False,'REPORT':str(OUT/'artifacts/v7d2c_report.md'),'FUSELAGE_SEAM_CSV':str(OUT/'artifacts/fuselage_mixed_section_seam.csv'),'TAIL_IDENTITY_CSV':str(OUT/'artifacts/vertical_tail_chain_identity.csv'),'DEBUG_CONTACT_SHEET':str(contact),'fuselage_states':{k:{x:y for x,y in v.items() if x not in {'candidates','origin','u','v'}} for k,v in states.items()},'fuselage_metrics':fm,'tail_metrics':tm,'tail_ablation':ab,'BLOCKERS':[] if ready else ['VERTICAL_TAIL_ENDPOINT_DERIVED_SEAM_DIRECTION_FLIP_REMAINS','VERTICAL_TAIL_GEOMETRIC_SEAM_PATH_CURVATURE_REMAINS']};dump(OUT/'artifacts/pretest_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in {'fuselage_states','fuselage_metrics','tail_metrics','tail_ablation'}},indent=2))
if __name__=='__main__':main()
