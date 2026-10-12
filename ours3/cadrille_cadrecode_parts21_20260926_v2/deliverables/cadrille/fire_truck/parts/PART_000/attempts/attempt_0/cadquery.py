import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,29))
w1=cq.Workplane('ZX',origin=(0,-54,0))
r=w0.sketch().circle(98).circle(60,mode='s').finalize().extrude(-94).union(w0.sketch().segment((-100,-2),(-95,-2)).arc((0,-98),(95,-2)).segment((100,-2)).segment((100,2)).segment((95,2)).arc((0,98),(-95,2)).segment((-100,2)).close().assemble().finalize().extrude(-88)).union(w1.workplane(offset=125/2).cylinder(125,79))