import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
w1=cq.Workplane('ZX',origin=(0,45,0))
r=w0.sketch().push([(0,1)]).circle(83).circle(65,mode='s').finalize().extrude(-50).union(w0.sketch().segment((-49,86),(-49,87)).arc((41,-89),(-37,93)).segment((-37,86)).close().assemble().finalize().extrude(-12)).union(w0.sketch().push([(0,1)]).circle(78).circle(63,mode='s').finalize().extrude(67)).union(w1.sketch().push([(0,1)]).circle(80).circle(64,mode='s').finalize().extrude(14))