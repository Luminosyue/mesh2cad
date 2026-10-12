import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,65))
w1=cq.Workplane('XY',origin=(0,0,75))
r=w0.sketch().segment((-100,-17),(-89,-17)).arc((99,11),(-91,-1)).segment((-100,-1)).close().assemble().push([(7,1)]).circle(34,mode='s').finalize().extrude(-144).union(w0.sketch().segment((-76,49),(10,49)).segment((10,87)).segment((-32,87)).arc((-43,83),(-54,87)).segment((-76,87)).close().assemble().finalize().extrude(2)).union(w1.sketch().arc((-89,-19),(69,-69),(1,95)).arc((-10,-31),(-89,-19)).assemble().finalize().extrude(-136))