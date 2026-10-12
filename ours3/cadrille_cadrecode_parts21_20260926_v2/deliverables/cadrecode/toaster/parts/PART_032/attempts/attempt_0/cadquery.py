import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-5,9),(1,-9)).segment((6,-9)).segment((4,7)).close().assemble().finalize().extrude(190).union(w0.sketch().arc((-6,0),(-2,-3),(2,-9)).arc((1,0),(-6,9)).close().assemble().finalize().extrude(200))