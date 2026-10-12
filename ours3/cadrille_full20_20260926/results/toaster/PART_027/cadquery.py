import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-100,-96),(-97,-99)).segment((-95,-91)).arc((-98,-91),(-97,-89)).segment((-95,-67)).segment((-99,-66)).close().assemble().finalize().extrude(199).union(w0.workplane(offset=199/2).moveTo(-95,-85).cylinder(199,4))