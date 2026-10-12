import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('YZ',origin=(-34,0,0))
r=w0.sketch().segment((-96,-62),(-93,-100)).segment((-23,-94)).segment((-26,-57)).close().assemble().finalize().extrude(54).union(w0.sketch().segment((-99,-94),(-30,-99)).segment((-28,-61)).segment((-98,-57)).close().assemble().finalize().extrude(198)).union(w1.sketch().segment((-98,-94),(-31,-94)).segment((-31,-66)).segment((-98,-66)).segment((-98,-70)).arc((-100,-78),(-98,-86)).close().assemble().finalize().extrude(124))