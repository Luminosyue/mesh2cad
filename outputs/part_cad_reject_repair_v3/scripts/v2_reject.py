from v2_common import *
import trimesh
from scipy.optimize import least_squares
from metric_runtime import plane
from fit_logic import basis_for_axis,projected_profile,candidate_axes
from cad_emit import emit_profiles
from v2_refit import fit_cylinder,section_refit,radial_refit
def box_code(m,axis):
 B=basis_for_axis(axis);q=m.vertices@B;lo=q.min(0);hi=q.max(0);extent=hi-lo
 if min(extent)<1e-6:raise ValueError('No measured solid thickness')
 center=B@((lo+hi)/2);return 'import cadquery as cq\nplane = '+plane(center,B)+'\nresult = cq.Workplane(plane).box('+','.join(map(repr,extent.tolist()))+')\n',{'basis':B.tolist(),'center':center.tolist(),'extents':extent.tolist()}
def sphere_code(points):
 A=np.c_[2*points,np.ones(len(points))];v=np.linalg.lstsq(A,(points*points).sum(1),rcond=None)[0];c=v[:3];rad=np.median(np.linalg.norm(points-c,axis=1));fit=least_squares(lambda x:np.linalg.norm(points-x[:3],axis=1)-x[3],np.r_[c,rad],loss='soft_l1',f_scale=.005,max_nfev=80);c=fit.x[:3];rad=float(abs(fit.x[3]));res=float(np.median(np.abs(np.linalg.norm(points-c,axis=1)-rad))/max(rad,1e-10))
 if res>.06:raise ValueError('Sphere unsupported by radial residual')
 return 'import cadquery as cq\nplane = '+plane(c,np.eye(3))+f'\nresult = cq.Workplane(plane).sphere({rad!r})\n',{'center':c.tolist(),'radius':rad,'relative_radial_mad':res}
def cone_code(m,f):
 B=np.array(f['basis']);q=m.vertices@B;rad=np.linalg.norm(q[:,:2]-f['center_xy'],axis=1);z=q[:,2];bins=np.linspace(z.min(),z.max(),12);zs=[];rs=[]
 for i in range(11):
  mask=(z>=bins[i])&(z<=bins[i+1])
  if mask.sum()>3:zs.append((bins[i]+bins[i+1])/2);rs.append(np.quantile(rad[mask],.85))
 if len(rs)<5:raise ValueError('Insufficient cone section evidence')
 slope,intercept=np.polyfit(zs,rs,1);r0=float(slope*z.min()+intercept);r1=float(slope*z.max()+intercept);h=float(np.ptp(z));res=float(np.mean(np.abs(np.array(rs)-(slope*np.array(zs)+intercept)))/max(np.mean(rs),1e-9))
 if min(r0,r1)<1e-5 or res>.08:raise ValueError('Cone/frustum unsupported')
 origin=B@np.r_[f['center_xy'],z.min()];code='import cadquery as cq\nplane = '+plane(origin,B)+f'\nresult = cq.Workplane(plane).circle({r0!r}).workplane(offset={h!r}).circle({r1!r}).loft(ruled=True)\n';return code,{'radius_start':r0,'radius_end':r1,'height':h,'section_residual':res,'basis':B.tolist(),'origin':origin.tolist()}
def multi_code(m):
 comps=sorted(m.split(only_watertight=False),key=lambda x:-x.area)
 if not 2<=len(comps)<=7:raise ValueError('Component count outside compact union budget')
 lines=['import cadquery as cq'];records=[]
 for i,comp in enumerate(comps):
  _,_,vh=np.linalg.svd(comp.vertices-comp.vertices.mean(0),full_matrices=False);code,param=box_code(comp,vh[0]);tree=ast.parse(code);tree.body=[x for x in tree.body if not isinstance(x,ast.Import)]
  class Rename(ast.NodeTransformer):
   def visit_Name(self,n):return ast.copy_location(ast.Name(id=n.id if n.id=='cq' else f'c{i}_'+n.id,ctx=n.ctx),n)
  tree=Rename().visit(tree);ast.fix_missing_locations(tree);lines.append(ast.unparse(tree));records.append(param)
 lines.append('result = c0_result'+''.join(f'.union(c{i}_result)' for i in range(1,len(comps))));return '\n'.join(lines)+'\n',{'component_fits':records,'primitive_n':len(comps),'no_component_dropped':True}
def structural_candidates(m,features,r,plan):
 out=[];errors=[];fam=plan['cad_family_v2'][0];fits=sorted([f for f in features['cylinder_fits'] if 'radius' in f],key=lambda f:f['relative_radial_mad']);axes=[np.array(f['axis']) for f in fits[:2]]+[np.array(features['pca_axes'][0])]+candidate_axes(m)[:2]
 def add(label,fn,*args):
  try:code,params=fn(*args);out.append((label,code,params))
  except Exception as e:errors.append(label+': '+str(e))
 def extrude(axis):
  spec=projected_profile(m,axis,96);return emit_profiles(spec),spec
 def stable(axis):
  spec=projected_profile(m,axis,96);return section_refit(m,spec)
 if fam=='F':add('component_primitive_union',multi_code,m)
 if fam in ['C','G','A']:
  for f in fits[:2]:add('robust_axis_cylinder_fit',fit_cylinder,f)
  if fits:add('cone_frustum_fit',cone_code,m,fits[0])
 if fam!='H':
  for axis in axes[:2]:add('stable_section_with_supported_cuts',stable,axis)
  for axis in axes[:2]:add('observed_profile_with_supported_cuts',extrude,axis)
 if fam in ['C','A','H']:
  # Reuse the original source-seed point set; do not select a new dataset sample.
  p=O/'cases'/features['case_id']/'source/frozen_evaluation_points.npy';add('robust_sphere_fit',sphere_code,np.load(p)[::4])
 if fam=='C' and fits:
  f=fits[0];add('radial_section_profile_fit',radial_refit,m,{'axis':f['axis'],'circle_center':f['center_xy']},.9)
 if fam!='H':add('oriented_primitive_fit',box_code,m,np.array(features['pca_axes'][0]))
 return out[:5],errors
