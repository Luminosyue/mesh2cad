import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,68))
r=w0.sketch().arc((-5,-12),(-3,-15),(0,-14)).arc((3,-11),(6,-7)).segment((5,-7)).segment((5,6)).arc((1,14),(-5,15)).close().assemble().finalize().extrude(-168).union(w0.sketch().arc((-5,-10),(5,0),(-5,10)).close().assemble().finalize().extrude(32))