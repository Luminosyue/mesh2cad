import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-90,0))
w1=cq.Workplane('YZ',origin=(96,0,0))
r=w0.sketch().segment((-100,-89),(87,-96)).segment((100,93)).segment((-96,96)).close().assemble().push([(0,1)]).circle(90,mode='s').finalize().extrude(179).union(w1.sketch().push([(-42,12)]).circle(53).circle(29,mode='s').finalize().extrude(-163))