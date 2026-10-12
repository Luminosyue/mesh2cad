import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
r=w0.sketch().arc((-1,-4),(0,-4),(1,-3)).segment((2,-3)).segment((2,-2)).arc((3,0),(2,2)).segment((2,3)).segment((1,3)).arc((0,3),(-1,4)).segment((-1,3)).arc((-4,0),(-1,-3)).close().assemble().finalize().extrude(-103).union(w0.sketch().segment((1,-7),(2,-7)).segment((3,7)).segment((1,7)).close().assemble().finalize().extrude(97))