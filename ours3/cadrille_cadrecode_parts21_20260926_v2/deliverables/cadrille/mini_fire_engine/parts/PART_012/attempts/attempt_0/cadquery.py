import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,32))
w1=cq.Workplane('XY',origin=(0,0,31))
r=w0.sketch().segment((-79,88),(-77,-46)).segment((-19,-45)).segment((-19,-99)).segment((80,-99)).segment((80,70)).segment((77,70)).segment((75,99)).close().assemble().finalize().extrude(-61).union(w1.sketch().arc((-29,-33),(-77,-73),(-15,-85)).arc((77,-26),(-29,-33)).assemble().finalize().extrude(-62))