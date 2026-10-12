import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-76,0))
w1=cq.Workplane('ZX',origin=(0,-98,0))
r=w0.sketch().push([(0,1)]).circle(76).circle(66,mode='s').finalize().extrude(-23).union(w0.sketch().push([(0,1)]).circle(96).circle(90,mode='s').finalize().extrude(175)).union(w1.sketch().push([(0,1)]).circle(76).circle(22,mode='s').finalize().extrude(21))