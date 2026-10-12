from v2_common import *
import trimesh
from shapely.geometry import Polygon,box
from shapely.ops import triangulate
from shapely.geometry.polygon import orient
from scipy.spatial import cKDTree
from fit_logic import basis_for_axis,voxel_occupancy
from metric_runtime import plane
from cad_emit import emit_profiles
from v2_optimize import proposals

def polygons(mesh,origin,normal,u,v):
 section=mesh.section(plane_origin=origin,plane_normal=normal)
 if section is None:return []
 rings=[]
 for pts in section.discrete:
  if len(pts)<4 or np.linalg.norm(pts[0]-pts[-1])>1e-6:continue
  q=(pts-origin)@np.column_stack([u,v]);p=Polygon(q)
  if p.is_valid and p.area>1e-10:rings.append(p)
 rings.sort(key=lambda p:-p.area);depth=[sum(q.contains(p.representative_point()) for q in rings[:i]) for i,p in enumerate(rings)];out=[]
 for i,p in enumerate(rings):
  if depth[i]%2:continue
  holes=[list(q.exterior.coords) for j,q in enumerate(rings) if depth[j]==depth[i]+1 and p.contains(q.representative_point())]
  r=Polygon(p.exterior.coords,holes)
  if r.is_valid:out.append(orient(r,sign=1))
 return out

def simplify(ps,budget):
 if not ps:raise ValueError('No supported closed section')
 scale=max(max(np.ptp(np.asarray(p.exterior.coords),axis=0)) for p in ps)
 for tol in [0,.0002,.0005,.001,.002,.004,.008,.015,.025]:
  qs=[p.simplify(scale*tol,preserve_topology=True) for p in ps]
  n=sum(len(p.exterior.coords)-1+sum(len(h.coords)-1 for h in p.interiors) for p in qs)
  if n<=budget and all(p.is_valid and p.area>1e-10 for p in qs):return qs
 raise ValueError('Measured section exceeds sketch budget')

def profile(p):return {'outer':np.asarray(p.exterior.coords)[:-1].tolist(),'holes':[np.asarray(h.coords)[:-1].tolist() for h in p.interiors]}

def capped_proxy(ps,B,center,zs,tracks=None):
 vertices=[];faces=[]
 def triangle(a,b,c):
  j=len(vertices);vertices.extend([a,b,c]);faces.append([j,j+1,j+2])
 for j,p in enumerate(ps):
  rings=[np.asarray(p.exterior.coords)[:-1]]+[np.asarray(h.coords)[:-1] for h in p.interiors]
  for ri,ring in enumerate(rings):
   levels=tracks[ri] if tracks is not None else [ring for z in zs]
   for k in range(len(zs)-1):
    r0=levels[k];r1=levels[k+1]
    for i in range(len(r0)):
     t=(i+1)%len(r0);a=np.r_[r0[i],zs[k]];b=np.r_[r0[t],zs[k]];c=np.r_[r1[t],zs[k+1]];d=np.r_[r1[i],zs[k+1]];triangle(a,b,c);triangle(a,c,d)
  for k in [0,len(zs)-1]:
   poly=Polygon(tracks[0][k], [t[k] for t in tracks[1:]]) if tracks is not None else p
   for tri in triangulate(poly):
    if not poly.covers(tri):continue
    pts=np.asarray(tri.exterior.coords)[:3];triangle(*[np.r_[x,zs[k]] for x in pts])
 if not vertices:raise ValueError('Empty proxy surface')
 return trimesh.Trimesh(vertices=np.asarray(vertices)@B.T+center,faces=faces,process=False)

def resample_ring(r,n):
 pts=np.asarray(r.coords);steps=np.linalg.norm(np.diff(pts,axis=0),axis=1);cum=np.r_[0,np.cumsum(steps)];t=np.linspace(0,cum[-1],n,endpoint=False);x=np.c_[np.interp(t,cum,pts[:,0]),np.interp(t,cum,pts[:,1])];return np.roll(x,-np.argmax(x[:,0]),axis=0)

def extrusion(mesh,B,center,section,zmin,zmax):
 ps=simplify(section,96);spec={'basis':B.tolist(),'center':center.tolist(),'zmin':float(zmin),'zmax':float(zmax),'profiles':[profile(p) for p in ps]}
 return emit_profiles(spec),spec,capped_proxy(ps,B,center,[zmin,zmax])

def loft(mesh,B,center,sections,zmin,zmax):
 if any(len(s)!=1 for s in sections):raise ValueError('Loft needs one observed outer component; no components dropped')
 hole_n=len(sections[0][0].interiors)
 if hole_n>2 or any(len(s[0].interiors)!=hole_n for s in sections):raise ValueError('Section topology changes')
 per=96//(3*(1+hole_n));tracks=[]
 for ri in range(1+hole_n):
  track=[]
  for s in sections:
   p=orient(s[0],sign=1);ring=p.exterior if ri==0 else sorted(p.interiors,key=lambda x:-Polygon(x).area)[ri-1];pts=resample_ring(ring,per)
   if track:pts=min((np.roll(pts,k,axis=0) for k in range(per)),key=lambda x:np.mean((x-track[-1])**2))
   track.append(pts)
  tracks.append(track)
 zs=[float(zmin),float((zmin+zmax)/2),float(zmax)];lines=['import cadquery as cq','plane = '+plane(center+B[:,2]*zs[0],B)]
 for ri,track in enumerate(tracks):
  expr=f'cq.Workplane(plane).polyline({track[0].tolist()!r}).close()'
  for k in [1,2]:expr+=f'.workplane(offset={zs[k]-zs[k-1]!r}).polyline({track[k].tolist()!r}).close()'
  lines.append(f'p{ri} = '+expr+'.loft(ruled=True)')
 lines.append('result = p0'+''.join(f'.cut(p{k})' for k in range(1,len(tracks))))
 spec={'basis':B.tolist(),'center':center.tolist(),'levels':zs,'tracks':[[x.tolist() for x in t] for t in tracks],'end_sections_extrapolated_from_fraction':.03,'holes_preserved':hole_n}
 return '\n'.join(lines)+'\n',spec,capped_proxy([sections[0][0]],B,center,zs,tracks)

def revolve(mesh,axis,center,angle):
 B=basis_for_axis(axis);u=B[:,0]*np.cos(angle)+B[:,1]*np.sin(angle);v=np.cross(axis,u);ps=polygons(mesh,center,v,u,axis);q=(mesh.vertices-center)@np.c_[u,axis];extent=max(np.ptp(q,axis=0));cut=box(0,q[:,1].min()-extent,extent*2,q[:,1].max()+extent);clipped=[]
 for p in ps:
  x=p.intersection(cut)
  clipped.extend([x] if x.geom_type=='Polygon' else [g for g in getattr(x,'geoms',[]) if g.geom_type=='Polygon'])
 ps=simplify([p for p in clipped if p.area>1e-10],96)
 if len(ps)+sum(len(p.interiors) for p in ps)>8 or len(ps)-1+sum(len(p.interiors) for p in ps)>6:raise ValueError('Revolve topology exceeds budget')
 K=np.c_[u,axis,-v];lines=['import cadquery as cq','plane = '+plane(center,K)];verts=[];faces=[]
 for j,p in enumerate(ps):
  rings=[p.exterior]+list(p.interiors)
  for k,ring in enumerate(rings):
   pts=np.asarray(ring.coords)[:-1];lines.append(f'p{j}_{k} = cq.Workplane(plane).polyline({pts.tolist()!r}).close().revolve(360,(0,0),(0,1))')
   theta=np.linspace(0,2*np.pi,64,endpoint=False);start=len(verts)
   for r,z in pts:verts.extend(center+z*axis+r*(np.cos(theta)[:,None]*u+np.sin(theta)[:,None]*v))
   for i in range(len(pts)):
    for t in range(64):
     a=start+i*64+t;b=start+i*64+(t+1)%64;c=start+((i+1)%len(pts))*64+(t+1)%64;d=start+((i+1)%len(pts))*64+t;faces.extend([[a,b,c],[a,c,d]])
  lines.append(f'b{j} = p{j}_0'+''.join(f'.cut(p{j}_{k})' for k in range(1,len(rings))))
 lines.append('result = b0'+''.join(f'.union(b{j})' for j in range(1,len(ps))))
 return '\n'.join(lines)+'\n',{'axis':axis.tolist(),'center':center.tolist(),'section_angle':angle,'profiles':[profile(p) for p in ps],'measured_inner_profile_preserved':True},trimesh.Trimesh(vertices=verts,faces=faces,process=False)

class Ranker:
 def __init__(self,m,points,seed):
  self.m=m;self.points=points[::5];self.tree=cKDTree(self.points);self.seed=seed;self.diag=np.linalg.norm(m.extents);self.pitch=max(m.extents)/60;self.origin=m.bounds[0]-.1;self.shape=tuple(np.ceil((m.bounds[1]+.1-self.origin)/self.pitch).astype(int)+1);self.occ=voxel_occupancy(m,self.origin,self.pitch,self.shape)
 def score(self,proxy):
  p=trimesh.sample.sample_surface(proxy,4000,seed=self.seed+1)[0];ncd=(self.tree.query(p)[0].mean()+cKDTree(p).query(self.points)[0].mean())*.5/self.diag;occ=voxel_occupancy(proxy,self.origin,self.pitch,self.shape);iou=np.logical_and(self.occ,occ).sum()/max(np.logical_or(self.occ,occ).sum(),1);cent=np.linalg.norm(proxy.centroid-self.m.centroid);bbox=max(np.max(np.abs(proxy.extents-self.m.extents)),np.linalg.norm(proxy.bounds.mean(0)-self.m.bounds.mean(0)));return float(10*ncd+1-iou+2*cent+bbox)

def generate(row,m,cm,basecode,features,points):
 errors=[];out=[];center=m.bounds.mean(0);ranker=Ranker(m,points,row['seed']);axes=[]
 raw=[np.asarray(x['axis']) for x in features['cylinder_fits']]+[np.asarray(x['normal']) for x in features['normal_clusters'][:4]]+[np.asarray(x) for x in features['pca_axes']]
 for axis in raw:
  if np.linalg.norm(axis)<1e-8:continue
  axis=axis/np.linalg.norm(axis)
  if not any(abs(np.dot(axis,b))>.995 for b in axes):axes.append(axis)
  if len(axes)==5:break
 def add(kind,family,fn,*args):
  try:
   code,param,proxy=fn(*args);s=ranker.score(proxy);out.append({'kind':kind,'family':family,'code':code,'parameters':param,'proxy_score':s})
  except Exception as e:errors.append({'method':kind,'error':str(e)})
 for axis in axes:
  B=basis_for_axis(axis);q=(m.vertices-center)@B;lo=float(q[:,2].min());hi=float(q[:,2].max());sections=[polygons(m,center+B[:,2]*(lo+f*(hi-lo)),B[:,2],B[:,0],B[:,1]) for f in [.03,.5,.97]]
  if sections[1]:add('measured_mid_section_extrusion','B_EXTRUSION',extrusion,m,B,center,sections[1],lo,hi)
  if all(sections):add('topology_preserving_section_loft','B_EXTRUSION',loft,m,B,center,sections,lo,hi)
 # Axes with measured cylinder evidence use a fitted center, preserving inner section boundaries.
 for fit in features['cylinder_fits'][:3]:
  if 'radius' not in fit:continue
  a=np.asarray(fit['axis']);B=np.asarray(fit['basis']);c=B@np.r_[fit['center_xy'],(fit['zmin']+fit['zmax'])/2]
  for angle in [0.,np.pi/2]:add('measured_inner_outer_revolve','C_REVOLVE',revolve,m,a,c,float(angle))
 # Continue local refinement from the actual V2 winner, not the old V1 candidate.
 attrs=[n.func.attr for n in ast.walk(ast.parse(basecode)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
 kind='revolve' if 'revolve' in attrs else 'sphere' if 'sphere' in attrs else 'cylinder' if attrs.count('circle')==1 and attrs.count('extrude')==1 and 'polyline' not in attrs else 'extrusion'
 try:
  pp,trace=proposals(m,cm,basecode,kind,points,row['seed']);best=[p for p in pp if p[0]=='coordinate_descent_strict'];out.extend({'kind':'v2_winner_'+name,'family':row.get('v2_family','V2_FAMILY'),'code':code,'parameters':param,'proxy_score':trace['best_score']} for name,code,param in best)
 except Exception as e:trace={};errors.append({'method':'v2_local_optimization','error':str(e)})
 # Reserve one V2-winner refinement; distribute remaining slots across construction methods.
 local=[x for x in out if x['kind'].startswith('v2_winner')];ordered=sorted([x for x in out if not x['kind'].startswith('v2_winner')],key=lambda x:x['proxy_score']);chosen=local[:1];counts={};seen={basecode.strip()}
 for cap in [2,7]:
  for x in ordered:
   if len(chosen)>=7:break
   if x['code'].strip() in seen or counts.get(x['kind'],0)>=cap:continue
   chosen.append(x);seen.add(x['code'].strip());counts[x['kind']]=counts.get(x['kind'],0)+1
 return chosen,{'proposal_n':len(out),'selected_n':len(chosen),'geometry_proposals':[dict(x,code_sha256=__import__('hashlib').sha256(x['code'].encode()).hexdigest()) for x in out],'errors':errors,'local_search':trace,'proxy_acceptance':False}
