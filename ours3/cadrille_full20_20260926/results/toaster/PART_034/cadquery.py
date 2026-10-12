import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-88,0))
w1=cq.Workplane('XY',origin=(0,0,98))
r=w0.sketch().arc((-98,-55),(-96,-75),(-82,-90)).close().assemble().reset().face(w0.sketch().segment((-81,-37),(-50,-90)).arc((-52,-60),(-81,-37)).assemble()).reset().face(w0.sketch().segment((2,-90),(94,-55)).arc((47,-34),(2,-90)).assemble()).reset().face(w0.sketch().arc((34,-99),(81,-91),(98,-45)).close().assemble()).finalize().extrude(-9).union(w1.sketch().push([(-64,-93)]).circle(6).circle(4,mode='s').finalize().extrude(-189))