import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,67))
w1=cq.Workplane('ZX',origin=(0,-58,0))
r=w0.workplane(offset=-164/2).moveTo(9,-5).cylinder(164,24).union(w0.workplane(offset=-75/2).moveTo(9,-5).cylinder(75,47)).union(w0.sketch().push([(9,-5)]).circle(95).circle(89,mode='s').finalize().extrude(-65)).union(w1.workplane(offset=129/2).moveTo(33,-59).cylinder(129,34))