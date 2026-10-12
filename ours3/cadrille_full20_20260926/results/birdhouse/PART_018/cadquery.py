import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('YZ',origin=(93,0,0))
r=w0.sketch().segment((-100,-97),(-99,-100)).segment((-97,-99)).segment((-97,-96)).segment((-73,-96)).segment((-74,-94)).arc((-87,-94),(-99,-95)).segment((-99,-97)).close().assemble().finalize().extrude(-194).union(w1.sketch().arc((-97,-40),(-100,-68),(-94,-96)).arc((-97,-68),(-97,-40)).close().assemble().finalize().extrude(-20))