import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-9,-6),(9,-6)).segment((8,6)).segment((-9,6)).close().assemble().circle(2,mode='s').finalize().extrude(200)