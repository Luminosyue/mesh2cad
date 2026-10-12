import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
w1=cq.Workplane('ZX',origin=(0,45,0))
r=w0.sketch().circle(85).circle(67,mode='s').finalize().extrude(-51).union(w0.workplane(offset=-15/2).cylinder(15,100)).union(w0.sketch().circle(79).circle(65,mode='s').finalize().extrude(67)).union(w1.sketch().circle(78).circle(65,mode='s').finalize().extrude(14))