import json,sys,tempfile,subprocess,os
from pathlib import Path
import cadquery as cq
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad')
import pilot_repaired as base
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_high_fidelity_air_tank_v1/cases/airplane/PART_000__complete_part_000')
pr=json.loads((root/'parameters.json').read_text())
w=[]
for sec in pr['sections']:
 pl=cq.Plane(origin=tuple(pr['origin'][i]+pr['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(pr['xdir']),normal=tuple(pr['normal']))
 w.append(cq.Workplane(pl).spline([tuple(x) for x in sec['points']],periodic=True).close().val())
sh=cq.Solid.makeLoft(w,False)
td=Path('/tmp/smooth_test'); td.mkdir(exist_ok=True)
cq.exporters.export(cq.Workplane(obj=sh),str(td/'smooth.step'))
cq.exporters.export(cq.Workplane(obj=sh),str(td/'smooth.stl'),tolerance=1e-5,angularTolerance=.1)
m=base.load(root/'source.stl'); cm=base.load(td/'smooth.stl'); mm=base.metrics(m,cm,high=True)
print('valid',sh.isValid(),'faces',len(sh.Faces()),'metrics',mm)

