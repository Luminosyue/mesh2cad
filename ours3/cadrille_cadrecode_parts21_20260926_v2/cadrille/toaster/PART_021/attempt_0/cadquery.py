import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().segment((-5,-10),(-2,-13)).arc((5,0),(-2,13)).arc((-4,11),(-5,10)).close().assemble().finalize().extrude(200)