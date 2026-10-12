from pathlib import Path
import json, math
import numpy as np
import trimesh
from PIL import Image, ImageDraw

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1')
SRC = Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases')
V = ROOT / 'visualizations'
V.mkdir(parents=True, exist_ok=True)
PALETTE = [(36,120,190),(225,125,35),(70,165,90),(180,75,150),(235,185,45),(90,95,190),(20,160,160),(210,80,70)]

def load(path):
    m=trimesh.load(path,force='mesh',process=False)
    if isinstance(m,trimesh.Scene): m=m.to_mesh()
    m.merge_vertices(); m.remove_unreferenced_vertices()
    return m

def bounds(meshes):
    lo=np.min([m.bounds[0] for m in meshes],axis=0); hi=np.max([m.bounds[1] for m in meshes],axis=0)
    return (lo+hi)/2.0, max(float(np.max(hi-lo))*.58,1e-9)

def project(vertices,center,radius,x0,y0,scale=165):
    p=np.asarray(vertices)
    u=(p[:,0]-center[0])*.86+(p[:,1]-center[1])*.34
    w=(p[:,2]-center[2])*.96-(p[:,1]-center[1])*.18
    return [(int(x0+scale*q/radius),int(y0-scale*t/radius)) for q,t in zip(u,w)]

def draw_mesh(draw,mesh,center,radius,x0,color,alpha=255,max_tri=1300):
    tri=mesh.triangles; stride=max(1,len(tri)//max_tri)
    fill=tuple(min(255,int(a+(255-a)*(1-alpha/255.0))) for a in color)
    for t in tri[::stride]: draw.polygon(project(t,center,radius,x0+200,225),fill=fill)

def panel(draw,meshes,center,radius,x0,color,alpha=255):
    for m in meshes: draw_mesh(draw,m,center,radius,x0,color,alpha)

def read_rows(case):
    rows=[]
    for mp in sorted((ROOT/'cases'/case).glob('*/metrics.json')):
        try:
            d=json.loads(mp.read_text(encoding='utf-8'))
            src=SRC/d['source_path']; cad=mp.parent/'reconstructed.stl'
            if not src.exists() or not cad.exists(): continue
            rows.append({'metrics':d,'dir':mp.parent,'source':src,'cad':cad,
                         'family':('xpart_parts' if '/xpart_parts/' in d.get('source_path','') else 'p3_parts')})
        except Exception as exc: print('skip',mp,repr(exc))
    return rows

def render_group(case,family,rows,src_meshes,cad_meshes):
    if not rows: return []
    group=f'{case}_{family}'; out=[]
    center,radius=bounds(src_meshes+cad_meshes)
    im=Image.new('RGB',(1600,550),'white'); dr=ImageDraw.Draw(im)
    titles=['SOURCE ASSEMBLY','CAD ASSEMBLY','SOURCE / CAD OVERLAY','CAD COMPONENTS']
    for j,title in enumerate(titles):
        x=400*j; dr.text((x+125,18),title,fill='black')
        if j==0: panel(dr,src_meshes,center,radius,x,(230,145,45),255)
        elif j==1: panel(dr,cad_meshes,center,radius,x,(45,130,190),255)
        elif j==2:
            panel(dr,src_meshes,center,radius,x,(230,145,45),90)
            panel(dr,cad_meshes,center,radius,x,(45,130,190),125)
        else:
            for i,m in enumerate(cad_meshes): draw_mesh(dr,m,center,radius,x,PALETTE[i%len(PALETTE)],225)
    dr.text((20,515),f'{case} / {family}: {len(rows)} components; orange=source, blue=CAD',fill='black')
    p=V/f'{group}_overall.png'; im.save(p); out.append(str(p))
    cs,rs=bounds(src_meshes); cc,rc=bounds(cad_meshes)
    sim=Image.new('RGB',(1200,455),'white'); sd=ImageDraw.Draw(sim)
    sd.text((135,18),'SOURCE FIT',fill='black'); sd.text((535,18),'CAD FIT',fill='black'); sd.text((935,18),'CAD COMPONENTS',fill='black')
    panel(sd,src_meshes,cs,rs,0,(230,145,45),255); panel(sd,cad_meshes,cc,rc,400,(45,130,190),255)
    for i,m in enumerate(cad_meshes): draw_mesh(sd,m,cc,rc,800,PALETTE[i%len(PALETTE)],225)
    sd.text((20,425),'Each panel uses its own bounds for shape inspection',fill='black')
    p=V/f'{group}_separate_scale.png'; sim.save(p); out.append(str(p))
    return out

def render_parts(case,family,rows,src_meshes,cad_meshes):
    if not rows: return []
    group=f'{case}_{family}'; out=[]; thumbs=[]
    for i,(row,src,cad) in enumerate(zip(rows,src_meshes,cad_meshes)):
        center,radius=bounds([src,cad])
        one=Image.new('RGB',(1200,455),'white'); d=ImageDraw.Draw(one)
        for j,title in enumerate(['SOURCE PART','CAD PART','OVERLAY']):
            x=400*j; d.text((x+150,18),title,fill='black')
            if j==0: draw_mesh(d,src,center,radius,x,(230,145,45),255)
            elif j==1: draw_mesh(d,cad,center,radius,x,(45,130,190),255)
            else:
                draw_mesh(d,src,center,radius,x,(230,145,45),90)
                draw_mesh(d,cad,center,radius,x,(45,130,190),125)
        m=row['metrics']; d.text((18,425),f"{m.get('part_id')} | IoU128={m.get('iou128',0):.4f} | {m.get('quality_level','')}",fill='black')
        p=V/f"{group}__{m.get('part_id',i)}.png"; one.save(p); out.append(str(p))
        thumb=one.copy(); thumb.thumbnail((600,228)); thumbs.append((thumb,m.get('part_id',str(i)),m.get('iou128',0)))
    cols,cell_w,cell_h=2,600,258
    sheet=Image.new('RGB',(cols*cell_w,max(cell_h,math.ceil(len(thumbs)/cols)*cell_h)),'white'); sd=ImageDraw.Draw(sheet)
    for i,(thumb,pid,score) in enumerate(thumbs):
        x,y=(i%cols)*cell_w,(i//cols)*cell_h; sheet.paste(thumb,(x,y)); sd.text((x+8,y+232),f'{pid} | IoU128={float(score):.4f}',fill='black')
    p=V/f'{group}_parts_contact_sheet.png'; sheet.save(p); out.append(str(p)); return out

def main():
    index={'cases':{},'output':str(V)}
    for case in ('airplane','tank'):
        all_rows=read_rows(case); info={'generated_visualized':len(all_rows),'families':{}}
        for family in ('p3_parts','xpart_parts'):
            rows=[r for r in all_rows if r['family']==family]
            if not rows: continue
            src_meshes=[]; cad_meshes=[]; kept=[]
            for r in rows:
                try:
                    src_meshes.append(load(r['source'])); cad_meshes.append(load(r['cad'])); kept.append(r)
                except Exception as exc: print('mesh skip',r['dir'],repr(exc))
            rows=kept; images=render_group(case,family,rows,src_meshes,cad_meshes); images+=render_parts(case,family,rows,src_meshes,cad_meshes)
            info['families'][family]={'count':len(rows),'images':images}
        index['cases'][case]=info
    (V/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf-8')
    (V/'README.txt').write_text('High fidelity Mesh-to-CAD visualization. *_overall.png uses original coordinates; *_parts_contact_sheet.png and *__part_*.png show source/CAD/overlay per component.\n',encoding='utf-8')
    print(json.dumps(index,ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()


