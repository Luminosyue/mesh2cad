from v2_common import *
import argparse,collections
from concurrent.futures import ProcessPoolExecutor
import trimesh
from scipy.optimize import least_squares
from shapely.geometry import Polygon
from fit_logic import basis_for_axis
def process(row):
 d=O/'cases'/row['case_id'];f=d/'features/features_v2.json'
 if f.exists():return read(f)
 m=trimesh.load(d/'source/part_local.ply',force='mesh',process=True);r=read(d/'source/v1_result.json');v1f=read(d/'source/v1_features.json');code=Path(r['cad_program_path']).read_text();B,origin=first_plane(code);a=B[:,1] if r['best_kind']=='revolve' else B[:,2]
 pts,ids=trimesh.sample.sample_surface(m,20000,seed=row['seed']);np.save(d/'source/frozen_evaluation_points.npy',pts);normals=m.face_normals[ids]
 cov=(normals.T@normals)/len(normals);eig,Q=np.linalg.eigh(cov);normal_axis=Q[:,0];normal_axis*=1 if np.dot(normal_axis,a)>=0 else -1
 _,_,vh=np.linalg.svd(pts-pts.mean(0),full_matrices=False);axes=[a,normal_axis,vh[0]];unique=[];cyl=[];sections=[]
 for axis in axes:
  if any(abs(np.dot(axis,x))>.99999 for x in unique):continue
  unique.append(axis);K=basis_for_axis(axis);q=pts@K;side=np.abs(normals@axis)<.30;xy=q[side,:2]
  if len(xy)>100:
   A=np.c_[2*xy,np.ones(len(xy))];sol=np.linalg.lstsq(A,np.sum(xy*xy,axis=1),rcond=None)[0];c=sol[:2];rad=np.linalg.norm(xy-c,axis=1);fit=least_squares(lambda x:np.linalg.norm(xy-x[:2],axis=1)-x[2],np.r_[c,np.median(rad)],loss='soft_l1',f_scale=.005,max_nfev=100);c=fit.x[:2];radius=abs(float(fit.x[2]));res=np.abs(np.linalg.norm(xy-c,axis=1)-radius)
   cyl.append({'axis':axis.tolist(),'basis':K.tolist(),'center_xy':c.tolist(),'radius':radius,'radial_mad':float(np.median(res)),'relative_radial_mad':float(np.median(res)/max(radius,1e-12)),'side_sample_fraction':float(side.mean()),'zmin':float((m.vertices@K)[:,2].min()),'zmax':float((m.vertices@K)[:,2].max())})
  else:cyl.append({'axis':axis.tolist(),'unsupported':'insufficient side samples'})
  qv=m.vertices@K;lo,hi=qv[:,2].min(),qv[:,2].max();sr=[]
  for t in [.15,.3,.5,.7,.85]:
   sec=m.section(plane_origin=axis*(lo+t*(hi-lo)),plane_normal=axis);loops=[]
   if sec is not None:
    for pp in sec.discrete:
     if len(pp)<4 or np.linalg.norm(pp[0]-pp[-1])>1e-5:continue
     uv=(pp@K)[:,:2];poly=Polygon(uv)
     if poly.is_valid and poly.area>1e-10:loops.append(poly)
   nested=sum(any(other.contains(p.representative_point()) and other.area>p.area*1.01 for other in loops) for p in loops)
   sr.append({'fraction':t,'closed_loops':len(loops),'nested_holes':nested,'areas':sorted([float(p.area) for p in loops],reverse=True)[:8]})
  sections.append({'axis':axis.tolist(),'sections':sr,'stable_hole_count':min(s['nested_holes'] for s in sr)})
 bins=np.round(m.face_normals/.05).astype(int);ub,inv=np.unique(bins,axis=0,return_inverse=True);w=np.bincount(inv,weights=m.area_faces);ix=np.argsort(w)[-12:][::-1];clusters=[{'normal':(ub[i]*.05).tolist(),'area_fraction':float(w[i]/m.area)} for i in ix]
 counts=np.bincount(m.edges_unique_inverse);be=m.edges_unique[counts==1];degree=np.bincount(be.ravel(),minlength=len(m.vertices));boundary_closed=bool(len(be)>0 and np.all(degree[degree>0]==2))
 angles=m.face_adjacency_angles;hist,bins=np.histogram(angles,bins=[0,.05,.15,.3,.6,1.,1.6,3.142]);components=sorted(m.split(only_watertight=False),key=lambda c:-c.area)
 ext=np.ptp(pts@vh.T,axis=0);out={'case_id':row['case_id'],'bbox':m.bounds.tolist(),'centroid':m.centroid.tolist(),'pca_axes':vh.tolist(),'aspect_ratios':(ext/max(ext)).tolist(),'normal_covariance_eigenvalues':eig.tolist(),'normal_clusters':clusters,'cylinder_fits':cyl,'cross_sections':sections,'boundary_edge_n':len(be),'boundary_all_degree_two':boundary_closed,'curvature_proxy':'dihedral-angle histogram, not differential surface curvature','dihedral_histogram':hist.tolist(),'dihedral_bins':bins.tolist(),'component_n':len(components),'component_extents':[c.extents.tolist() for c in components[:8]],'repeated_feature_evidence':'component extent similarities only, no repeated-design assertion','protrusion_evidence':'cross-section area variation; topology not guessed','slots':'nested noncircular loops require candidate verification','native_axis':a.tolist(),'normal_axis_angle_degrees':float(np.degrees(np.arccos(np.clip(abs(a@normal_axis),0,1)))),'source_points_sha256':sha(d/'source/frozen_evaluation_points.npy'),'source_mesh_sha256':sha(d/'source/part_local.ply')}
 dump(f,out)
 met=r['metrics'];fails=failed(met);kind=r['best_kind'];primary='CENTROID_ALIGNMENT_ERROR' if fails==['centroid'] else 'WRONG_RADIUS' if kind=='cylinder' and 'bbox' in fails else 'WRONG_REVOLVE_PROFILE' if kind=='revolve' else 'WRONG_SKETCH_PROFILE' if 'extrusion' in kind and 'IoU' in fails else 'PARAMETER_ONLY_ERROR';secondary=[]
 if 'centroid' in fails and primary!='CENTROID_ALIGNMENT_ERROR':secondary.append('CENTROID_ALIGNMENT_ERROR')
 if 'bbox' in fails and primary!='WRONG_RADIUS':secondary.append('WRONG_SCALE')
 if out['normal_axis_angle_degrees']>3 and cyl[0].get('relative_radial_mad',1)>.08 and kind=='cylinder':secondary.append('WRONG_AXIS')
 if any(s['stable_hole_count']>0 for s in sections) and kind in ['cylinder','revolve','extrusion']:secondary.append('MISSING_HOLE')
 diagnosis={'case_id':row['case_id'],'object_id':row['object_id'],'part_id':row['part_id'],'current_cad_family':r['cad_family'],'current_native_kind':kind,**{'V1_'+k:met[key] for k,key in [('NCD','normalized_chamfer'),('IoU','iou'),('bbox_error','bbox_error'),('centroid_error','centroid_l2_error')]},'strict_failed_by':fails,'primary_failure':primary,'secondary_failures':secondary,'diagnosis_certainty':'hypothesis from measured residuals; not asserted causal truth','structural_change_authorized':False,'feature_path':str(f)};dump(d/'diagnosis/diagnosis.json',diagnosis)
 print(json.dumps({'case':row['case_id'],'primary':primary,'secondary':secondary,'axis_angle':round(out['normal_axis_angle_degrees'],2),'cyl_mad':round(cyl[0].get('relative_radial_mad',1),3),'components':len(components),'aspect':[round(x,3) for x in out['aspect_ratios']]}),flush=True);return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--group',choices=['near','reject','strict','all'],required=True);a=ap.parse_args();statusmap={'near':'NEAR_PASS','reject':'REJECT','strict':'STRICT_ACCEPT'};rows=[r for r in read(O/'manifests/cases.json') if a.group=='all' or r['v1_status']==statusmap[a.group]]
 with ProcessPoolExecutor(max_workers=8) as pool:list(pool.map(process,rows))
 print('FEATURES_COMPLETE',a.group,len(rows))
