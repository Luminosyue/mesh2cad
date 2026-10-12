import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[k]='1'
from pathlib import Path
import json,sys,base64,colorsys,traceback,subprocess,concurrent.futures,signal,time
import numpy as np,trimesh,cadquery as cq,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
from rebuild_cases import ROOT,CODE,RUN,dump

def poly(m,center,extent):
    p=vtk.vtkPolyData();v=vtk.vtkPoints();v.SetData(numpy_to_vtk((m.vertices-center)/extent,deep=True));p.SetPoints(v)
    c=vtk.vtkCellArray();c.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].ravel().astype(np.int64),deep=True));p.SetPolys(c);return p

def render(meshes,colors,view=(2.7,2.2,3),size=(1100,800)):
    ren=vtk.vtkRenderer();ren.SetBackground(.95,.97,.98)
    for m,c in zip(meshes,colors):
        normals=vtk.vtkPolyDataNormals();normals.SetInputData(poly(m,np.zeros(3),1));normals.SplittingOff();normals.Update()
        mapper=vtk.vtkPolyDataMapper();mapper.SetInputConnection(normals.GetOutputPort());actor=vtk.vtkActor();actor.SetMapper(mapper);prop=actor.GetProperty();prop.SetColor(*c);prop.SetAmbient(.3);prop.SetDiffuse(.7);prop.SetSpecular(.15);ren.AddActor(actor)
    cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetPosition(*view);cam.SetFocalPoint(0,0,0);cam.SetViewUp(*((0,0,1) if abs(view[1])>3 else (0,1,0)));ren.ResetCamera();cam.Zoom(1.12);ren.ResetCameraClippingRange()
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(*size);win.SetMultiSamples(4);win.AddRenderer(ren);win.Render();cap=vtk.vtkWindowToImageFilter();cap.SetInput(win);cap.Update()
    a=vtk_to_numpy(cap.GetOutput().GetPointData().GetScalars()).reshape(size[1],size[0],3);im=Image.fromarray(a[::-1].copy());win.Finalize();return im

def assemble(name):
    case=ROOT/name;src=case/'xpart_parts_cadquery_features';out=case/'xpart_parts_cadquery_assembly';out.mkdir(exist_ok=True)
    source_files=sorted((case/'xpart_parts').rglob('complete*.obj'));rows=[];missing=[];meshes=[];originals=[];colors=[];shapes=[];assy=cq.Assembly(name=name)
    for i,f in enumerate(source_files):
        pid=f.parent.name;folder=src/pid
        if not (folder/'report.json').exists():missing.append(pid);continue
        r=json.loads((folder/'report.json').read_text());s=cq.importers.importStep(str(folder/f'{pid}.step')).val()
        assert s.isValid() and len(s.Solids())==r['cad_solids']
        col=colorsys.hsv_to_rgb((i*.618)%1,.32,.78);colors.append(col);assy.add(s,name=pid,color=cq.Color(*col));shapes.append(s)
        meshes.append(trimesh.load(folder/f'{pid}_preview.stl',force='mesh'));originals.append(trimesh.load(f,force='mesh'));rows.append(r)
    if not rows:raise RuntimeError('No CAD parts available')
    assy.export(str(out/f'{name}_assembly.step'));s=cq.importers.importStep(str(out/f'{name}_assembly.step')).val();assert s.isValid()
    expected=sum(r['cad_solids'] for r in rows);assert len(s.Solids())==expected
    lo=np.min([m.bounds[0] for m in originals],axis=0);hi=np.max([m.bounds[1] for m in originals],axis=0);center=(lo+hi)/2;extent=(hi-lo).max()
    data=[];scene=trimesh.Scene();visuals=[];offsets={}
    for i,(m,r,col) in enumerate(zip(meshes,rows,colors)):
        m.apply_translation(-center);m.apply_scale(1/extent)
        d=vtk.vtkDecimatePro();d.SetInputData(poly(m,np.zeros(3),1));d.SetTargetReduction(max(0,1-9000/len(m.faces)));d.PreserveTopologyOn();d.Update();p=d.GetOutput()
        visual=trimesh.Trimesh(vtk_to_numpy(p.GetPoints().GetData()),vtk_to_numpy(p.GetPolys().GetData()).reshape(-1,4)[:,1:],process=False);visuals.append(visual)
        visual.visual.vertex_colors=np.tile(np.array([*col,1])*255,(len(visual.vertices),1)).astype(np.uint8);scene.add_geometry(visual,node_name=r['part'],geom_name=r['part'])
        iv=np.c_[visual.vertices,visual.vertex_normals].astype('<f4');idx=np.asarray(visual.faces,dtype='<u4')
        data.append(dict(name=r['part'],color=col,review=r['status']!='APPROXIMATION_ACCEPTED',v=base64.b64encode(iv.tobytes()).decode(),f=base64.b64encode(idx.tobytes()).decode(),count=idx.size))
        offsets[r['part']]=(m.bounds.mean(0)*1.4).tolist()
    scene.export(out/f'{name}_preview.glb')
    template=(CODE/'tank_viewer_template.html').read_text(encoding='utf-8')
    import re,html
    template=re.sub(r'<title>.*?</title>',f'<title>{html.escape(name)} CAD</title>',template)
    template=re.sub(r'<h1>.*?</h1>',f'<h1>{html.escape(name)} · CadQuery 装配</h1>',template)
    review=sum(r['status']!='APPROXIMATION_ACCEPTED' for r in rows)
    note=f'原始坐标装配 · {len(rows)}/{len(source_files)} 个零件 / {expected} 个实体<br>{review} 件需要细化；缺失 {len(missing)} 件。爆炸位移仅作展示。'
    template=re.sub(r'<div class="note">.*?</div>',f'<div class="note">{note}</div>',template)
    template=template.replace('<aside>','<aside><label>爆炸程度 <input id="explode" type="range" min="0" max="1" step="0.01" value="0" style="width:165px"></label>')
    template=template.replace('uniform mat4 vp;varying','uniform mat4 vp;uniform vec3 offset;varying').replace('vec4(pos,1.)','vec4(pos+offset,1.)')
    template=template.replace('let yaw=.84,pitch=.50,dist=1.85;',"const exploded="+json.dumps(offsets)+";const off=gl.getUniformLocation(p,'offset');let yaw=.84,pitch=.50,dist=2.3;")
    template=template.replace('gl.drawElements(gl.TRIANGLES,d.count',"gl.uniform3fv(off,new Float32Array(exploded[d.name].map(x=>x*document.getElementById('explode').value)));gl.drawElements(gl.TRIANGLES,d.count")
    template=template.replace('onresize=draw;draw();',"document.getElementById('explode').oninput=()=>{dist=2.3+Number(document.getElementById('explode').value)*2;draw()};onresize=draw;draw();")
    (out/f'{name}_viewer.html').write_text(template.replace('__DATA__',json.dumps(data)),encoding='utf-8')
    render(visuals,colors).save(out/f'{name}_assembly.png')
    sheet=Image.new('RGB',(1800,1350),'#f2f7fa');font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',22)
    for k,(label,view) in enumerate([('Perspective',(2.7,2.2,3)),('Reverse',(-2.7,2.2,-3)),('Top',(0,4,0)),('Side',(0,0,3))]):
        x=k%2*900;y=k//2*675;sheet.paste(render(visuals,colors,view,(900,630)),(x,y+40));ImageDraw.Draw(sheet).text((x+25,y+8),label,font=font,fill='#254254')
    sheet.save(out/f'{name}_multiview.png')
    for m in originals:m.apply_translation(-center);m.apply_scale(1/extent)
    comparison=Image.new('RGB',(1800,740),'#f2f7fa');comparison.paste(render(originals,[(.4,.63,.73)]*len(originals),size=(900,680)),(0,45));comparison.paste(render(visuals,[(.4,.63,.73)]*len(visuals),size=(900,680)),(900,45));d=ImageDraw.Draw(comparison);d.text((20,10),'Completed input OBJ',font=font,fill='#254254');d.text((920,10),'Reconstructed CAD',font=font,fill='#254254');comparison.save(out/f'{name}_comparison.png')
    exploded=[]
    for m,r in zip(visuals,rows):n=m.copy();n.apply_translation(offsets[r['part']]);exploded.append(n)
    render(exploded,colors,size=(1500,1100)).save(out/f'{name}_exploded.png');dump(out/'explosion_offsets.json',dict(normalized_translations=offsets,source_extent=float(extent),note='Illustrative radial explosion; not a disassembly sequence'))
    report=dict(case=name,source_parts=len(source_files),part_count=len(rows),missing_parts=missing,solid_count=expected,assembly_step_valid=True,review_parts=review,complete_assembly=not missing,parts=rows,units='Original numeric coordinates preserved; physical units unknown',method='Identity placement; no mechanical mates inferred')
    dump(out/'assembly_report.json',report)
    rebuild='from pathlib import Path\nimport cadquery as cq\nr=Path(__file__).resolve().parent\na=cq.Assembly(name='+repr(name)+')\nfor p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):\n    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)\na.export(str(r/'+repr(name+'_assembly.step')+'))\n'
    (out/'rebuild_assembly.py').write_text(rebuild)
    readme=f'# {name} CadQuery 重建\n\n重建零件 {len(rows)}/{len(source_files)}；待细化 {review}；缺失 {missing}。\n\n逐件代码和 STEP 位于 ../xpart_parts_cadquery_features。代码可独立运行，仅依赖 CadQuery。基于截面推断拉伸、旋转、放样或少量轮廓凸台，不是原设计特征树。\n\n质量筛选：双向各 6000 个采样点到三角面距离，P95≤对角线1%、采样最大值≤4%、体积误差≤10%；这是探索性筛选，不是制造公差。原始数值坐标保留，输入物理单位未知。多个实体和误差详见报告。\n\nHTML 可旋转、隐藏零件和切换爆炸展示。爆炸图按质心径向位移，不代表拆卸顺序。预览可简化，STEP 保持重建几何。\n'
    (out/'README.md').write_text(readme,encoding='utf-8');(src/'README.md').write_text(readme,encoding='utf-8');dump(src/'summary.json',report)
    print('ASSEMBLED',name,len(rows),len(missing),flush=True)

def all_cases(names):
    cases=[c.name for c in sorted(ROOT.iterdir()) if c.name!='tank' and (c/'xpart_parts_cadquery_features').is_dir() and (not names or c.name in names)]
    def one(name):
        out=ROOT/name/'xpart_parts_cadquery_assembly';out.mkdir(exist_ok=True)
        if (out/'assembly_report.json').exists():return dict(case=name,status='DONE')
        with (out/'assembly.log').open('w') as log:
            p=subprocess.Popen(['xvfb-run','-a',sys.executable,str(__file__),'case',name],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:rc=p.wait(timeout=600)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();rc=-9
        return dict(case=name,status='DONE' if rc==0 else 'FAILED',returncode=rc)
    rows=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        for r in pool.map(one,cases):rows.append(r);dump(RUN/'assembly_progress.json',rows);print(r,flush=True)

def watch():
    tasks=json.loads((RUN/'task_manifest.json').read_text())['tasks'];cases={}
    for case,pid in tasks:cases.setdefault(case,[]).append(pid)
    submitted=set();futures={};rows=[]
    def launch(name):
        out=ROOT/name/'xpart_parts_cadquery_assembly';out.mkdir(exist_ok=True)
        if (out/'assembly_report.json').exists():return dict(case=name,status='DONE')
        with (out/'assembly.log').open('w') as log:
            p=subprocess.Popen(['xvfb-run','-a',sys.executable,str(__file__),'case',name],stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
            try:rc=p.wait(timeout=600)
            except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait();rc=-9
        return dict(case=name,status='DONE' if rc==0 else 'FAILED',returncode=rc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        while len(rows)<len(cases):
            for name,ids in cases.items():
                if name not in submitted and all((ROOT/name/'xpart_parts_cadquery_features'/pid/'job_status.json').exists() for pid in ids):
                    submitted.add(name);futures[pool.submit(launch,name)]=name
            for f in list(futures):
                if f.done():
                    try:r=f.result()
                    except Exception as e:r=dict(case=futures[f],status='FAILED',error=str(e))
                    rows.append(r);del futures[f];print(r,flush=True)
            dump(RUN/'assembly_progress.json',rows);time.sleep(12)

if __name__=='__main__':
    if sys.argv[1]=='case':assemble(sys.argv[2])
    elif sys.argv[1]=='watch':watch()
    else:all_cases(sys.argv[2:])
