"""Geometry-derived compact curve recognition. No case identifiers are used."""
from v2_common import *
from scipy.optimize import least_squares
from scipy.interpolate import splprep,splev
from shapely.geometry import Polygon,LineString
from scipy.spatial import cKDTree

def resample(p,n=160):
 p=np.asarray(p,float)
 if np.linalg.norm(p[0]-p[-1])>1e-10:p=np.vstack([p,p[0]])
 t=np.r_[0,np.cumsum(np.linalg.norm(np.diff(p,axis=0),axis=1))];mask=np.r_[True,np.diff(t)>1e-12];t=t[mask];p=p[mask];s=np.linspace(0,t[-1],n,endpoint=False);return np.c_[np.interp(s,t,p[:,0]),np.interp(s,t,p[:,1])]
def circle_fit(points,seed=0):
 p=resample(points);scale=max(np.ptp(p,axis=0));rng=np.random.default_rng(seed)
 def solve(q):
  a=np.c_[2*q,np.ones(len(q))];x=np.linalg.lstsq(a,np.sum(q*q,axis=1),rcond=None)[0];return np.r_[x[:2],np.sqrt(max(1e-16,x[2]+sum(x[:2]**2)))]
 initial=solve(p);candidates=[initial]
 for _ in range(50):
  try:candidates.append(solve(p[rng.choice(len(p),3,replace=False)]))
  except Exception:pass
 start=min(candidates,key=lambda c:np.median(abs(np.linalg.norm(p-c[:2],axis=1)-c[2])))
 opt=least_squares(lambda x:np.linalg.norm(p-x[:2],axis=1)-x[2],start,loss='soft_l1',f_scale=scale*.003,max_nfev=80).x
 err=abs(np.linalg.norm(p-opt[:2],axis=1)-opt[2]);angles=np.sort(np.mod(np.arctan2(p[:,1]-opt[1],p[:,0]-opt[0]),2*np.pi));coverage=1-max(np.diff(np.r_[angles,angles[0]+2*np.pi]))/(2*np.pi)
 return {'type':'CIRCLE','center':opt[:2].tolist(),'radius':float(opt[2]),'mean_residual':float(err.mean()),'p95_residual':float(np.quantile(err,.95)),'relative_p95':float(np.quantile(err,.95)/scale),'angular_coverage':float(coverage),'methods':['least_squares','fixed_seed_RANSAC_50','robust_geometric_refinement']}
def ellipse_fit(points):
 p=resample(points);center=p.mean(0);_,_,v=np.linalg.svd(p-center,full_matrices=False);q=(p-center)@v.T;r=np.ptp(q,axis=0)/2;theta=np.arctan2(v[0,1],v[0,0]);scale=max(np.ptp(p,axis=0))
 def residual(x):
  c=np.cos(x[4]);s=np.sin(x[4]);R=np.array([[c,s],[-s,c]]);q=(p-x[:2])@R.T;a,b=np.exp(x[2:4]);f=(q[:,0]/a)**2+(q[:,1]/b)**2-1;g=2*np.sqrt((q[:,0]/a**2)**2+(q[:,1]/b**2)**2);return f/np.maximum(g,1e-9)
 x=least_squares(residual,np.r_[center,np.log(np.maximum(r,scale*.01)),theta],loss='soft_l1',f_scale=scale*.003,max_nfev=100).x;a,b=np.exp(x[2:4]);err=abs(residual(x))
 return {'type':'ELLIPSE','center':x[:2].tolist(),'major_radius':float(a),'minor_radius':float(b),'orientation_degrees':float(np.rad2deg(x[4])),'mean_residual':float(err.mean()),'relative_p95':float(np.quantile(err,.95)/scale),'axis_ratio':float(max(a,b)/min(a,b))}
def rounded_rect_fit(points):
 p=resample(points);poly=Polygon(points);rect=np.asarray(poly.minimum_rotated_rectangle.exterior.coords)[:-1];vec=rect[1]-rect[0];theta=np.arctan2(vec[1],vec[0]);center=rect.mean(0);c=np.cos(theta);s=np.sin(theta);q=(p-center)@np.array([[c,-s],[s,c]]);half=np.ptp(q,axis=0)/2;scale=max(np.ptp(p,axis=0))
 def unpack(x):return x[:2],np.exp(x[2:4]),x[4],1/(1+np.exp(-x[5]))
 def residual(x):
  center,half,a,rfrac=unpack(x);r=min(half)*rfrac;R=np.array([[np.cos(a),-np.sin(a)],[np.sin(a),np.cos(a)]]);q=abs((p-center)@R)-half+r;return np.linalg.norm(np.maximum(q,0),axis=1)+np.minimum(np.max(q,axis=1),0)-r
 x=least_squares(residual,np.r_[center,np.log(np.maximum(half,1e-6)),theta,-1.5],loss='soft_l1',f_scale=scale*.002,max_nfev=90).x;cc,hh,aa,rf=unpack(x);err=abs(residual(x));rad=float(min(hh)*rf)
 return {'type':'ROUNDED_RECT','center':cc.tolist(),'half_extents':hh.tolist(),'orientation':float(aa),'radius':rad,'relative_p95':float(np.quantile(err,.95)/scale),'slot_like':bool(rad/min(hh)>.95)}
def arc_segment(q,tol):
 if len(q)<4:return None
 a=q[0];b=q[len(q)//2];c=q[-1];mat=2*np.array([b-a,c-a]);rhs=np.array([sum(b*b)-sum(a*a),sum(c*c)-sum(a*a)])
 if abs(np.linalg.det(mat))<1e-12:return None
 center=np.linalg.solve(mat,rhs);rad=np.linalg.norm(a-center);err=abs(np.linalg.norm(q-center,axis=1)-rad);ang=np.unwrap(np.arctan2(q[:,1]-center[1],q[:,0]-center[0]));span=ang[-1]-ang[0]
 if max(err)>tol or abs(span)>np.pi*1.8 or abs(span)<.10 or np.any(np.diff(ang)*np.sign(span)<-1e-3):return None
 mid=center+rad*np.array([np.cos((ang[0]+ang[-1])/2),np.sin((ang[0]+ang[-1])/2)])
 return {'op':'ARC','mid':mid.tolist(),'end':c.tolist(),'center':center.tolist(),'radius':float(rad),'angular_span':float(span),'max_residual':float(max(err))}
def composite_fit(points,tol_relative=.004):
 p=np.asarray(points,float);scale=max(np.ptp(p,axis=0));p=np.asarray(Polygon(p).simplify(scale*.0005,preserve_topology=True).exterior.coords)[:-1]
 if len(p)>96:p=resample(p,96)
 v=np.roll(p,-1,axis=0)-p;v/=np.maximum(np.linalg.norm(v,axis=1,keepdims=True),1e-12);turn=np.arccos(np.clip((v*np.roll(v,1,axis=0)).sum(1),-1,1));p=np.roll(p,-int(np.argmax(turn)),axis=0);q=np.vstack([p,p[0]]);n=len(p);cost=[float('inf')]*(n+1);paths=[None]*(n+1);cost[0]=0;paths[0]=[];tol=scale*tol_relative
 for i in range(n):
  if paths[i] is None:continue
  for j in range(i+1,n+1):
   seg=q[i:j+1];vec=seg[-1]-seg[0];ln=np.linalg.norm(vec)
   if ln<1e-12:continue
   perp=abs(np.cross(vec,seg-seg[0]))/ln;proj=(seg-seg[0])@vec/(ln*ln);op=None
   if max(perp)<=tol and proj.min()>=-.01 and proj.max()<=1.01:op={'op':'LINE','end':seg[-1].tolist(),'max_residual':float(max(perp))};weight=1
   else:op=arc_segment(seg,tol);weight=1.5
   if op is not None and cost[i]+weight<cost[j]:cost[j]=cost[i]+weight;paths[j]=paths[i]+[op]
 path=paths[n]
 if path is None or len(path)>32 or not any(x['op']=='ARC' for x in path):return None
 # Report tangent jumps; preserve corners rather than silently blending them.
 tangents=[]
 start=q[0]
 for s in path:
  end=np.array(s['end'])
  if s['op']=='LINE':a=b=(end-start)/np.linalg.norm(end-start)
  else:
   sign=np.sign(s['angular_span']);a=(start-np.array(s['center']))*sign;b=(end-np.array(s['center']))*sign;a=np.array([-a[1],a[0]])/s['radius'];b=np.array([-b[1],b[0]])/s['radius']
  tangents.append((a,b));start=end
 jumps=[float(np.rad2deg(np.arccos(np.clip(tangents[i-1][1]@tangents[i][0],-1,1)))) for i in range(len(path))]
 return {'type':'COMPOSITE_PROFILE','start':q[0].tolist(),'segments':path,'tangent_jumps_degrees':jumps,'smooth_junction_n':sum(x<10 for x in jumps),'retained_corner_n':sum(x>=10 for x in jumps),'relative_tolerance':tol_relative}
def smooth_controls(points,n=16):
 p=resample(points,160);closed=np.vstack([p,p[0]]);tck,_=splprep(closed.T,s=(max(np.ptp(p,axis=0))*.0015)**2*len(p),per=True);q=np.array(splev(np.linspace(0,1,n,endpoint=False),tck)).T;return q.tolist()
def recognize(points,seed=0):
 p=np.asarray(points);out={'point_n':len(p),'scale':float(max(np.ptp(p,axis=0))),'fits':[]}
 for fn in [lambda:circle_fit(p,seed),lambda:ellipse_fit(p),lambda:rounded_rect_fit(p),lambda:composite_fit(p)]:
  try:
   r=fn()
   if r:out['fits'].append(r)
  except Exception as e:out.setdefault('errors',[]).append(str(e))
 return out
def choose(rec,mode):
 fits={x['type']:x for x in rec['fits']}
 c=fits.get('CIRCLE');e=fits.get('ELLIPSE');rr=fits.get('ROUNDED_RECT');comp=fits.get('COMPOSITE_PROFILE')
 if c and c['radius']>0 and c['relative_p95']<.006 and c['angular_coverage']>.94:return c
 if e and e['relative_p95']<.006 and e['axis_ratio']>1.025 and e['axis_ratio']<25:return e
 if rr and rr['relative_p95']<.005 and rr['radius']/min(rr['half_extents'])>.03:return rr
 if comp and len(comp['segments'])<rec['point_n']*.8:return comp
 return {'type':'BSPLINE'} if mode=='spline' else {'type':'POLYLINE'}
def profile_expression(receiver,points,rep):
 typ=rep['type'];p=np.asarray(points,float)
 if typ=='CIRCLE':return receiver+f'.moveTo({rep["center"][0]!r},{rep["center"][1]!r}).circle({rep["radius"]!r})'
 if typ=='ELLIPSE':return receiver+f'.moveTo({rep["center"][0]!r},{rep["center"][1]!r}).ellipse({rep["major_radius"]!r},{rep["minor_radius"]!r},rotation_angle={rep["orientation_degrees"]!r})'
 if typ=='ROUNDED_RECT':
  hx,hy=rep['half_extents'];rad=rep['radius'];corners=[(hx-rad,hy-rad,0),( -hx+rad,hy-rad,np.pi/2),(-hx+rad,-hy+rad,np.pi),(hx-rad,-hy+rad,np.pi*1.5)];ang=rep['orientation'];R=np.array([[np.cos(ang),-np.sin(ang)],[np.sin(ang),np.cos(ang)]]);center=np.array(rep['center'])
  def cv(q):return (np.asarray(q)@R.T+center).tolist()
  start=cv([hx,hy-rad]);expr=receiver+f'.moveTo({start[0]!r},{start[1]!r})'
  for i,(cx,cy,a) in enumerate(corners):
   a0=cv([cx+rad*np.cos(a),cy+rad*np.sin(a)]);mid=cv([cx+rad*np.cos(a+np.pi/4),cy+rad*np.sin(a+np.pi/4)]);end=cv([cx+rad*np.cos(a+np.pi/2),cy+rad*np.sin(a+np.pi/2)])
   if i:expr+=f'.lineTo({a0[0]!r},{a0[1]!r})'
   expr+=f'.threePointArc({mid!r},{end!r})'
  return expr+'.close()'
 if typ=='COMPOSITE_PROFILE':
  start=rep['start'];expr=receiver+f'.moveTo({start[0]!r},{start[1]!r})'
  for seg in rep['segments']:
   if seg['op']=='LINE':expr+=f'.lineTo({seg["end"][0]!r},{seg["end"][1]!r})'
   else:expr+=f'.threePointArc({seg["mid"]!r},{seg["end"]!r})'
  return expr+'.close()'
 if typ=='BSPLINE':return receiver+f'.spline({smooth_controls(p,16)!r},periodic=True,makeWire=True)'
 return receiver+f'.polyline({p.tolist()!r}).close()'
def upgrade_code(code,mode='analytic',seed=0):
 records=[]
 class Edit(ast.NodeTransformer):
  def visit_Call(self,node):
   if isinstance(node.func,ast.Attribute) and node.func.attr=='close' and isinstance(node.func.value,ast.Call):
    inner=node.func.value
    if isinstance(inner.func,ast.Attribute) and inner.func.attr=='polyline':
     p=ast.literal_eval(inner.args[0]);rec=recognize(p,seed+len(records));rep=choose(rec,mode)
     if mode=='spline':
      v=np.diff(np.vstack([p,p[0]]),axis=0);v/=np.maximum(np.linalg.norm(v,axis=1,keepdims=True),1e-10);turn=np.arccos(np.clip((v*np.roll(v,1,axis=0)).sum(1),-1,1))
      if max(turn)>np.deg2rad(95) or len(p)<8:rep=choose(rec,'analytic')
     records.append({'recognition':rec,'selected':rep})
     return ast.parse(profile_expression(ast.unparse(inner.func.value),p,rep),mode='eval').body
   return self.generic_visit(node)
 tree=Edit().visit(ast.parse(code));ast.fix_missing_locations(tree);return ast.unparse(tree)+'\n',records
