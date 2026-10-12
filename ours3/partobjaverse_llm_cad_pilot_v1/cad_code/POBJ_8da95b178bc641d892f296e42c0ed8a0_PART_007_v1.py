import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_8da95b178bc641d892f296e42c0ed8a0_PART_007'
VERSION='v1'
dx,dy,dz=(90.0, 89.99998447778081, 69.80973208649671)
shape=cq.Workplane('XY').box(dx,dy,dz)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
