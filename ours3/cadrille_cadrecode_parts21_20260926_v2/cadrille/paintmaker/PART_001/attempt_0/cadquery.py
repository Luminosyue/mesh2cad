import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('XY',origin=(0,0,-94))
r=w0.sketch().segment((-59,94),(-58,14)).arc((-61,-1),(-58,-16)).segment((-57,-96)).segment((60,-94)).segment((58,-14)).arc((61,1),(58,16)).segment((57,96)).close().assemble().finalize().extrude(-197).union(w1.sketch().segment((-100,-5),(-99,-5)).segment((-99,-59)).segment((99,-59)).segment((99,-5)).segment((100,-5)).segment((100,5)).segment((99,5)).segment((99,59)).segment((-99,59)).segment((-99,5)).segment((-100,5)).close().assemble().finalize().extrude(189))