from OCP.GeomAPI import GeomAPI_PointsToBSplineSurface
from OCP.TColgp import TColgp_Array2OfPnt
from OCP.gp import gp_Pnt
import numpy as np
from pathlib import Path
import json
from smooth_runtime import section_surface
sections=[dict(z=float(z),outer=dict(kind='circle',center=[0,0],radius=10+z*.1),holes=[]) for z in np.linspace(0,50,9)]
try:
 s=section_surface(sections);print('SYNTHETIC',s.isValid(),s.Volume(),len(s.Faces()))
except Exception as e:print(type(e).__name__,str(e))
p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922/cases/3d_dollhouse_sofa/PART_001/candidate_parameters.json')
spec=json.loads(p.read_text());secs=spec['features'][0]['sections'];n=len(secs[0]['outer']['points'])
arr=TColgp_Array2OfPnt(1,n,1,len(secs))
for j,s in enumerate(secs):
 for i,pt in enumerate(s['outer']['points']):arr.SetValue(i+1,j+1,gp_Pnt(*pt,s['z']))
from OCP.Approx import Approx_IsoParametric
fit=GeomAPI_PointsToBSplineSurface();fit.Interpolate(arr,Approx_IsoParametric,True);surf=fit.Surface();u0,u1,v0,v1=surf.Bounds()
print('BOUND',surf.IsUPeriodic(),surf.IsVPeriodic(),surf.Bounds(),'source z',secs[0]['z'],secs[-1]['z'])
for v in [v0,v1]:
 q=np.array([[surf.Value(u,v).X(),surf.Value(u,v).Y(),surf.Value(u,v).Z()] for u in np.linspace(u0,u1,101)])
 print('CAP',v,q.min(0),q.max(0))
