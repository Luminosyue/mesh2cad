import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-97,0))
r=w0.sketch().arc((-4,0),(0,-2),(4,0)).arc((3,3),(1,6)).arc((-1,5),(-3,5)).arc((-4,3),(-4,0)).assemble().finalize().extrude(-3).union(w0.sketch().segment((-2,-2),(1,-4)).segment((2,-2)).segment((2,-1)).segment((3,-1)).segment((3,0)).segment((-1,0)).segment((-1,-1)).segment((-2,-1)).arc((0,-5),(-2,-2)).assemble().finalize().extrude(197))