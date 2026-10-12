import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('ZX',origin=(0,-91,0))
r=w0.sketch().segment((-94,28),(-87,-85)).segment((-1,-80)).segment((-8,33)).arc((-48,-99),(-88,30)).close().assemble().finalize().extrude(7).union(w1.sketch().arc((-93,25),(-92,1),(-81,-20)).arc((-39,-91),(14,-25)).arc((23,-1),(22,25)).arc((-35,-100),(-93,25)).assemble().finalize().extrude(190))