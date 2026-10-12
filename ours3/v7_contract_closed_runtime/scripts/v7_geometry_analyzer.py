#!/usr/bin/env python3
import json,hashlib,math
from pathlib import Path
import numpy as np,trimesh

def dump(p,x):p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2)+'\n')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frame(direction):
 d=np.asarray(direction,float);d/=np.linalg.norm(d);ref=np.array([0.,0.,1.]) if abs(d[2])<.9 else np.array([0.,1.,0.]);e1=np.cross(d,ref);e1/=np.linalg.norm(e1);return d,e1,np.cross(d,e1)
def resample(loop,count=24):
 p=np.asarray(loop,float)
 if np.linalg.norm(p[0]-p[-1])>1e-8:p=np.vstack([p,p[0]])
 seg=np.linalg.norm(np.diff(p,axis=0),axis=1);cum=np.r_[0,np.cumsum(seg)];out=[]
 for t in np.linspace(0,cum[-1],count,endpoint=False):
  i=min(np.searchsorted(cum,t,side='right')-1,len(seg)-1);a=(t-cum[i])/max(seg[i],1e-12);out.append(p[i]*(1-a)+p[i+1]*a)
 return np.asarray(out)
def analyze(mesh_path,part_id,axis_direction,axis_origin=None,station_count=12,profile_points=24):
 mesh=trimesh.load(mesh_path,force='mesh',process=False);d,e1,e2=frame(axis_direction);origin=np.asarray(axis_origin if axis_origin is not None else mesh.centroid,float);proj=(np.asarray(mesh.vertices)-origin)@d;lo,hi=float(proj.min()),float(proj.max());span=hi-lo;ts=np.linspace(.03,.97,station_count);profiles=[];fail=[]
 for i,t in enumerate(ts):
  po=origin+d*(lo+t*span);sec=mesh.section(plane_origin=po,plane_normal=d);loops=[] if sec is None else [np.asarray(x,float) for x in sec.discrete if len(x)>=4 and np.linalg.norm(x[0]-x[-1])<max(span*1e-4,1e-7)]
  if not loops:fail.append({'station_id':f'S{i:02d}','status':'PROFILE_INVALID'});continue
  loop=max(loops,key=lambda x:np.linalg.norm(np.diff(x,axis=0),axis=1).sum());pts=resample(loop,profile_points);uv=np.c_[(pts-po)@e1,(pts-po)@e2];area=abs(.5*np.sum(uv[:,0]*np.roll(uv[:,1],-1)-uv[:,1]*np.roll(uv[:,0],-1)));per=float(np.linalg.norm(np.diff(np.vstack([pts,pts[0]]),axis=0),axis=1).sum())
  profiles.append({'station_id':f'S{i:02d}','t':float(t),'plane_origin':po.tolist(),'plane_normal':d.tolist(),'closed':True,'points_3d':pts.tolist(),'points_2d':uv.tolist(),'area':float(area),'perimeter':per,'source':'HIGH_POLY_MESH_SECTION'})
 analysis={'schema':'GeometryAnalyzerV7','part_id':part_id,'source_mesh':str(mesh_path),'source_mesh_sha256':sha(mesh_path),'bbox':mesh.bounds.tolist(),'dimensions':mesh.extents.tolist(),'axis':{'origin':origin.tolist(),'direction':d.tolist()},'span':span,'stations':[p['t'] for p in profiles],'profiles':profiles,'PROFILE_COUNT':len(profiles),'PROFILE_FAILURES':fail,'PROFILE_CLOSED_RATE':len(profiles)/station_count if station_count else 0,'GEOMETRY_ANALYZER_PROFILES_ARE_REAL_SECTIONS':True}
 return analysis
