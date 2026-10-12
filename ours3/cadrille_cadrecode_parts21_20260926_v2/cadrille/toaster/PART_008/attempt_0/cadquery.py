import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-7,-2),(-1,-4)).arc((0,-2),(1,-4)).segment((4,-4)).segment((7,-1)).segment((4,3)).close().assemble().finalize().extrude(-200)