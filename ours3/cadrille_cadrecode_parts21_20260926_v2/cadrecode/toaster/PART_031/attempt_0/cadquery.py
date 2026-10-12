import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
w1=cq.Workplane('ZX',origin=(0,79,0))
r=w0.sketch().arc((-3,-2),(0,-4),(3,-2)).close().assemble().reset().face(w0.sketch().segment((-3,2),(3,2)).arc((0,4),(-3,2)).assemble()).finalize().extrude(-199).union(w1.sketch().arc((1,-7),(4,0),(1,7)).close().assemble().finalize().extrude(-83))