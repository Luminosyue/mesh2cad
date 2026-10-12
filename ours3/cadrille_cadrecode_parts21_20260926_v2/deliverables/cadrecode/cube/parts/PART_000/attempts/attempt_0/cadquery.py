import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,19))
w1=cq.Workplane('ZX',origin=(0,-41,0))
r=w0.sketch().arc((10,53),(10,73),(16,91)).arc((7,96),(10,100)).close().assemble().finalize().extrude(-38).union(w0.sketch().segment((-16,3),(3,-55)).segment((14,-52)).segment((-3,12)).close().assemble().finalize().extrude(-34)).union(w1.sketch().arc((-18,8),(0,9),(15,6)).arc((16,10),(16,14)).arc((-1,15),(-18,8)).assemble().finalize().extrude(-59))