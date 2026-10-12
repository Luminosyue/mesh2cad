import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-31))
w1=cq.Workplane('ZX',origin=(0,-44,0))
r=w0.sketch().segment((-84,3),(-21,-100)).segment((60,-51)).segment((58,-48)).arc((49,69),(-61,52)).segment((-63,50)).segment((-62,49)).arc((-71,27),(-73,3)).close().assemble().finalize().extrude(49).union(w0.sketch().push([(4,31)]).circle(69).circle(48,mode='s').finalize().extrude(52)).union(w0.workplane(offset=63/2).moveTo(-8,-84).cylinder(63,15)).union(w1.workplane(offset=144/2).moveTo(0,8).cylinder(144,26))