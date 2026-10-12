import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((6,-3),(6,0)).segment((8,0)).arc((-8,1),(7,-3)).close().assemble().finalize().extrude(-200)