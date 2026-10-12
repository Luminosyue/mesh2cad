import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-27,0))
w1=cq.Workplane('XY',origin=(0,0,-27))
r=w0.workplane(offset=-56/2).moveTo(0,6).cylinder(56,79).union(w0.workplane(offset=85/2).moveTo(0,6).cylinder(85,80)).union(w0.workplane(offset=126/2).moveTo(0,6).cylinder(126,51)).union(w1.sketch().arc((-93,0),(92,-19),(-92,11)).arc((-91,6),(-93,0)).assemble().finalize().extrude(55))