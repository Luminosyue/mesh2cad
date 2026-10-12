from v2_common import *
import copy
import trimesh
from shapely.geometry import Polygon
from metric_runtime import plane
from cad_emit import emit_profiles
from fit_logic import basis_for_axis
def fit_cylinder(f):
 B=np.array(f['basis']);h=f['zmax']-f['zmin'];origin=B@np.r_[f['center_xy'],f['zmin']];radius=f['radius']
 code='import cadquery as cq\nplane = '+plane(origin,B)+f'\nresult = cq.Workplane(plane).circle({radius!r}).extrude({h!r})\n';return code,dict(f)
def radial_refit(m,params,quantile):
 B=basis_for_axis(np.array(params['axis']));xy=np.array(params['circle_center']);q=m.vertices@B;z=q[:,2];rad=np.linalg.norm(q[:,:2]-xy,axis=1);lo=float(z.min());hi=float(z.max());cuts=np.linspace(lo,hi,25);profile=[]
 for i in range(24):
  mask=(z>=cuts[i])&(z<=cuts[i+1])
  if mask.sum()>2:profile.append([float(np.quantile(rad[mask],quantile)),float((cuts[i]+cuts[i+1])/2)])
 if len(profile)<4:raise ValueError('insufficient axial bins')
 profile[0][1]=lo;profile[-1][1]=hi;poly=[[0.,lo]]+profile+[[0.,hi]];origin=B@np.r_[xy,0.];rp=np.column_stack([B[:,0],B[:,2],-B[:,1]])
 code='import cadquery as cq\nplane = '+plane(origin,rp)+f'\nresult = cq.Workplane(plane).polyline({poly!r}).close().revolve(360,(0,0),(0,1))\n';return code,{'profile':poly,'axis':params['axis'],'circle_center':xy.tolist(),'radial_quantile':quantile,'construction_structure_unchanged':True}
def section_refit(m,spec):
 B=np.array(spec['basis']);center=np.array(spec['center']);a=B[:,2];zmin=spec['zmin'];zmax=spec['zmax'];expected_holes=sum(len(x['holes']) for x in spec['profiles']);expected_outer=len(spec['profiles']);options=[]
 for frac in [.25,.4,.5,.6,.75]:
  s=m.section(plane_origin=center+a*(zmin+(zmax-zmin)*frac),plane_normal=a)
  if s is None:continue
  polygons=[]
  for pts in s.discrete:
   if len(pts)<4 or np.linalg.norm(pts[0]-pts[-1])>1e-5:continue
   p=Polygon(((pts-center)@B)[:,:2])
   if p.is_valid and p.area>1e-9:polygons.append(p)
  polygons.sort(key=lambda p:-p.area);outer=[];holes=[]
  for p in polygons:
   containing=[i for i,q in enumerate(outer) if q.contains(p.representative_point())]
   if containing:holes[containing[-1]].append(p)
   else:outer.append(p);holes.append([])
  if len(outer)!=expected_outer or sum(map(len,holes))!=expected_holes:continue
  for tol in [.0005,.001,.002,.004,.008]:
   profiles=[{'outer':list(map(list,p.simplify(tol,preserve_topology=True).exterior.coords[:-1])),'holes':[list(map(list,h.simplify(tol,preserve_topology=True).exterior.coords[:-1])) for h in hh]} for p,hh in zip(outer,holes)]
   if sum(len(p['outer'])+sum(map(len,p['holes'])) for p in profiles)<=96:break
  new=copy.deepcopy(spec);new['profiles']=profiles;new['section_fraction']=frac
  try:code=emit_profiles(new);options.append((sum(p.area for p in outer),code,new))
  except ValueError:pass
 if not options:raise ValueError('No stable closed section with matching native topology')
 options.sort(key=lambda x:x[0]);v=options[len(options)//2];return v[1],v[2]
def refined_candidates(m,features,r):
 params=read(Path(r['cad_program_path']).parent/'parameters.json');kind=r['best_kind'];out=[];errors=[]
 if kind=='cylinder':
  fits=[x for x in features['cylinder_fits'] if 'radius' in x]
  for f in fits[:2]:
   try:c,p=fit_cylinder(f);out.append(('robust_cylinder_parameter_fit',c,p))
   except Exception as e:errors.append(str(e))
 elif kind=='revolve':
  for quantile in [.95,.80]:
   try:c,p=radial_refit(m,params,quantile);out.append(('axial_profile_refit',c,p))
   except Exception as e:errors.append(str(e))
 elif kind in ['extrusion','extrusion_with_cuts']:
  try:c,p=section_refit(m,params);out.append(('stable_cross_section_refit',c,p))
  except Exception as e:errors.append(str(e))
 return out,errors
