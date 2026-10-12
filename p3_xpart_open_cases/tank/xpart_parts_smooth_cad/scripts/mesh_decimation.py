import numpy as np,trimesh,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
def decimate(mesh,target):
 poly=vtk.vtkPolyData();points=vtk.vtkPoints();points.SetData(numpy_to_vtk(mesh.vertices,deep=True));poly.SetPoints(points)
 cells=vtk.vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(mesh.faces),3),mesh.faces].ravel().astype(np.int64),deep=True));poly.SetPolys(cells)
 dec=vtk.vtkDecimatePro();dec.SetInputData(poly);dec.SetTargetReduction(max(0,1-target/len(mesh.faces)));dec.PreserveTopologyOn();dec.SplittingOff();dec.BoundaryVertexDeletionOff();dec.Update();out=dec.GetOutput()
 return trimesh.Trimesh(vtk_to_numpy(out.GetPoints().GetData()),vtk_to_numpy(out.GetPolys().GetData()).reshape(-1,4)[:,1:],process=True)
