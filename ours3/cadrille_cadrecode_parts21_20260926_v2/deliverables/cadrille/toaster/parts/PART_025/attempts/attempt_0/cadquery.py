import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-4,-8),(3,-14)).segment((4,-11)).segment((4,9)).close().assemble().finalize().extrude(196).union(w0.sketch().segment((1,14),(3,14)).segment((3,11)).arc((4,12),(4,13)).arc((2,13),(1,14)).assemble().finalize().extrude(200))