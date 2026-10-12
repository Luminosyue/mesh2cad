import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-1,-5),(1,-6)).segment((2,0)).arc((0,0),(-1,5)).arc((-4,1),(-1,-2)).close().assemble().finalize().extrude(200)