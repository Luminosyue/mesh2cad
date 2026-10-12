import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-3,-1),(1,-7)).segment((3,-5)).segment((1,-4)).arc((3,2),(-2,3)).arc((-3,0),(-3,-1)).assemble().finalize().extrude(200)