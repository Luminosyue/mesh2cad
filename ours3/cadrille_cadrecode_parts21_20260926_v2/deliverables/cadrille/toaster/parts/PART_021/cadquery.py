import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-5,-11),(5,0),(-3,12)).close().assemble().finalize().extrude(200)