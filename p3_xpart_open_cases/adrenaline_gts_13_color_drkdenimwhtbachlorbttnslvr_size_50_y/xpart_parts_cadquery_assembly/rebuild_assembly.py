from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='adrenaline_gts_13_color_drkdenimwhtbachlorbttnslvr_size_50_y')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'adrenaline_gts_13_color_drkdenimwhtbachlorbttnslvr_size_50_y_assembly.step'))
