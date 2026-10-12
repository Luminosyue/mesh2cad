import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-24,-18),(24,-17)).arc((18,2),(-2,11)).segment((-13,18)).segment((-24,1)).close().assemble().finalize().extrude(-200)