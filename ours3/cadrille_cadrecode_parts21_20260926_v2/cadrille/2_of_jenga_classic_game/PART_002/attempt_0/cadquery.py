import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,99,0))
w1=cq.Workplane('ZX',origin=(0,100,0))
r=w0.sketch().segment((-23,-25),(-18,-25)).segment((-18,-35)).segment((18,-35)).segment((18,-25)).segment((23,-25)).segment((23,25)).segment((18,25)).segment((18,33)).segment((-18,34)).segment((-18,25)).segment((-23,25)).close().assemble().finalize().extrude(-198).union(w1.sketch().arc((-22,-28),(0,-33),(22,-28)).segment((22,28)).segment((-22,28)).close().assemble().finalize().extrude(-199))