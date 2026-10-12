import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-16,0),(-10,-3)).segment((-1,1)).segment((-16,1)).close().assemble().finalize().extrude(-41).union(w0.workplane(offset=-5/2).moveTo(4,-0.5).box(24,5,5)).union(w1.sketch().arc((-8,1),(-3,0),(-8,2)).arc((-7,1),(-8,1)).assemble().finalize().extrude(-200))