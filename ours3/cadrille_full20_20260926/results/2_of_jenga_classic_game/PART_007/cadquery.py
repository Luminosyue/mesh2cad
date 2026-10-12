import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-57))
w1=cq.Workplane('YZ',origin=(96,0,0))
r=w0.sketch().segment((-96,96),(-94,34)).arc((-99,-1),(-93,-36)).segment((-91,-98)).segment((96,-96)).segment((94,-34)).arc((99,1),(93,36)).segment((91,98)).close().assemble().circle(72,mode='s').finalize().extrude(-43).union(w1.sketch().push([(-1,-79)]).circle(21).push([(-1,-79.5)]).rect(28,19,mode='s').finalize().extrude(-189))