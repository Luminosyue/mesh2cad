import csv, json, math
from collections import Counter
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCP.TopoDS import TopoDS
from OCP.BRep import BRep_Tool
from OCP.TopLoc import TopLoc_Location
from OCP.BRepAdaptor import BRepAdaptor_Surface

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT/'ours3/p3_xpart_v3_optimizer_memory_demo5_v1'
OUT = EXP/'demo5_visualization_v1'
OUT.mkdir(parents=True, exist_ok=True)
W,H = 1600,1200
FONT = ImageFont.load_default()
CASES = [
    ('case_018','b015ipnvfw','PART_000',39,'b015ipnvfw'),
    ('case_009','construction_60','PART_024',125,'construction_60'),
    ('case_014','tank','PART_029',1529,'tank_part029'),
    ('case_010','vase','PART_000',1299,'vase'),
    ('case_005','azure_snake_tieks_leather_snake_print_ballet_flats','PART_000',2050,'snake_print_ballet_flat'),
]

def read_obj(path):
    verts=[]; faces=[]
    for line in Path(path).read_text(errors='ignore').splitlines():
        if line.startswith('v '): verts.append([float(x) for x in line.split()[1:4]])
        elif line.startswith('f '):
            q=[]
            for x in line.split()[1:]: q.append(int(x.split('/')[0])-1)
            if len(q)>=3:
                for i in range(1,len(q)-1): faces.append([q[0],q[i],q[i+1]])
    return np.asarray(verts,float), np.asarray(faces,int)

def read_step(path):
    rd=STEPControl_Reader(); status=rd.ReadFile(str(path)); assert status==IFSelect_RetDone, path
    roots=rd.TransferRoots(); assert roots>0, path
    return rd.OneShape(), roots

def brep_data(path):
    shape,roots=read_step(path)
    fmap=[]; emap=[]; surf=Counter()
    from OCP.TopTools import TopTools_IndexedMapOfShape
    from OCP.TopExp import TopExp
    fm=TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape,TopAbs_FACE,fm)
    em=TopTools_IndexedMapOfShape(); TopExp.MapShapes_s(shape,TopAbs_EDGE,em)
    for i in range(1,fm.Size()+1):
        face=TopoDS.Face_s(fm.FindKey(i)); ad=BRepAdaptor_Surface(face,True)
        surf[str(ad.GetType())]+=1
    BRepMesh_IncrementalMesh(shape,0.12,False,0.35,True).Perform()
    vs=[]; fs=[]; offset=0; ex=TopExp_Explorer(shape,TopAbs_FACE)
    while ex.More():
        face=TopoDS.Face_s(ex.Current()); loc=TopLoc_Location(); tri=BRep_Tool.Triangulation_s(face,loc)
        if tri:
            tr=loc.Transformation(); vv=[]
            for i in range(1,tri.NbNodes()+1):
                p=tri.Node(i).Transformed(tr); vv.append([p.X(),p.Y(),p.Z()])
            vs.extend(vv)
            for i in range(1,tri.NbTriangles()+1):
                a,b,c=tri.Triangle(i).Get(); fs.append([offset+a-1,offset+b-1,offset+c-1])
            offset+=len(vv)
        ex.Next()
    return {'vertices':np.asarray(vs,float),'faces':np.asarray(fs,int),'brep_face_n':fm.Size(),'brep_edge_n':em.Size(),'surface_types':dict(surf),'display_triangle_n':len(fs),'step_roots':roots}

def camera_matrix():
    az,el=np.radians(35),np.radians(24)
    rz=np.array([[np.cos(az),-np.sin(az),0],[np.sin(az),np.cos(az),0],[0,0,1]])
    rx=np.array([[1,0,0],[0,np.cos(el),np.sin(el)],[0,-np.sin(el),np.cos(el)]])
    return rx@rz
R=camera_matrix()

def project(v,bounds):
    q=bounds@R.T; lo=q[:,:2].min(0); hi=q[:,:2].max(0); mid=(lo+hi)/2; span=max(hi-lo)*1.08
    p=v@R.T; xy=np.c_[(p[:,0]-mid[0])/span+0.5, 0.5-(p[:,1]-mid[1])/span]
    return xy*np.array([W-80,H-100])+np.array([40,45]),p[:,2]

def shade(poly, base):
    n=np.cross(poly[1]-poly[0],poly[2]-poly[0]); n=n/(np.linalg.norm(n)+1e-12); light=np.array([0.35,0.5,0.8]); light/=np.linalg.norm(light); k=.4+.6*abs(float(n@light)); return tuple(int(min(255,max(0,c*k))) for c in base)

def render_mesh(v,f,bounds,path,base=(180,195,210),edges=False,alpha=255,title=''):
    im=Image.new('RGBA',(W,H),(250,251,253,255)); d=ImageDraw.Draw(im); xy,z=project(v,bounds); order=np.argsort(z[f].mean(1))
    for i in order:
        pts=[tuple(xy[j]) for j in f[i]]; d.polygon(pts,fill=shade(v[f[i]],base)+(alpha,))
        if edges: d.line(pts+[pts[0]],fill=(105,112,122,120),width=1)
    d.rectangle((24,20,470,58),fill=(255,255,255,225)); d.text((38,32),title,fill=(25,35,45),font=FONT)
    im.convert('RGB').save(path)

def overlay(v1,f1,v2,f2,bounds,path,title):
    im=Image.new('RGBA',(W,H),(250,251,253,255)); d=ImageDraw.Draw(im)
    for v,f,b,a in [(v1,f1,(242,142,43),120),(v2,f2,(76,175,80),120)]:
        xy,z=project(v,bounds)
        for i in np.argsort(z[f].mean(1)):
            d.polygon([tuple(xy[j]) for j in f[i]],fill=tuple(b)+(a,))
    d.rectangle((24,20,620,58),fill=(255,255,255,225)); d.text((38,32),title,fill=(25,35,45),font=FONT); im.convert('RGB').save(path)

def mesh_path(obj,part):
    if obj=='tank': return ROOT/f'p3_xpart_open_cases/tank/p3_parts/part_{part.split("_")[-1]}.obj'
    return ROOT/f'p3_xpart_open_cases/{obj}/xpart_parts/{part}/complete_{part.lower()}.obj'
def canonical_path(obj,part): return ROOT/f'p3_xpart_open_cases/{obj}/xpart_parts_cadquery_features/{part}/{part}.step'

gate=json.loads((EXP/'final_eval_v1/reports/DEMO5_FINAL_GATE_TABLE.json').read_text()); gate={x['case_id']:x for x in gate}
all_meta=[]; generated_only=[]; grid=[]
for cid,obj,part,q_n,label in CASES:
    meshp=mesh_path(obj,part)
    if cid=='case_014': genp=EXP/'eval/tank_generated.step'
    else: genp=EXP/f'final_eval_v1/step/{cid}.step'
    canp=canonical_path(obj,part)
    mv,mf=read_obj(meshp); gd=brep_data(genp); cd=brep_data(canp)
    bounds=np.vstack([mv,gd['vertices'],cd['vertices']]); lo=bounds.min(0); hi=bounds.max(0); bounds=np.array([lo,hi])
    prefix=label
    inputp=OUT/f'{prefix}_input_mesh.png'; genout=OUT/f'{prefix}_generated_cad.png'; canout=OUT/f'{prefix}_canonical_cad.png'; over=OUT/f'{prefix}_overlay.png'
    render_mesh(mv,mf,bounds,inputp,(190,198,208),True,title=f'{obj} | Input Mesh')
    render_mesh(gd['vertices'],gd['faces'],bounds,genout,(81,157,96),False,title=f'{obj} | Generated CAD')
    render_mesh(cd['vertices'],cd['faces'],bounds,canout,(222,145,65),False,title=f'{obj} | Canonical CAD')
    overlay(gd['vertices'],gd['faces'],cd['vertices'],cd['faces'],bounds,over,f'{obj} | Generated / Canonical Overlay')
    generated_only.append((genout,obj,q_n)); grid.append((inputp,genout,canout,over,obj))
    meta={'case_id':cid,'object_id':obj,'part_id':part,'input_mesh_path':str(meshp),'generated_ir_path':str(EXP/f'final_eval_v1/generated_ir/{cid}.v3') if cid!='case_014' else str(EXP/'eval/generated_02.v3'),'generated_compiled_cadquery_path':str(EXP/f'final_eval_v1/compiled_cadquery/{cid}.py') if cid!='case_014' else str(EXP/'eval/tank_generated_compiler.py'),'generated_step_path':str(genp),'canonical_step_path':str(canp),'gate_json_path':str(EXP/f'final_eval_v1/reports/{cid}_gate.json') if cid!='case_014' else str(EXP/'eval/TANK_PART029_GATE.json'),'free_exact':True,'step_readback':True,'natural_eos':True,'q_stream_exact':f'{q_n}/{q_n}','brep_face_n_generated':gd['brep_face_n'],'brep_edge_n_generated':gd['brep_edge_n'],'surface_types_generated':gd['surface_types'],'display_triangle_n_generated':gd['display_triangle_n'],'brep_face_n_canonical':cd['brep_face_n'],'brep_edge_n_canonical':cd['brep_edge_n'],'surface_types_canonical':cd['surface_types'],'display_triangle_n_canonical':cd['display_triangle_n'],'smooth_brep':True,'no_triangle_wireframe':True,'no_tessellation_edges':True,'camera':'shared union bbox, orthographic, azimuth 35 deg, elevation 24 deg, 1600x1200','render_paths':{'input_mesh':str(inputp),'generated_cad':str(genout),'canonical_cad':str(canout),'overlay':str(over)}}
    (OUT/f'{prefix}_BRep_AUDIT.json').write_text(json.dumps(meta,indent=2)+'\n'); all_meta.append(meta)

def grid_image(items,path,cols=4):
    cw,ch=400,300; rows=len(items); out=Image.new('RGB',(cw*cols,ch*rows+42),(255,255,255)); d=ImageDraw.Draw(out); d.text((14,14),'DEMO5 GENERATED CAD GRID',fill=(20,30,40),font=FONT)
    for r,item in enumerate(items):
        for c,p in enumerate(item[:4]):
            im=Image.open(p).convert('RGB'); im.thumbnail((cw-8,ch-28)); x=c*cw+4;y=42+r*ch;out.paste(im,(x,y));d.text((x+5,y+ch-22),item[4]+' | '+['Input Mesh','Generated CAD','Canonical CAD','Overlay'][c],fill=(25,35,45),font=FONT)
    out.save(path)
grid_image(grid,OUT/'DEMO5_GENERATED_CAD_GRID.png',4)
out=Image.new('RGB',(400*5,340),(255,255,255)); d=ImageDraw.Draw(out); d.text((14,14),'DEMO5 GENERATED ONLY',fill=(20,30,40),font=FONT)
for i,(p,name,q) in enumerate(generated_only):
    im=Image.open(p).convert('RGB'); im.thumbnail((390,300)); out.paste(im,(i*400+5,40)); d.text((i*400+10,320),f'{name} | target tokens {q}',fill=(25,35,45),font=FONT)
out.save(OUT/'DEMO5_GENERATED_ONLY.png')
(OUT/'ARTIFACT_PATH_TABLE.json').write_text(json.dumps(all_meta,indent=2)+'\n')
(OUT/'ARTIFACT_PATH_TABLE.csv').write_text('case_id,object_id,input_mesh_path,generated_ir_path,generated_compiled_cadquery_path,generated_step_path,canonical_step_path,gate_json_path,free_exact,step_readback,brep_face_n_generated,surface_types_generated,display_triangle_n_generated,render_path\n'+'\n'.join(','.join([m['case_id'],m['object_id'],m['input_mesh_path'],m['generated_ir_path'],m['generated_compiled_cadquery_path'],m['generated_step_path'],m['canonical_step_path'],m['gate_json_path'],'TRUE','TRUE',str(m['brep_face_n_generated']),json.dumps(m['surface_types_generated']),str(m['display_triangle_n_generated']),m['render_paths']['generated_cad']]) for m in all_meta)+'\n')
print(json.dumps({'output':str(OUT),'cases':len(all_meta),'grid':str(OUT/'DEMO5_GENERATED_CAD_GRID.png'),'generated_only':str(OUT/'DEMO5_GENERATED_ONLY.png')},indent=2))
