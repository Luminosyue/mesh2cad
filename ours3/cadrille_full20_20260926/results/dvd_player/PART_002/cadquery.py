import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
r=w0.sketch().segment((-100,-99),(-52,-100)).segment((-52,-91)).segment((-53,-91)).segment((-53,-83)).segment((-90,-65)).segment((-91,-67)).arc((-98,-78),(-100,-91)).close().assemble().reset().face(w0.sketch().segment((-69,-99),(-68,-100)).segment((-67,-99)).segment((-68,-98)).close().assemble(),mode='s').finalize().extrude(198)