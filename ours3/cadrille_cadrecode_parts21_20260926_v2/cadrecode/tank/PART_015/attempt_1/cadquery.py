import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('ZX',origin=(0,-70,0))
r=w0.sketch().segment((-92,11),(-89,11)).arc((-88,10),(-87,9)).arc((86,-21),(-86,16)).arc((-88,15),(-89,14)).segment((-92,14)).close().assemble().finalize().extrude(55).union(w0.sketch().segment((-81,-1),(-55,-1)).arc((0,-55),(55,-1)).segment((81,-1)).segment((81,42)).segment((55,42)).arc((0,86),(-55,42)).segment((-81,42)).close().assemble().finalize().extrude(59)).union(w1.sketch().push([(0,-1)]).circle(31).circle(27,mode='s').finalize().extrude(169))