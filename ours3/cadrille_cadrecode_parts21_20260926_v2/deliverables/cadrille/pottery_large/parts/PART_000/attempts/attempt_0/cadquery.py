import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-76,0))
w1=cq.Workplane('ZX',origin=(0,-99,0))
r=w0.sketch().circle(87).circle(76,mode='s').finalize().extrude(176).union(w1.sketch().circle(79).push([(-28,10)]).circle(37,mode='s').finalize().extrude(22))