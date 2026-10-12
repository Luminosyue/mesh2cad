from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
R=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/model_v1')
gate=json.loads((R/'generated/pottery_large/free_320/OBJECT_GATE.json').read_text());assert gate['FULL_NEW_MODEL_GENERATED_OBJECT'] and gate['FULL_MODEL_ASSEMBLY_PASS']
folder=Path(gate['render_dir']);out=R/'paper_demo';out.mkdir(exist_ok=True)
canvas=Image.new('RGB',(1660,1410),'white');d=ImageDraw.Draw(canvas);font='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';title=ImageFont.truetype(font,30);label=ImageFont.truetype(font,24);small=ImageFont.truetype(font,21)
d.text((30,20),'P1 / q14 / Compact IR V3: Pottery Large',font=title,fill='#142635')
d.text((30,64),'3/3 empty-target free exact + natural EOS | All 3 parts compiled and assembled',font=label,fill='#24485c')
panels=[('Full input mesh','full_mesh.png'),('All generated CAD parts','cad_parts.png'),('Generated CAD assembly','assembled_cad.png'),('Original-coordinate mesh / CAD overlay','overlay.png')]
for i,(name,f) in enumerate(panels):
 x=30+(i%2)*815;y=114+(i//2)*632
 d.text((x,y),name,font=label,fill='#142635');im=Image.open(folder/f);assert im.size==(1600,1200);im.thumbnail((800,600));canvas.paste(im,(x,y+30))
d.text((30,1380),'Training-object memorization; template-dependent compiler. Mesh CD 0.008021; surface IoU64 0.579514.',font=small,fill='#24485c')
canvas.save(out/'POTTERY_LARGE_MODEL_DEMO.png')
print(out/'POTTERY_LARGE_MODEL_DEMO.png')
