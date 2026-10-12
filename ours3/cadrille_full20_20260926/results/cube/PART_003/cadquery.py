import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,89,0))
w1=cq.Workplane('XY',origin=(0,0,-90))
r=w0.sketch().segment((-100,-91),(88,-99)).segment((91,-2)).arc((97,16),(93,35)).segment((94,91)).segment((-94,94)).close().assemble().push([(-3,-3)]).circle(88,mode='s').finalize().extrude(-185).union(w1.sketch().push([(0,-4)]).circle(96).circle(91,mode='s').finalize().extrude(180))