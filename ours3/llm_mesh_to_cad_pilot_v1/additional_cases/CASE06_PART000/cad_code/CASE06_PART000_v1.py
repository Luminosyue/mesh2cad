#!/usr/bin/env python3
from pathlib import Path
import cadquery as cq, trimesh
CASE_ID='CASE06_PART000'; VERSION='v1'; S=1000.0
CENTER=(-0.499789355,-0.00631659,0.00353268); RX,RY,RZ=.486,.328,.495
def build():
    # Seven semantic elliptical sections form an editable organic loft baseline.
    zs=[-RZ,-.72*RZ,-.35*RZ,0,.35*RZ,.72*RZ,RZ]
    factors=[.10,.69,.93,1.0,.94,.70,.10]
    wp=cq.Workplane('XY')
    last=0
    for i,(z,f) in enumerate(zip(zs,factors)):
        wp=wp.workplane(offset=(z-last)*S).ellipse(RX*f*S,RY*f*S); last=z
    solid=wp.loft(combine=True,ruled=False).translate(tuple(c*S for c in CENTER))
    return solid
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'
    cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.3,angularTolerance=.15)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')
