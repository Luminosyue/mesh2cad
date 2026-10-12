import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-77,7),(-81,-1),(-73,-8)).arc((-73,0),(-72,8)).arc((-75,8),(-77,7)).assemble().reset().face(w0.sketch().arc((-1,-8),(5,0),(1,8)).arc((-8,1),(-1,-8)).assemble()).push([(73,0)]).circle(8).finalize().extrude(-200)