import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_cdc707fbe68c474497cb9dd676ede842_PART_000'
VERSION='v2'
dx,dy,dz=(77.6842038707169, 100.0, 65.89148344209609)
shape=cq.Workplane('XZ').circle(35.8939218282).extrude(100,both=True)
shape=shape.cut(cq.Workplane('XZ').circle(7.8966628022).extrude(120,both=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
