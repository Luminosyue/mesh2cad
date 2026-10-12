import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
w1=cq.Workplane('YZ',origin=(78,0,0))
r=w0.sketch().arc((84,-12),(99,3),(91,21)).close().assemble().finalize().extrude(21).union(w1.sketch().segment((-20,-11),(-15,-11)).arc((-14,-1),(-16,11)).arc((-18,0),(-20,-11)).assemble().finalize().extrude(-159))