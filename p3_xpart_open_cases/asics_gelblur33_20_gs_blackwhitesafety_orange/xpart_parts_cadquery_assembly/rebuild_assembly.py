from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='asics_gelblur33_20_gs_blackwhitesafety_orange')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'asics_gelblur33_20_gs_blackwhitesafety_orange_assembly.step'))
