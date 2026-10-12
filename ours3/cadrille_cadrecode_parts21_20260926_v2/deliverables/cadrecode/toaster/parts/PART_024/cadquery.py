import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-65,0))
r=w0.sketch().segment((-1,-8),(2,-9)).segment((4,-4)).segment((1,-4)).segment((1,0)).close().assemble().finalize().extrude(-35).union(w0.sketch().arc((-3,-4),(1,-8),(4,-4)).segment((3,-4)).segment((3,-2)).segment((3,-1)).arc((0,-1),(-3,-3)).segment((-2,-3)).segment((-2,-4)).close().assemble().finalize().extrude(165))