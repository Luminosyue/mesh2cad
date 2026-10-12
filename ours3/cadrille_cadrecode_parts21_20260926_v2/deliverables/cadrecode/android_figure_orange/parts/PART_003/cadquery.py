import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
w1=cq.Workplane('ZX',origin=(0,17,0))
r=w0.workplane(offset=-101/2).moveTo(-3,-1).cylinder(101,35).union(w0.workplane(offset=79/2).moveTo(8,1).cylinder(79,35)).union(w0.workplane(offset=99/2).moveTo(8,1).cylinder(99,19)).union(w1.sketch().arc((-100,-1),(10,-35),(58,44)).segment((58,1)).segment((-9,1)).segment((-9,-34)).segment((-100,-34)).close().assemble().finalize().extrude(-31))