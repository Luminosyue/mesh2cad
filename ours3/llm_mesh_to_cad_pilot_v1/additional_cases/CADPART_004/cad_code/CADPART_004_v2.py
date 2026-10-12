#!/usr/bin/env python3
from pathlib import Path
import math, numpy as np, cadquery as cq, trimesh
CASE_ID='CADPART_004'; VERSION='v2'; S=1000.0
ORIGIN=(-0.73826781,-0.317574275,-0.55519514); AXIS=(0.019200709,0.019285248,0.999629637)
T0,T1=-.200543391,.199136552; BODY_R=.1125; BODY_TOP=.035; NECK_R=.061; RING_R=.066
def build():
    result=cq.Workplane('XY').workplane(offset=T0*S).circle(BODY_R*S).extrude((BODY_TOP-T0)*S).union(cq.Workplane('XY').workplane(offset=BODY_TOP*S).circle(NECK_R*S).extrude((T1-BODY_TOP)*S))
    for z0 in np.linspace(BODY_TOP+.022,T1-.018,5): result=result.union(cq.Workplane('XY').workplane(offset=z0*S).circle(RING_R*S).extrude(.012*S))
    z=cq.Vector(0,0,1); a=cq.Vector(*AXIS); cross=z.cross(a); angle=math.degrees(math.acos(max(-1.,min(1.,z.dot(a)))))
    if cross.Length>1e-12: result=result.rotate((0,0,0),cross.toTuple(),angle)
    return result.translate(tuple(x*S for x in ORIGIN))
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'; cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.15,angularTolerance=.12)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')

