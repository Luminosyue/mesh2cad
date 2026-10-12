import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-22,0))
w1=cq.Workplane('YZ',origin=(-23,0,0))
r=w0.sketch().segment((-71,-26),(71,-22)).segment((71,54)).segment((-71,51)).close().assemble().finalize().extrude(-68).union(w0.sketch().segment((-100,3),(-99,3)).arc((-68,-27),(-26,-20)).arc((99,10),(-29,26)).arc((-69,49),(-99,10)).segment((-100,10)).close().assemble().finalize().extrude(63)).union(w0.workplane(offset=120/2).moveTo(0,13).cylinder(120,38)).union(w1.workplane(offset=75/2).moveTo(0,3).cylinder(75,96))