import cadquery as cq
w0=cq.Workplane('YZ',origin=(5,0,0))
w1=cq.Workplane('ZX',origin=(0,-58,0))
r=w0.sketch().segment((-100,5),(-87,-12)).segment((-71,2)).segment((-72,2)).segment((-72,12)).close().assemble().finalize().extrude(-10).union(w1.workplane(offset=158/2).moveTo(7,0).cylinder(158,2))