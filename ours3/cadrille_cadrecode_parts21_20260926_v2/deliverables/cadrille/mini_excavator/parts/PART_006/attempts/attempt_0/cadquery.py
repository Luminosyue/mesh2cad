import cadquery as cq
w0=cq.Workplane('YZ',origin=(-12,0,0))
w1=cq.Workplane('YZ',origin=(-19,0,0))
r=w0.sketch().segment((14,-91),(20,-100)).segment((37,-90)).segment((32,-81)).close().assemble().finalize().extrude(14).union(w0.workplane(offset=28/2).moveTo(29,26).cylinder(28,26)).union(w0.sketch().segment((-64,61),(-12,32)).segment((5,63)).segment((10,63)).segment((10,72)).segment((11,74)).segment((-48,100)).close().assemble().finalize().extrude(31)).union(w1.sketch().arc((14,-52),(32,-94),(56,-56)).arc((37,-10),(14,-52)).assemble().finalize().extrude(32))