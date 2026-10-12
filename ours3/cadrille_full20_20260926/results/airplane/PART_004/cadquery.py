import cadquery as cq
w0=cq.Workplane('YZ',origin=(-11,0,0))
w1=cq.Workplane('XY',origin=(0,0,-67))
r=w0.sketch().segment((-100,-68),(20,-99)).segment((21,-96)).segment((-96,-62)).close().assemble().finalize().extrude(-87).union(w0.sketch().segment((-93,-63),(-92,-70)).segment((-5,-87)).segment((-5,-81)).close().assemble().finalize().extrude(107)).union(w1.sketch().push([(48,-59)]).circle(31).circle(30,mode='s').finalize().extrude(7))