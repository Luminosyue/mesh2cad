import cadquery as cq
from pathlib import Path
OUT=Path('/data/home/cuiyuehan/project/mesh2cad/ours3/partobjaverse_llm_cad_pilot_v1')
CASE='POBJ_2830f5fdb88942d5a3285a7433b4efea_PART_000'
VERSION='v3'
dx,dy,dz=(99.85351745299333, 100.0, 99.78026068168613)
shape=(cq.Workplane('XY').workplane(offset=-dz/2).ellipse(dx*.32,dy*.38).workplane(offset=dz*.25).ellipse(dx*.48,dy*.45).workplane(offset=dz*.25).ellipse(dx*.42,dy*.34).workplane(offset=dz*.25).ellipse(dx*.28,dy*.30).loft(combine=True))
assert shape.val() is not None
assert shape.val().isValid()
cq.exporters.export(shape,str(OUT/'step'/f'{CASE}_{VERSION}.step'))
cq.exporters.export(shape,str(OUT/'recon_mesh'/f'{CASE}_{VERSION}.stl'),tolerance=0.08,angularTolerance=0.15)
