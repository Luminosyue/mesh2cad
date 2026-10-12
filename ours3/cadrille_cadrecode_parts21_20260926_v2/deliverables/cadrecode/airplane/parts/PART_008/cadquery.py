import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-16,0))
w1=cq.Workplane('ZX',origin=(0,-1,0))
r=w0.sketch().segment((-13,-17),(-1,-20)).segment((4,0)).arc((-3,3),(-6,6)).close().assemble().finalize().extrude(-84).union(w0.sketch().arc((-2,16),(9,8),(4,-2)).segment((7,-9)).arc((12,10),(-2,16)).assemble().finalize().extrude(110)).union(w1.sketch().arc((0,18),(10,3),(3,-12)).segment((3,-14)).arc((13,7),(0,19)).close().assemble().finalize().extrude(101))