import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_3b204e1c8fa34183821cf925128f545c_PART_002'
VERSION='v2'
dx,dy,dz=(100.0, 89.15732760575673, 71.2633055790453)
outer=cq.Workplane('XY').box(dx,dy,dz)
inner=cq.Workplane('XY').box(max(dx-2*7.1263305579,.2),max(dy-2*7.1263305579,.2),max(dz-7.1263305579,.2)).translate((0,0,3.56316527895))
shape=outer.cut(inner)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
