import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-31))
w1=cq.Workplane('ZX',origin=(0,62,0))
r=w0.sketch().segment((-7,-100),(7,-100)).segment((7,-94)).arc((98,0),(7,94)).segment((7,100)).segment((-7,100)).segment((-7,94)).arc((-98,0),(-7,-94)).close().assemble().finalize().extrude(-65).union(w0.workplane(offset=121/2).cylinder(121,70)).union(w1.sketch().arc((-96,-10),(89,-16),(-96,10)).close().assemble().finalize().extrude(-148))