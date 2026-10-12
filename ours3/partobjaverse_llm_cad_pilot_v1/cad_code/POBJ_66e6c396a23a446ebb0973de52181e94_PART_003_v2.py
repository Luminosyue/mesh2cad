import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_66e6c396a23a446ebb0973de52181e94_PART_003'
VERSION='v2'
dx,dy,dz=(46.884881678855066, 24.522316630200773, 100.0)
outer=cq.Workplane('XY').box(dx,dy,dz)
inner=cq.Workplane('XY').box(max(dx-2*2.45223166302,.2),max(dy-2*2.45223166302,.2),max(dz-2.45223166302,.2)).translate((0,0,1.22611583151))
shape=outer.cut(inner)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
