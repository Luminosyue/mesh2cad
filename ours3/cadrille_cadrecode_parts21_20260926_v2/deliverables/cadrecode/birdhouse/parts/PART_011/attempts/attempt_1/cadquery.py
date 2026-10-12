import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-50,0))
w1=cq.Workplane('YZ',origin=(-11,0,0))
r=w0.sketch().push([(1,-3)]).circle(8).circle(7,mode='s').finalize().extrude(-47).union(w0.sketch().arc((-6,-6),(-5,-9),(-3,-10)).segment((-3,-9)).segment((6,-9)).arc((8,-3),(6,3)).segment((6,2)).segment((5,2)).segment((5,3)).segment((6,3)).arc((-1,3),(-6,-1)).arc((-6,-3),(-6,-6)).assemble().finalize().extrude(150)).union(w1.workplane(offset=14/2).moveTo(-48,0).cylinder(14,11))