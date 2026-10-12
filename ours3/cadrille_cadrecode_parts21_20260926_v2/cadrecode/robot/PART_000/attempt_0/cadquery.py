import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
w1=cq.Workplane('XY',origin=(0,0,97))
r=w0.workplane(offset=-111/2).moveTo(0,8).cylinder(111,23).union(w0.sketch().segment((-100,12),(-1,-89)).segment((100,11)).segment((1,89)).close().assemble().finalize().extrude(-15)).union(w0.sketch().push([(0,8)]).circle(79).circle(47,mode='s').finalize().extrude(87)).union(w1.sketch().push([(-1,8)]).circle(81).circle(51,mode='s').finalize().extrude(-174))