import json
from pathlib import Path
import numpy as np
import cadquery as cq
def align(sections):
 out=[np.array(sections[0]['points'],float)]
 for sec in sections[1:]:
  a=np.array(sec['points'],float);prev=out[-1]
  best=None
  for rev in [False,True]:
   b=a[::-1] if rev else a
   for k in range(len(b)):
    q=np.roll(b,-k,axis=0); cost=np.mean(np.linalg.norm(q-prev,axis=1))
    if best is None or cost<best[0]:best=(cost,q)
  out.append(best[1])
 return [np.asarray(x) for x in out]
for n in ['PART_001__complete_part_001','PART_004__complete_part_004','PART_006__complete_part_006','PART_007__complete_part_007']:
 p=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts')/n;pr=json.loads((p/'parameters.json').read_text());aa=align(pr['sections'])
 try:
  w=[]
  for sec,pts in zip(pr['sections'],aa):
   pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
   w.append(cq.Workplane(pl).spline([tuple(x) for x in pts],periodic=True).close().val())
  s=cq.Solid.makeLoft(w,False);b=s.BoundingBox();print(n,'faces',len(s.Faces()),'valid',s.isValid(),'ext',[round(b.xlen,3),round(b.ylen,3),round(b.zlen,3)])
 except Exception as e:print(n,'FAIL',type(e).__name__,str(e)[:120])

