import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_da7af66ce5df4629802e97dc03d186f5_PART_000'
VERSION='v1'
dx,dy,dz=(90.0, 57.65976433902256, 75.05767802768463)
shape=cq.Workplane('YZ').circle(33.1793605917).extrude(90,both=True)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
