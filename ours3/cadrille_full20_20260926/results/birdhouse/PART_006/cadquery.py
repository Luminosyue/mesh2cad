import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-89))
w1=cq.Workplane('XY',origin=(0,0,-70))
r=w0.sketch().push([(-37,56)]).circle(44).circle(33,mode='s').finalize().extrude(-9).union(w0.sketch().segment((-99,40),(-93,-100)).segment((25,-93)).segment((20,16)).arc((19,18),(19,20)).segment((18,44)).close().assemble().push([(-37,-28)]).circle(51,mode='s').finalize().extrude(19)).union(w1.sketch().push([(-37,56)]).circle(25).circle(11,mode='s').finalize().extrude(-19))