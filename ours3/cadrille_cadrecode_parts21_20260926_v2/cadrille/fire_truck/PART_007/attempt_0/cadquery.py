import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,11))
w1=cq.Workplane('ZX',origin=(0,-57,0))
r=w0.workplane(offset=-94/2).moveTo(7,-5).cylinder(94,22).union(w0.workplane(offset=-82/2).moveTo(7,-5).cylinder(82,38)).union(w0.sketch().arc((-30,-94),(-16,-96),(-2,-98)).arc((28,96),(-30,-94)).assemble().finalize().extrude(64)).union(w1.sketch().arc((13,-90),(66,-78),(80,-25)).arc((21,12),(13,-59)).close().assemble().finalize().extrude(142))