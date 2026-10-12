import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-9,-6),(9,-7)).segment((9,-6)).segment((9,6)).segment((-9,7)).close().assemble().circle(1,mode='s').finalize().extrude(200)