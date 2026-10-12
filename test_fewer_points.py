import json
from pathlib import Path
import cadquery as cq
for n in ['PART_006__complete_part_006','PART_007__complete_part_007']:
 p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts')/n;pr=json.loads((p/'parameters.json').read_text())
 for step in [5,6,8,12]:
  try:
   w=[]
   for sec in pr['sections']:
    pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
    pts=[tuple(x) for x in sec['points']][::step]
    w.append(cq.Workplane(pl).spline(pts,periodic=True).close().val())
   s=cq.Solid.makeLoft(w,False);b=s.BoundingBox();print(n,step,len(pts),[round(v,3) for v in [b.xlen,b.ylen,b.zlen]])
  except Exception as e:print(n,step,'FAIL',type(e).__name__)
