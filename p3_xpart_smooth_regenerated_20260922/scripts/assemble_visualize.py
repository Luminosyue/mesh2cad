"""Assemble the regenerated native CAD in source coordinates and render each case."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['LP_NUM_THREADS']='2';os.environ['VTK_SMP_MAX_THREADS']='2'
from pathlib import Path
import json,sys,time,subprocess,gzip,base64,hashlib,urllib.request,html,zipfile
from concurrent.futures import ThreadPoolExecutor
import numpy as np,trimesh,cadquery as cq,vtk
from vtk.util.numpy_support import numpy_to_vtk,numpy_to_vtkIdTypeArray,vtk_to_numpy
from PIL import Image,ImageDraw,ImageFont
vtk.vtkMultiThreader.SetGlobalMaximumNumberOfThreads(2);vtk.vtkSMPTools.Initialize(2)
ROOT=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922');OUT=ROOT/'assemblies';SCRIPTS=Path(__file__).parent
BG=(.95,.968,.98);BLUE=(.44,.69,.82);AMBER=(.91,.56,.23)
PALETTE=[(.38,.66,.82),(.9,.65,.39),(.49,.73,.63),(.72,.6,.8),(.84,.49,.51),(.5,.71,.78),(.75,.74,.48),(.55,.6,.8)]
def font(n):return ImageFont.truetype(str(SCRIPTS/'msyh.ttc'),n)
def dump(p,o):p.write_text(json.dumps(o,indent=2,ensure_ascii=False),encoding='utf-8')
def polydata(m):
    pd=vtk.vtkPolyData();pts=vtk.vtkPoints();pts.SetData(numpy_to_vtk(np.array(m.vertices),deep=True));pd.SetPoints(pts);cells=vtk.vtkCellArray();cells.SetCells(len(m.faces),numpy_to_vtkIdTypeArray(np.c_[np.full(len(m.faces),3),m.faces].ravel().astype(np.int64),deep=True));pd.SetPolys(cells)
    n=vtk.vtkPolyDataNormals();n.SetInputData(pd);n.SplittingOn();n.SetFeatureAngle(45);n.ConsistencyOn();n.ComputePointNormalsOn();n.Update();result=vtk.vtkPolyData();result.DeepCopy(n.GetOutput());return result
def render(parts,mode='blue',view='iso',source=False,edges=False):
    ren=vtk.vtkRenderer();ren.SetBackground(*BG)
    for p in parts:
        pd=p['source_poly'] if source else p['poly'];mp=vtk.vtkPolyDataMapper();mp.SetInputData(pd);a=vtk.vtkActor();a.SetMapper(mp);pr=a.GetProperty();pr.SetColor(*((.64,.72,.76) if source else p['color'] if mode=='parts' else AMBER if mode=='quality' and p['status']!='ACCEPTED' else BLUE));pr.SetAmbient(.3);pr.SetDiffuse(.67);pr.SetSpecular(.18);pr.SetSpecularPower(30);pr.SetInterpolationToPhong();ren.AddActor(a)
        if edges and not source:
            pts=vtk.vtkPoints();cells=vtk.vtkCellArray()
            for line in p['curves']:
                pl=vtk.vtkPolyLine();pl.GetPointIds().SetNumberOfIds(len(line))
                for j,v in enumerate(line):pl.GetPointIds().SetId(j,pts.InsertNextPoint(*v))
                cells.InsertNextCell(pl)
            pd2=vtk.vtkPolyData();pd2.SetPoints(pts);pd2.SetLines(cells);mp2=vtk.vtkPolyDataMapper();mp2.SetInputData(pd2);a2=vtk.vtkActor();a2.SetMapper(mp2);a2.GetProperty().SetColor(.12,.25,.33);a2.GetProperty().SetLineWidth(1.2);a2.GetProperty().LightingOff();ren.AddActor(a2)
    cam=ren.GetActiveCamera();cam.ParallelProjectionOn();cam.SetFocalPoint(0,0,0);cam.SetPosition(*({'iso':(2.8,-2.8,2.8),'front':(0,-4,0),'top':(0,0,4)}[view]));cam.SetViewUp(*( (0,1,0) if view=='top' else (0,0,1)));cam.SetParallelScale(.68);ren.ResetCameraClippingRange()
    win=vtk.vtkRenderWindow();win.SetOffScreenRendering(1);win.SetSize(1000,740);win.SetMultiSamples(8);win.AddRenderer(ren);win.Render();capture=vtk.vtkWindowToImageFilter();capture.SetInput(win);capture.SetInputBufferTypeToRGB();capture.ReadFrontBufferOff();capture.Update();arr=vtk_to_numpy(capture.GetOutput().GetPointData().GetScalars()).reshape(740,1000,3);im=Image.fromarray(np.flipud(arr).copy());win.Finalize();return im
def title(draw,text,xy,maxwidth=1880,size=32):
    while draw.textbbox((0,0),text,font=font(size))[2]>maxwidth:size-=1
    draw.text(xy,text,font=font(size),fill='#213e53')
def interactive(parts,case,od,report):
    chunks=[];offset=0;records=[]
    def add(a,dtype):
        nonlocal offset
        a=np.asarray(a,dtype=dtype).ravel();b=a.tobytes();desc=dict(offset=offset,count=len(a));chunks.append(b);offset+=len(b);return desc
    budget=max(2500,min(15000,220000//len(parts)))
    for p in parts:
        m=p['mesh'];display=m
        if len(m.faces)>budget:
            import open3d as o3d
            om=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(m.vertices),o3d.utility.Vector3iVector(m.faces)).simplify_quadric_decimation(budget)
            display=trimesh.Trimesh(np.asarray(om.vertices),np.asarray(om.triangles),process=False)
        pd=polydata(display);positions=vtk_to_numpy(pd.GetPoints().GetData());normals=vtk_to_numpy(pd.GetPointData().GetNormals());indices=vtk_to_numpy(pd.GetPolys().GetData()).reshape(-1,4)[:,1:]
        lines=np.concatenate([np.stack([q[:-1],q[1:]],axis=1).reshape(-1,3) for q in p['curves']],axis=0) if p['curves'] else np.empty((0,3))
        records.append(dict(id=p['id'],status=p['status'],color=p['color'],center=p['mesh'].bounds.mean(0).tolist(),positions=add(positions,'<f4'),normals=add(normals,'<f4'),indices=add(indices,'<u4'),edges=add(lines,'<f4')))
    payload=base64.b64encode(gzip.compress(b''.join(chunks),compresslevel=6)).decode();template=(SCRIPTS/'assembly_viewer.html').read_text(encoding='utf-8');counts=f'{len(parts)} 个零件 · {report["accepted"]} 件通过 / {report["needs_refinement"]} 件待改进'
    page=template.replace('__CASE__',html.escape(case)).replace('__COUNTS__',counts).replace('__MANIFEST__',json.dumps(dict(parts=records))).replace('__PAYLOAD__',payload).replace('__THREE__',(SCRIPTS/'three.min.js').read_text())
    (od/'interactive.html').write_text(page,encoding='utf-8')
def one(case):
    start=time.time();od=OUT/case;od.mkdir(parents=True,exist_ok=True);files=sorted((ROOT/'cases'/case).glob('PART_*/report.json'));parts=[];assembly=cq.Assembly(name=case);hashes={}
    for i,rp in enumerate(files):
        r=json.loads(rp.read_text());d=rp.parent;shape=cq.importers.importStep(str(d/'model.step')).val();assert shape.isValid();color=PALETTE[i%len(PALETTE)];assembly.add(shape,name=r['part_id'],color=cq.Color(*color))
        m=trimesh.load(d/'model.stl',force='mesh',process=True);source=trimesh.load(r['source_path'],force='mesh',process=False);xyz=np.load(d/'curve_samples_256.npz')['curve_xyz'];curves=json.loads((d/'curves.json').read_text())['curves'];lines=[]
        for rec,q in zip(curves,xyz):
            if not rec['is_seam']:lines.append(np.vstack([q,q[0]]) if rec['is_closed'] else q)
        parts.append(dict(id=r['part_id'],mesh=m,source=source,curves=lines,status=r['status'],color=color));hashes[r['part_id']]=hashlib.sha256((d/'model.step').read_bytes()).hexdigest()
    bounds=np.array([p[k].bounds for p in parts for k in ('mesh','source')]);low=bounds[:,0].min(0);high=bounds[:,1].max(0);center=(low+high)/2;extent=float((high-low).max())
    for p in parts:
        p['mesh'].vertices=(p['mesh'].vertices-center)/extent;p['source'].vertices=(p['source'].vertices-center)/extent;p['curves']=[(q-center)/extent for q in p['curves']];p['poly']=polydata(p['mesh']);p['source_poly']=polydata(p['source'])
    assembly.export(str(od/'assembly.step'),mode='default');check=cq.importers.importStep(str(od/'assembly.step')).val();assert check.isValid()
    report=dict(case_id=case,parts=len(parts),accepted=sum(p['status']=='ACCEPTED' for p in parts),needs_refinement=sum(p['status']!='ACCEPTED' for p in parts),coordinate_policy='original part coordinates; identity placement; no Boolean union or registration adjustment',part_step_sha256=hashes,assembly_step_valid=True,assembly_solids=len(check.Solids()),render_center=center.tolist(),render_extent=extent,files=['assembly.step','assembly.png','cover.png','source_vs_assembly.png','interactive.html'])
    iso=render(parts);colored=render(parts,'parts');front=render(parts,view='front');quality=render(parts,'quality');source=render(parts,source=True)
    bg=tuple(round(v*255) for v in BG);canvas=Image.new('RGB',(2000,1720),bg);d=ImageDraw.Draw(canvas);title(d,case+' · 装配 CAD',(55,22));d.text((55,78),f'{len(parts)} 个零件 · 保持原始坐标 · {report["accepted"]} 件拟合通过 / {report["needs_refinement"]} 件待改进',font=font(24),fill='#5a7384')
    for im,label,x,y in [(iso,'整体 · 斜视',0,155),(colored,'部件分色 · 斜视',1000,155),(front,'整体 · 正视',0,960),(quality,'拟合状态 · 橙色零件待改进',1000,960)]:
        canvas.paste(im,(x,y));ImageDraw.Draw(canvas).text((x+55,y-39),label,font=font(26),fill='#234356')
    canvas.save(od/'assembly.png');cover=Image.new('RGB',(1000,850),bg);cover.paste(iso,(0,68));d=ImageDraw.Draw(cover);title(d,case,(35,18),920,27);d.text((35,803),f'{len(parts)} 个零件 | {report["needs_refinement"]} 件待改进',font=font(22),fill='#587181');cover.save(od/'cover.png')
    compare=Image.new('RGB',(2000,870),bg);compare.paste(source,(0,90));compare.paste(iso,(1000,90));d=ImageDraw.Draw(compare);title(d,'原始零件拼合',(55,22));title(d,'新 CAD 拼合',(1055,22));d.text((55,825),'同一坐标 / 同一比例 · CAD 的局部拟合误差可能影响拼合外观',font=font(22),fill='#587181');compare.save(od/'source_vs_assembly.png')
    interactive(parts,case,od,report);report['seconds']=time.time()-start;report['complete']=True;dump(od/'assembly_report.json',report);print(case,'COMPLETE',len(parts),round(report['seconds'],1),flush=True)
def package():
    review=OUT/'review';review.mkdir(exist_ok=True);records=[];cases=sorted(p for p in OUT.iterdir() if (p/'assembly_report.json').exists())
    assert len(cases)==77, f'Expected 77 completed case assemblies, found {len(cases)}'
    for case in cases:
        r=json.loads((case/'assembly_report.json').read_text());r['slug']=case.name;dest=review/case.name;dest.mkdir(exist_ok=True)
        import shutil
        for name in ('cover.png','assembly.png','source_vs_assembly.png','interactive.html','assembly_report.json'):shutil.copy2(case/name,dest/name)
        records.append(r)
    assert sum(r['parts'] for r in records)==793
    overview=Image.new('RGB',(2800,3500),'#edf3f7');d=ImageDraw.Draw(overview);title(d,'77 个 case · 拼合 CAD 总览',(45,25),2700,44);d.text((45,88),'保持原始零件坐标 · 各格单独缩放 · tank 跳过 · 局部拟合问题见逐 case 预览',font=font(26),fill='#566f80')
    for i,case in enumerate(cases):
        with Image.open(case/'cover.png') as im:
            im=im.crop((50,100,950,760));im.thumbnail((386,245));x=10+(i%7)*400;y=145+(i//7)*302;overview.paste(im,(x+(386-im.width)//2,y))
        name=case.name;label=name if len(name)<34 else name[:31]+'…';title(d,label,(15+(i%7)*400,145+(i//7)*302+247),375,16)
    overview.save(review/'overview.png')
    cards=[]
    for r in records:
        slug=html.escape(r['slug']);cards.append(f'<article data-case="{slug}"><a href="{slug}/interactive.html"><img src="{slug}/cover.png" loading="lazy"></a><h2>{slug}</h2><p>{r["parts"]} 个零件 · {r["accepted"]} 件通过 / {r["needs_refinement"]} 件待改进</p><nav><a href="{slug}/interactive.html">旋转查看 3D</a><a href="{slug}/assembly.png">装配四视图</a><a href="{slug}/source_vs_assembly.png">原始 / CAD 对比</a></nav></article>')
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>拼合 CAD · 全部案例</title><style>body{background:#eef4f8;color:#243f52;font:15px system-ui,'Microsoft YaHei';margin:0}header,main{max-width:1480px;margin:auto;padding:25px}h1{font-size:28px}p{line-height:1.7}#grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(330px,1fr));gap:22px}article{background:white;border-radius:10px;border:1px solid #d9e3e9;overflow:hidden}article img{width:100%;display:block}article h2{font-size:16px;overflow-wrap:anywhere;margin:14px 18px}article p,nav{margin:12px 18px}nav{display:flex;gap:16px;flex-wrap:wrap;padding-bottom:15px}a{color:#216287}input{padding:12px;border:1px solid #b6cad7;border-radius:6px;width:360px;max-width:90%;margin-bottom:22px}</style><header><h1>拼合 CAD · 全部 77 个 case</h1><p>793 个 CAD 零件按原始坐标拼合，保持零件独立。点击模型可旋转、缩放、隐藏零件或拆分查看。<br>橙色状态表示拟合仍待改进；装配完成不代表这些局部误差已消除。tank 已跳过。</p><a href="overview.png">全部案例总览图</a> · <a href="README.md">装配说明与服务器位置</a></header><main><input id="search" placeholder="搜索 case"><div id="grid">__CARDS__</div></main><script>document.getElementById('search').oninput=e=>{document.querySelectorAll('article').forEach(a=>a.hidden=!a.dataset.case.includes(e.target.value.toLowerCase()))}</script></html>'''.replace('__CARDS__',''.join(cards))
    (review/'index.html').write_text(page,encoding='utf-8');dump(review/'manifest.json',records)
    (review/'README.md').write_text(f'所有 77 个非 tank case 的 793 个 CAD 零件按原始数值坐标拼合，未施加额外配准或布尔合并。每个零件保持独立。\n\n精确装配 STEP 位于服务器 `{OUT}/<case>/assembly.step`。\n\n四视图展示整体、部件分色、正视和拟合状态；橙色代表待改进零件。对比图左右保持同一坐标和比例。零件拟合误差仍会出现在装配中。\n\n离线打开 index.html 浏览，进入每个 interactive.html 可旋转、缩放、隐藏零件、显示实际 B-Rep 边界或拆分查看。拆分滑块为 0 时是原始装配位置。交互显示网格经过简化，精确几何请使用 STEP。输入物理单位未确认。\n\nThree.js 0.160.1 (MIT) 已内嵌，不需要联网；使用支持 WebGL 和 DecompressionStream 的现代 Chrome / Edge。\n',encoding='utf-8')
    with zipfile.ZipFile(OUT/'assembly_review.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in review.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(review))
    print('PACKAGED',len(records),sum(r['parts'] for r in records),(OUT/'assembly_review.zip').stat().st_size,flush=True)
def main():
    OUT.mkdir(exist_ok=True)
    if not (SCRIPTS/'three.min.js').exists():urllib.request.urlretrieve('https://cdnjs.cloudflare.com/ajax/libs/three.js/0.160.1/three.min.js',SCRIPTS/'three.min.js')
    if '--case' in sys.argv:return one(sys.argv[sys.argv.index('--case')+1])
    if '--package' in sys.argv:return package()
    cases=sorted(p.name for p in (ROOT/'cases').iterdir() if p.is_dir() and p.name!='tank')
    def run(case):
        od=OUT/case;od.mkdir(exist_ok=True)
        if (od/'assembly_report.json').exists() and '--force' not in sys.argv:return
        with (od/'run.log').open('w') as f:
            try:rr=subprocess.run([sys.executable,__file__,'--case',case],stdout=f,stderr=subprocess.STDOUT,timeout=600);assert rr.returncode==0
            except Exception as e:print('FAILED',case,str(e),flush=True);return
        print('DONE',case,flush=True)
    with ThreadPoolExecutor(max_workers=10) as pool:list(pool.map(run,cases))
    package()
if __name__=='__main__':main()
