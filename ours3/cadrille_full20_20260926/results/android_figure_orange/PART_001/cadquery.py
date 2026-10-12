import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-47))
w1=cq.Workplane('XY',origin=(0,0,-48))
r=w0.sketch().segment((-71,11),(-34,-67)).segment((44,-30)).segment((7,48)).close().assemble().push([(-14,-10)]).circle(27,mode='s').finalize().extrude(-93).union(w0.sketch().arc((-62,55),(29,-88),(-56,58)).segment((-56,55)).close().assemble().finalize().extrude(146)).union(w1.sketch().push([(-14,-10)]).circle(84).circle(65,mode='s').finalize().extrude(147))