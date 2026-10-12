import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_9e7856dd34ae444a934499782c5bd606_PART_004'
VERSION='v1'
dx,dy,dz=(69.44636313842676, 90.0, 67.26678605661732)
a=cq.Workplane('XY').box(dx*.62,dy,dz)
b=cq.Workplane('XY').box(dx*.28,dy*.55,dz*.55).translate((dx*.47,0,0))
shape=cq.Workplane(obj=cq.Compound.makeCompound([a.val(),b.val()]))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
