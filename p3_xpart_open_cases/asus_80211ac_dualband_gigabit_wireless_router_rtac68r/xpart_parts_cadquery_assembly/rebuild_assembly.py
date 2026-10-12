from pathlib import Path
import cadquery as cq
r=Path(__file__).resolve().parent
a=cq.Assembly(name='asus_80211ac_dualband_gigabit_wireless_router_rtac68r')
for p in sorted((r.parent/"xpart_parts_cadquery_features").glob("PART_*/*.step")):
    a.add(cq.importers.importStep(str(p)).val(),name=p.stem)
a.export(str(r/'asus_80211ac_dualband_gigabit_wireless_router_rtac68r_assembly.step'))
