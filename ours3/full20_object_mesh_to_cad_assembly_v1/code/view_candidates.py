import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import sys,json,numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,str(Path(__file__).parent));import pipeline as p
names=['fire_truck','android_figure_orange','aroma_stainless_steel_milk_frother_2_cup','mini_excavator','baby_car']
out=p.O/'reports/camera_review';out.mkdir(exist_ok=True);sheet=Image.new('RGB',(1500,400*len(names)),'white');dr=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
 d=p.O/'objects'/name;f=json.loads((d/'OBJECT_FRAME.json').read_text());m=p.mesh(next(d.glob('full_mesh.*')));xyz=(m.vertices-f['center'])*f['scale']
 for j,up in enumerate([(1,0,0),(0,1,0),(0,0,1)]):
  pd=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(xyz,deep=True));pd.SetPoints(v);cs=vtk.vtkCellArray();cs.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].ravel().astype(np.int64),deep=True));pd.SetPolys(cs);norm=vtk.vtkPolyDataNormals();norm.SetInputData(pd);norm.SplittingOff();norm.Update();mp=vtk.vtkPolyDataMapper();mp.SetInputConnection(norm.GetOutputPort());a=vtk.vtkActor();a.SetMapper(mp);a.GetProperty().SetColor(.55,.65,.75);ren=vtk.vtkRenderer();ren.SetBackground(.96,.97,.98);ren.AddActor(a);cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetPosition(2.5,1.8,2.8);cam.SetViewUp(*up);cam.SetFocalPoint(0,0,0);ren.ResetCamera();win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(500,350);win.AddRenderer(ren);win.Render();cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update();im=Image.fromarray(vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(350,500,3)[::-1].copy());win.Finalize();sheet.paste(im,(j*500,i*400));dr.text((j*500+20,i*400+360),name+' | UP '+'XYZ'[j],font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',15),fill='black')
sheet.save(out/'up_axis_contact_sheet.png')
