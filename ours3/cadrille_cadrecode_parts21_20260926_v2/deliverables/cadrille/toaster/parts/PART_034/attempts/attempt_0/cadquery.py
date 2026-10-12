import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,3,0))
w1=cq.Workplane('XY',origin=(0,0,50))
r=w0.sketch().push([(69,1)]).circle(31).circle(21,mode='s').finalize().extrude(-9).union(w0.sketch().push([(-61,0)]).circle(39).circle(22,mode='s').push([(14.5,0)]).rect(81,70).push([(14,0)]).circle(23,mode='s').finalize().extrude(2)).union(w1.sketch().push([(0,0)]).circle(6).push([(0,1)]).circle(3,mode='s').finalize().extrude(-129))