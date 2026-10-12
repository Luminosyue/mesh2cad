import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().arc((-1,2),(-2,-1),(1,-3)).segment((1,-2)).segment((2,-2)).segment((2,-3)).arc((3,-2),(3,-1)).arc((4,1),(2,2)).arc((1,3),(-1,2)).assemble().finalize().extrude(-200).union(w0.sketch().segment((-6,0),(1,-4)).segment((6,0)).segment((-1,4)).close().assemble().finalize().extrude(-24))