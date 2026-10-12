import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-99,0))
w1=cq.Workplane('ZX',origin=(0,-100,0))
r=w0.sketch().segment((-24,-27),(-19,-27)).segment((-19,-34)).segment((19,-34)).segment((19,-27)).segment((24,-27)).segment((24,27)).segment((19,27)).segment((19,34)).segment((-19,34)).segment((-19,27)).segment((-24,27)).close().assemble().finalize().extrude(194).union(w1.sketch().arc((-23,-25),(0,-28),(23,-25)).segment((23,25)).segment((-23,25)).close().assemble().finalize().extrude(199))