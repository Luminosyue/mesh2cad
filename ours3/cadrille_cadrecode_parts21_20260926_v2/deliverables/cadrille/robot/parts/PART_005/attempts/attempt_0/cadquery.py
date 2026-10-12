import cadquery as cq
w0=cq.Workplane('YZ',origin=(29,0,0))
w1=cq.Workplane('XY',origin=(0,0,39))
r=w0.sketch().segment((-92,-1),(-43,-74)).segment((-11,-53)).arc((35,-47),(68,-13)).segment((92,1)).segment((43,74)).segment((11,53)).arc((-35,47),(-68,13)).close().assemble().finalize().extrude(-72).union(w0.sketch().circle(68).circle(47,mode='s').finalize().extrude(33)).union(w0.workplane(offset=71/2).cylinder(71,16)).union(w1.sketch().arc((-78,39),(77,-20),(-74,47)).arc((-73,41),(-78,39)).assemble().finalize().extrude(-91))