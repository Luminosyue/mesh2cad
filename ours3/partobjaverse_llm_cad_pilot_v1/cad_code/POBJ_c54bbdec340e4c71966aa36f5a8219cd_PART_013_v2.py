import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_c54bbdec340e4c71966aa36f5a8219cd_PART_013'
VERSION='v2'
dx,dy,dz=(45.10774054132871, 100.0, 32.18581064059452)
shape=cq.Workplane('XZ').circle(19.3233877955).extrude(100,both=True)
shape=shape.cut(cq.Workplane('XZ').circle(4.25114531501).extrude(120,both=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
