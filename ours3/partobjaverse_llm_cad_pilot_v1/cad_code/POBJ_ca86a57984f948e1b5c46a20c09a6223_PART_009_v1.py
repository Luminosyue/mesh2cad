import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_ca86a57984f948e1b5c46a20c09a6223_PART_009'
VERSION='v1'
dx,dy,dz=(90.0, 43.7435015767202, 54.74019988488391)
shape=cq.Workplane('XY').box(dx,dy,dz)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
