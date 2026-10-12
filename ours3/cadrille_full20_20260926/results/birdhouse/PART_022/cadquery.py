import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
r=w0.sketch().segment((-100,-90),(15,-90)).segment((15,-86)).arc((25,-50),(15,-14)).segment((15,27)).segment((-100,27)).close().assemble().finalize().extrude(198).union(w0.sketch().segment((-100,-90),(15,-100)).segment((25,0)).segment((-90,10)).close().assemble().finalize().extrude(198))