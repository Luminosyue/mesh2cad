import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_da7af66ce5df4629802e97dc03d186f5_PART_000'
VERSION='v2'
dx,dy,dz=(100.0, 64.06640482113617, 83.3974200307607)
shape=cq.Workplane('YZ').circle(36.865956213).extrude(100,both=True)
shape=shape.cut(cq.Workplane('YZ').circle(8.11051036685).extrude(120,both=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
