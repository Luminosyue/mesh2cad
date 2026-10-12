import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-9,-6),(9,-6)).segment((9,-5)).segment((9,6)).segment((-1,7)).segment((-1,5)).segment((-5,5)).segment((-5,7)).segment((-9,6)).close().assemble().finalize().extrude(200)