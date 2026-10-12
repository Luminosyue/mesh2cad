import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().arc((-3,-1),(-1,-3),(1,-7)).arc((3,1),(0,7)).close().assemble().finalize().extrude(-200)