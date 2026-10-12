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
]
font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def ft(n): return ImageFont.truetype(font_path, n)

def paths(obj, free):
    base = EXP / 'model_v1/generated' / obj / free
    rdir = base / 'objects' / obj / 'renders'
    gate = json.loads((base / 'OBJECT_GATE.json').read_text())
    return base, rdir, gate

def make_single(pretty, base, rdir, gate, path):
    files = ['full_mesh.png', 'cad_parts.png', 'assembled_cad.png', 'overlay.png']
    labels = ['Full Mesh', 'Generated CAD Parts', 'Assembled CAD', 'Overlay']
    w, h, gap = 720, 500, 20
    canvas = Image.new('RGB', (2*w+3*gap, 2*h+3*gap+120), 'white')
    d = ImageDraw.Draw(canvas)
    d.text((gap, 18), f'{pretty} | P1 model-generated full object', font=ft(30), fill='#142c3d')
    m = gate['metrics']; d.text((gap, 65), f"q14 + Compact IR V3 | CD {m['CD']:.6f} | IoU64 {m['IOU']:.6f} | volume error {m.get('VOLUME_ERROR',0):.2%}", font=ft(17), fill='#35586c')
    for i, (f, lab) in enumerate(zip(files, labels)):
        x = gap + (i % 2) * (w + gap); y = 105 + (i // 2) * (h + gap)
        d.text((x + 8, y), lab, font=ft(20), fill='#17384d')
        im = Image.open(rdir / f).convert('RGB'); im.thumbnail((w, h-35), Image.Resampling.LANCZOS)
        canvas.paste(im, (x + (w-im.width)//2, y+32+(h-35-im.height)//2))
    canvas.save(path, quality=95)

def main():
    cards = []
    completed = OUT / 'completed_objects'; completed.mkdir(parents=True, exist_ok=True)
    for obj, free, pretty in ITEMS:
        base, rdir, gate = paths(obj, free)
        single = completed / f'{obj}_MODEL_DEMO.png'
        make_single(pretty, base, rdir, gate, single)
        cards.append((pretty, gate, rdir))
    cw, ch, gapx, gapy = 560, 420, 18, 26
    left, top = 245, 150
    W = left + 4*(cw+gapx) + 20
    H = top + len(cards)*(ch+gapy) + 70
    canvas = Image.new('RGB', (W,H), 'white'); d = ImageDraw.Draw(canvas)
    d.text((left, 20), 'PAPER FULL-OBJECT DEMO | 3 completed model-generated objects', font=ft(34), fill='#142c3d')
    d.text((left, 72), 'q14 + Compact IR V3 | empty-target greedy | no GT prefix | natural EOS | original object coordinates | no ICP', font=ft(18), fill='#35586c')
    labels = ['Full Mesh', 'Generated CAD Parts', 'Assembled CAD', 'Overlay']
    for j, lab in enumerate(labels): d.text((left+j*(cw+gapx)+10, 120), lab, font=ft(20), fill='#17384d')
    for i, (pretty, gate, rdir) in enumerate(cards):
        y = top + i*(ch+gapy); d.text((20,y+ch//2-15), pretty, font=ft(22), fill='#203746')
        for j, f in enumerate(['full_mesh.png','cad_parts.png','assembled_cad.png','overlay.png']):
            x = left + j*(cw+gapx); im = Image.open(rdir/f).convert('RGB'); im.thumbnail((cw,ch), Image.Resampling.LANCZOS); canvas.paste(im,(x+(cw-im.width)//2,y+(ch-im.height)//2))
        m=gate['metrics']; d.text((left,y+ch+4),f"CD {m['CD']:.6f} | IoU64 {m['IOU']:.6f} | volume error {m.get('VOLUME_ERROR',0):.2%}",font=ft(15),fill='#456474')
    path = OUT/'PAPER_FULL_OBJECT_DEMO_3.png'; canvas.save(path,quality=95); print(path)

if __name__ == '__main__': main()
