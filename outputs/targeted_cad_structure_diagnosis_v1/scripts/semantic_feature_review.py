"""Conservative semantic check: distinguish enclosed holes/pockets from generic boundary trims.

Post-hoc diagnostic only. Never changes fitted geometry, candidate selection or metrics.
"""
from structure_common import *
def check(p,vox):
 a=vox['source'];origin=vox['origin'];pitch=float(vox['pitch']);B=np.asarray(p['basis']);c=np.asarray(p['center']);dx,dy,dz=p['dimensions'];rings=[]
 for z in [-.25,0,.25]:
  if p['shape']=='CYLINDER':
   t=np.linspace(0,2*np.pi,32,endpoint=False);r=dx/2+1.5*pitch;local=np.column_stack([r*np.cos(t),r*np.sin(t),np.full(32,z*dz)])
  elif p['shape']=='SLOT':
   t=np.linspace(-np.pi/2,np.pi/2,16);rr=dy/2+1.5*pitch;h=max(0,(dx-dy)/2);xy=np.vstack([np.column_stack([h+rr*np.cos(t),rr*np.sin(t)]),np.column_stack([-h-rr*np.cos(t),-rr*np.sin(t)])]);local=np.column_stack([xy,np.full(len(xy),z*dz)])
  else:
   u=np.linspace(-1,1,9);xx=dx/2+1.5*pitch;yy=dy/2+1.5*pitch;xy=np.vstack([np.column_stack([u*xx,np.full(9,yy)]),np.column_stack([u*xx,np.full(9,-yy)]),np.column_stack([np.full(9,xx),u*yy]),np.column_stack([np.full(9,-xx),u*yy])]);local=np.column_stack([xy,np.full(len(xy),z*dz)])
  world=c+local@B.T;idx=np.rint((world-origin)/pitch).astype(int);valid=np.all((idx>=0)&(idx<np.array(a.shape)),axis=1);hits=np.zeros(len(idx),bool);ii=idx[valid];hits[valid]=a[ii[:,0],ii[:,1],ii[:,2]];rings.append(float(hits.mean()))
 coverage=float(np.mean(rings));supported=p['operation']=='union' or coverage>=.65
 semantic=p['feature_type'] if supported else 'GENERIC_CUT_OR_END_TRIM'
 return {'semantic_feature_type':semantic,'semantic_rule_supported':supported,'source_sidewall_coverage':coverage,'sidewall_coverage_by_depth':rings,'semantic_rule':'cut requires >=.65 source occupancy around measured tool sidewalls at 3 axial depths; addition retains contact-based primitive hypothesis','semantic_status':'RULE_HYPOTHESIS_NOT_GROUND_TRUTH' if supported else 'NO_ENCLOSED_HOLE_SLOT_POCKET_EVIDENCE'}
if __name__=='__main__':
 out=[]
 for row in read(O/'manifests/subset.json'):
  for path in sorted((O/'cases'/row['case_id']/'rounds').glob('round_*/residual.json')):
   vox=np.load(path.parent/'residual.npz')
   for j,p in enumerate(read(path)['proposals']):out.append({'case_id':row['case_id'],'round':int(path.parent.name.split('_')[1]),'candidate':j,'raw_feature_type':p['feature_type'],**check(p,vox)})
 dump(O/'reports/SEMANTIC_FEATURE_REVIEW.json',out);table('feature_semantic_review.csv',out);print('SEMANTIC_REVIEW',len(out),flush=True)
