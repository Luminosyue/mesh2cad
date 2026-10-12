import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-28,0))
w1=cq.Workplane('XY',origin=(0,0,-34))
r=w0.workplane(offset=-62/2).cylinder(62,48).union(w0.workplane(offset=83/2).cylinder(83,93)).union(w0.workplane(offset=127/2).cylinder(127,44)).union(w1.sketch().arc((-4,-100),(10,-97),(22,-93)).arc((-10,99),(-4,-100)).assemble().finalize().extrude(52))