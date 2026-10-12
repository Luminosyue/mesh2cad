import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-5,0),(-1,-1)).segment((-1,0)).segment((1,0)).segment((1,-2)).segment((2,-2)).arc((2,3),(-5,0)).assemble().finalize().extrude(-200)