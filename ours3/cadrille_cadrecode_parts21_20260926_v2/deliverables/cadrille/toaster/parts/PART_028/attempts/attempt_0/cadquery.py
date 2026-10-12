import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-45,-39),(-42,-39)).arc((-1,-100),(40,-39)).segment((44,-39)).segment((44,59)).segment((41,59)).arc((0,100),(-41,59)).segment((-45,59)).close().assemble().finalize().extrude(-2)