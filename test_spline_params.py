import json
from pathlib import Path
import cadquery as cq
import numpy as np
for n in ['PART_006__complete_part_006','PART_007__complete_part_007']:
 p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts')/n;pr=json.loads((p/'parameters.json').read_text())
 for scale in [True,False]:
  for tol in [None,1e-3,1e-4,1e-2]:
   try:
    w=[]
    for sec in pr['sections']:
     pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
     w.append(cq.Workplane(pl).spline([tuple(x) for x in sec['points']],periodic=True,scale=scale,tol=tol).close().val())
    s=cq.Solid.makeLoft(w,False);b=s.BoundingBox();print(n,'scale',scale,'tol',tol,'faces',len(s.Faces()),'ext',[round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)])
   except Exception as e: print(n,'scale',scale,'tol',tol,'FAIL',type(e).__name__)

