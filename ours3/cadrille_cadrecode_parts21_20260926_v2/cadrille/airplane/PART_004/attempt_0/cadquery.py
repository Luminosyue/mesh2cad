import cadquery as cq
w0=cq.Workplane('YZ',origin=(-97,0,0))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-59,12),(48,-18)).segment((49,-12)).segment((-57,18)).close().assemble().finalize().extrude(197).union(w1.workplane(offset=25/2).moveTo(51,-15).cylinder(25,8))