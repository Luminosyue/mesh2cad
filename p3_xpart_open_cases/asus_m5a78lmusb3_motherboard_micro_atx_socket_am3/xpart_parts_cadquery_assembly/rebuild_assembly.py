from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='asus_m5a78lmusb3_motherboard_micro_atx_socket_am3')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'asus_m5a78lmusb3_motherboard_micro_atx_socket_am3_assembly.step'))
