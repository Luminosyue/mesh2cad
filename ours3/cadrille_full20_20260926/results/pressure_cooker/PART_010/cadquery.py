import cadquery as cq
w0=cq.Workplane('YZ',origin=(-57,0,0))
w1=cq.Workplane('ZX',origin=(0,28,0))
r=w0.workplane(offset=118/2).moveTo(50,-30).cylinder(118,50).union(w0.sketch().push([(-21,-34)]).circle(66).circle(45,mode='s').finalize().extrude(138)).union(w1.sketch().push([(-34,-11)]).circle(86).circle(65,mode='s').finalize().extrude(-72))