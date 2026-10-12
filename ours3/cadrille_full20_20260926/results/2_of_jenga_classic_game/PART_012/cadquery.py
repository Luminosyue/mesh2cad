import cadquery as cq
w0=cq.Workplane('YZ',origin=(92,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-100,-65),(-96,-100)).segment((-47,-96)).segment((-47,-99)).segment((10,-99)).segment((10,-94)).segment((19,-93)).segment((15,-58)).segment((-44,-62)).segment((-44,-58)).segment((-82,-58)).segment((-82,-64)).close().assemble().finalize().extrude(-192).union(w1.workplane(offset=-198/2).moveTo(-21,-79).cylinder(198,21))