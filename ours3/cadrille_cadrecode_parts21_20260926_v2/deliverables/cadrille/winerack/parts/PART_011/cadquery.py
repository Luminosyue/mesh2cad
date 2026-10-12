import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-9,-6),(9,-6)).segment((9,6)).segment((6,6)).arc((2,5),(-2,6)).segment((-9,6)).segment((-9,4)).arc((-7,2),(-9,0)).close().assemble().finalize().extrude(-200)