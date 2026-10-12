import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
w1=cq.Workplane('XY',origin=(0,0,-18))
r=w0.sketch().segment((-18,99),(-16,92)).arc((-20,74),(-12,57)).segment((-11,50)).segment((-7,51)).arc((-3,54),(0,50)).segment((1,50)).segment((0,51)).arc((-12,83),(-18,99)).assemble().reset().face(w0.sketch().segment((-16,-98),(-10,-100)).segment((-8,-94)).arc((-11,-67),(3,-42)).segment((20,-1)).segment((14,1)).close().assemble()).finalize().extrude(35).union(w1.workplane(offset=34/2).moveTo(7,0).cylinder(34,13))