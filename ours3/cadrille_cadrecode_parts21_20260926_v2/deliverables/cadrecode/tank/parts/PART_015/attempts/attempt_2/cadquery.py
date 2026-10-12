import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('XY',origin=(0,0,-30))
r=w0.workplane(offset=55/2).moveTo(0,3).cylinder(55,92).union(w0.sketch().segment((-82,-36),(-10,-36)).segment((-10,-100)).arc((41,85),(-82,-36)).assemble().finalize().extrude(55)).union(w1.sketch().arc((-62,26),(-57,-1),(-43,-23)).segment((-43,-13)).segment((-12,-13)).segment((-12,-23)).arc((10,-10),(20,13)).arc((22,81),(-43,72)).segment((-43,71)).arc((-57,50),(-62,26)).assemble().finalize().extrude(60))