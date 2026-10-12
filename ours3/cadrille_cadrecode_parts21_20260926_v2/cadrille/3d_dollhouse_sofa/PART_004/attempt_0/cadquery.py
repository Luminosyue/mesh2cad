import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-6,-10),(5,-12)).segment((6,10)).segment((-5,11)).close().assemble().finalize().extrude(-200)