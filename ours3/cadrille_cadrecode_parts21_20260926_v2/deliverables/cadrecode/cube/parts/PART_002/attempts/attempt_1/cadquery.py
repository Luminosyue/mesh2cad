import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,99,0))
r=w0.sketch().segment((-29,-93),(-17,-99)).segment((25,93)).segment((14,99)).close().assemble().finalize().extrude(-199).union(w0.sketch().segment((-7,-59),(-3,-59)).segment((-3,-4)).arc((7,8),(-3,20)).segment((-3,59)).segment((-7,59)).segment((-7,20)).arc((-15,8),(-7,-4)).close().assemble().finalize().extrude(-19))