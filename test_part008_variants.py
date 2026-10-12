import json
from pathlib import Path
import cadquery as cq
base=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts/PART_008__complete_part_008')
p=json.loads((base/'parameters.json').read_text())
for periodic in [True,False]:
 for ruled in [True,False]:
  try:
   wires=[]
   for sec in p['sections']:
    pl=cq.Plane(origin=tuple(p['origin'][i]+p['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(p['xdir']),normal=tuple(p['normal']))
    pts=[tuple(x) for x in sec['points']]
    w=cq.Workplane(pl).spline(pts,periodic=periodic).close().val();wires.append(w)
   s=cq.Solid.makeLoft(wires,ruled)
   print('ok',periodic,ruled,s.isValid(),len(s.Faces()),len(s.Solids()))
   cq.exporters.export(s,str(base/f'test_{periodic}_{ruled}.step'))
  except Exception as e: print('fail',periodic,ruled,type(e).__name__,str(e)[:180])

