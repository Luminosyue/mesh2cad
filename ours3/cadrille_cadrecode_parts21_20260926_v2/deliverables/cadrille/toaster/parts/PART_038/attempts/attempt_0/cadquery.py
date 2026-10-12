import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-4,-12),(4,-14)).segment((4,12)).segment((-4,5)).close().assemble().finalize().extrude(200)