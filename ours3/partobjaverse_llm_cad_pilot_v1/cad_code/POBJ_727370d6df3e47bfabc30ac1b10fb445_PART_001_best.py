import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_727370d6df3e47bfabc30ac1b10fb445_PART_001'
VERSION='v1'
dx,dy,dz=(32.51492654905326, 7.5225882800909405, 90.0)
outer=cq.Workplane('XY').box(dx,dy,dz)
inner=cq.Workplane('XY').box(max(dx-2*0.752258828009,.2),max(dy-2*0.752258828009,.2),max(dz-0.752258828009,.2)).translate((0,0,0.376129414005))
shape=outer.cut(inner)
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
