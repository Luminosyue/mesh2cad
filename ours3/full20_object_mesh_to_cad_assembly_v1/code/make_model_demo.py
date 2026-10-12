from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import json

ROOT=Path('/data/home/cuiyuehan/project/mesh2cad')
E=ROOT/'ours3/full20_object_mesh_to_cad_assembly_v1/model_v1'
OUT=E/'paper_demo'; OUT.mkdir(exist_ok=True)
objects=[('pottery_large','Pottery Large'),('aroma_stainless_steel_milk_frother_2_cup','Milk Frother')]
rows=[('full_mesh.png','Input mesh'),('cad_parts.png','Generated CAD parts'),('overlay.png','Overlay'),('assembled_cad.png','Assembled CAD')]
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
title=ImageFont.truetype(font_path,42); subtitle=ImageFont.truetype(font_path,24); label=ImageFont.truetype(font_path,25); stats=ImageFont.truetype(font_path,21)
thumb_w,thumb_h=820,510; left=260; gap=32; top=205; row_gap=78
W=left+len(objects)*(thumb_w+gap)+30; H=top+len(rows)*(thumb_h+row_gap)+130
canvas=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(canvas)
d.text((left,24),'P1 Full-sequence Mesh-to-CAD | Model-generated objects',font=title,fill='#152637')
d.text((left,82),'q14 + Compact IR V3 | empty-target greedy | no GT prefix | natural EOS | measured mesh-vs-CAD',font=subtitle,fill='#35556a')
for col,(obj,pretty) in enumerate(objects):
    gate=json.loads((E/'generated'/obj/'free_320/OBJECT_GATE.json').read_text())
    rdir=Path(gate['render_dir']);x=left+col*(thumb_w+gap)
    m=gate['metrics']; header=f'{pretty}  |  {gate["required_parts"]} parts  |  {gate["free_exact_n"]}/{gate["required_parts"]} free exact'
    d.text((x,115),header,font=label,fill='#17384d')
    d.text((x,168),f'CD {m["CD"]:.6f}   surface IoU64 {m["IOU"]:.6f}   volume err {m.get("VOLUME_ERROR",0):.2%}',font=stats,fill='#456474')
    for ri,(filename,rowlabel) in enumerate(rows):
        y=top+ri*(thumb_h+row_gap)
        if col==0:d.text((20,y+thumb_h//2-12),rowlabel,font=label,fill='#203746')
        im=Image.open(rdir/filename).convert('RGB'); im.thumbnail((thumb_w,thumb_h),Image.Resampling.LANCZOS)
        px=x+(thumb_w-im.width)//2; py=y+(thumb_h-im.height)//2
        canvas.paste(im,(px,py))
footer=top+len(rows)*(thumb_h+row_gap)-20
d.text((left,footer),'Both objects: FULL_MODEL_ASSEMBLY_PASS = TRUE | CAD is geometry only; texture reconstruction is out of scope.',font=stats,fill='#35556a')
path=OUT/'MODEL_GENERATED_OBJECTS_DEMO.png';canvas.save(path,quality=95);print(path)
