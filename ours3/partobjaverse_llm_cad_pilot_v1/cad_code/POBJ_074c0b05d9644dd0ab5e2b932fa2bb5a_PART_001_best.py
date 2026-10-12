import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_074c0b05d9644dd0ab5e2b932fa2bb5a_PART_001'
VERSION='v1'
dx,dy,dz=(3.10608085220106, 90.0, 73.0820420551282)
outer=cq.Workplane('XY').box(dx,dy,dz)
inner=cq.Workplane('XY').box(max(dx-2*0.35,.2),max(dy-2*0.35,.2),max(dz-0.35,.2)).translate((0,0,0.175))
shape=outer.cut(inner)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
