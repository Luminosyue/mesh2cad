from pathlib import Path
import os,sys,json,time,hashlib,traceback,concurrent.futures
os.environ['OMP_NUM_THREADS']='1';os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,trimesh,vtk,cadquery as cq
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_REVERSED
from mesh_decimation import decimate
from regular_patch import patch_solid
from scipy.spatial import cKDTree
from fit_revolve import fit,build
ROOT=Path(__file__).resolve().parent;SRC=Path(os.environ.get('TANK_SOURCE',str(ROOT/'tank_input')));OUT=Path(os.environ.get('TANK_OUTPUT',str(ROOT.parent/'outputs/tank_cad')))
WHEELS={5,6,9,14,18,21,24,26}

def dump(p,v):p.write_text(json.dumps(v,indent=2),encoding='utf-8')

def tessellate(shape):
 BRepMesh_IncrementalMesh(shape.wrapped,.025,False,.35,False)
 verts=[];faces=[]
 for f in shape.Faces():
  loc=TopLoc_Location();poly=BRep_Tool.Triangulation_s(f.wrapped,loc)
  if poly is None:continue
  offset=len(verts);tr=loc.Transformation()
  for i in range(1,poly.NbNodes()+1):
   p=poly.Node(i).Transformed(tr);verts.append((p.X(),p.Y(),p.Z()))
  reverse=f.wrapped.Orientation()==TopAbs_REVERSED
  for i in range(1,poly.NbTriangles()+1):
   a,b,c=poly.Triangle(i).Get();faces.append((a-1+offset,c-1+offset,b-1+offset) if reverse else (a-1+offset,b-1+offset,c-1+offset))
 return trimesh.Trimesh(verts,faces,process=True)

def distance_to(mesh,points):
 poly=vtk.vtkPolyData();p=vtk.vtkPoints();p.SetData(numpy_to_vtk(mesh.vertices,deep=True));poly.SetPoints(p)
 cells=vtk.vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(mesh.faces),3),mesh.faces].ravel().astype(np.int64),deep=True));poly.SetPolys(cells)
 dist=vtk.vtkImplicitPolyDataDistance();dist.SetInput(poly)
 return np.array([abs(dist.EvaluateFunction(x)) for x in points])

def evaluate(source,actual):
 a,_=trimesh.sample.sample_surface(source,6000,seed=123);b,_=trimesh.sample.sample_surface(actual,6000,seed=456)
 da=distance_to(actual,a);db=distance_to(source,b);d=np.r_[da,db];diag=np.linalg.norm(source.extents)
 return {'mean_distance_pct_diagonal':float(d.mean()/diag*100),'p95_distance_pct_diagonal':float(np.percentile(d,95)/diag*100),'sampled_max_distance_pct_diagonal':float(d.max()/diag*100),'source_to_cad_p95_pct':float(np.percentile(da,95)/diag*100),'cad_to_source_p95_pct':float(np.percentile(db,95)/diag*100),'volume_error_pct':float(abs(abs(actual.volume)-abs(source.volume))/max(abs(source.volume),1e-12)*100),'bbox_max_error_pct_diagonal':float(abs(actual.bounds-source.bounds).max()/diag*100),'samples_per_direction':6000,'measurement':'sampled point-to-triangle distances to original STL and tessellated reimported STEP; no registration','cad_tessellation_absolute_deflection_normalized':.025}

def passed(q):return q['p95_distance_pct_diagonal']<=.5 and q['mean_distance_pct_diagonal']<=.2 and q['sampled_max_distance_pct_diagonal']<=2 and q['volume_error_pct']<=5

def one(pid):
 p=SRC/f'{pid}.stl';folder=OUT/pid;folder.mkdir(parents=True,exist_ok=True);start=time.time();attempts=[]
 try:
  original=trimesh.load(p,force='mesh');center=original.bounds.mean(0);scale=100/original.extents.max();m=original.copy();m.apply_translation(-center);m.apply_scale(scale)
  spec=None;chosen=None;last_reduced_count=-1
  routes=[('revolve',0)] if int(pid[-3:]) in WHEELS else []
  routes += [('patch',n) for n in [3000,6000,12000,24000,48000,100000] if n<=max(len(m.faces)*2,3000)]
  if pid=='PART_042':routes=[('patch',48000),('patch',100000)]
  for method,target in routes:
   tick=time.time();print(pid,method,target,flush=True)
   try:
    if method=='revolve':
     if pid=='PART_006':
      from reference_tire import build_smooth
      shape=build_smooth().translate(tuple(-center)).scale(scale);spec={'method':'original_tire_revolve','reference_source_sha256':'6c2386a98c8866326526f9c67ce0612f74b8cece4d8acd7aecefe27e36d3921f'}
     else:spec=fit(m);shape=build(spec)
    else:
     reduced=decimate(m,min(target,len(m.faces)));print(pid,'reduced',len(reduced.faces),flush=True)
     repair=None
     components=reduced.split(only_watertight=False)
     if len(components)>1:
      main=max(components,key=lambda x:abs(x.volume));artifacts=[x for x in components if x is not main]
      if main.is_watertight and all(len(x.faces)<=2 and abs(x.volume)<1e-8 for x in artifacts):
       repair={'removed_zero_volume_double_triangle_sheets':len(artifacts),'removed_faces':sum(len(x.faces) for x in artifacts),'original_source_modified':False};reduced=main
     if len(reduced.faces)==last_reduced_count:continue
     last_reduced_count=len(reduced.faces);normals=m.vertex_normals[cKDTree(m.vertices).query(reduced.vertices)[1]]
     strength=.25 if pid=='PART_042' else 1.0;limit=None
     shape=patch_solid(reduced,strength,normals,limit);spec={'method':'cubic_bezier_patch_reconstruction','curvature_strength':strength,'max_normal_projection':limit,'patches':len(reduced.faces),'surface_parameterization':'regular tensor Bezier surface trimmed by a triangular parameter wire','normal_source':'original STL vertex normals at retained control vertices'}
     if repair:spec['simplification_topology_repair']=repair
     if not shape.isValid():
      healed=shape.fix()
      if healed.isValid() and len(healed.Solids())==1:shape=healed;spec['apply_shape_fix']=True
     if not shape.isValid() or len(shape.Solids())!=1:
      for strength in ([.3,.1] if pid=='PART_042' else [.6,.3,.1]):
       print(pid,'retry curvature',strength,flush=True);shape=patch_solid(reduced,strength,normals,.3)
       if shape.isValid() and len(shape.Solids())==1:
        spec.update(curvature_strength=strength,max_normal_projection=.3);break
    if not shape.isValid() or len(shape.Solids())!=1:raise ValueError('CAD must be one valid solid')
    source_shape=shape.scale(1/scale).translate(tuple(center));tmp=folder/'candidate.step';source_shape.exportStep(str(tmp))
    reopened=cq.importers.importStep(str(tmp)).val()
    if pid=='PART_042' and not reopened.isValid():
     from step_patch_repair import repair_patches
     reopened,repairs=repair_patches(reopened,center,scale);reopened.exportStep(str(tmp),precision_mode=1);reopened=cq.importers.importStep(str(tmp)).val();spec.update(repair_step_roundtrip=True,step_patch_repair=True,precision_mode=1,step_patch_repair_details=repairs)
    if not reopened.isValid() or len(reopened.Solids())!=1:raise ValueError('STEP reimport is not one valid solid')
    print(pid,'STEP valid; tessellating',flush=True)
    recovered=reopened.translate(tuple(-center)).scale(scale);tri=tessellate(recovered);q=evaluate(m,tri);ok=passed(q)
    if method=='revolve':ok=q['p95_distance_pct_diagonal']<=.8 and q['mean_distance_pct_diagonal']<=.3 and q['sampled_max_distance_pct_diagonal']<=2 and q['volume_error_pct']<=5
    if spec['method']=='original_tire_revolve':ok=q['p95_distance_pct_diagonal']<=1.0 and q['mean_distance_pct_diagonal']<=.3 and q['sampled_max_distance_pct_diagonal']<=3 and q['volume_error_pct']<=5
    attempts.append({'method':method,'target_faces':target,'metrics':q,'accepted':ok,'seconds':time.time()-tick});dump(folder/'attempts.json',attempts)
    print(pid,'evaluation',json.dumps(q),'accepted',ok,flush=True)
    if ok:
     chosen=(reopened,tri,q,method,spec,reduced if method=='patch' else None);tmp.replace(folder/f'{pid}.step');break
   except Exception as e:
    attempts.append({'method':method,'target_faces':target,'error':str(e)});dump(folder/'attempts.json',attempts);print(pid,'attempt failed',repr(e),flush=True)
  if chosen is None:raise RuntimeError('No candidate met validity and approximation thresholds')
  reopened,tri,q,method,spec,reduced=chosen
  spec.update(center=center.tolist(),construction_scale=scale,source_numeric_coordinates_preserved=True,source_physical_units='unknown',step_unit='mm')
  if method=='patch':np.savez_compressed(folder/'control_mesh.npz',vertices=reduced.vertices,faces=reduced.faces,normals=normals)
  dump(folder/'parameters.json',spec);reopened.exportBrep(str(folder/f'{pid}.brep'))
  tri.apply_scale(1/scale);tri.apply_translation(center);tri.export(folder/f'{pid}_preview.stl')
  (folder/f'{pid}_cad.py').write_text("from pathlib import Path\nimport sys\nsys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))\nfrom rebuild import rebuild\nif __name__=='__main__': rebuild(Path(__file__).resolve().parent)\n",encoding='utf-8')
  report={'part':pid,'status':'SUCCESS','source_path':'/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/tank/xpart_parts/'+p.name,'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'source_faces':len(original.faces),'method':spec['method'],'cad_faces':len(reopened.Faces()),'cad_solids':len(reopened.Solids()),'step_valid':bool(reopened.isValid()),'source_bounds':original.bounds.tolist(),'quality':q,'seconds':time.time()-start,'attempt_count':len(attempts),'limitations':'Approximate fitted geometry; original design history is not recovered. Bezier patch joins share boundaries but global G1/G2 continuity is not guaranteed.'}
  dump(folder/'report.json',report);return report
 except Exception as e:
  report={'part':pid,'status':'FAILED','error':str(e),'traceback':traceback.format_exc(),'seconds':time.time()-start};dump(folder/'report.json',report);return report

if __name__=='__main__':
 OUT.mkdir(parents=True,exist_ok=True);ids=sys.argv[1:] or [p.stem for p in sorted(SRC.glob('*.stl'))];rows=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=3) as pool:
  futures={pool.submit(one,p):p for p in ids}
  for f in concurrent.futures.as_completed(futures):
   r=f.result();rows.append(r);dump(OUT/'batch_progress.json',{'total':len(ids),'processed':len(rows),'results':rows});print('COMPLETE',r['part'],r['status'],flush=True)
 dump(OUT/'batch_report.json',rows)
