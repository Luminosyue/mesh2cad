import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.workplane(offset=-200/2).moveTo(-1,2).cylinder(200,3).union(w0.sketch().segment((-2,-5),(2,-5)).arc((0,-4),(-2,-5)).assemble().finalize().extrude(-172))