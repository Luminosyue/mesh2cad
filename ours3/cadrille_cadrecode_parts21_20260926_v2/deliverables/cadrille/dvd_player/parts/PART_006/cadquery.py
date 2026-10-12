import cadquery as cq
w0=cq.Workplane('YZ',origin=(95,0,0))
r=w0.sketch().segment((-1,-100),(1,-100)).segment((1,-89)).segment((0,-89)).segment((0,-86)).segment((1,-86)).segment((1,100)).segment((-1,100)).close().assemble().finalize().extrude(-191)