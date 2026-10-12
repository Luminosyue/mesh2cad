import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-8,10),(-7,-11)).segment((8,-11)).segment((7,11)).segment((-7,11)).close().assemble().finalize().extrude(-200)