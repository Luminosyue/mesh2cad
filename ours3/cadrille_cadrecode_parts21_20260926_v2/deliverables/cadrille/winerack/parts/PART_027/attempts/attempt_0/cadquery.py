import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-9,-5),(9,-6)).segment((9,5)).segment((-9,6)).close().assemble().circle(3,mode='s').finalize().extrude(90).union(w0.sketch().segment((-8,-5),(8,-5)).segment((8,1)).arc((1,6),(-8,5)).close().assemble().finalize().extrude(200))