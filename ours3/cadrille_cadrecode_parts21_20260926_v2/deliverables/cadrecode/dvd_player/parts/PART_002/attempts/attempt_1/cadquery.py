import cadquery as cq
w0=cq.Workplane('YZ',origin=(-99,0,0))
w1=cq.Workplane('XY',origin=(0,0,-11))
r=w0.sketch().segment((-15,17),(-14,15)).arc((-24,-10),(-1,-17)).segment((24,-18)).segment((22,1)).close().assemble().finalize().extrude(198).union(w1.sketch().segment((-100,-14),(-99,-14)).arc((-99,-13),(-100,-12)).close().assemble().finalize().extrude(-6))