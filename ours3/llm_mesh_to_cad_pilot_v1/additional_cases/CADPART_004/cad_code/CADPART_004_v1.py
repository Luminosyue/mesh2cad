#!/usr/bin/env python3
from pathlib import Path
import numpy as np, cadquery as cq, trimesh
CASE_ID='CADPART_004'; VERSION='v1'; S=1000.0
ORIGIN=np.array([-0.73826781,-0.317574275,-0.55519514]); Z=np.array([0.019200709,0.019285248,0.999629637])
T0,T1=-0.200543391,0.199136552
BODY_R=.1125; BODY_TOP=.035; NECK_R=.061; RING_R=.066
def frame_matrix():
    ref=np.array([1.,0.,0.]); x=ref-Z*np.dot(ref,Z); x/=np.linalg.norm(x); y=np.cross(Z,x)
    return cq.Matrix([[x[0],y[0],Z[0],ORIGIN[0]*S],[x[1],y[1],Z[1],ORIGIN[1]*S],[x[2],y[2],Z[2],ORIGIN[2]*S],[0,0,0,1]])
def build():
    body=cq.Workplane('XY').workplane(offset=T0*S).circle(BODY_R*S).extrude((BODY_TOP-T0)*S)
    neck=cq.Workplane('XY').workplane(offset=BODY_TOP*S).circle(NECK_R*S).extrude((T1-BODY_TOP)*S)
    result=body.union(neck)
    for z in np.linspace(BODY_TOP+.022,T1-.018,5):
        ring=cq.Workplane('XY').workplane(offset=z*S).circle(RING_R*S).extrude(.012*S)
        result=result.union(ring)
    shape=result.val().transformShape(frame_matrix()); return cq.Workplane(obj=shape)
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'
    cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.15,angularTolerance=.12)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')

