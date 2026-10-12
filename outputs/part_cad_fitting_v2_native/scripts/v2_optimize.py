from v2_common import *
import trimesh
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
from scipy.ndimage import affine_transform
from fit_logic import voxel_occupancy
def transform_parameters(x,kind):
 x=np.asarray(x)
 if kind=='cylinder':sc=np.exp([x[0],x[0],x[1]]);delta=x[2:5];rot=x[5:8]
 elif kind=='revolve':sc=np.exp([x[0],x[1],x[0]]);delta=x[2:5];rot=x[5:8]
 elif kind=='sphere':sc=np.exp([x[0]]*3);delta=x[1:4];rot=np.zeros(3)
 else:sc=np.exp(x[:3]);delta=x[3:6];rot=x[6:9]
 return sc,delta,Rotation.from_rotvec(rot).as_matrix()
def matrix(x,kind,B,center):
 scales,delta,R=transform_parameters(x,kind);A=R@B@np.diag(scales)@B.T;b=center-A@center+delta;return A,b
def rewrite(code,x,kind,center):
 B,_=first_plane(code);sc,delta,R=transform_parameters(x,kind);A,b=matrix(x,kind,B,np.asarray(center))
 def literal(v):return ast.parse(repr(np.asarray(v).tolist()),mode='eval').body
 class Edit(ast.NodeTransformer):
  def visit_Call(self,n):
   n=self.generic_visit(n)
   if not isinstance(n.func,ast.Attribute):return n
   k=n.func.attr
   if k=='Plane':
    for kw in n.keywords:
     if kw.arg=='origin':kw.value=literal(A@np.array(ast.literal_eval(kw.value))+b)
     elif kw.arg in ['xDir','normal']:kw.value=literal(R@np.array(ast.literal_eval(kw.value)))
   elif k=='polyline':n.args[0]=literal(np.array(ast.literal_eval(n.args[0]))*sc[:2])
   elif k in ['circle','sphere']:n.args[0]=literal(float(ast.literal_eval(n.args[0]))*sc[0])
   elif k=='extrude':n.args[0]=literal(float(ast.literal_eval(n.args[0]))*sc[2])
   elif k=='box':
    for i in range(3):n.args[i]=literal(float(ast.literal_eval(n.args[i]))*sc[i])
   elif k=='workplane':
    for kw in n.keywords:
     if kw.arg=='offset':kw.value=literal(float(ast.literal_eval(kw.value))*sc[2])
   return n
 t=Edit().visit(ast.parse(code));ast.fix_missing_locations(t);return ast.unparse(t)+'\n'
class Proxy:
 def __init__(self,m,cm,code,kind,points,seed):
  self.m=m;self.cm=cm;self.kind=kind;self.B,_=first_plane(code);self.center=cm.bounds.mean(0);self.a=points[::5];self.b=trimesh.sample.sample_surface(cm,20000,seed=seed+1)[0][::5];self.tree=cKDTree(self.a);self.diag=np.linalg.norm(m.extents);self.origin=m.bounds[0]-.15;self.pitch=max(m.extents)/(64-4);self.shape=tuple(np.ceil((m.bounds[1]+.15-self.origin)/self.pitch).astype(int)+1);self.so=voxel_occupancy(m,self.origin,self.pitch,self.shape);self.co=voxel_occupancy(cm,self.origin,self.pitch,self.shape);self.cache={};self.trace=[]
 def evaluate(self,x):
  key=tuple(np.round(x,10))
  if key in self.cache:return self.cache[key]
  A,b=matrix(x,self.kind,self.B,self.center);v=self.cm.vertices@A.T+b;p=self.b@A.T+b;da=self.tree.query(p,workers=1)[0];db=cKDTree(p).query(self.a,workers=1)[0];ncd=float((da.mean()+db.mean())*.5/self.diag)
  # Exact transformed tessellation centroid, not affine-transforming a surface centroid.
  tri=v[self.cm.faces];area=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1);cent=(tri.mean(axis=1)*area[:,None]).sum(0)/area.sum();ce=float(np.linalg.norm(cent-self.m.centroid));lo=v.min(0);hi=v.max(0);be=max(float(np.max(np.abs(hi-lo-self.m.extents))),float(np.linalg.norm((hi+lo)/2-self.m.bounds.mean(0))))
  inv=np.linalg.inv(A);offset=(inv@(self.origin-b)-self.origin)/self.pitch;occ=affine_transform(self.co.astype(np.uint8),inv,offset=offset,output_shape=self.shape,order=0,prefilter=False)>0;u=np.logical_or(self.so,occ).sum();iou=float(np.logical_and(self.so,occ).sum()/max(u,1));base=10*ncd+1-iou+2*ce+be
  r={'parameters':np.asarray(x).tolist(),'proxy_score':base,'proxy_iou64_warped':iou,'proxy_ncd_fixed_subset':ncd,'centroid_error':ce,'bbox_error':be};self.cache[key]=r;self.trace.append(r);return r
 def objective(self,x,mode):
  r=self.evaluate(x);return r['proxy_score']+(8*max(0,r['centroid_error']-.018)+5*max(0,r['bbox_error']-.028) if mode=='strict' else 0)
def proposals(m,cm,code,kind,points,seed):
 proxy=Proxy(m,cm,code,kind,points,seed);n=8 if kind in ['cylinder','revolve'] else 4 if kind=='sphere' else 9;ns=2 if n==8 else 1 if n==4 else 3;x0=np.zeros(n);lower=np.r_[[-.20]*ns,[-.08]*3,[-.06]*(n-ns-3)];upper=-lower
 delta=m.centroid-cm.centroid;aligned=x0.copy();aligned[ns:ns+3]=np.clip(delta,-.08,.08)
 outputs=[('centroid_alignment',aligned.copy())]
 for mode,start in [('balanced',x0),('strict',aligned)]:
  x=start.copy();best=proxy.objective(x,mode)
  for scale in [1.,.4,.15]:
   steps=np.r_[[.035*scale]*ns,[.006*scale]*3,[.01*scale]*(n-ns-3)]
   for j in range(n):
    for sign in [-1,1]:
     y=x.copy();y[j]=np.clip(y[j]+sign*steps[j],lower[j],upper[j]);val=proxy.objective(y,mode)
     if val<best-1e-8:x=y;best=val
  outputs.append(('coordinate_descent_'+mode,x.copy()))
 ranked=sorted(proxy.trace,key=lambda r:r['proxy_score'])
 for rec in ranked:
  x=np.array(rec['parameters'])
  if all(np.linalg.norm(x-y)>.008 for _,y in outputs):outputs.append(('local_search_alternative',x))
  if len(outputs)>=5:break
 return [(name,rewrite(code,x,kind,proxy.center),{'numeric_parameter_vector':x.tolist(),'scale_translation_rotation':True,'construction_structure_unchanged':True}) for name,x in outputs],{'initial_parameters':x0.tolist(),'initial_score':proxy.evaluate(x0)['proxy_score'],'best_parameters':ranked[0]['parameters'],'best_score':ranked[0]['proxy_score'],'optimization_steps':len(proxy.trace),'steps':proxy.trace,'objective_note':'Proxy only: fixed-grid warped voxel occupancy plus frozen point subsets. Final acceptance always uses regenerated native CQ -> STEP -> reload and unchanged evaluator.'}
