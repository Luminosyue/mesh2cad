import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_8730f3aafc784a849de8e9f2d9c707f8_PART_009'
VERSION='v2'
dx,dy,dz=(61.56655434161942, 100.00000000000001, 23.80687028948076)
shape=cq.Workplane('XY').box(dx,dy,dz)
hole=max(min(dx,dy)*.18,.25)
shape=shape.cut(cq.Workplane('XY').circle(hole).extrude(dz*1.2,both=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
