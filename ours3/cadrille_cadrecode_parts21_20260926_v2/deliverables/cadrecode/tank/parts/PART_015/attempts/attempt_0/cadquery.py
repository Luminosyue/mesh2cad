import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('XY',origin=(0,0,-30))
r=w0.sketch().arc((-40,-85),(-11,-98),(20,-93)).arc((10,98),(-40,-85)).assemble().finalize().extrude(55).union(w0.workplane(offset=59/2).moveTo(-1,32).cylinder(59,60)).union(w1.sketch().arc((-79,-16),(-42,-68),(22,-85)).arc((23,-73),(29,-63)).segment((29,-62)).segment((30,-62)).arc((43,-54),(54,-45)).arc((45,-47),(36,-48)).arc((15,-60),(-10,-62)).segment((-10,-63)).arc((-23,-73),(-36,-84)).arc((-39,-83),(-41,-81)).arc((-64,-54),(-79,-16)).assemble().finalize().extrude(57))