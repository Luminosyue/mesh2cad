import cadquery as cq
w0=cq.Workplane('YZ',origin=(-70,0,0))
w1=cq.Workplane('YZ',origin=(-69,0,0))
r=w0.sketch().segment((-100,-1),(-97,-1)).arc((0,-97),(97,-17)).segment((99,-17)).segment((100,1)).segment((97,1)).arc((0,97),(-97,1)).segment((-99,1)).close().assemble().finalize().extrude(76).union(w0.workplane(offset=77/2).cylinder(77,98)).union(w1.sketch().arc((-68,14),(67,-59),(-11,85)).arc((-58,70),(-68,14)).assemble().finalize().extrude(76))