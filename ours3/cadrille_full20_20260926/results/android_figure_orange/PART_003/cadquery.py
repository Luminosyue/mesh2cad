import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-58,0))
w1=cq.Workplane('XY',origin=(0,0,52))
r=w0.sketch().push([(-66,-59)]).circle(31).circle(29,mode='s').finalize().extrude(-34).union(w0.sketch().segment((-96,-60),(-88,-60)).arc((-66,-74),(-43,-60)).segment((-35,-60)).segment((-35,-40)).segment((-43,-40)).arc((-66,-26),(-88,-40)).segment((-96,-40)).close().assemble().push([(44,-49)]).circle(51).circle(50,mode='s').finalize().extrude(-27)).union(w1.sketch().push([(-59,-64)]).circle(36).circle(34,mode='s').finalize().extrude(-141))