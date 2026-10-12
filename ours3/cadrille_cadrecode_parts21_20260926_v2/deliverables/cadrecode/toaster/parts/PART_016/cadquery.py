import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-96))
r=w0.sketch().segment((-14,-8),(-6,-18)).segment((9,10)).segment((2,17)).close().assemble().finalize().extrude(-4).union(w0.sketch().arc((1,12),(4,9),(6,12)).segment((5,12)).segment((5,14)).arc((3,14),(1,13)).close().assemble().finalize().extrude(196))