from pathlib import Path
import json
import numpy as np
import vtk
vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(2)
vtk.vtkSMPTools.Initialize(2)
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
from OCP.BRep import BRep_Tool
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_UniformAbscissa
BG=(.958,.971,.984)

def extract(shape):
    curves=[];samples=[];faces=shape.Faces()
    for idx,e in enumerate(shape.Edges()):
        if BRep_Tool.Degenerated_s(e.wrapped):continue
        ad=BRepAdaptor_Curve(e.wrapped);u0,u1=ad.FirstParameter(),ad.LastParameter()
        if not np.isfinite([u0,u1]).all():continue
        closed=e.IsClosed();adj=[i for i,f in enumerate(faces) if any(e.isSame(ee) for ee in f.Edges())]
        seam=any(BRep_Tool.IsClosed_s(e.wrapped,faces[i].wrapped) for i in adj)
        n=257 if closed else 256
        sampler=GCPnts_UniformAbscissa(ad,n,u0,u1,1e-9)
        if sampler.IsDone() and sampler.NbPoints()==n:
            us=[sampler.Parameter(i+1) for i in range(n)];mode='equal_arc_length'
        else:us=np.linspace(u0,u1,n);mode='uniform_parameter_fallback'
        if closed:us=us[:-1]
        points=np.array([[ad.Value(float(u)).X(),ad.Value(float(u)).Y(),ad.Value(float(u)).Z()] for u in us])
        rec=dict(edge_id=idx,curve_type=e.geomType(),is_closed=bool(closed),is_seam=bool(seam),face_ids=adj,u_range=[u0,u1],length=e.Length(),sampling=mode)
        if e.geomType()=='CIRCLE':
            c=ad.Circle();rec['parameters']=dict(center=[c.Location().X(),c.Location().Y(),c.Location().Z()],radius=c.Radius(),normal=[c.Axis().Direction().X(),c.Axis().Direction().Y(),c.Axis().Direction().Z()])
        elif e.geomType()=='BSPLINE':
            b=ad.BSpline();rec['parameters']=dict(degree=b.Degree(),poles=[[b.Pole(j).X(),b.Pole(j).Y(),b.Pole(j).Z()] for j in range(1,b.NbPoles()+1)],knots=[b.Knot(j) for j in range(1,b.NbKnots()+1)],multiplicities=[b.Multiplicity(j) for j in range(1,b.NbKnots()+1)],weights=[b.Weight(j) for j in range(1,b.NbPoles()+1)],periodic=b.IsPeriodic())
        samples.append(points);curves.append(rec)
    return curves,np.asarray(samples)

def render(mesh,curves,records,surface,top):
    renderer=vtk.vtkRenderer();renderer.SetBackground(*BG)
    if surface:
        p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk(mesh.vertices.copy(),deep=True));p.SetPoints(v)
        cells=vtk.vtkCellArray();cells.SetCells(len(mesh.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(mesh.faces),3),mesh.faces].ravel().astype(np.int64),deep=True));p.SetPolys(cells)
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(p);normals.SplittingOn();normals.SetFeatureAngle(45);normals.ConsistencyOn();normals.ComputePointNormalsOn();normals.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());mapper.SetResolveCoincidentTopologyToPolygonOffset();mapper.SetRelativeCoincidentTopologyPolygonOffsetParameters(1,1)
        actor=vtk.vtkActor();actor.SetMapper(mapper);prop=actor.GetProperty();prop.SetColor(.43,.70,.84);prop.SetAmbient(.3);prop.SetDiffuse(.67);prop.SetSpecular(.18);prop.SetSpecularPower(30);prop.SetInterpolationToPhong();renderer.AddActor(actor)
    pts=vtk.vtkPoints();cells=vtk.vtkCellArray()
    for rec,points in zip(records,curves):
        if rec['is_seam']:continue
        if rec['is_closed']:points=np.vstack([points,points[0]])
        line=vtk.vtkPolyLine();line.GetPointIds().SetNumberOfIds(len(points))
        for j,p in enumerate(points):line.GetPointIds().SetId(j,pts.InsertNextPoint(*p))
        cells.InsertNextCell(line)
    poly=vtk.vtkPolyData();poly.SetPoints(pts);poly.SetLines(cells);tube=vtk.vtkTubeFilter();tube.SetInputData(poly);tube.SetRadius(.0013);tube.SetNumberOfSides(8);tube.CappingOn()
    mp=vtk.vtkPolyDataMapper();mp.SetInputConnection(tube.GetOutputPort());a=vtk.vtkActor();a.SetMapper(mp);a.GetProperty().SetColor(.1,.26,.38);a.GetProperty().LightingOff();renderer.AddActor(a)
    cam=renderer.GetActiveCamera();cam.ParallelProjectionOn();cam.SetFocalPoint(0,0,0);cam.SetPosition(*([0,0,4] if top else [2.8,-2.8,2.8]));cam.SetViewUp(*([0,1,0] if top else [0,0,1]));cam.SetParallelScale(.70);renderer.ResetCameraClippingRange()
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1000,720);win.SetMultiSamples(8);win.AddRenderer(renderer);win.Render()
    capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update();arr=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(720,1000,3)
    result=Image.fromarray(np.flipud(arr).copy());win.Finalize();return result

def extract_and_render(shape,mesh,od,report,source=None):
    records,xyz=extract(shape)
    (od/'curves.json').write_text(json.dumps(dict(source='model.step',curves=records),indent=2))
    np.savez_compressed(od/'curve_samples_256.npz',curve_xyz=xyz,edge_id=np.array([r['edge_id'] for r in records]))
    center=mesh.bounds.mean(0);extent=mesh.extents.max();m=mesh.copy();m.vertices=(mesh.vertices-center)/extent;normalized=(xyz-center)/extent
    (od/'render_transform.json').write_text(json.dumps(dict(center=center.tolist(),scale=1/float(extent),coordinate_space='original source coordinates in model and samples; normalization is rendering-only')))
    fonts=Path(__file__).parent/'msyh.ttc'
    def font(n):return ImageFont.truetype(str(fonts),n)
    canvas=Image.new('RGB',(2000,1630),tuple(round(c*255) for c in BG));d=ImageDraw.Draw(canvas)
    label=report['case_id']+' / '+report['part_id']
    size=32
    while d.textbbox((0,0),label,font=font(size))[2]>1880:size-=1
    d.text((65,24),label,font=font(size),fill='#19354a');d.text((65,92),'曲面 + B-Rep 边界',font=font(28),fill='#19354a');d.text((1065,92),'仅 B-Rep 边界',font=font(28),fill='#19354a')
    for row,top in enumerate([False,True]):
        for col,surface in enumerate([True,False]):canvas.paste(render(m,normalized,records,surface,top),(col*1000,145+row*710))
    n=sum(not r['is_seam'] for r in records);s=sum(r['is_seam'] for r in records);q=report['quality'];accepted=report['status']=='ACCEPTED'
    status='拟合通过' if accepted else ('待改进：存在边缘波纹' if report.get('visual_review') else '待改进：拟合误差超限')
    text=f'{n} 条边界 / 隐藏 {s} 条周期接缝  ·  斜视 / 俯视  ·  P95 {q["p95_distance_pct_diagonal"]:.2f}%  ·  {status}'
    ImageDraw.Draw(canvas).text((65,1565),text,font=font(23),fill='#365369' if accepted else '#a54424');canvas.save(od/'surface_boundaries.png')
    if source is not None:
        sm=source.copy();sm.vertices=(source.vertices-center)/extent
        comparison=Image.new('RGB',(2000,860),tuple(round(c*255) for c in BG))
        comparison.paste(render(sm,[],[],True,False),(0,90));comparison.paste(render(m,normalized,records,True,False),(1000,90))
        dr=ImageDraw.Draw(comparison);dr.text((65,20),'源网格',font=font(30),fill='#19354a');dr.text((1065,20),'新拟合 CAD',font=font(30),fill='#19354a');dr.text((65,810),status+' · 同一坐标 / 同一比例',font=font(22),fill='#365369' if accepted else '#a54424');comparison.save(od/'source_vs_cad.png')
    return dict(boundary_count=n,seam_count=s,total_curve_count=len(records))
