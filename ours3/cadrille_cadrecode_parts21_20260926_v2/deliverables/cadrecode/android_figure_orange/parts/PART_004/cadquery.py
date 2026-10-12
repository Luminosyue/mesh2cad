import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-45))
w1=cq.Workplane('ZX',origin=(0,-16,0))
r=w0.workplane(offset=-50/2).moveTo(0,-1).cylinder(50,34).union(w0.workplane(offset=123/2).moveTo(0,-1).cylinder(123,57)).union(w0.workplane(offset=145/2).moveTo(0,-1).cylinder(145,30)).union(w1.sketch().push([(-18,0)]).circle(82).circle(57,mode='s').finalize().extrude(40))