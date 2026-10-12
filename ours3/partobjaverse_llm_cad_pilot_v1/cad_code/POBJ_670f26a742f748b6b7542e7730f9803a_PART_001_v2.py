import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_670f26a742f748b6b7542e7730f9803a_PART_001'
VERSION='v2'
dx,dy,dz=(100.0, 67.2465054851644, 99.6154452894859)
shape=cq.Workplane('YZ').circle(41.7154876937).extrude(100,both=True)
shape=shape.cut(cq.Workplane('YZ').circle(9.17740729261).extrude(120,both=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
