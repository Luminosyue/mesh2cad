import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-99))
w1=cq.Workplane('YZ',origin=(61,0,0))
r=w0.sketch().arc((-100,-5),(-99,-19),(-95,-33)).arc((99,3),(-98,10)).arc((-99,8),(-100,5)).segment((-99,5)).arc((-98,0),(-96,-5)).close().assemble().push([(1,-4)]).circle(93,mode='s').finalize().extrude(118).union(w1.sketch().push([(0,-40)]).circle(60).circle(56,mode='s').finalize().extrude(-129))