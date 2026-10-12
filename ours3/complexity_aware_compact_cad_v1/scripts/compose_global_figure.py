#!/usr/bin/env python3
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path("/data/home/cuiyuehan/project/mesh2cad/ours3/complexity_aware_compact_cad_v1");FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf";font=ImageFont.truetype(FONT,24) if Path(FONT).is_file() else ImageFont.load_default();cases=[("CASE_03",ROOT/"case03_control"),("CASE_04",ROOT/"case04"),("CASE_05",ROOT/"case05"),("CASE_09",ROOT/"case09")];names=["source_mesh.png","baseline_cad_shaded.png","occ_unify_cad_shaded.png","ours_compact_cad_shaded.png"];headers=["SOURCE MESH","BASELINE STEP","OCC UNIFY","OURS COMPACT"]
sheet=Image.new("RGB",(4*520,4*450),"white");draw=ImageDraw.Draw(sheet)
for r,(cid,d) in enumerate(cases):
 for c,(name,head) in enumerate(zip(names,headers)):
  im=Image.open(d/name).convert("RGB");im.thumbnail((510,395),Image.Resampling.LANCZOS);x=c*520+(510-im.width)//2;y=r*450+48+(395-im.height)//2;sheet.paste(im,(x,y));draw.rectangle((c*520,r*450,c*520+520,r*450+44),fill="#25364b");draw.text((c*520+12,r*450+10),f"{cid} | {head}",font=font,fill="white")
sheet.save(ROOT/"artifacts/compact_cad_comparison.png",dpi=(180,180))
