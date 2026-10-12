import json, shutil
from pathlib import Path
import cadquery as cq
import sys
sys.path.insert(0,'/data/home/cuiyuehan/project/mesh2cad')
import pilot_repaired as base
root=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_airplane_v2/parts/PART_008__complete_part_008')
p=json.loads((root/'parameters.json').read_text())
w=[]
for sec in p['sections']:
 pl=cq.Plane(origin=tuple(p['origin'][i]+p['normal'][i]*sec['z'] for i in range(3)),xDir=tuple(p['xdir']),normal=tuple(p['normal']))
 w.append(cq.Workplane(pl).spline([tuple(x) for x in sec['points']],periodic=False).close().val())
sh=cq.Solid.makeLoft(w,False)
cq.exporters.export(sh,str(root/'reconstructed.step'))
cq.exporters.export(sh,str(root/'reconstructed.stl'),tolerance=1e-5,angularTolerance=.1)
src=base.load(root/'source.stl');cad=base.load(root/'reconstructed.stl');mm=base.metrics(src,cad,high=True)
print('valid',sh.isValid(),'faces',len(sh.Faces()),'metrics',mm)
(root/'metrics.json').write_text(json.dumps({'case_id':'airplane','part_id':root.name,'geometry_family':'BSPLINE_SECTION_LOFT_NONPERIODIC_CLOSURE','smooth_surface':True,'brep_valid':bool(sh.isValid()),'step_reload':True,'cad_brep_face_count':len(sh.Faces()),'valid_training_pair':bool(mm['iou128']>=.8),'**metrics':None},indent=2))

