import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,33))
w1=cq.Workplane('XY',origin=(0,0,27))
r=w0.sketch().segment((-100,23),(-98,22)).arc((-68,-25),(-13,-45)).segment((-11,-46)).segment((-10,-45)).arc((31,-53),(66,-35)).segment((94,-45)).segment((100,-45)).arc((49,-39),(4,-31)).segment((-1,-28)).segment((-1,-29)).arc((-31,26),(-86,45)).segment((-88,46)).close().assemble().push([(-62,16)]).circle(21,mode='s').finalize().extrude(-67).union(w1.sketch().arc((-45,56),(-77,-19),(-36,52)).arc((-37,58),(-45,56)).assemble().push([(-62,16)]).circle(20,mode='s').finalize().extrude(-53))