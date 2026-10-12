import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-7))
w1=cq.Workplane('YZ',origin=(47,0,0))
r=w0.sketch().push([(84,9)]).circle(16).circle(10,mode='s').finalize().extrude(19).union(w1.sketch().arc((-26,-12),(-22,-14),(-19,-14)).segment((-19,-5)).segment((-18,-5)).segment((-18,5)).segment((-19,5)).segment((-19,14)).arc((-22,14),(-26,12)).close().assemble().finalize().extrude(-147))