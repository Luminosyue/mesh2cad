import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((0,1),(0,9)).arc((-1,-8),(2,8)).segment((2,1)).close().assemble().finalize().extrude(36).union(w0.workplane(offset=200/2).moveTo(0,-4).cylinder(200,4))