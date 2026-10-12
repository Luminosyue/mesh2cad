from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='azure_snake_tieks_leather_snake_print_ballet_flats')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'azure_snake_tieks_leather_snake_print_ballet_flats_assembly.step'))
