#!/usr/bin/env python3
from pathlib import Path
import numpy as np, cadquery as cq, trimesh
CASE_ID='CASE05_PART000'; VERSION='v2'; S=1000.0
O=np.array([-.855958135,.018089475,-.28889187]); X=np.array([-.082352452,.996603131,.000522353]); X/=np.linalg.norm(X)
Y0=np.array([.996377,.082340,-.021118]); Z=np.cross(X,Y0); Z/=np.linalg.norm(Z); Y=np.cross(Z,X); Y/=np.linalg.norm(Y)
L,W,T,R=1.056318713,.276,.066,.052
def matrix(): return cq.Matrix([[X[0],Y[0],Z[0],O[0]*S],[X[1],Y[1],Z[1],O[1]*S],[X[2],Y[2],Z[2],O[2]*S],[0,0,0,1]])
def build():
    a=cq.Workplane('XY').rect((L-2*R)*S,W*S).extrude(T*S/2,both=True); b=cq.Workplane('XY').rect(L*S,(W-2*R)*S).extrude(T*S/2,both=True); result=a.union(b)
    for x in (-L/2+R,L/2-R):
      for y in (-W/2+R,W/2-R): result=result.union(cq.Workplane('XY').center(x*S,y*S).circle(R*S).extrude(T*S/2,both=True))
    return cq.Workplane(obj=result.val().transformGeometry(matrix()))
if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]; obj=build(); val=obj.val()
    if not val.isValid() or val.Volume()<=0: raise RuntimeError('invalid solid')
    step=root/'step'/f'{CASE_ID}_{VERSION}.step'; stl=root/'recon_mesh'/f'{CASE_ID}_{VERSION}.stl'; cq.exporters.export(obj,str(step)); cq.exporters.export(obj,str(stl),tolerance=.15,angularTolerance=.12)
    m=trimesh.load(stl,force='mesh',process=False); m.apply_scale(1/S); m.export(stl); print('SOLID_VALID')
