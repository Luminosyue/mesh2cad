import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import numpy as np,cadquery as cq,vtk
from vtk.util.numpy_support import numpy_to_vtk
from PIL import Image,ImageDraw,ImageFont
def font(n):return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',n)
def camera_basis(az=35,el=22):
 a=np.deg2rad(az);e=np.deg2rad(el);z=np.array([np.cos(e)*np.sin(a),np.sin(e),np.cos(e)*np.cos(a)]);x=np.cross([0,1,0],z);x/=np.linalg.norm(x);y=np.cross(z,x);return np.c_[x,y,z]
def polydata(vertices,faces,normals=None):
 points=vtk.vtkPoints();points.SetData(numpy_to_vtk(np.asarray(vertices,dtype=np.float64),deep=True));polys=vtk.vtkCellArray()
 for tri in faces:polys.InsertNextCell(3);[polys.InsertCellPoint(int(i)) for i in tri]
 data=vtk.vtkPolyData();data.SetPoints(points);data.SetPolys(polys)
 if normals is not None:
  arr=numpy_to_vtk(np.asarray(normals,dtype=np.float32),deep=True);arr.SetName('Normals');data.GetPointData().SetNormals(arr)
 return data
def actor(data,color=(.45,.64,.78),opacity=1):
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputData(data);a=vtk.vtkActor();a.SetMapper(mapper);p=a.GetProperty();p.SetColor(*color);p.SetOpacity(opacity);p.SetInterpolationToPhong();p.SetAmbient(.25);p.SetDiffuse(.75);p.SetSpecular(.18);p.SetSpecularPower(30);return a
def step_data(path,T,linear_deflection,angular_deflection=.03):
 shape=cq.importers.importStep(str(path)).val();T=np.asarray(T);A=T[:3,:3];translation=T[:3,3];inv=np.linalg.inv(A);vv=[];nn=[];ff=[];normal_fail=0
 for face in shape.Faces():
  vertices,triangles=face.tessellate(linear_deflection,angular_deflection)
  if not triangles:continue
  n=[]
  for v in vertices:
   try:n.append(face.normalAt(v).toTuple())
   except Exception:normal_fail+=1;n.append(face.normalAt().toTuple())
  start=len(vv);vv.extend(np.asarray([v.toTuple() for v in vertices])@A.T+translation);norm=np.asarray(n)@inv;norm/=np.maximum(np.linalg.norm(norm,axis=1,keepdims=True),1e-12);nn.extend(norm);ff.extend(np.asarray(triangles)+start)
 data=polydata(vv,ff,nn);points=vtk.vtkPoints();lines=vtk.vtkCellArray();edge_samples=0
 for edge in shape.Edges():
  vertices,_=edge.sample(2 if edge.geomType()=='LINE' else 300);pts=np.asarray([v.toTuple() for v in vertices])@A.T+translation;start=points.GetNumberOfPoints()
  for p in pts:points.InsertNextPoint(*p)
  lines.InsertNextCell(len(pts))
  for i in range(len(pts)):lines.InsertCellPoint(start+i)
  edge_samples+=len(pts)
 edges=vtk.vtkPolyData();edges.SetPoints(points);edges.SetLines(lines)
 return data,edges,{'face_n':len(shape.Faces()),'display_vertex_n':len(vv),'display_triangle_n':len(ff),'normal_fallback_n':normal_fail,'edge_sample_n':edge_samples,'linear_deflection_local':linear_deflection,'angular_deflection':angular_deflection}
def render(actors,center,span,R,size=800,title='',subtitle='',edge_actors=None):
 ren=vtk.vtkRenderer();ren.SetBackground(247/255,249/255,252/255);win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(size,size);win.SetMultiSamples(4);win.AddRenderer(ren)
 for a in actors:ren.AddActor(a)
 for a in edge_actors or []:ren.AddActor(a)
 cam=ren.GetActiveCamera();cam.ParallelProjectionOn();center=np.asarray(center);cam.SetFocalPoint(*center);cam.SetPosition(*(center+R[:,2]*span*4));cam.SetViewUp(*R[:,1]);cam.SetParallelScale(span/(2*.78));cam.SetWindowCenter(0,.08);ren.ResetCameraClippingRange();win.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update();data=capture.GetOutput();arr=vtk.util.numpy_support.vtk_to_numpy(data.GetPointData().GetScalars()).reshape(size,size,3);im=Image.fromarray(np.flipud(arr));win.Finalize();draw=ImageDraw.Draw(im);draw.rectangle((0,0,size,95*size/800),fill='#f7f9fc');draw.text((24*size/800,18*size/800),title,font=font(int(27*size/800)),fill='#182536');draw.text((24*size/800,58*size/800),subtitle,font=font(int(16*size/800)),fill='#536477');return im
def edge_actor(data):
 a=actor(data,(.10,.16,.23));a.GetProperty().SetLineWidth(1.15);a.GetProperty().LightingOff();a.GetMapper().SetResolveCoincidentTopologyToPolygonOffset();a.GetMapper().SetRelativeCoincidentTopologyLineOffsetParameters(0,-2);return a
