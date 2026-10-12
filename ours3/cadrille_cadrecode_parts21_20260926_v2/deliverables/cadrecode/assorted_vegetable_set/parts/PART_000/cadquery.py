import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,7))
w1=cq.Workplane('XY',origin=(0,0,6))
r=w0.sketch().segment((-28,96),(-2,-94)).segment((1,-94)).arc((21,-94),(19,-73)).segment((5,-10)).arc((26,15),(10,41)).segment((10,42)).arc((14,47),(16,53)).segment((17,53)).segment((5,95)).segment((1,94)).arc((-11,100),(-24,97)).close().assemble().finalize().extrude(-14).union(w1.sketch().arc((-19,26),(2,1),(15,31)).arc((-3,73),(-19,26)).assemble().finalize().extrude(-10))