import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((6,-4),(7,-2)).segment((8,-2)).arc((-7,3),(7,-3)).close().assemble().finalize().extrude(-200)