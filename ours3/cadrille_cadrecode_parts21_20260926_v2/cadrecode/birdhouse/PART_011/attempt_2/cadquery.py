import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-51,0))
w1=cq.Workplane('YZ',origin=(-10,0,0))
r=w0.sketch().arc((-11,-9),(0,-10),(11,-11)).segment((11,6)).segment((2,6)).segment((2,11)).segment((-1,11)).segment((-1,6)).segment((-11,6)).close().assemble().finalize().extrude(5).union(w0.sketch().arc((-6,-1),(-6,-7),(-2,-9)).arc((7,2),(-6,-1)).assemble().finalize().extrude(151)).union(w1.workplane(offset=13/2).moveTo(-97,1).cylinder(13,3))