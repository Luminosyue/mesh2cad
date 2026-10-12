import cadquery as cq
w0=cq.Workplane('YZ',origin=(-95,0,0))
r=w0.sketch().segment((-95,14),(-25,-7)).arc((-19,2),(-10,10)).segment((-92,26)).close().assemble().reset().face(w0.sketch().segment((-10,-10),(92,-26)).segment((95,-14)).segment((25,7)).arc((19,-2),(10,-10)).close().assemble()).finalize().extrude(192).union(w0.workplane(offset=194/2).moveTo(-54,13).cylinder(194,11))