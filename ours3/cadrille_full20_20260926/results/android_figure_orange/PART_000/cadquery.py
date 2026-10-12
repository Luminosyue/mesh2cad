import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('ZX',origin=(0,-80,0))
r=w0.sketch().segment((-100,-5),(-99,-5)).arc((-6,-100),(97,-5)).segment((100,-5)).segment((100,5)).segment((97,5)).arc((90,39),(72,68)).segment((72,78)).segment((61,78)).arc((-21,97),(-91,41)).segment((-92,41)).segment((-92,39)).arc((-97,22),(-99,5)).segment((-100,5)).close().assemble().finalize().extrude(14).union(w1.sketch().push([(-57,0)]).circle(63).circle(56,mode='s').finalize().extrude(145))