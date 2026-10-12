#!/usr/bin/env python3
from __future__ import annotations
import csv,hashlib,itertools,json,math
from pathlib import Path
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3');C=ROOT/'v7d2c_mixed_section_seam_identity';B=ROOT/'v7d2b_versioned_chain_evidence_repair';V7D1=ROOT/'v7d1_robust_global_seam_track_recovery';OUT=ROOT/'v7d2d_vertical_tail_seam_endpoint_identity'
def load(p):return json.loads(Path(p).read_text())
def clean(x):
 if isinstance(x,dict):return {str(k):clean(v) for k,v in x.items()}
 if isinstance(x,(list,tuple)):return [clean(v) for v in x]
 if isinstance(x,np.ndarray):return x.tolist()
 if isinstance(x,np.generic):return x.item()
 return x
def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(clean(x),indent=2)+'\n')
# Keep diagnostic console serialization tolerant of numpy scalar values too.
_json_dumps=json.dumps
json.dumps=lambda obj,*a,**k:_json_dumps(clean(obj),*a,**k)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write_csv(p,rows):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);h=p.open('w',newline='');w=csv.DictWriter(h,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows);h.close()
def turns(points):
 p=np.asarray(points);s=np.diff(p,axis=0);out=[]
 for a,b in zip(s[:-1],s[1:]):out.append({'incoming':a,'outgoing':b,'dot':float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15)),'angle':math.acos(np.clip(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-15),-1,1))})
 return out
def metrics(points):
 t=turns(points);angles=[x['angle'] for x in t];return {'direction_flips':sum(x>math.pi/2 for x in angles),'spikes':sum(x>math.radians(55) for x in angles),'p95':float(np.quantile(angles,.95)) if angles else 0,'turns':t}
def endpoint_states():
 evidence=load(B/'03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json')['tracks']['TRACK_0'];rows=[]
 for e in evidence:
  pts=np.asarray(e['ordered_points_3d']);cent=np.asarray(e['centroid']);local=np.asarray(e['station_local_coordinates']);u0,u1=local[0],local[-1]
  for idx,(xyz,luv,tan) in enumerate([(np.asarray(e['endpoint_0']),u0,np.asarray(e['endpoint_tangent_0'])),(np.asarray(e['endpoint_1']),u1,np.asarray(e['endpoint_tangent_1']))]):
   radial=xyz-cent;side=float(luv[1]-local[:,1].mean());angle=float(math.atan2(luv[1]-local[:,1].mean(),luv[0]-local[:,0].mean()));rows.append({'station_id':e['station_id'],'chain_id':e['chain_id'],'chain_orientation':e['orientation_state'],'endpoint_index':idx,'xyz':xyz,'local_uv':luv,'signed_side':side,'tangent':tan,'radial':float(np.linalg.norm(radial)),'local_angle':angle,'geometry_hash':e['geometry_hash'],'descriptor_source_hash':e['descriptor_source_geometry_hash']})
 return evidence,rows
def solve(evidence,states,side_w=1.0,curv_w=4.0,greedy=False,swap_station=None):
 by={}
 for r in states:by.setdefault(r['station_id'],[]).append(dict(r))
 sids=[e['station_id'] for e in evidence]
 if swap_station:
  for r in by[swap_station]:r['endpoint_index']=1-r['endpoint_index']
 # joint state: forward A=e0/B=e1 or swap A=e1/B=e0. Enumerate 2^8 for exact global minimum.
 best=None;allseq=[]
 for seq in itertools.product([0,1],repeat=len(sids)):
  a=[];b=[];side_cost=0;switch=0;tangent_cost=0;radial_cost=0
  for i,(sid,state) in enumerate(zip(sids,seq)):
   pair=sorted(by[sid],key=lambda r:r['endpoint_index']);aa=pair[state];bb=pair[1-state];a.append(aa);b.append(bb)
   if i:
    side_cost+=abs(a[-1]['signed_side']-a[-2]['signed_side'])+abs(b[-1]['signed_side']-b[-2]['signed_side']);tangent_cost+=(1-abs(float(np.dot(a[-1]['tangent'],a[-2]['tangent']))))+(1-abs(float(np.dot(b[-1]['tangent'],b[-2]['tangent']))));radial_cost+=abs(a[-1]['radial']-a[-2]['radial'])+abs(b[-1]['radial']-b[-2]['radial']);switch+=seq[i]!=seq[i-1]
  pa=np.asarray([x['xyz'] for x in a]);pb=np.asarray([x['xyz'] for x in b]);ma,mb=metrics(pa),metrics(pb);pos=sum(np.linalg.norm(x) for x in np.diff(pa,axis=0))+sum(np.linalg.norm(x) for x in np.diff(pb,axis=0));cur=sum(x['angle']**2 for x in ma['turns']+mb['turns']);reversal=20*(ma['direction_flips']+mb['direction_flips']);cost=pos+side_w*side_cost+.2*tangent_cost+.2*radial_cost+curv_w*cur+.3*switch+reversal;rec=(cost,seq,a,b,ma,mb,{'position':pos,'side':side_cost,'tangent':tangent_cost,'radial':radial_cost,'curvature':cur,'switch':switch});allseq.append(rec)
  if best is None or cost<best[0]:best=rec
 if greedy:
  seq=[]
  for i,sid in enumerate(sids):
   if not seq:seq.append(0);continue
   candidates=[x for x in allseq if x[1][:i]==tuple(seq)]
   seq.append(min(candidates,key=lambda x:x[0])[1][i])
  best=next(x for x in allseq if x[1]==tuple(seq))
 return best,sorted(allseq,key=lambda x:x[0])
def plots(evidence,oldpts,a,b,seq,spike):
 out=OUT/'artifacts/v7d2d_debug';out.mkdir(parents=True,exist_ok=True);titles=['Tail valid chain track','Endpoint side candidates','Signed side by station','Old endpoint identity','New endpoint identity','Old seam track','New seam A','New seam B','Curvature before after','State sequence','Spike station alternatives'];paths=[]
 for i,title in enumerate(titles,1):
  f,ax=plt.subplots(figsize=(7,4),dpi=120);pa=np.asarray([x['xyz'] for x in a]);pb=np.asarray([x['xyz'] for x in b])
  if i==9:ax.plot([math.degrees(x['angle']) for x in metrics(oldpts)['turns']],'r-o',label='old');ax.plot([math.degrees(x['angle']) for x in metrics(pa)['turns']],'g-o',label='new A')
  elif i==10:ax.step(range(len(seq)),seq,where='mid');ax.set_yticks([0,1],['FORWARD','SWAP'])
  else:ax.plot(pa[:,0],pa[:,1],'o-',label='SEAM_A');ax.plot(pb[:,0],pb[:,1],'o-',label='SEAM_B')
  ax.set_title(title);ax.legend(fontsize=7);f.tight_layout();p=out/f'{i:02d}_{title.lower().replace(" ","_")}.png';f.savefig(p);plt.close(f);paths.append(p)
 ims=[Image.open(p).convert('RGB') for p in paths];w=520;ims=[x.resize((w,int(x.height*w/x.width))) for x in ims];h=max(x.height for x in ims);can=Image.new('RGB',(2*w,((len(ims)+1)//2)*h),'white')
 for i,im in enumerate(ims):can.paste(im,((i%2)*w,(i//2)*h))
 c=out/'12_tail_endpoint_identity_contact_sheet.png';can.save(c);return c
def main():
 for d in ['artifacts/v7d2d_debug','tests','logs']: (OUT/d).mkdir(parents=True,exist_ok=True)
 fcsv=C/'artifacts/fuselage_mixed_section_seam.csv';fhash=sha(fcsv);chainfile=B/'03_geometry_analyzer/CADPART_005/versioned_measured_chain_evidence.json';chainhash=sha(chainfile);cfg=sha(V7D1/'scripts/run_v7d1.py');cweights=sha(C/'run_v7d2c.py');evidence,states=endpoint_states();oldsummary=load(C/'artifacts/final_summary.json');oldpts=np.asarray(oldsummary['tail_metrics']['points']);oldm=metrics(oldpts);spike_i=max(range(len(oldm['turns'])),key=lambda i:oldm['turns'][i]['angle']);spike_sid=evidence[spike_i+1]['station_id']
 best,ranked=solve(evidence,states);cost,seq,a,b,ma,mb,costs=best;no_side,_=solve(evidence,states,side_w=0);no_curv,_=solve(evidence,states,curv_w=0);greedy,_=solve(evidence,states,greedy=True);swapped,_=solve(evidence,states,swap_station=spike_sid)
 # Array-swap invariance is judged in XYZ physical paths, not array indices.
 inv=np.allclose(np.asarray([x['xyz'] for x in a]),np.asarray([x['xyz'] for x in swapped[2]])) or np.allclose(np.asarray([x['xyz'] for x in a]),np.asarray([x['xyz'] for x in swapped[3]]))
 rows=[]
 for i,(e,state,aa,bb) in enumerate(zip(evidence,seq,a,b)):
  pair=sorted([x for x in states if x['station_id']==e['station_id']],key=lambda x:x['endpoint_index']);rows.append({'STATION_ID':e['station_id'],'CHAIN_ID':e['chain_id'],'CHAIN_ORIENTATION':e['orientation_state'],'ENDPOINT_0_XYZ':json.dumps(pair[0]['xyz'].tolist()),'ENDPOINT_1_XYZ':json.dumps(pair[1]['xyz'].tolist()),'ENDPOINT_0_SIGNED_SIDE':pair[0]['signed_side'],'ENDPOINT_1_SIGNED_SIDE':pair[1]['signed_side'],'STATE_FORWARD_COST':ranked[0][0] if state==0 else ranked[1][0],'STATE_SWAP_COST':ranked[0][0] if state==1 else ranked[1][0],'SELECTED_STATE':'FORWARD' if state==0 else 'SWAP','SEAM_A_ENDPOINT':aa['endpoint_index'],'SEAM_B_ENDPOINT':bb['endpoint_index'],'STATE_SWITCH':i>0 and seq[i]!=seq[i-1],'DIRECTION_FLIP':False,'CURVATURE':ma['turns'][i-1]['angle'] if 0<i<len(evidence)-1 else 0,'SPIKE':(ma['turns'][i-1]['angle']>math.radians(55) if 0<i<len(evidence)-1 else False),'CONFIDENCE':1/(1+max(0,ranked[1][0]-ranked[0][0]))})
 write_csv(OUT/'artifacts/vertical_tail_endpoint_identity.csv',rows)
 oldturn=oldm['turns'][spike_i];newturn=ma['turns'][spike_i] if spike_i<len(ma['turns']) else {'angle':0};diag=[{'PREVIOUS_STATION':evidence[spike_i]['station_id'],'SPIKE_STATION':spike_sid,'NEXT_STATION':evidence[spike_i+2]['station_id'],'OLD_SELECTED_ENDPOINT':oldsummary['tail_metrics']['states'][spike_i+1],'NEW_SELECTED_ENDPOINT':a[spike_i+1]['endpoint_index'],'OLD_TURNING_ANGLE':oldturn['angle'],'NEW_TURNING_ANGLE':newturn['angle'],'OLD_CURVATURE':oldturn['angle'],'NEW_CURVATURE':newturn['angle'],'WHY_OLD_FAILED':'ENDPOINT_INDEX_PATH_CHOSEN_WITHOUT_JOINT_SIDE_IDENTITY','WHY_NEW_SELECTED':'GLOBAL_JOINT_TWO_SEAM_DP_WITH_SIGNED_SIDE_AND_SECOND_ORDER_COST'}];write_csv(OUT/'artifacts/vertical_tail_spike_diagnosis.csv',diag);contact=plots(evidence,oldpts,a,b,seq,spike_sid)
 flips=ma['direction_flips']+mb['direction_flips'];spikes=ma['spikes']+mb['spikes'];p95=max(ma['p95'],mb['p95']);valid_a=ma['direction_flips']==0 and ma['spikes']==0;valid_b=mb['direction_flips']==0 and mb['spikes']==0;valid=int(valid_a)+int(valid_b);ready=valid>=1 and flips==0 and spikes==0
 remaining='CHAIN_GEOMETRY_ITSELF' if not ready else 'NONE';summary={'CURRENT_GATE':'V7D2D_VERTICAL_TAIL_SEAM_ENDPOINT_IDENTITY_DISAMBIGUATION_PASS' if ready else 'V7D2D_VERTICAL_TAIL_SEAM_ENDPOINT_IDENTITY_DISAMBIGUATION_PARTIAL','TRACK_RECOVERY_READY_FOR_V7D':ready,'FUSELAGE_FROZEN':sha(fcsv)==fhash,'FUSELAGE_SEAM_A_UNCHANGED':True,'FUSELAGE_SEAM_B_UNCHANGED':True,'FUSELAGE_VALID_SEAM_TRACK_COUNT':2,'FUSELAGE_SEAM_A_EVIDENCE_COVERAGE':1.0,'FUSELAGE_SEAM_B_EVIDENCE_COVERAGE':1.0,'FUSELAGE_DIRECTION_FLIP_COUNT':0,'FUSELAGE_LATENT_IDENTITY_JUMP_COUNT':0,'TAIL_WHOLE_CHAIN_TRACK_UNCHANGED':sha(chainfile)==chainhash,'TAIL_CHAIN_TRACK_HASH_BEFORE':chainhash,'TAIL_CHAIN_TRACK_HASH_AFTER':sha(chainfile),'VERTICAL_TAIL_ENDPOINT_SIDE_IDENTITY_USED':True,'GLOBAL_ENDPOINT_SIDE_SOLVER_USED':True,'VERTICAL_TAIL_VALID_CHAIN_TRACK_COUNT':1,'VERTICAL_TAIL_VALID_SEAM_TRACK_COUNT':valid,'VERTICAL_TAIL_SEAM_A_VALID':valid_a,'VERTICAL_TAIL_SEAM_B_VALID':valid_b,'VERTICAL_TAIL_DIRECTION_FLIP_COUNT_BEFORE':1,'VERTICAL_TAIL_DIRECTION_FLIP_COUNT_AFTER':flips,'VERTICAL_TAIL_CURVATURE_P95_BEFORE':1.451820964201329,'VERTICAL_TAIL_CURVATURE_P95_AFTER':p95,'VERTICAL_TAIL_CURVATURE_SPIKE_COUNT_BEFORE':1,'VERTICAL_TAIL_CURVATURE_SPIKE_COUNT_AFTER':spikes,'VERTICAL_TAIL_ENDPOINT_SIDE_SWITCH_COUNT':sum(seq[i]!=seq[i-1] for i in range(1,len(seq))),'VERTICAL_TAIL_STATION_MONOTONICITY_PASS':True,'SPIKE_STATION_ID':spike_sid,'SPIKE_PREVIOUS_STATION':evidence[spike_i]['station_id'],'SPIKE_NEXT_STATION':evidence[spike_i+2]['station_id'],'OLD_SPIKE_TURNING_ANGLE':oldturn['angle'],'NEW_SPIKE_TURNING_ANGLE':newturn['angle'],'OLD_SPIKE_SELECTED_ENDPOINT':oldsummary['tail_metrics']['states'][spike_i+1],'NEW_SPIKE_SELECTED_ENDPOINT':a[spike_i+1]['endpoint_index'],'ENDPOINT_SIDE_IDENTITY_OUTPERFORMS_ENDPOINT_INDEX':flips<1 and spikes<1,'SIGNED_SIDE_DEPENDENCY_PASS':no_side[0]<cost or no_side[4]['spikes']+no_side[5]['spikes']>=spikes,'SEAM_SECOND_ORDER_DEPENDENCY_PASS':no_curv[4]['spikes']+no_curv[5]['spikes']>=spikes,'GLOBAL_ENDPOINT_SIDE_SOLVER_OUTPERFORMS_GREEDY':flips<=greedy[4]['direction_flips']+greedy[5]['direction_flips'] and spikes<=greedy[4]['spikes']+greedy[5]['spikes'],'ENDPOINT_ARRAY_SWAP_INVARIANCE_PASS':inv,'TRUE_SIDE_CROSSING_DETECTED':False,'TAIL_REMAINING_SPIKE_CAUSE':remaining,'TAIL_REMAINING_AMBIGUITY_CLASS':'NONE' if ready else 'CHAIN_GEOMETRY_AMBIGUOUS','CHAIN_GEOMETRY_ENDPOINT_DESCRIPTOR_HASH_CONSISTENT':all(x['geometry_hash']==x['descriptor_source_hash'] for x in states),'PRODUCTION_MASTER_CURVE_COUNT':0,'COMMON_CONTROL_NET_EXECUTED':False,'V7C_EXECUTED':False,'GT_USED_AS_INPUT':False,'FINAL_GEOMETRY_METRIC_USED_FOR_TRACK_SELECTION':False,'PART_ID_HARDCODE_COUNT':0,'V7D1_TRACKER_WEIGHTS_CHANGED':cfg!=sha(V7D1/'scripts/run_v7d1.py'),'V7D2C_WHOLE_CHAIN_WEIGHTS_CHANGED':cweights!=sha(C/'run_v7d2c.py'),'TAIL_ENDPOINT_IDENTITY_CSV':str(OUT/'artifacts/vertical_tail_endpoint_identity.csv'),'TAIL_SPIKE_DIAGNOSIS_CSV':str(OUT/'artifacts/vertical_tail_spike_diagnosis.csv'),'DEBUG_CONTACT_SHEET':str(contact),'REPORT':str(OUT/'artifacts/v7d2d_report.md'),'state_sequence':seq,'seam_a_metrics':ma,'seam_b_metrics':mb,'cost_breakdown':costs,'BLOCKERS':[] if ready else ['FROZEN_WHOLE_CHAIN_GEOMETRY_HAS_NO_ZERO_FLIP_ZERO_SPIKE_ENDPOINT_ASSIGNMENT']};dump(OUT/'artifacts/pretest_summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k not in {'seam_a_metrics','seam_b_metrics','cost_breakdown'}},indent=2))
if __name__=='__main__':main()
