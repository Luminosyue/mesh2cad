import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,96,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-6,4),(1,4)).segment((1,-1)).segment((6,-1)).segment((6,1)).segment((4,1)).segment((4,4)).segment((5,4)).segment((5,-3)).segment((3,-3)).arc((6,-2),(6,1)).segment((4,1)).segment((4,3)).arc((-1,4),(-6,4)).assemble().finalize().extrude(-196).union(w1.sketch().arc((1,-6),(5,0),(4,6)).arc((4,4),(3,3)).arc((3,1),(1,-1)).close().assemble().finalize().extrude(-105))