import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-15,0))
r=w0.workplane(offset=7/2).cylinder(7,46).union(w0.sketch().segment((-100,44),(-99,-46)).segment((100,-46)).segment((99,46)).close().assemble().reset().face(w0.sketch().segment((-93,-42),(94,-42)).segment((94,40)).segment((-93,40)).segment((-93,13)).arc((-96,10),(-93,7)).close().assemble(),mode='s').finalize().extrude(30))