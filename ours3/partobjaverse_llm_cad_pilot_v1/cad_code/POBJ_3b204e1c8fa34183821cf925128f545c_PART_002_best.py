import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_3b204e1c8fa34183821cf925128f545c_PART_002'
VERSION='v1'
dx,dy,dz=(90.0, 80.24159484518107, 64.13697502114077)
outer=cq.Workplane('XY').box(dx,dy,dz)
inner=cq.Workplane('XY').box(max(dx-2*6.41369750211,.2),max(dy-2*6.41369750211,.2),max(dz-6.41369750211,.2)).translate((0,0,3.20684875106))
shape=outer.cut(inner)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
