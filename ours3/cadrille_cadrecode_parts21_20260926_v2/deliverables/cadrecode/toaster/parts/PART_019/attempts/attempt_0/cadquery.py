import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-95))
w1=cq.Workplane('XY',origin=(0,0,-100))
r=w0.sketch().arc((-17,14),(0,-14),(17,14)).segment((14,14)).arc((0,-9),(-13,14)).close().assemble().finalize().extrude(195).union(w1.sketch().arc((-10,-5),(10,-9),(10,13)).arc((10,10),(9,7)).arc((6,-7),(-10,-5)).assemble().finalize().extrude(193))