#!/usr/bin/env python3
"""V3 fixes the axial sign: neck at negative PCA end, body at positive end."""
from pathlib import Path
import math, numpy as np, cadquery as cq, trimesh
CASE_ID='CADPART_004'; VERSION='v3'; S=1000.0
ORIGIN=(-0.73826781,-0.317574275,-0.55519514); AXIS=(0.019200709,0.019285248,0.999629637)
T0,T1=-.200543391,.199136552
NECK_TOP=-.045; SHOULDER_TOP=.018; NECK_R=.0615; RING_R=.066; BODY_R=.1185
def build():
    # Neck occupies the negative PCA end, matching measured source sections.
    result=cq.Workplane('XY').workplane(offset=T0*S).circle(NECK_R*S).extrude((NECK_TOP-T0)*S)
    for z0 in np.linspace(T0+.018,NECK_TOP-.014,5):
        result=result.union(cq.Workplane('XY').workplane(offset=z0*S).circle(RING_R*S).extrude(.011*S))
    # Conical shoulder bridges neck and body; main body occupies positive PCA end.
    shoulder=(cq.Workplane('XY').workplane(offset=NECK_TOP*S).circle(NECK_R*S)
              .workplane(offset=(SHOULDER_TOP-NECK_TOP)*S).circle(BODY_R*S).loft(combine=True))
    body=cq.Workplane('XY').workplane(offset=SHOULDER_TOP*S).circle(BODY_R*S).extrude((T1-SHOULDER_TOP)*S)
    result=result.union(shoulder).union(body)
    z=cq.Vector(0,0,1); a=cq.Vector(*AXIS); cross=z.cross(a); angle=math.degrees(math.acos(max(-1.,min(1.,z.dot(a)))))
    if cross.Length>1e-12: result=result.rotate((0,0,0),cross.toTuple(),angle)
    return result.translate(tuple(x*S for x in ORIGIN))
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'
    cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.15,angularTolerance=.12)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')
