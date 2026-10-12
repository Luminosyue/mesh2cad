from pathlib import Path
import json,sys,os
import numpy as np,trimesh,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent;OUT=Path(os.environ.get('TANK_OUTPUT',str(ROOT.parent/'outputs/tank_cad')));SRC=Path(os.environ.get('TANK_SOURCE',str(ROOT/'tank_input')));FONT='C:/Windows/Fonts/msyh.ttc'
def font(n):return ImageFont.truetype(FONT,n)
def render(m,center,extent,size=(450,360),edges=False,top=False):
 poly=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk((m.vertices-center)/extent,deep=True));poly.SetPoints(pts)
 cells=vtk.vtkCellArray();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].ravel().astype(np.int64),deep=True));poly.SetPolys(cells)
 normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly);normals.SplittingOff();normals.ConsistencyOn();normals.Update()
 mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper);prop=actor.GetProperty();prop.SetColor(.43,.70,.84);prop.SetAmbient(.3);prop.SetDiffuse(.67);prop.SetSpecular(.18);prop.SetSpecularPower(30);prop.SetInterpolationToPhong()
 renderer=vtk.vtkRenderer();renderer.SetBackground(.958,.971,.984);renderer.AddActor(actor);cam=renderer.GetActiveCamera();cam.ParallelProjectionOn();cam.SetPosition(*(np.array([0,0,4.]) if top else [2.8,-2.8,2.8]));cam.SetViewUp(*([0,1,0] if top else [0,0,1]));cam.SetFocalPoint(0,0,0);cam.SetParallelScale(.72);renderer.ResetCameraClippingRange()
 win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(*size);win.SetMultiSamples(8);win.AddRenderer(renderer);win.Render();cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update();arr=vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(size[1],size[0],3);img=Image.fromarray(np.flipud(arr).copy());win.Finalize();return img

def part(pid):
 folder=OUT/pid;report=json.loads((folder/'report.json').read_text());a=trimesh.load(SRC/f'{pid}.stl',force='mesh');b=trimesh.load(folder/f'{pid}_preview.stl',force='mesh');c=a.bounds.mean(0);e=a.extents.max()
 canvas=Image.new('RGB',(900,850),(244,248,251));d=ImageDraw.Draw(canvas);d.text((22,12),pid+' · 原始 STL / 重建 CAD',font=font(24),fill='#19354a')
 for row,top in enumerate([False,True]):
  for col,m in enumerate([a,b]):canvas.paste(render(m,c,e,top=top),(col*450,55+row*365))
 d=ImageDraw.Draw(canvas);method='旋转轮廓' if 'revolve' in report['method'] else 'Bézier 曲面分块';q=report['quality'];d.text((22,793),f"{method} · {report['cad_faces']} 个 CAD 面 · P95 偏差 {q['p95_distance_pct_diagonal']:.3f}% 对角线",font=font(20),fill='#365369');canvas.save(folder/f'{pid}_comparison.png');return canvas

if __name__=='__main__':
 gallery_only='--gallery-only' in sys.argv
 ids=([] if gallery_only else sys.argv[1:]) or [p.parent.name for p in sorted(OUT.glob('PART_*/report.json')) if json.loads(p.read_text()).get('status')=='SUCCESS']
 if not gallery_only:
  for pid in ids:part(pid);print(pid,flush=True)
 if len(ids)==45:
  for page in range(3):
   sheet=Image.new('RGB',(1800,1700),(244,248,251));d=ImageDraw.Draw(sheet);d.text((25,10),f'坦克零件 CAD 重建 · {page+1}/3 · 每组左 STL，右 CAD',font=font(30),fill='#19354a')
   for k,pid in enumerate(ids[page*15:page*15+15]):
    im=Image.open(OUT/pid/f'{pid}_comparison.png');im=im.crop((0,0,900,420)).resize((600,280));x=k%3*600;y=k//3*325+60;sheet.paste(im,(x,y));r=json.loads((OUT/pid/'report.json').read_text());d.text((x+15,y+285),f"{r['cad_faces']} 面 | P95 {r['quality']['p95_distance_pct_diagonal']:.3f}%",font=font(19),fill='#365369')
   sheet.save(OUT/f'comparison_gallery_{page+1}.png')
