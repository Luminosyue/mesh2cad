import json
from pathlib import Path
import cadquery as cq
import numpy as np
for name in ['PART_001__complete_part_001','PART_004__complete_part_004','PART_006__complete_part_006','PART_007__complete_part_007']:
 p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v2/parts')/name
 if not p.exists(): p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts')/name
 pr=json.loads((p/'parameters.json').read_text())
 for periodic in [True,False]:
  for step in [1,2,3,4]:
   try:
    w=[]
    for sec in pr['sections']:
     pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
     pts=[tuple(x) for x in sec['points']][::step]
     w.append(cq.Workplane(pl).spline(pts,periodic=periodic).close().val())
    s=cq.Solid.makeLoft(w,False); b=s.BoundingBox(); ext=[b.xlen,b.ylen,b.zlen]
    print(name,periodic,step,s.isValid(),len(s.Faces()),[round(x,3) for x in ext])
   except Exception as e: print(name,periodic,step,'FAIL',type(e).__name__)

