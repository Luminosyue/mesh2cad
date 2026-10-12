import numpy as np, trimesh, cadquery as cq
from scipy.optimize import least_squares
from scipy.ndimage import gaussian_filter1d

def fit_polar(mesh):
 p,fi=trimesh.sample.sample_surface(mesh,160000,seed=20260920);n=mesh.face_normals[fi]
 center=mesh.bounds.mean(0)[:2];r=np.linalg.norm(p[:,:2]-center,axis=1);R=np.percentile(r,99.5)
 sel=(r>R*.85)&(np.abs(n[:,2])<.45)
 if sel.sum()>100:
  fit=least_squares(lambda a:np.linalg.norm(p[sel,:2]-a[:2],axis=1)-a[2],[*center,R],loss='soft_l1',f_scale=R*.015)
  center=fit.x[:2]
 r=np.linalg.norm(p[:,:2]-center,axis=1);bottom=np.percentile(p[:,2],.15);z=p[:,2]-bottom;R=np.percentile(r,99.5);H=np.percentile(z,99.8)
 rp,zp=.45*R,.4*H
 angle=np.arctan2(z-zp,r-rp);dist=np.hypot(r-rp,z-zp)
 t0=np.arctan2(-zp,-rp);t1=np.arctan2(H-zp,-rp)
 theta=np.linspace(t0+.018,t1-.018,161);values=[]
 for t in theta:
  ids=np.abs(angle-t)<.022
  if ids.sum()<5:ids=np.abs(angle-t)<.055
  values.append(np.percentile(dist[ids],65) if ids.any() else np.nan)
 values=np.array(values);good=np.isfinite(values);values=np.interp(theta,theta[good],values[good]);values=gaussian_filter1d(values,1.3)
 profile=np.c_[rp+values*np.cos(theta),zp+values*np.sin(theta)]
 profile=profile[profile[:,0]>.012*R][::2];profile[:,1]+=bottom
 return {'center_xy':center.tolist(),'profile':profile.tolist(),'method':'axisymmetric_spline_revolve','segments':10}

def fit(mesh):
 from shapely.geometry import Polygon,box
 p,fi=trimesh.sample.sample_surface(mesh,100000,seed=20260920);n=mesh.face_normals[fi];center=mesh.bounds.mean(0)[:2];r=np.linalg.norm(p[:,:2]-center,axis=1);R=np.percentile(r,99.5);sel=(r>R*.85)&(np.abs(n[:,2])<.45)
 if sel.sum()>100:
  ls=least_squares(lambda a:np.linalg.norm(p[sel,:2]-a[:2],axis=1)-a[2],[*center,R],loss='soft_l1',f_scale=R*.015);center=ls.x[:2]
 profiles=[]
 for theta in np.linspace(0,2*np.pi,16,endpoint=False):
  radial=np.array([np.cos(theta),np.sin(theta),0]);normal=np.array([-np.sin(theta),np.cos(theta),0]);section=mesh.section(plane_origin=[*center,0],plane_normal=normal)
  if section is None:continue
  loops=[]
  for loop in section.discrete:
   rz=np.c_[(loop-np.array([*center,0]))@radial,loop[:,2]];poly=Polygon(rz)
   if not poly.is_valid:poly=poly.buffer(0)
   poly=poly.intersection(box(0,mesh.bounds[0,2]-100,R*2,mesh.bounds[1,2]+100))
   if poly.is_empty:continue
   choices=list(poly.geoms) if hasattr(poly,'geoms') else [poly]
   loops.extend([x for x in choices if x.geom_type=='Polygon'])
  if not loops:continue
  poly=max(loops,key=lambda x:x.area);coords=np.array(poly.exterior.coords[:-1]);axis=np.where(coords[:,0]<1e-6)[0]
  if len(axis)<2:continue
  best=[]
  for start in axis:
   seq=[coords[start]]
   for k in range(1,len(coords)):
    v=coords[(start+k)%len(coords)];seq.append(v)
    if v[0]<1e-6:break
   if len(seq)>len(best):best=seq
  q=np.array(best)
  if len(q)<8:continue
  if q[0,1]>q[-1,1]:q=q[::-1]
  arc=np.r_[0,np.cumsum(np.linalg.norm(np.diff(q,axis=0),axis=1))];arc/=arc[-1];ts=np.linspace(0,1,161);profiles.append(np.c_[np.interp(ts,arc,q[:,0]),np.interp(ts,arc,q[:,1])])
 if len(profiles)<4:raise ValueError('Insufficient valid meridian sections')
 q=np.median(np.stack(profiles),axis=0);q=gaussian_filter1d(q,.8,axis=0,mode='nearest');q=q[q[:,0]>R*.015][::2]
 return {'center_xy':center.tolist(),'profile':q.tolist(),'method':'axisymmetric_spline_revolve','segments':12,'fitting':'median of 16 meridian cross-sections; spline profile with shared endpoint tangents'}

def build(data):
 points=np.array(data['profile']);n=len(points);bounds=np.unique(np.linspace(0,n-1,data.get('segments',10)+1).astype(int));z0=points[0,1];z1=points[-1,1]
 wp=cq.Workplane('XZ').moveTo(0,z0).lineTo(*points[0])
 for a,b in zip(bounds[:-1],bounds[1:]):
  def tan(k):
   t=points[min(k+1,n-1)]-points[max(k-1,0)];t/=np.linalg.norm(t);return tuple(t)
  wp=wp.spline([tuple(x) for x in points[a+1:b+1]],includeCurrent=True,tangents=[tan(a),tan(b)],scale=False)
 wp=wp.lineTo(0,z1).close();s=wp.revolve(360,(0,0),(0,1)).val();return s.translate((*data['center_xy'],0))
