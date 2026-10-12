import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('ZX',origin=(0,71,0))
r=w0.sketch().segment((-98,-74),(-94,-78)).segment((-90,-74)).segment((-94,-68)).close().assemble().finalize().extrude(145).union(w0.sketch().segment((-100,-68),(-98,-75)).segment((-93,-74)).segment((-95,-67)).close().assemble().finalize().extrude(149)).union(w1.sketch().arc((-94,-94),(-76,-97),(-93,-89)).arc((-91,-92),(-94,-94)).assemble().finalize().extrude(29))