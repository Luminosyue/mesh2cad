import cadquery as cq
w0=cq.Workplane('YZ',origin=(78,0,0))
w1=cq.Workplane('XY',origin=(0,0,-71))
r=w0.sketch().push([(-68,-82)]).circle(9).circle(5,mode='s').finalize().extrude(13).union(w1.sketch().segment((-100,-99),(-46,-99)).arc((35,-100),(96,-51)).arc((88,-47),(80,-48)).arc((30,-92),(-36,-91)).segment((-100,-91)).close().assemble().finalize().extrude(-29))