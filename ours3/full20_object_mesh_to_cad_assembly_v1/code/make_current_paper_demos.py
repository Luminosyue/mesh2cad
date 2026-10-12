from pathlib import Path
import json
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
EXP = ROOT / 'ours3/full20_object_mesh_to_cad_assembly_v1'
OUT = EXP / 'paper_demo'
ITEMS = [
    ('pottery_large', 'free_320', 'Pottery Large'),
    ('aroma_stainless_steel_milk_frother_2_cup', 'free_320', 'Milk Frother'),
    ('cube', 'completion_side_final_v1', 'Cube'),
    ('baby_car', 'completion_side_final_v1', 'Baby Car'),
    ('android_figure_orange', 'completion_side_final_v1', 'Android Figure'),
    ('speaker_big', 'completion_side_final_v2', 'Speaker Big'),
    ('fire_truck', 'completion_side_final_v1', 'Fire Truck'),
    ('robot', 'completion_side_final_v1', 'Robot'),
    ('pressure_cooker', 'completion_side_final_v1', 'Pressure Cooker'),
    ('dvd_player', 'completion_side_final_v1', 'DVD Player'),
]
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def f(n): return ImageFont.truetype(FONT, n)

def load(item):
    obj, free, pretty = item
    base = EXP / 'model_v1/generated' / obj / free
    gate = json.loads((base/'OBJECT_GATE.json').read_text())
    rdir = base/'objects'/obj/'renders'
    return pretty, gate, rdir

def grid(items, out, title):
    cards = [load(x) for x in items]
    cw, ch, gx, gy, left, top = 560, 420, 18, 26, 245, 150
    W = left + 4*(cw+gx) + 20; H = top + len(cards)*(ch+gy) + 70
    canvas = Image.new('RGB',(W,H),'white'); d=ImageDraw.Draw(canvas)
    d.text((left,20),title,font=f(34),fill='#142c3d')
    d.text((left,72),'q14 + Compact IR V3 | empty-target greedy | no GT prefix | natural EOS | original object coordinates | no ICP',font=f(18),fill='#35586c')
    labels=['Full Mesh','Generated CAD Parts','Assembled CAD','Overlay']
    for j,l in enumerate(labels): d.text((left+j*(cw+gx)+10,120),l,font=f(20),fill='#17384d')
    files=['full_mesh.png','cad_parts.png','assembled_cad.png','overlay.png']
    for i,(pretty,gate,rdir) in enumerate(cards):
        y=top+i*(ch+gy); d.text((20,y+ch//2-15),pretty,font=f(22),fill='#203746')
        for j,name in enumerate(files):
            x=left+j*(cw+gx); im=Image.open(rdir/name).convert('RGB'); im.thumbnail((cw,ch),Image.Resampling.LANCZOS); canvas.paste(im,(x+(cw-im.width)//2,y+(ch-im.height)//2))
        m=gate['metrics']; d.text((left,y+ch+4),f"CD {m['CD']:.6f} | IoU64 {m['IOU']:.6f} | volume error {m.get('VOLUME_ERROR',0):.2%}",font=f(15),fill='#456474')
    canvas.save(out,quality=95); print(out)

def main():
    grid(ITEMS[:3], OUT/'PAPER_FULL_OBJECT_DEMO_3.png', 'PAPER FULL-OBJECT DEMO | 3 completed model-generated objects')
    grid(ITEMS[:4], OUT/'PAPER_MAIN_4_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 4 completed model-generated objects')
    grid(ITEMS[:5], OUT/'PAPER_MAIN_5_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 5 completed model-generated objects')
    grid(ITEMS[:6], OUT/'PAPER_MAIN_6_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 6 completed model-generated objects')
    grid(ITEMS[:7], OUT/'PAPER_MAIN_7_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 7 completed model-generated objects')
    grid(ITEMS, OUT/'PAPER_MAIN_8_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 8 completed model-generated objects')
    grid(ITEMS[:9], OUT/'PAPER_MAIN_9_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 9 completed model-generated objects')
    grid(ITEMS[:10], OUT/'PAPER_MAIN_10_OBJECT_DEMO.png', 'PAPER MAIN DEMO | 10 completed model-generated objects')
    grid(ITEMS, OUT/'FULL_OBJECT_ASSEMBLY_GALLERY_CURRENT.png', 'FULL OBJECT ASSEMBLY GALLERY | 8 complete full-object reconstructions')

if __name__ == '__main__': main()
