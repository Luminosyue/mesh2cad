import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-3,-1),(1,-7)).arc((3,1),(1,7)).arc((-1,3),(-3,2)).arc((-3,1),(-3,-1)).assemble().finalize().extrude(-200)