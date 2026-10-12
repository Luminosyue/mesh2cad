import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,20))
w1=cq.Workplane('ZX',origin=(0,-96,0))
r=w0.sketch().push([(0,2)]).circle(98).circle(89,mode='s').finalize().extrude(-45).union(w1.workplane(offset=177/2).moveTo(0,-10).cylinder(177,27))