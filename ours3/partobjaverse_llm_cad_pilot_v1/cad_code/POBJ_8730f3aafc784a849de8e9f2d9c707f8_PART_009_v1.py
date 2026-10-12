import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_8730f3aafc784a849de8e9f2d9c707f8_PART_009'
VERSION='v1'
dx,dy,dz=(55.40989890745748, 90.00000000000001, 21.426183260532685)
shape=cq.Workplane('XY').box(dx,dy,dz)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
