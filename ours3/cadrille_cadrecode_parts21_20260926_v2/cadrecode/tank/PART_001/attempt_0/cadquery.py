import cadquery as cq
w0=cq.Workplane('YZ',origin=(-5,0,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-98,7),(-87,-12)).segment((-68,1)).segment((-72,12)).segment((-72,7)).close().assemble().finalize().extrude(10).union(w1.workplane(offset=200/2).moveTo(7,0).cylinder(200,2))