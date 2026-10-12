import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,14))
w1=cq.Workplane('ZX',origin=(0,23,0))
r=w0.workplane(offset=-103/2).moveTo(-3,-1).cylinder(103,36).union(w0.workplane(offset=76/2).moveTo(7,1).cylinder(76,35)).union(w1.sketch().arc((-10,28),(-99,-7),(-4,-18)).arc((99,12),(-10,28)).assemble().finalize().extrude(-45))