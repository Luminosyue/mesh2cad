import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,16))
w1=cq.Workplane('XY',origin=(0,0,18))
r=w0.sketch().segment((-18,98),(-17,94)).arc((-20,73),(-12,54)).segment((-11,45)).arc((-10,44),(-10,43)).segment((-1,-15)).segment((20,-13)).segment((19,-2)).arc((1,41),(-10,93)).segment((-11,100)).close().assemble().finalize().extrude(-34).union(w1.sketch().arc((-14,-100),(-11,-89),(-10,-77)).arc((-12,-73),(-11,-69)).arc((-11,-67),(-10,-65)).arc((-18,-64),(-14,-69)).arc((-18,-84),(-14,-100)).assemble().finalize().extrude(-35))