import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-86,0))
w1=cq.Workplane('XY',origin=(0,0,12))
r=w0.workplane(offset=163/2).moveTo(2,0).box(2,70,163).union(w0.sketch().segment((-12,40),(-4,40)).segment((-4,39)).segment((12,52)).segment((11,54)).close().assemble().finalize().extrude(172)).union(w1.sketch().arc((-54,-91),(0,-95),(54,-91)).arc((56,-89),(56,-87)).arc((63,-52),(54,-17)).arc((0,-86),(-54,-17)).arc((-63,-54),(-54,-91)).assemble().reset().face(w1.sketch().arc((-54,82),(0,88),(54,82)).arc((0,99),(-54,82)).assemble()).finalize().extrude(-24))