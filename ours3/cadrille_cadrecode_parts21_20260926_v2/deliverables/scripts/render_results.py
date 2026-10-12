import os
os.environ.setdefault('EGL_PLATFORM','surfaceless')
from pathlib import Path
import json
import numpy as np
import trimesh
import open3d as o3d
from PIL import Image,ImageDraw,ImageFont

root=Path(__file__).resolve().parent
out=root/'deliverables';renders=out/'previews';renders.mkdir(exist_ok=True)
manifest=json.loads((root/'MANIFEST.json').read_text())
summary={(r['case'],r['method']):r for r in json.loads((out/'SUMMARY.json').read_text())}
fontfile='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(fontfile,22);small=ImageFont.truetype(fontfile,17);title=ImageFont.truetype(fontfile,30)
renderer=o3d.visualization.rendering.OffscreenRenderer(520,420)
renderer.scene.set_background([1,1,1,1])
material=o3d.visualization.rendering.MaterialRecord();material.shader='defaultLit'

def render(path,center,extent,color):
    renderer.scene.clear_geometry()
    if not path.exists():return Image.new('RGB',(520,420),'white')
    tm=trimesh.load(path,force='mesh',process=False)
    mesh=o3d.geometry.TriangleMesh(o3d.utility.Vector3dVector(np.asarray(tm.vertices,dtype=np.float64)),o3d.utility.Vector3iVector(np.asarray(tm.faces,dtype=np.int32)))
    mesh.compute_vertex_normals();mesh.paint_uniform_color(color)
    material.base_color=[*color,1]
    renderer.scene.add_geometry('object',mesh,material)
    dist=extent*1.8
    renderer.setup_camera(38,center,center+np.array([dist,-dist,dist*0.8]),[0,0,1])
    return Image.fromarray(np.asarray(renderer.render_to_image())).convert('RGB')

names=['Jenga Classic','Dollhouse Sofa','Android Figure','Milk Frother','Vegetable Set','Baby Car','Birdhouse','Cube','DVD Player','Fire Truck','Mini Excavator','Mini Fire Engine','Paintmaker','Pottery Large','Pressure Cooker','Robot','Speaker Big','Tank','Toaster','Winerack','Airplane']
thumbs=[]
for index,case in enumerate(manifest['cases']):
    name=case['case'];source=out/'input_parts'/name/'assembled_input.stl'
    tm=trimesh.load(source,force='mesh');center=tm.bounds.mean(0);extent=max(tm.extents)
    panel=Image.new('RGB',(1560,520),'white');draw=ImageDraw.Draw(panel)
    draw.text((16,8),f'{index+1:02d}  {names[index]}',font=title,fill='#182e43')
    for col,method in enumerate(['input','cadrille','cadrecode']):
        path=source if method=='input' else out/method/name/'assembled.stl'
        color=[0.42,0.48,0.53] if method=='input' else [0.89,0.48,0.04]
        image=render(path,center,extent,color)
        panel.paste(image,(col*520,62))
        if method=='input':label=f'Input: {case["required_parts"]} X-Part parts';labelcolor='#4b5b67'
        else:
            r=summary[name,method];label=f'{"Cadrille" if method=="cadrille" else "CAD-Recode"}: {r["valid_parts"]}/{r["required_parts"]} parts';labelcolor='#007559' if r['status']=='COMPLETE' else '#b74921'
        draw.text((col*520+16,489),label,font=font,fill=labelcolor)
    panel.save(renders/f'{index+1:02d}_{name}.png')
    thumbs.append(panel.resize((780,260),Image.Resampling.LANCZOS))
    print('RENDER',name,flush=True)
sheet=Image.new('RGB',(2400,2040),'#edf1f4');draw=ImageDraw.Draw(sheet)
draw.text((22,17),'X-Part decomposition > independent CAD generation > assembly',font=title,fill='#182e43')
draw.text((22,65),'21 objects | 306 source parts per method | Same view and scale | Counts show valid CAD parts, not shape accuracy',font=small,fill='#4b5b67')
for i,im in enumerate(thumbs):sheet.paste(im,(20+(i%3)*790,112+(i//3)*273))
sheet.save(out/'comparison_21.png')
print('RENDER_COMPLETE',flush=True)
