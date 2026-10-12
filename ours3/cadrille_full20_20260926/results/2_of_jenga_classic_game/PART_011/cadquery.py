import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-99,-97),(-43,-100)).segment((-40,-10)).segment((-99,-7)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-99,-99),(-47,-99)).segment((-47,-4)).segment((-99,-4)).segment((-99,-54)).arc((-96,-56),(-99,-58)).close().assemble().finalize().extrude(-199))