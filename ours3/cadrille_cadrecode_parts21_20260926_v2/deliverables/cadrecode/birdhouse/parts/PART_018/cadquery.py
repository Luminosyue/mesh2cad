import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-18,0))
w1=cq.Workplane('YZ',origin=(98,0,0))
r=w0.sketch().segment((-31,-100),(-26,-100)).segment((-26,68)).segment((28,74)).segment((31,91)).segment((-29,100)).segment((-31,81)).close().assemble().finalize().extrude(2).union(w1.sketch().segment((-18,-28),(18,-27)).segment((18,-25)).segment((-18,-25)).close().assemble().finalize().extrude(-194))