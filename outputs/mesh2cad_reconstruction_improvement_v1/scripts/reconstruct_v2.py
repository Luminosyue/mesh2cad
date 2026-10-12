"""General geometry-driven reconstruction; no case-specific dimensions or family overrides."""
import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import sys,json,hashlib,subprocess,shutil,traceback,argparse,datetime
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import trimesh
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy.spatial import ConvexHull
from fit_logic import candidate_axes,basis_for_axis,projected_profile
from historical_fit import section_loft_profile,primitive_profile
from v1_runtime import evaluate,plane,sha
O=Path('/data/home/cuiyuehan/project/mesh2cad/outputs');OLD=O/'mesh2cad_data_factory_v1_smoke100';I=O/'mesh2cad_reconstruction_improvement_v1';R=O/'mesh2cad_resmoke100_v2';D=O/'mesh2cad_reconstruction_diagnosis_v1'
def dump(p,x):
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,allow_nan=False,default=lambda a:a.item() if isinstance(a,np.generic) else a.tolist()))
def score(m):return 10*m['normalized_chamfer']+(1-m['iou'])+2*m['centroid_l2_error']+m['bbox_error']
def emit_profiles(spec):
 B=np.asarray(spec['basis']);origin=np.asarray(spec['center'])+B[:,2]*spec['zmin'];h=spec['zmax']-spec['zmin'];ps=spec['profiles']
 if h<1e-6 or len(ps)>7 or sum(len(p['holes']) for p in ps)+len(ps)-1>6:raise ValueError('invalid depth or Boolean budget')
 if sum(len(p['outer'])+sum(map(len,p['holes'])) for p in ps)>96:raise ValueError('profile complexity budget')
 lines=['import cadquery as cq','plane = '+plane(origin,B)]
 for j,p in enumerate(ps):
  lines.append(f'p{j} = cq.Workplane(plane).polyline({p["outer"]!r}).close().extrude({h!r})')
  for k,hole in enumerate(p['holes']):
   lines.extend([f'h{j}_{k} = cq.Workplane(plane).polyline({hole!r}).close().extrude({h!r})',f'p{j} = p{j}.cut(h{j}_{k})'])
 lines.append('result = p0'+''.join(f'.union(p{j})' for j in range(1,len(ps))));return '\n'.join(lines)+'\n'
def planar_regions(mesh):
 """Fit coplanar patches; merge triangles into bounded 2D contours, never emit mesh faces."""
 verts=np.asarray(mesh.vertices);tri=np.asarray(mesh.triangles);groups=[]
 for idx in np.argsort(-mesh.area_faces):
  n=np.asarray(mesh.face_normals[idx]);p=tri[idx].mean(0);found=False
  for g in groups:
   if abs(np.dot(n,g['normal']))>.9995 and np.max(np.abs((tri[idx]-g['point'])@g['normal']))<.0005:
    g['ids'].append(int(idx));found=True;break
  if not found:groups.append({'normal':n,'point':p,'ids':[int(idx)]})
 if len(groups)>7:raise ValueError('more than 7 fitted planes; refuse faceted surface approximation')
 regions=[]
 for g in groups:
  # At least two triangles support every fitted region. Reject triangular face wrappers.
  if len(g['ids'])<2:raise ValueError('single-triangle region forbidden')
  pts=tri[g['ids']].reshape(-1,3);c=pts.mean(0);_,_,vh=np.linalg.svd(pts-c,full_matrices=False);B=basis_for_axis(vh[2]);loc=(pts-c)@B
  if np.max(np.abs(loc[:,2]))>.0005:raise ValueError('plane residual too large')
  poly=unary_union([Polygon(t) for t in loc[:,:2].reshape(-1,3,2)]).buffer(0).simplify(.00002,preserve_topology=True)
  polys=list(poly.geoms) if poly.geom_type=='MultiPolygon' else [poly]
  for p in polys:
   outer=np.asarray(p.exterior.coords[:-1]).tolist();holes=[np.asarray(x.coords[:-1]).tolist() for x in p.interiors]
   if len(outer)<4:raise ValueError('triangular region forbidden by compact sheet policy')
   regions.append({'center':c.tolist(),'basis':B.tolist(),'outer':outer,'holes':holes,'support_triangle_n':len(g['ids']),'plane_residual':float(np.max(np.abs(loc[:,2])))})
 if len(regions)>7 or sum(len(p['holes']) for p in regions)+len(regions)-1>6:raise ValueError('planar assembly Boolean budget')
 if sum(len(p['outer'])+sum(map(len,p['holes'])) for p in regions)>96:raise ValueError('planar assembly sketch budget')
 return regions
def emit_regions(regions,thickness):
 lines=['import cadquery as cq']
 for j,p in enumerate(regions):
  B=np.array(p['basis']);origin=np.array(p['center'])-B[:,2]*thickness/2
  lines.extend([f'plane{j} = '+plane(origin,B),f'p{j} = cq.Workplane(plane{j}).polyline({p["outer"]!r}).close().extrude({thickness!r})'])
  for k,hole in enumerate(p['holes']):
   lines.extend([f'h{j}_{k} = cq.Workplane(plane{j}).polyline({hole!r}).close().extrude({thickness!r})',f'p{j} = p{j}.cut(h{j}_{k})'])
 lines.append('result = p0'+''.join(f'.union(p{j})' for j in range(1,len(regions))));return '\n'.join(lines)+'\n'
def emit_loft(spec):
 tracks=spec['outer_tracks'];holes=spec['hole_tracks']
 if holes or len(tracks)>1:raise ValueError('compact loft supports one outer track; no dropped holes')
 track=tracks[0]
 if sum(len(x) for x in track)>96:raise ValueError('loft sketch budget')
 B=np.asarray(spec['basis']);c=np.asarray(spec['center']);lines=['import cadquery as cq'];expr=None
 for i,pts in enumerate(track):
  q=(np.asarray(pts)-c)@B;z=float(q[:,2].mean());p=q[:,:2].tolist()
  if i==0:lines.append('plane = '+plane(c+B[:,2]*z,B));expr=f'cq.Workplane(plane).polyline({p!r}).close()';zprev=z
  else:expr+=f'.workplane(offset={z-zprev!r}).polyline({p!r}).close()';zprev=z
 lines.append('result = '+expr+'.loft(ruled=True)');return '\n'.join(lines)+'\n'
def make_candidates(mesh,old,family):
 proposals=[];notes=[]
 def add(kind,code,params):
  if not any(code==x['code'] for x in proposals):proposals.append({'kind':kind,'code':code,'parameters':params})
 if old.get('cad_program_path'):add('v1_incumbent',Path(old['cad_program_path']).read_text(),{'policy':'re-execute incumbent, no degradation safeguard'})
 if not mesh.is_watertight and family in {'A_SINGLE_PRIMITIVE','B_EXTRUSION_LIKE','E_MULTI_PRIMITIVE_ASSEMBLY','G_UNSUPPORTED_OR_AMBIGUOUS'}:
  try:
   regs=planar_regions(mesh)
   for t in [.0002,.001,.004]:add('planar_region_assembly',emit_regions(regs,t),{'regions':regs,'thickness':t,'thickness_observed':False,'policy':'explicit thin-solid regularization of merged planar surface regions; not recovered design thickness'})
  except Exception as e:notes.append('planar regions: '+str(e))
 axes=candidate_axes(mesh)
 # Surface-normal directions supplement PCA/world axes; this affects internal modeling frames only.
 for idx in np.argsort(-mesh.area_faces):
  n=mesh.face_normals[idx]
  if not any(abs(np.dot(n,a))>.995 for a in axes):axes.append(n)
  if len(axes)>=9:break
 # Reuse section tracking with a compact 6 x 12 sketch budget instead of the old 32 x 40.
 if mesh.is_watertight:
  for axis in axes[:2]:
   try:
    spec=section_loft_profile(mesh,axis,True,section_count=6,points_per_loop=12);add('compact_section_loft',emit_loft(spec),spec)
   except Exception as e:notes.append('loft: '+str(e))
 for axis in axes[2:]+axes[:2]:
  if len(proposals)>=7:break
  try:
   spec=projected_profile(mesh,axis,96);add('normal_axis_extrusion',emit_profiles(spec),spec)
  except Exception as e:notes.append('extrusion: '+str(e))
 # Geometry-fitted sphere is useful only for near-isotropic closed sources.
 if len(proposals)<8 and mesh.is_watertight:
  v=np.asarray(mesh.vertices);A=np.column_stack([2*v,np.ones(len(v))]);sol=np.linalg.lstsq(A,np.sum(v*v,axis=1),rcond=None)[0];c=sol[:3];radius=float(np.sqrt(max(0,sol[3]+c@c)))
  if radius>1e-6:
   add('least_squares_sphere','import cadquery as cq\nplane = '+plane(c,np.eye(3))+f'\nresult = cq.Workplane(plane).sphere({radius!r})\n',{'center':c.tolist(),'radius':radius})
 return proposals[:8],notes
def worker(old):
 cid=old['case_id'];d=R/'cases'/cid
 if (d/'manifest.json').exists():return json.loads((d/'manifest.json').read_text())
 d.mkdir(exist_ok=False)
 for x in ['source','normalized','attempts','cad','step','reload','mesh','metrics','logs']:(d/x).mkdir()
 original=OLD/'cases'/cid
 if sha(old['source_mesh_path'])!=old['source_mesh_sha256']:raise ValueError('source hash drift')
 for src,dst in [('source/source_mesh.stl','source/source_mesh.stl'),('normalized/normalized_mesh.ply','normalized/normalized_mesh.ply'),('normalized/transform.json','normalized/transform.json')]:shutil.copyfile(original/src,d/dst)
 m=trimesh.load(d/'normalized/normalized_mesh.ply',force='mesh',process=True)
 result={'case_id':cid,'source_mesh_sha256':old['source_mesh_sha256'],'source_mesh_path':old['source_mesh_path'],'split_group_id':old['split_group_id'],
  'normalization':old['normalization'],'branch':'DIRECT','p3_xpart_used':False,'attempts':[],'status':'REJECT','failure_reason':None,
  'family':next(x['cad_family'] for x in json.loads((D/'tables/descriptors_and_diagnosis.json').read_text()) if x['case_id']==cid)}
 proposals,notes=make_candidates(m,old,result['family']);result.update(proposed_candidate_count=len(proposals),planning_notes=notes)
 dump(d/'proposals.json',[{k:v for k,v in p.items() if k!='code'} for p in proposals])
 for i,p in enumerate(proposals):
  a=d/'attempts'/f'candidate_{i:02d}';a.mkdir();(a/'cad.py').write_text(p['code']);dump(a/'parameters.json',p['parameters'])
  rec={'candidate_id':i,'kind':p['kind'],'parameters':p['parameters'],'path':str(a),'generation_timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),'llm_used':False}
  try:
   ex=subprocess.run([sys.executable,'-B',str(I/'scripts/execute_v2.py'),str(a/'cad.py'),str(a/'execution')],capture_output=True,text=True,timeout=120,env=os.environ.copy())
   (a/'execution.log').write_text(ex.stdout+'\n'+ex.stderr);rec['execution']=json.loads((a/'execution/execution.json').read_text())
   if rec['execution'].get('tessellation_pass'):
    cad=trimesh.load(a/'execution/cad_mesh_from_reloaded_step.ply',force='mesh',process=True)
    met=evaluate(m,cad,20261006+int(cid.split('_')[1])*10);met.update(source_mesh_sha256=sha(d/'normalized/normalized_mesh.ply'),cad_mesh_sha256=sha(a/'execution/cad_mesh_from_reloaded_step.ply'),step_sha256=sha(a/'execution/cad.step'))
    rec.update(metrics=met,geometry_score=score(met));dump(a/'metrics.json',met)
  except Exception as e:rec.update(error=str(e),traceback=traceback.format_exc())
  result['attempts'].append(rec);dump(a/'record.json',rec)
  # General early stopping at the unchanged strict gate, never keyed by case id.
  if rec.get('metrics',{}).get('strict_pass'):result['early_stop']='unchanged strict gate reached';break
 good=[a for a in result['attempts'] if a.get('metrics')]
 if good:
  best=min(good,key=lambda a:(not a['metrics']['strict_pass'],a['geometry_score']));a=Path(best['path'])
  for s,t in [('cad.py','cad/cad.py'),('parameters.json','cad/parameters.json'),('execution/cad.step','step/cad.step'),('execution/execution.json','reload/reload_metadata.json'),('execution/cad_mesh_from_reloaded_step.ply','mesh/cad_mesh_from_reloaded_step.ply'),('metrics.json','metrics/metrics.json')]:shutil.copyfile(a/s,d/t)
  result.update(status='STRICT_ACCEPT' if best['metrics']['strict_pass'] else 'RELAXED_ANALYSIS_ONLY',metrics=best['metrics'],best_candidate_id=best['candidate_id'],best_kind=best['kind'],
    initial_score=score(old['geometry_metrics']) if old['geometry_metrics'] else None,best_score=best['geometry_score'],optimization_steps=max(0,len(result['attempts'])-1),candidate_count=len(result['attempts']),
    failure_reason=None if best['metrics']['strict_pass'] else 'GEOMETRY_MISMATCH',near_pass=best['metrics']['iou']>=.7 and best['metrics']['normalized_chamfer']<=.02,
    thickness_assumed=best['kind']=='planar_region_assembly',cad_program_path=str(d/'cad/cad.py'),step_path=str(d/'step/cad.step'),cad_mesh_path=str(d/'mesh/cad_mesh_from_reloaded_step.ply'))
 else:result.update(failure_reason='UNSUPPORTED_GEOMETRY' if not proposals else 'CAD_OR_EVALUATION_FAILURE',candidate_count=len(result['attempts']),initial_score=None,best_score=None,optimization_steps=0)
 dump(d/'manifest.json',result);print(json.dumps({'case':cid,'status':result['status'],'kind':result.get('best_kind'),'iou':result.get('metrics',{}).get('iou'),'candidate_n':len(result['attempts'])}),flush=True);return result
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int,choices=[3,10,100],required=True);a=ap.parse_args();rows=json.loads((R/'configs/frozen_sources.json').read_text())[:a.limit]
 with ProcessPoolExecutor(max_workers=4) as pool:out=list(pool.map(worker,rows))
 dump(R/'reports'/f'stage_{a.limit}.json',{'n':len(out),'strict_n':sum(x['status']=='STRICT_ACCEPT' for x in out),'reject_n':sum(x['status']=='REJECT' for x in out)});print('STAGE_DONE',a.limit,flush=True)
if __name__=='__main__':main()
