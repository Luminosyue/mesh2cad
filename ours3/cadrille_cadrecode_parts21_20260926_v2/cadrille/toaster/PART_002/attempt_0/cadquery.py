import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,77,0))
r=w0.sketch().segment((0,-3),(0,-2)).segment((2,-2)).arc((-1,2),(0,-3)).assemble().finalize().extrude(-177).union(w0.sketch().segment((-6,1),(4,-2)).segment((6,2)).segment((1,4)).arc((-1,2),(-3,4)).segment((-4,4)).close().assemble().finalize().extrude(23))