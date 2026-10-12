import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_00790c705e4c4a1fbc0af9bf5c9e9525_PART_016'
VERSION='v1'
dx,dy,dz=(90.0, 9.140624010842076, 11.658264007884055)
shape=cq.Workplane('XY').box(dx,dy,dz)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
