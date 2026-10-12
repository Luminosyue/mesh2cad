import json
from pathlib import Path
import numpy as np, trimesh, cadquery as cq, vtk
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad'); EXP=ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'; V1=ROOT/'ours3/p3_xpart_20case_compact_ir_v1'; OUT=EXP/'final_eval_v1/renders'; OUT.mkdir(parents=True,exist_ok=True)
manifest={x['CASE_ID']:x for x in json.loads((V1/'CASE_MANIFEST.json').read_text())['cases']}; cases=[('case_018','00'),('case_009','01'),('case_014','tank'),('case_010','03'),('case_005','04')]
def stepmesh(path):
 s=cq.importers.importStep(str(path)).val(); vs,fs=s.tessellate(0.15); return np.array([[float(v.x),float(v.y),float(v.z)] for v in vs]),np.array([[int(t[0]),int(t[1]),int(t[2])] for t in fs])
def actor(verts,faces,color,alpha=1.0):
 pts=vtk.vtkPoints(); pts.SetNumberOfPoints(len(verts)); [pts.SetPoint(i,*map(float,p)) for i,p in enumerate(verts)]
 cells=vtk.vtkCellArray()
 for f in faces:
  tri=vtk.vtkTriangle(); [tri.GetPointIds().SetId(j,int(f[j])) for j in range(3)]; cells.InsertNextCell(tri)
 poly=vtk.vtkPolyData(); poly.SetPoints(pts); poly.SetPolys(cells); a=vtk.vtkActor(); a.SetMapper(vtk.vtkPolyDataMapper()); a.GetMapper().SetInputData(poly); a.GetProperty().SetColor(*color); a.GetProperty().SetOpacity(alpha); a.GetProperty().EdgeVisibilityOff(); a.GetProperty().SetInterpolationToPhong(); return a
def render(path,layers,title):
 ren=vtk.vtkRenderer(); ren.SetBackground(0.96,0.96,0.96); win=vtk.vtkRenderWindow(); win.SetOffScreenRendering(1); win.SetSize(900,700); win.AddRenderer(ren); [ren.AddActor(a) for a in layers]; ren.ResetCamera(); ren.GetActiveCamera().Azimuth(35); ren.GetActiveCamera().Elevation(24); ren.ResetCameraClippingRange(); win.Render(); w2i=vtk.vtkWindowToImageFilter(); w2i.SetInput(win); w2i.Update(); wr=vtk.vtkPNGWriter(); wr.SetFileName(str(path)); wr.SetInputConnection(w2i.GetOutputPort()); wr.Write(); win.Finalize()
for cid,idx in cases:
 mesh=trimesh.load_mesh(manifest[cid]['MESH_PATH'],process=False); mv=np.asarray(mesh.vertices); mf=np.asarray(mesh.faces); gen=EXP/'final_eval_v1/step'/f'{cid}.step'; can=ROOT/'ours3/p3_xpart_20case_compact_ir_v3/step_v3'/f'{cid}.step'; gv,gf=stepmesh(gen); cv,cf=stepmesh(can); stem='tank' if cid=='case_014' else cid
 render(OUT/f'{stem}_input_mesh.png',[actor(mv,mf,(0.20,0.45,0.72))],f'{cid} input mesh'); render(OUT/f'{stem}_generated_brep.png',[actor(gv,gf,(0.25,0.65,0.30))],f'{cid} generated smooth BRep'); render(OUT/f'{stem}_canonical_brep.png',[actor(cv,cf,(0.90,0.48,0.12))],f'{cid} canonical smooth BRep'); render(OUT/f'{stem}_overlay.png',[actor(cv,cf,(0.90,0.48,0.12),0.5),actor(gv,gf,(0.25,0.65,0.30),0.5)],f'{cid} overlay')
(OUT/'TANK_DEMO_CAPTION.txt').write_text('Tank PART_029\n1,529 / 1,529 q-stream exact\nNatural EOS\nSTEP valid\nVolume error 0.0\nGenerated and canonical views are smooth-shaded BRep displays with triangle edges hidden.')
print('rendered',len(cases)*4)
