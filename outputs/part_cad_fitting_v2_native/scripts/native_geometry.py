from v2_common import *
from profile_native import *
from v3_geometry import polygons
from fit_logic import basis_for_axis,voxel_occupancy
from metric_runtime import plane
from scipy.spatial.transform import Rotation
from scipy.ndimage import affine_transform
import trimesh

FAMILIES=['A_SIMPLE_PRIMITIVE','B_EXTRUSION','C_REVOLVE','D_EXTRUDE_WITH_CUTS','E_REVOLVE_WITH_CUTS','F_BOOLEAN_COMPOSITION','G_MULTI_PRIMITIVE','H_FRAME_BEAM','I_LOFT','J_FREEFORM_UNSUPPORTED']
def calls(code):return [n.func.attr for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)]
def family(code):
 c=calls(code)
 if 'loft' in c:return 'I_LOFT'
 if 'revolve' in c:return 'E_REVOLVE_WITH_CUTS' if 'cut' in c else 'C_REVOLVE'
 if 'union' in c:return 'G_MULTI_PRIMITIVE'
 if 'cut' in c:return 'D_EXTRUDE_WITH_CUTS' if 'extrude' in c else 'F_BOOLEAN_COMPOSITION'
 if 'box' in c or 'sphere' in c or ('circle' in c and c.count('extrude')==1 and 'polyline' not in c):return 'A_SIMPLE_PRIMITIVE'
 return 'B_EXTRUSION'
def profile_types(code):
 c=set(calls(code));r=[]
 for op,t in [('polyline','POLYLINE'),('circle','CIRCLE'),('ellipse','ELLIPSE'),('spline','BSPLINE'),('rect','LINE'),('box','LINE')]:
  if op in c:r.append(t)
 if 'threePointArc' in c:r.append('COMPOSITE_PROFILE' if 'lineTo' in c else 'ARC')
 return r
def section_evidence(m,code,seed):
 B,origin=first_plane(code);center=m.bounds.mean(0);q=(m.vertices-center)@B;lo,hi=q[:,2].min(),q[:,2].max();records=[];sections=[]
 for fraction in [.2,.35,.5,.65,.8]:
  ps=polygons(m,center+B[:,2]*(lo+fraction*(hi-lo)),B[:,2],B[:,0],B[:,1]);sections.append(ps);records.append({'fraction':fraction,'closed_component_n':len(ps),'holes':sum(len(p.interiors) for p in ps),'area':sum(p.area for p in ps),'perimeter':sum(p.length for p in ps)})
 valid=[i for i,s in enumerate(sections) if s];stable=False;variation=None;distances=[]
 if len(valid)>=3:
  areas=np.array([records[i]['area'] for i in valid]);variation=float(np.std(areas)/max(areas.mean(),1e-12));middle=valid[len(valid)//2];reference=sections[middle]
  if len(reference)==1:
   distances=[float(reference[0].hausdorff_distance(sections[i][0])) for i in valid if len(sections[i])==1]
  stable=variation<.06 and len(set((records[i]['closed_component_n'],records[i]['holes']) for i in valid))==1 and bool(distances) and max(distances)<.04
 return {'axis':B[:,2].tolist(),'basis':B.tolist(),'center':center.tolist(),'zmin':float(lo),'zmax':float(hi),'sections':records,'valid_section_n':len(valid),'area_coefficient_variation':variation,'hausdorff_distances':distances,'extrusion_supported':stable,'profile_stability':'STABLE' if stable else 'VARIABLE_OR_OPEN','end_cap_evidence':'not inferred from bbox alone; full source/CAD evaluation required'},sections
def section_code(evidence,sections,seed,mode='analytic'):
 valid=[i for i,s in enumerate(sections) if s]
 if not evidence['extrusion_supported']:raise ValueError('Multiple closed stable sections not demonstrated')
 i=min(valid,key=lambda j:abs(evidence['sections'][j]['fraction']-.5));ps=sections[i]
 if len(ps)+sum(len(p.interiors) for p in ps)>8 or len(ps)-1+sum(len(p.interiors) for p in ps)>6:raise ValueError('Measured component/hole complexity exceeds budget')
 B=np.array(evidence['basis']);center=np.array(evidence['center']);lo=evidence['zmin'];hi=evidence['zmax'];lines=['import cadquery as cq','plane = '+plane(center+B[:,2]*lo,B)];records=[]
 for j,p in enumerate(ps):
  for k,ring in enumerate([p.exterior]+list(p.interiors)):
   pts=np.asarray(ring.coords)[:-1];simple=np.asarray(Polygon(pts).simplify(.001,preserve_topology=True).exterior.coords)[:-1]
   if len(simple)>80:simple=resample(simple,80)
   rec=recognize(simple,seed+j*10+k);rep=choose(rec,mode);expr=profile_expression('cq.Workplane(plane)',simple,rep);lines.append(f'p{j}_{k} = '+expr+f'.extrude({float(hi-lo)!r})');records.append({'component':j,'hole':k>0,'recognition':rec,'selected':rep})
  lines.append(f'b{j} = p{j}_0'+''.join(f'.cut(p{j}_{k})' for k in range(1,1+len(p.interiors))))
 lines.append('result = b0'+''.join(f'.union(b{j})' for j in range(1,len(ps))))
 return '\n'.join(lines)+'\n',records

def param_transform(code,x,center,depth_mode=False):
 B,_=first_plane(code)
 if depth_mode:sc=np.exp([x[0],x[0],x[1]]);delta=x[2:5];R=Rotation.from_rotvec(x[5:8]).as_matrix()
 else:sc=np.exp([x[0]]*3);delta=x[1:4];R=Rotation.from_rotvec(x[4:7]).as_matrix()
 A=R@B@np.diag(sc)@B.T;b=np.asarray(center)-A@np.asarray(center)+delta
 def literal(v):return ast.parse(repr(np.asarray(v).tolist()),mode='eval').body
 def scale_arg(n,i,f):n.args[i]=literal(np.asarray(ast.literal_eval(n.args[i]))*f)
 class Edit(ast.NodeTransformer):
  def visit_Call(self,n):
   n=self.generic_visit(n)
   if not isinstance(n.func,ast.Attribute):return n
   k=n.func.attr
   if k=='Plane':
    for kw in n.keywords:
     if kw.arg=='origin':kw.value=literal(A@np.asarray(ast.literal_eval(kw.value))+b)
     elif kw.arg in ['xDir','normal']:kw.value=literal(R@np.asarray(ast.literal_eval(kw.value)))
   elif k in ['polyline','spline']:scale_arg(n,0,sc[0])
   elif k in ['moveTo','lineTo']:
    for i in range(min(2,len(n.args))):scale_arg(n,i,sc[0])
   elif k=='threePointArc':
    for i in range(2):scale_arg(n,i,sc[0])
   elif k in ['circle','sphere','ellipse','rect']:
    for i in range(2 if k in ['ellipse','rect'] else 1):scale_arg(n,i,sc[0])
   elif k=='extrude':scale_arg(n,0,sc[2])
   elif k=='box':
    for i in range(3):scale_arg(n,i,sc[i])
   elif k=='workplane':
    for kw in n.keywords:
     if kw.arg=='offset':kw.value=literal(float(ast.literal_eval(kw.value))*sc[2])
   elif k=='revolve':
    for i in range(1,min(3,len(n.args))):scale_arg(n,i,sc[0])
   return n
 tree=Edit().visit(ast.parse(code));ast.fix_missing_locations(tree);return ast.unparse(tree)+'\n',A,b

def optimize_candidate(m,cm,code,points,seed):
 B,_=first_plane(code);c=calls(code);depth_mode='revolve' not in c
 # Anisotropic depth fitting is valid only for parallel construction planes.
 for n in ast.walk(ast.parse(code)):
  if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='Plane':
   normals=[ast.literal_eval(k.value) for k in n.keywords if k.arg=='normal']
   if normals and abs(np.dot(np.asarray(normals[0])/np.linalg.norm(normals[0]),B[:,2]))<.99999:depth_mode=False
 n=8 if depth_mode else 7;ns=2 if depth_mode else 1;center=cm.bounds.mean(0);src=points[::5];target=trimesh.sample.sample_surface(cm,4000,seed=seed+1)[0];tree=cKDTree(src);diag=np.linalg.norm(m.extents);origin=m.bounds[0]-.12;pitch=max(m.extents)/44;shape=tuple(np.ceil((m.bounds[1]+.12-origin)/pitch).astype(int)+1);so=voxel_occupancy(m,origin,pitch,shape);co=voxel_occupancy(cm,origin,pitch,shape);trace=[];cache={}
 def objective(x):
  key=tuple(np.round(x,10))
  if key in cache:return cache[key]
  _,A,b=param_transform(code,x,center,depth_mode);p=target@A.T+b;dist=(tree.query(p)[0].mean()+cKDTree(p).query(src)[0].mean())*.5/diag;inv=np.linalg.inv(A);occ=affine_transform(co.astype(np.uint8),inv,offset=(inv@(origin-b)-origin)/pitch,output_shape=shape,order=0,prefilter=False)>0;iou=np.logical_and(so,occ).sum()/max(np.logical_or(so,occ).sum(),1);vv=cm.vertices@A.T+b;tri=vv[cm.faces];areas=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1);cent=(tri.mean(1)*areas[:,None]).sum(0)/areas.sum();ce=np.linalg.norm(cent-m.centroid);be=max(np.max(abs(np.ptp(vv,axis=0)-m.extents)),np.linalg.norm((vv.max(0)+vv.min(0))/2-m.bounds.mean(0)));val=float(10*dist+(1-iou)+2*ce+be+4*max(ce-.018,0)+2*max(be-.028,0));rec={'x':x.tolist(),'proxy_loss':val,'ncd':float(dist),'iou48_warped':float(iou),'centroid':float(ce),'bbox':float(be)};trace.append(rec);cache[key]=val;return val
 x=np.zeros(n);initial=objective(x);best=initial;aligned=x.copy();aligned[ns:ns+3]=np.clip(m.centroid-cm.centroid,-.04,.04)
 if objective(aligned)<best:x=aligned;best=objective(x)
 lower=np.r_[[-.12]*ns,[-.05]*3,[-.045]*3];upper=-lower
 for mul in [1.,.35]:
  steps=np.r_[[.025*mul]*ns,[.004*mul]*3,[.008*mul]*3]
  for j in range(n):
   for sign in [-1,1]:
    y=x.copy();y[j]=np.clip(y[j]+sign*steps[j],lower[j],upper[j]);loss=objective(y)
    if loss<best-1e-9:x=y;best=loss
 output,A,b=param_transform(code,x,center,depth_mode)
 return output,{'initial_proxy_loss':initial,'best_proxy_loss':best,'steps':trace,'best_x':x.tolist(),'depth_mode':depth_mode,'radius_depth_center_rotation_fitted':True,'seed':seed,'proxy_only':True,'acceptance_uses_unchanged_full_evaluation':True}

def proposals(row,m,code,features):
 out=[];diagnosis={};seen={code.strip()}
 def add(kind,c,parameters):
  if c.strip() in seen:return
  seen.add(c.strip());out.append({'kind':kind,'code':c,'parameters':parameters,'family':family(c),'profile_types':profile_types(c)})
 # Baseline structure with fresh local fit is a candidate independent of baseline preservation.
 out.append({'kind':'BASELINE_LOCAL_REFINEMENT','code':code,'parameters':{},'family':family(code),'profile_types':profile_types(code)})
 for mode in ['analytic','spline']:
  try:c,recs=upgrade_code(code,mode,row['seed']);add('PROFILE_'+mode.upper(),c,{'profile_reconstruction':recs});diagnosis[mode]=recs
  except Exception as e:diagnosis[mode+'_error']=str(e)
 try:
  evidence,sections=section_evidence(m,code,row['seed']);diagnosis['cross_sections']=evidence
  for mode in ['analytic','spline']:
   try:c,recs=section_code(evidence,sections,row['seed'],mode);add('STABLE_SECTION_'+mode.upper(),c,{'cross_sections':evidence,'profile_reconstruction':recs})
   except Exception as e:diagnosis.setdefault('section_candidate_errors',[]).append(str(e))
 except Exception as e:diagnosis['cross_section_error']=str(e)
 # Change family only in the V1 reject phase, using measured alternate principal axes.
 if row['v1_status']=='REJECT':
  from v3_geometry import revolve,loft
  for fit in features.get('cylinder_fits',[])[:2]:
   if 'radius' not in fit:continue
   try:
    axis=np.asarray(fit['axis']);B=np.asarray(fit['basis']);center=B@np.r_[fit['center_xy'],(fit['zmin']+fit['zmax'])/2];c,param,_=revolve(m,axis,center,0.);c,recs=upgrade_code(c,'analytic',row['seed']);add('MEASURED_REVOLVE_ANALYTIC',c,{'axis_fit':fit,'section_fit':param,'profile_reconstruction':recs})
   except Exception as e:diagnosis.setdefault('revolve_errors',[]).append(str(e))
  try:
   B=basis_for_axis(np.asarray(features['pca_axes'][0]));center=m.bounds.mean(0);q=(m.vertices-center)@B;lo=float(q[:,2].min());hi=float(q[:,2].max());ss=[polygons(m,center+B[:,2]*(lo+f*(hi-lo)),B[:,2],B[:,0],B[:,1]) for f in [.05,.5,.95]];c,param,_=loft(m,B,center,ss,lo,hi);c,recs=upgrade_code(c,'analytic',row['seed']);add('MEASURED_LOFT',c,{'loft_sections':param,'profile_reconstruction':recs})
  except Exception as e:diagnosis['loft_error']=str(e)
 # Geometric evidence, not LLM-guessed sizes: retain original dimensional/boolean structure.
 v1=read(O/'cases'/row['case_id']/'source/v1_result.json');met=v1['metrics'];failed_by=failed(met);attrs=calls(code);primary='PARAMETER_ONLY_ERROR';secondary=[]
 if 'polyline' in attrs:primary='POLYLINE_APPROXIMATION_ERROR';secondary.append('PROFILE_TOO_COARSE')
 if 'centroid' in failed_by:secondary.append('WRONG_CENTER')
 if 'bbox' in failed_by and 'extrude' in attrs:secondary.append('WRONG_EXTRUSION_DEPTH')
 if diagnosis.get('cross_sections',{}).get('profile_stability')=='VARIABLE_OR_OPEN':secondary.append('FREEFORM_RESIDUAL')
 diagnosis.update(primary_failure=primary,secondary_failures=secondary,strict_failed_by=failed_by,diagnosis_confidence='hypothesis; corroborate with candidate deltas',missing_hole_slot_fillet_chamfer='UNCONFIRMED unless supported by measured section topology; no invented cuts',family_v1=row['v1_family'],family_v2=family(code),family_changed=row['v1_family']!=family(code),family_confidence='feature code + measured sections; semantic family labels normalized',all_root_cause_categories=['PARAMETER_ONLY_ERROR','PROFILE_TOO_COARSE','POLYLINE_APPROXIMATION_ERROR','WRONG_PROFILE_TYPE','WRONG_RADIUS','WRONG_EXTRUSION_DEPTH','WRONG_REVOLVE_AXIS','WRONG_REVOLVE_PROFILE','WRONG_CENTER','WRONG_ORIENTATION','MISSING_HOLE','MISSING_SLOT','MISSING_CUT','MISSING_PROTRUSION','MISSING_FILLET','MISSING_CHAMFER','MISSING_BOOLEAN_STRUCTURE','WRONG_BOOLEAN_ORDER','WRONG_CAD_FAMILY','FREEFORM_RESIDUAL','UNKNOWN'])
 return out[:7],diagnosis
