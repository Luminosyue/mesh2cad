import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,19))
w1=cq.Workplane('ZX',origin=(0,48,0))
r=w0.sketch().push([(0,2)]).circle(96).circle(69,mode='s').finalize().extrude(-44).union(w0.workplane(offset=4/2).moveTo(0,2).cylinder(4,98)).union(w1.workplane(offset=-148/2).moveTo(0,2).cylinder(148,27))