import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-6,13),(-5,13)).segment((-5,-13)).arc((-3,-14),(-1,-16)).arc((5,0),(-1,16)).arc((-3,15),(-6,13)).assemble().finalize().extrude(200)