from structure_common import *
import trimesh
from scipy import ndimage
from scipy.spatial import cKDTree
from scipy.optimize import minimize
from fit_logic import voxel_occupancy,basis_for_axis

def grid(source,cad):
 lo=np.minimum(source.bounds[0],cad.bounds[0]);hi=np.maximum(source.bounds[1],cad.bounds[1]);pitch=float(max(hi-lo)/124);origin=lo-2*pitch;shape=tuple(np.ceil((hi-origin)/pitch).astype(int)+3)
 a=voxel_occupancy(source,origin,pitch,shape);b=voxel_occupancy(cad,origin,pitch,shape)
 return a,b,origin,pitch
def iou(a,b):return float(np.logical_and(a,b).sum()/max(1,np.logical_or(a,b).sum()))
def components(mask,origin,pitch,cad,source):
 labels,n=ndimage.label(mask);objects=ndimage.find_objects(labels);counts=np.bincount(labels.ravel());tree=cKDTree(cad.triangles_center);stree=cKDTree(source.triangles_center);out=[]
 for k,sl in enumerate(objects,1):
  if sl is None:continue
  ids=np.argwhere(labels[sl]==k)+np.array([s.start for s in sl]);pts=origin+ids*pitch;center=pts.mean(0)
  vals,B=np.linalg.eigh(np.cov(pts.T)) if len(pts)>3 else (np.zeros(3),np.eye(3));B=B[:,np.argsort(vals)[::-1]]
  if np.linalg.det(B)<0:B[:,-1]*=-1
  q=(pts-center)@B;dims=np.ptp(q,axis=0)+pitch;sample=pts[::max(1,len(pts)//512)];dist,_=tree.query(sample);_,idx=stree.query(sample);normals=source.face_normals[idx];orientation=normals.mean(0);cov=normals.T@normals/max(1,len(normals))
  out.append({'component_id':k,'voxel_n':int(counts[k]),'volume':float(counts[k]*pitch**3),'bbox':[(pts.min(0)-pitch/2).tolist(),(pts.max(0)+pitch/2).tolist()],'centroid':center.tolist(),'principal_axes':B.tolist(),'oriented_extents':dims.tolist(),'aspect_ratio':float(max(dims)/max(min(dims),pitch)),'distance_to_base_cad':float(np.median(dist)),'distance_method':'nearest CAD triangle centroid proxy','surface_orientation':orientation.tolist(),'normal_covariance_eigenvalues':np.linalg.eigvalsh(cov).tolist(),'grid_bbox':[[s.start for s in sl],[s.stop for s in sl]]})
 return sorted(out,key=lambda c:-c['voxel_n']),labels

def inside(points,p):
 q=(points-np.asarray(p['center']))@np.asarray(p['basis']);dims=np.asarray(p['dimensions']);half=dims/2
 if p['shape']=='BOX':return np.all(np.abs(q)<=half,axis=1)
 if p['shape']=='CYLINDER':return (q[:,0]**2+q[:,1]**2<=half[0]**2)&(np.abs(q[:,2])<=half[2])
 # X elongated capsule, width along Y, extrusion Z.
 axial=np.maximum(np.abs(q[:,0])-max(0,(dims[0]-dims[1])/2),0)
 return (axial**2+q[:,1]**2<=half[1]**2)&(np.abs(q[:,2])<=half[2])

def fit_component(c,labels,sign,a,b,origin,pitch,code):
 lo=np.array(c['grid_bbox'][0]);hi=np.array(c['grid_bbox'][1]);sl=tuple(slice(x,y) for x,y in zip(lo,hi));ids=np.argwhere(labels[sl]==c['component_id'])+lo;pts=origin+ids*pitch
 center=np.array(c['centroid']);P=np.array(c['principal_axes']);bases=[P]
 # Include the CAD construction axes. Rotationally symmetric sections can make PCA unstable.
 try:
  for n in ast.walk(ast.parse(code)):
   if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Plane':
    kw={k.arg:ast.literal_eval(k.value) for k in n.keywords};x=np.array(kw['xDir']);z=np.array(kw['normal']);x/=np.linalg.norm(x);z/=np.linalg.norm(z);bases.append(np.column_stack([x,np.cross(z,x),z]));break
 except Exception:pass
 fits=[]
 for B0 in bases:
  # Each basis axis can be a bore/extrusion axis. Box needs only one ordering.
  for axis in range(3):
   order=[i for i in range(3) if i!=axis]+[axis];B=B0[:,order].copy()
   if np.linalg.det(B)<0:B[:,0]*=-1
   q=(pts-center)@B;ql=q.min(0)-pitch/2;qh=q.max(0)+pitch/2;dims=qh-ql;cc=center+B@((qh+ql)/2)
   kinds=['CYLINDER','SLOT']+(['BOX'] if axis==2 else [])
   for kind in kinds:
    if kind=='SLOT' and dims[0]<dims[1]:continue
    dd=dims.copy()
    if kind=='CYLINDER':
     # Uniform voxel volume: outer radial support, then occupancy precision validation.
     radius=float(np.quantile(np.linalg.norm((pts-cc)@B[:,:2],axis=1),.98)+pitch/2);dd[:2]=2*radius
    p={'shape':kind,'center':cc.tolist(),'basis':B.tolist(),'dimensions':dd.tolist(),'operation':'cut' if sign=='EXTRA' else 'union','component_id':c['component_id'],'residual_sign':sign}
    pred=inside(pts,p);support=float(pred.mean());predvol=(np.prod(dd) if kind=='BOX' else np.pi*(dd[0]/2)**2*dd[2] if kind=='CYLINDER' else (max(0,dd[0]-dd[1])*dd[1]+np.pi*(dd[1]/2)**2)*dd[2]);precision=min(1,float(pred.sum()*pitch**3/max(predvol,1e-15)))
    if precision<.55 or support<.75:continue
    p.update(component_fit_precision=precision,component_fit_recall=support)
    fits.append(p)
 # Best support model per shape, not dozens of feature hypotheses.
 best=[]
 for kind in ['CYLINDER','SLOT','BOX']:
  fs=[p for p in fits if p['shape']==kind]
  if fs:best.append(max(fs,key=lambda p:p['component_fit_precision']*p['component_fit_recall']))
 return best

def optimize_feature(p,a,b,origin,pitch):
 B=np.asarray(p['basis']);center=np.asarray(p['center']);dims=np.asarray(p['dimensions']);corners=np.array([[x,y,z] for x in [-.7,.7] for y in [-.7,.7] for z in [-.7,.7]])*dims;world=center+corners@B.T;lo=np.maximum(0,np.floor((world.min(0)-origin)/pitch).astype(int)-3);hi=np.minimum(a.shape,np.ceil((world.max(0)-origin)/pitch).astype(int)+4);sl=tuple(slice(x,y) for x,y in zip(lo,hi));indices=np.indices(tuple(hi-lo)).reshape(3,-1).T+lo;points=origin+indices*pitch;aa=a[sl].ravel();bb=b[sl].ravel();inter=int((a&b).sum());union=int((a|b).sum());oldi=int((aa&bb).sum());oldu=int((aa|bb).sum());initial=iou(a,b);calls=[]
 def params(x):
  x=np.asarray(x);r=dict(p);r['center']=(center+B@(x[:3]*pitch)).tolist();d=dims*np.array(x[3:]);
  if p['shape']=='CYLINDER':d[1]=d[0]
  if p['shape']=='SLOT':d[0]=max(d[0],d[1])
  r['dimensions']=d.tolist();return r
 def score(x,record=True):
  r=params(x);mask=inside(points,r);new=(bb&~mask) if p['operation']=='cut' else (bb|mask);val=(inter-oldi+int((aa&new).sum()))/max(1,union-oldu+int((aa|new).sum()))
  if record:calls.append({'x':np.asarray(x).tolist(),'iou_proxy':val})
  return -val
 x0=np.array([0.,0.,0.,1.,1.,1.]);score(x0);res=minimize(score,x0,method='Powell',bounds=[(-2,2)]*3+[(.75,1.2)]*3,options={'maxiter':3,'maxfev':90,'xtol':.04,'ftol':1e-4});best=min(calls,key=lambda z:-z['iou_proxy']);out=params(best['x']);out.update(proxy_iou=best['iou_proxy'],proxy_delta_iou=best['iou_proxy']-initial,optimization_trace=calls)
 # How much of the feature's affected material is actually a residual? Independent rule check.
 mask=inside(points,out);affected=(bb&mask) if p['operation']=='cut' else (~bb&mask);correct=(~aa&affected) if p['operation']=='cut' else (aa&affected)
 out['edit_precision']=float(correct.sum()/max(1,affected.sum()));out['affected_voxel_n']=int(affected.sum());out['rule_verified']=bool(out['edit_precision']>=.65 and out['affected_voxel_n']>=16 and out['proxy_delta_iou']>0)
 # Through/Blind is a measured span hypothesis, not semantic ground truth.
 axis=B[:,2];cadpts=origin+np.argwhere(b)*pitch;span=np.ptp(cadpts@axis);through=out['dimensions'][2]>=.9*span
 if p['operation']=='cut':
  out['feature_type']='HOLE' if p['shape']=='CYLINDER' else 'SLOT' if p['shape']=='SLOT' else 'RECESS'
  out['feature_subtype']=('THROUGH_HOLE' if through else 'BLIND_HOLE_OR_CIRCULAR_RECESS') if p['shape']=='CYLINDER' else 'SLOT' if p['shape']=='SLOT' else 'RECTANGULAR_RECESS_OR_CUT'
 else:
  # Contact distinguishes attached boss from detached secondary primitive.
  mask3=mask.reshape(tuple(hi-lo));contact=bool((ndimage.binary_dilation(mask3)&b[sl]).any());out['feature_type']='BOSS' if contact else 'SECONDARY_PRIMITIVE';out['feature_subtype']=p['shape']
 return out

def analyze(source,cad,code,save=None,propose=True):
 a,b,origin,pitch=grid(source,cad);missing=a&~b;extra=b&~a;mc,ml=components(missing,origin,pitch,cad,source);ec,el=components(extra,origin,pitch,cad,source);union=int((a|b).sum());res={'iou':iou(a,b),'origin':origin.tolist(),'pitch':pitch,'shape':list(a.shape),'source_voxel_n':int(a.sum()),'cad_voxel_n':int(b.sum()),'missing_voxel_n':int(missing.sum()),'extra_voxel_n':int(extra.sum()),'missing_components':mc,'extra_components':ec,'voxel_protocol':'inherited evaluator: majority XYZ scan fill + binary_fill_holes; approximate occupancy, not exact solid difference','component_connectivity':6,'source_watertight':bool(source.is_watertight),'cad_watertight':bool(cad.is_watertight)}
 if save is not None:np.savez_compressed(save,source=a,cad=b,missing=missing,extra=extra,origin=origin,pitch=pitch)
 proposals=[]
 if propose:
  for sign,cs,labels in [('EXTRA',ec,el),('MISSING',mc,ml)]:
   for c in cs[:4]:
    if c['voxel_n']<16 or c['voxel_n']/max(1,union)>.35:continue
    for p in fit_component(c,labels,sign,a,b,origin,pitch,code):
     p=optimize_feature(p,a,b,origin,pitch)
     if p['rule_verified']:proposals.append(p)
 # Four best occupancy gains, with deterministic priority for engineering features on ties.
 priority={'HOLE':0,'SLOT':1,'RECESS':2,'BOSS':3,'SECONDARY_PRIMITIVE':4}
 proposals.sort(key=lambda p:(-p['proxy_delta_iou'],priority[p['feature_type']]))
 res['proposals']=proposals[:4];res['unselected_valid_proposal_n']=max(0,len(proposals)-4)
 return res,(a,b,origin,pitch)

def emit(p,index):
 B=np.array(p['basis']);dims=p['dimensions'];origin=np.array(p['center'])-B[:,2]*dims[2]/2
 plane='cq.Plane(origin='+repr(origin.tolist())+', xDir='+repr(B[:,0].tolist())+', normal='+repr(B[:,2].tolist())+')';name='feature_'+str(index);head=name+' = cq.Workplane('+plane+')'
 if p['shape']=='BOX':shape=head+'.rect('+repr(dims[0])+', '+repr(dims[1])+').extrude('+repr(dims[2])+')'
 elif p['shape']=='CYLINDER':shape=head+'.circle('+repr(dims[0]/2)+').extrude('+repr(dims[2])+')'
 else:
  r=dims[1]/2;h=max(0,(dims[0]-dims[1])/2)
  if h<1e-8:shape=head+'.circle('+repr(r)+').extrude('+repr(dims[2])+')'
  else:shape=head+f'.moveTo({-h!r}, {-r!r}).lineTo({h!r}, {-r!r}).threePointArc({[h+r,0]!r}, {[h,r]!r}).lineTo({-h!r}, {r!r}).threePointArc({[-h-r,0]!r}, {[-h,-r]!r}).close().extrude({dims[2]!r})'
 return shape+'\nresult = result.'+p['operation']+'('+name+')\n'
