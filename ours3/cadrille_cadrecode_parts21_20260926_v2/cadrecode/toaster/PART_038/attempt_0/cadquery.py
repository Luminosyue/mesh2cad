import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-4,-11),(3,-15)).arc((4,0),(3,15)).close().assemble().finalize().extrude(31).union(w0.sketch().arc((-3,-2),(0,-1),(-1,-4)).arc((2,7),(-3,-2)).assemble().finalize().extrude(200))