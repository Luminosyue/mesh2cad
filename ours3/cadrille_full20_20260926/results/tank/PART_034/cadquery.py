import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-90))
w1=cq.Workplane('XY',origin=(0,0,-35))
r=w0.sketch().segment((-31,91),(-18,47)).arc((-82,-46),(26,-64)).segment((31,-75)).segment((31,-91)).segment((37,-91)).segment((37,-86)).segment((40,-84)).segment((37,-75)).segment((37,-69)).arc((82,24),(-16,64)).segment((-16,69)).segment((26,69)).segment((-13,100)).close().assemble().finalize().extrude(55).union(w0.workplane(offset=55/2).moveTo(-10,-11).cylinder(55,89)).union(w1.workplane(offset=-65/2).moveTo(-10,-11).cylinder(65,89))