import cadquery as cq
w0=cq.Workplane('YZ',origin=(-43,0,0))
w1=cq.Workplane('XY',origin=(0,0,-18))
r=w0.sketch().segment((-68,-1),(-59,-1)).arc((-52,-2),(-45,-1)).segment((-36,-1)).arc((-13,-16),(10,-1)).segment((54,-1)).segment((54,17)).segment((10,17)).arc((-13,24),(-36,17)).segment((-68,17)).close().assemble().finalize().extrude(139).union(w0.sketch().push([(82,-14)]).circle(19).circle(11,mode='s').finalize().extrude(73)).union(w1.sketch().arc((-43,68),(31,-95),(-26,75)).arc((-33,70),(-43,68)).assemble().push([(0,-16)]).circle(63,mode='s').finalize().extrude(51))