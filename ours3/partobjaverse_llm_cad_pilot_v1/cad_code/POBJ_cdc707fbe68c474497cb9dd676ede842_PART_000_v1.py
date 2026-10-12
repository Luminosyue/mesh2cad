import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_cdc707fbe68c474497cb9dd676ede842_PART_000'
VERSION='v1'
dx,dy,dz=(69.91578348364521, 90.0, 59.302335097886484)
shape=cq.Workplane('XZ').circle(32.3045296454).extrude(90,both=True)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
