import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-97))
r=w0.sketch().segment((-100,-96),(-24,-100)).segment((-23,96)).segment((-98,99)).close().assemble().push([(-61,29)]).circle(68,mode='s').finalize().extrude(199).union(w1.sketch().push([(-61.5,0)]).rect(57,192).push([(-61,0)]).circle(24,mode='s').finalize().extrude(194))