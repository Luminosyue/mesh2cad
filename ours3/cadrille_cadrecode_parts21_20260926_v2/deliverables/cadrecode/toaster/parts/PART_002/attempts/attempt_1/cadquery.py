import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-2,1),(-1,1)).segment((-1,3)).segment((0,3)).segment((0,2)).segment((2,2)).segment((2,3)).arc((-2,-1),(0,3)).segment((-1,3)).segment((-1,1)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-5,-1),(1,-4)).segment((5,1)).segment((-1,4)).close().assemble().finalize().extrude(-23))