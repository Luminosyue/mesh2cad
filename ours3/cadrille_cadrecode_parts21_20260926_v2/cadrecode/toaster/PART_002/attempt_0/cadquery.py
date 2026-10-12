import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,76,0))
r=w0.sketch().segment((1,-4),(4,-1)).segment((3,1)).arc((2,0),(1,-1)).close().assemble().finalize().extrude(-176).union(w0.sketch().segment((-7,1),(1,-4)).segment((7,1)).segment((0,4)).arc((-2,3),(-3,3)).close().assemble().finalize().extrude(24))