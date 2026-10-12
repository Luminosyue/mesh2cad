import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_c54bbdec340e4c71966aa36f5a8219cd_PART_013'
VERSION='v1'
dx,dy,dz=(40.59696648719584, 90.0, 28.96722957653507)
shape=cq.Workplane('XZ').circle(17.3910490159).extrude(90,both=True)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
