import json
from pathlib import Path
import cadquery as cq
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1/cases/airplane')
p=next(q for q in root.glob('*/parameters.json') if 'xpart_parts' in json.loads((q.parent/'metrics.json').read_text()).get('source_path',''))
pr=json.loads(p.read_text())
print('using',p)
for periodic in [True,False]:
  try:
    wires=[]
    for sec in pr['sections']:
      pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
      pts=[tuple(x) for x in sec['points']]
      w=cq.Workplane(pl).spline(pts,periodic=periodic).close().val()
      wires.append(w)
    for ruled in [False,True]:
      try:
        sh=cq.Solid.makeLoft(wires,ruled)
        print('OK', 'periodic',periodic,'ruled',ruled,'valid',sh.isValid(),'faces',len(sh.Faces()),'solids',len(sh.Solids()))
      except Exception as e: print('LOFT_FAIL',periodic,ruled,type(e).__name__,str(e)[:200])
  except Exception as e: print('WIRE_FAIL',periodic,type(e).__name__,str(e)[:200])


