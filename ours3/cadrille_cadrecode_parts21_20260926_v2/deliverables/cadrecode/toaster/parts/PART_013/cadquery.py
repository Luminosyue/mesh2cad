import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-11,0))
w1=cq.Workplane('XY',origin=(0,0,90))
r=w0.sketch().segment((88,3),(92,1)).segment((100,7)).segment((96,9)).close().assemble().finalize().extrude(7).union(w0.workplane(offset=23/2).moveTo(69,0).cylinder(23,3)).union(w1.workplane(offset=-190/2).moveTo(-4,-5).cylinder(190,2))