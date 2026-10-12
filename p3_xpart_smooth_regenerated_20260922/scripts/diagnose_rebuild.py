from pathlib import Path
import runpy,tempfile
import cadquery as cq
r=Path('/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922')
od=r/'cases/school_bus/PART_017';ns=runpy.run_path(str(od/'cad.py'));spec=ns['PARAMETERS'];scale=spec['construction_scale'];center=spec['center']
def stat(name,s):print(name,'valid',s.isValid(),'faces',len(s.Faces()),'volume',s.Volume(),flush=True)
with tempfile.TemporaryDirectory(dir=r/'validation') as td:
    p=Path(td)/'candidate.step';body=ns['build_normalized'](spec);stat('normalized',body)
    world=body.scale(1/scale).translate(tuple(center));stat('world',world);world.exportStep(str(p));world=cq.importers.importStep(str(p)).val();stat('first_roundtrip',world)
    final=ns['partition_periodic_faces'](world.translate(tuple(-v for v in center)).scale(scale)).scale(1/scale).translate(tuple(center));stat('partition_roundtrip',final)
    final.exportStep(str(p));final=cq.importers.importStep(str(p)).val();stat('second_roundtrip',final)
    direct=ns['build_model'](spec);stat('original_script',direct);direct.exportStep(str(p));stat('direct_roundtrip',cq.importers.importStep(str(p)).val())
stat('delivered',cq.importers.importStep(str(od/'model.step')).val())
