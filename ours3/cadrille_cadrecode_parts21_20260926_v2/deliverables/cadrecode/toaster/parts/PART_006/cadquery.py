import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-5,0),(1,-4)).segment((5,-1)).segment((-2,3)).close().assemble().finalize().extrude(32).union(w0.workplane(offset=200/2).moveTo(1,1).cylinder(200,3))