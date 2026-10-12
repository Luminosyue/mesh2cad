from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='asus_z97iplus_motherboard_mini_itx_lga1150_socket')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'asus_z97iplus_motherboard_mini_itx_lga1150_socket_assembly.step'))
