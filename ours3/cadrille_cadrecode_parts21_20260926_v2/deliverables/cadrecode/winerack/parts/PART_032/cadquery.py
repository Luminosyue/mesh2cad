import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-10,-5),(-9,-7)).segment((10,-7)).segment((10,6)).segment((-10,7)).close().assemble().finalize().extrude(200)