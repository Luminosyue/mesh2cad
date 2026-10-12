import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,28))
w1=cq.Workplane('XY',origin=(0,0,27))
r=w0.sketch().arc((-15,1),(-1,-100),(15,1)).segment((15,100)).segment((20,94)).segment((-15,70)).close().assemble().push([(0,-39)]).circle(41,mode='s').finalize().extrude(-56).union(w0.sketch().push([(0,-39)]).circle(56).circle(30,mode='s').finalize().extrude(-37)).union(w1.sketch().arc((-1,79),(-1,-96),(1,79)).arc((0,77),(-1,79)).assemble().push([(0,-39)]).circle(41,mode='s').finalize().extrude(-54))