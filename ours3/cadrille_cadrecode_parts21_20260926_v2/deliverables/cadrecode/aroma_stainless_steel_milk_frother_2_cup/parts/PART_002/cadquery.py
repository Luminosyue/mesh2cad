import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
w1=cq.Workplane('XY',origin=(0,0,2))
r=w0.sketch().arc((-88,42),(-99,-10),(-76,-62)).segment((-76,-69)).segment((-70,-69)).arc((-28,-93),(19,-96)).arc((1,-14),(97,-20)).arc((99,10),(90,40)).segment((90,47)).segment((85,47)).arc((0,98),(-85,47)).segment((-88,47)).close().assemble().push([(-35,17)]).circle(51,mode='s').finalize().extrude(-7).union(w1.sketch().push([(10,0)]).circle(90).circle(84,mode='s').finalize().extrude(-4))