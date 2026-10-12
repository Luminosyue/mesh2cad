import numpy as np, trimesh, vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.TopAbs import TopAbs_REVERSED
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
 return {'mean_distance_pct_diagonal':float(d.mean()/diag*100),'p95_distance_pct_diagonal':float(np.percentile(d,95)/diag*100),'sampled_max_distance_pct_diagonal':float(d.max()/diag*100),'source_to_cad_p95_pct':float(np.percentile(da,95)/diag*100),'cad_to_source_p95_pct':float(np.percentile(db,95)/diag*100),'volume_error_pct':float(abs(abs(actual.volume)-abs(source.volume))/max(abs(source.volume),1e-12)*100),'bbox_max_error_pct_diagonal':float(abs(actual.bounds-source.bounds).max()/diag*100),'samples_per_direction':6000,'measurement':'sampled point-to-triangle distances to original completed OBJ and tessellated reimported STEP; no registration','cad_tessellation_absolute_deflection_normalized':.025}