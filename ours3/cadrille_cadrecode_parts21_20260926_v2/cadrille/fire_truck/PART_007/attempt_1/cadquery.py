import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,17))
w1=cq.Workplane('ZX',origin=(0,-57,0))
r=w0.workplane(offset=-98/2).moveTo(8,-6).cylinder(98,28).union(w0.sketch().arc((-27,18),(12,-96),(94,-10)).arc((44,96),(-27,18)).assemble().finalize().extrude(58)).union(w0.sketch().arc((-66,78),(-98,-15),(-27,-90)).segment((-27,-95)).segment((1,-95)).segment((1,-90)).arc((72,-10),(19,84)).segment((19,95)).segment((-66,95)).close().assemble().finalize().extrude(65)).union(w1.workplane(offset=156/2).moveTo(44,-26).cylinder(156,37))