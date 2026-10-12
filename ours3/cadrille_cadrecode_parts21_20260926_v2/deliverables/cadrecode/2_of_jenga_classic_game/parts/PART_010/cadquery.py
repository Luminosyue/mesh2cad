import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-76))
w1=cq.Workplane('XY',origin=(0,0,-75))
r=w0.sketch().segment((-97,-93),(92,-100)).segment((99,94)).segment((-94,100)).close().assemble().push([(-19,2)]).circle(75,mode='s').finalize().extrude(115).union(w0.workplane(offset=153/2).moveTo(63,-65).cylinder(153,33)).union(w1.sketch().segment((-97,-93),(94,-93)).segment((94,96)).segment((-97,96)).segment((-97,-28)).arc((-99,-37),(-97,-46)).close().assemble().finalize().extrude(113))