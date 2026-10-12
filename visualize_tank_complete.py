from pathlib import Path
import json
from PIL import Image, ImageDraw
import visualize_high_fidelity as vh

ROOT=vh.ROOT
SRC=vh.SRC
V=vh.V

def main():
    source=next((SRC/'tank'/'source').glob('*'))
    src=vh.load(source)
    rows=[]
    for mp in sorted((ROOT/'cases'/'tank').glob('*/metrics.json')):
        d=json.loads(mp.read_text(encoding='utf-8'))
        fam='xpart' if '/xpart_parts/' in d.get('source_path','') else 'p3'
        rows.append((fam,d,mp.parent/'reconstructed.stl'))
    xrows=[r for r in rows if r[0]=='xpart']
    prows=[r for r in rows if r[0]=='p3']
    xmesh=[vh.load(r[2]) for r in xrows]
    pmesh=[vh.load(r[2]) for r in prows]
    center,radius=vh.bounds([src]+xmesh+pmesh)
    im=Image.new('RGB',(2000,585),'white'); d=ImageDraw.Draw(im)
    titles=['ORIGINAL TANK SOURCE','X-PART CAD ASSEMBLY (45/45)','P3 CAD ASSEMBLY (43/45)','SOURCE / X-PART OVERLAY','ALL X-PART CAD COMPONENTS']
    for j,title in enumerate(titles):
        x=400*j; d.text((x+105,18),title,fill='black')
        if j==0: vh.draw_mesh(d,src,center,radius,x,(230,145,45),255,max_tri=3200)
        elif j==1: vh.panel(d,xmesh,center,radius,x,(45,130,190),255)
        elif j==2: vh.panel(d,pmesh,center,radius,x,(55,165,90),255)
        elif j==3:
            vh.draw_mesh(d,src,center,radius,x,(230,145,45),90,max_tri=3200)
            vh.panel(d,xmesh,center,radius,x,(45,130,190),125)
        else:
            for i,m in enumerate(xmesh):
                vh.draw_mesh(d,m,center,radius,x,vh.PALETTE[i%len(vh.PALETTE)],225)
    missing=[f'part_{i:03d}' for i in (8,34)]
    d.text((20,550),'Tank source is the complete original mesh; P3 missing CAD: part_008, part_034; X-Part contains all 45 components.',fill='black')
    out=V/'tank_complete_overall.png'; im.save(out)
    # A compact completeness report card.
    rep=Image.new('RGB',(1200,360),'white'); rd=ImageDraw.Draw(rep)
    rd.text((30,25),'TANK COMPONENT COMPLETENESS',fill='black')
    rd.text((50,90),'Original source mesh',fill='black'); rd.text((500,90),'1 complete tank mesh',fill=(35,120,190))
    rd.text((50,140),'P3 parts',fill='black'); rd.text((500,140),'45 input / 43 CAD / 2 failed: part_008, part_034',fill=(180,90,30))
    rd.text((50,190),'X-Part parts',fill='black'); rd.text((500,190),'45 input / 45 CAD / 0 failed',fill=(35,120,190))
    rd.text((50,240),'Visualized CAD',fill='black'); rd.text((500,240),'88 generated CAD components; source overlay included',fill=(35,120,190))
    rd.text((50,300),'IoU-valid pairs',fill='black'); rd.text((500,300),'24 (all from X-Part)',fill=(35,120,190))
    rep.save(V/'tank_completeness_report.png')
    print(out)
    print(V/'tank_completeness_report.png')

if __name__=='__main__':
    main()

