import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,99))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-100,-99),(-15,-99)).segment((-15,34)).segment((-100,34)).segment((-100,-39)).segment((-99,-39)).segment((-99,-41)).segment((-100,-41)).close().assemble().reset().face(w0.sketch().segment((-93,-99),(-25,-99)).segment((-25,-44)).arc((-20,-27),(-25,-10)).segment((-25,34)).segment((-93,34)).close().assemble(),mode='s').finalize().extrude(-198).union(w1.sketch().arc((-43,-99),(-29,-46),(-43,7)).close().assemble().finalize().extrude(-199))