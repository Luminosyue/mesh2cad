#!/usr/bin/env python3
from pathlib import Path
import numpy as np, cadquery as cq, trimesh
CASE_ID='CASE05_PART000'; VERSION='v1'; S=1000.0
ORIGIN=np.array([-0.855958135,0.018089475,-0.28889187])
X=np.array([-0.082352452,0.996603131,0.000522353]); Y=np.array([0.996377,0.082340,-0.021118]); Z=np.cross(X,Y); Y=np.cross(Z,X); X/=np.linalg.norm(X); Y/=np.linalg.norm(Y); Z/=np.linalg.norm(Z)
L,W,T=1.056318713,.276,.066; CORNER_R=.052
def matrix(): return cq.Matrix([[X[0],Y[0],Z[0],ORIGIN[0]*S],[X[1],Y[1],Z[1],ORIGIN[1]*S],[X[2],Y[2],Z[2],ORIGIN[2]*S],[0,0,0,1]])
def build():
    base=cq.Workplane('XY').rect((L-2*CORNER_R)*S,W*S).extrude(T*S/2, both=True)
    spine=cq.Workplane('XY').rect(L*S,(W-2*CORNER_R)*S).extrude(T*S/2,both=True)
    result=base.union(spine)
    for x in (-L/2+CORNER_R,L/2-CORNER_R):
      for y in (-W/2+CORNER_R,W/2-CORNER_R): result=result.union(cq.Workplane('XY').center(x*S,y*S).circle(CORNER_R*S).extrude(T*S/2,both=True))
    return cq.Workplane(obj=result.val().transformShape(matrix()))
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'
    cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.15,angularTolerance=.12)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')
