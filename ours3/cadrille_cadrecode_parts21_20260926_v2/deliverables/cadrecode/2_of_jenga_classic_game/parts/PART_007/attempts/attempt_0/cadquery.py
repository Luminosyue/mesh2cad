import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,21))
w1=cq.Workplane('XY',origin=(0,0,21))
r=w0.sketch().segment((-100,-28),(-93,-28)).segment((-93,-93)).segment((96,-99)).segment((100,95)).segment((-95,100)).close().assemble().push([(0,1)]).circle(81,mode='s').finalize().extrude(-42).union(w1.sketch().segment((-96,37),(-68,37)).segment((-68,-96)).segment((94,-96)).segment((94,37)).segment((99,37)).segment((99,96)).segment((-96,96)).close().assemble().finalize().extrude(-41))