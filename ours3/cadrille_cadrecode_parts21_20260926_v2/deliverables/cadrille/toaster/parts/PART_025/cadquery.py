import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-4,-8),(0,-13),(4,-14)).segment((4,9)).arc((0,9),(-4,7)).close().assemble().finalize().extrude(198).union(w0.sketch().segment((1,14),(2,-9)).segment((4,-9)).segment((2,14)).close().assemble().finalize().extrude(200))