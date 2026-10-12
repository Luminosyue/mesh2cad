import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('YZ',origin=(92,0,0))
r=w0.sketch().segment((-99,-60),(-98,-100)).segment((100,-95)).segment((99,-58)).close().assemble().finalize().extrude(-197).union(w1.sketch().push([(0,-79)]).circle(21).push([(-10,-80)]).circle(10,mode='s').finalize().extrude(-192))