import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_670f26a742f748b6b7542e7730f9803a_PART_001'
VERSION='v1'
dx,dy,dz=(90.0, 60.52185493664797, 89.65390076053731)
shape=cq.Workplane('YZ').circle(37.5439389243).extrude(90,both=True)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
